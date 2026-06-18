"""Pipeline orchestrator — runs the full RAG document processing pipeline.

Flow:
    Document Upload → Parser → Summary → Classify → Embedding

The orchestrator commits after each stage so that partial progress is
persisted even if a later stage fails. Each task is a standalone async
function that can also be retried independently.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.crud.knowledge_document import get_document_by_id, update_document_status
from app.models.knowledge_document import KnowledgeDocument
from app.tasks.parser_task import run_parser_task
from app.tasks.summary_task import run_summary_task
from app.tasks.classification_task import run_classification_task
from app.tasks.embedding_task import run_embedding_task
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_pipeline(
    document_id: int,
    db: Session,
    *,
    categories: list[str] | None = None,
    skip_classification: bool = False,
) -> dict[str, Any]:
    """Run the full RAG processing pipeline on a single document.

    Stages (sequential, commits after each):
        1. Parser       — file → plain text
        2. Summary      — text → AI summary
        3. Classify     — text → category labels
        4. Embedding    — text chunks → vectors

    Args:
        document_id: The KnowledgeDocument primary key.
        db: Active SQLAlchemy session.
        categories: Optional custom category list for classification.
        skip_classification: If True, skip the classify stage.

    Returns:
        Dict with final status of each stage and summary text.
    """
    doc = get_document_by_id(db, document_id)
    if doc is None:
        return {"document_id": document_id, "error": "文档不存在"}

    logger.info("Pipeline START for document_id=%d, title=%s", doc.id, doc.title)

    result: dict[str, Any] = {
        "document_id": doc.id,
        "parse_status": TaskStatus.WAITING,
        "summary_status": TaskStatus.WAITING,
        "classify_status": TaskStatus.WAITING,
        "embedding_status": TaskStatus.WAITING,
        "summary_text": None,
    }

    # ── Stage 1: Parse ──────────────────────────
    try:
        doc = await run_parser_task(doc)
        update_document_status(
            db,
            doc,
            parse_status=doc.parse_status,
            content_text=doc.content_text,
            page_count=doc.page_count,
        )
    except Exception as exc:
        logger.exception("Parser stage exception: %s", exc)
        doc.parse_status = TaskStatus.FAILED
        update_document_status(db, doc, parse_status=TaskStatus.FAILED)
    result["parse_status"] = doc.parse_status

    if doc.parse_status != TaskStatus.SUCCESS:
        result["error"] = "解析失败，流水线中止"
        return result

    # ── Stage 2: Summary ────────────────────────
    try:
        doc = await run_summary_task(doc)
        update_document_status(
            db,
            doc,
            summary_status=doc.summary_status,
            summary_text=doc.summary_text,
        )
    except Exception as exc:
        logger.exception("Summary stage exception: %s", exc)
        doc.summary_status = TaskStatus.FAILED
        update_document_status(db, doc, summary_status=TaskStatus.FAILED)
    result["summary_status"] = doc.summary_status
    result["summary_text"] = doc.summary_text

    # ── Stage 3: Classify ───────────────────────
    if not skip_classification:
        try:
            doc = await run_classification_task(doc, categories)
            update_document_status(db, doc, classify_status=doc.classify_status)
        except Exception as exc:
            logger.exception("Classify stage exception: %s", exc)
            doc.classify_status = TaskStatus.FAILED
            update_document_status(db, doc, classify_status=TaskStatus.FAILED)
    result["classify_status"] = doc.classify_status

    # ── Stage 4: Embedding ──────────────────────
    try:
        doc = await run_embedding_task(doc)
        update_document_status(db, doc, embedding_status=doc.embedding_status)
    except Exception as exc:
        logger.exception("Embedding stage exception: %s", exc)
        doc.embedding_status = TaskStatus.FAILED
        update_document_status(db, doc, embedding_status=TaskStatus.FAILED)
    result["embedding_status"] = doc.embedding_status

    logger.info("Pipeline END for document_id=%d statuses=%s", doc.id, result)
    return result


async def run_single_task(
    document_id: int,
    db: Session,
    task_name: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a single task stage independently (for retries or manual triggers).

    Args:
        document_id: The KnowledgeDocument primary key.
        db: Active SQLAlchemy session.
        task_name: One of "parser", "summary", "classify", "embedding".
        **kwargs: Passed to the task function.

    Returns:
        Status dict.
    """
    doc = get_document_by_id(db, document_id)
    if doc is None:
        return {"document_id": document_id, "error": "文档不存在"}

    task_map = {
        "parser": run_parser_task,
        "summary": run_summary_task,
        "classify": run_classification_task,
        "embedding": run_embedding_task,
    }

    task_fn = task_map.get(task_name)
    if task_fn is None:
        return {"error": f"未知任务: {task_name}，可选: {list(task_map.keys())}"}

    logger.info("Single task '%s' START for document_id=%d", task_name, doc.id)

    try:
        updated_doc = await task_fn(doc, **kwargs)

        # Persist status changes
        status_kwargs: dict[str, Any] = {}
        if task_name == "parser":
            status_kwargs["parse_status"] = updated_doc.parse_status
            status_kwargs["content_text"] = updated_doc.content_text
            status_kwargs["page_count"] = updated_doc.page_count
        elif task_name == "summary":
            status_kwargs["summary_status"] = updated_doc.summary_status
            status_kwargs["summary_text"] = updated_doc.summary_text
        elif task_name == "classify":
            status_kwargs["classify_status"] = updated_doc.classify_status
        elif task_name == "embedding":
            status_kwargs["embedding_status"] = updated_doc.embedding_status

        update_document_status(db, doc, **status_kwargs)
        logger.info("Single task '%s' SUCCESS for document_id=%d", task_name, doc.id)

        return {
            "document_id": doc.id,
            "task": task_name,
            "status": "success",
        }
    except Exception as exc:
        logger.exception("Single task '%s' FAILED for document_id=%d: %s", task_name, doc.id, exc)
        return {
            "document_id": doc.id,
            "task": task_name,
            "status": "failed",
            "error": str(exc),
        }
