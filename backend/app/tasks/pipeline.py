"""Pipeline orchestrator — runs the full RAG document processing pipeline.

Flow:
    Upload → Parser → Summary → Classify → Embedding → Ready

Each stage commits independently with current_step tracking.
Failed stages record error_message for diagnostics and retry.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.crud.knowledge_document import get_document_by_id, update_document_status
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
        1. Parser       → file → plain text
        2. Summary      → text → AI summary
        3. Classify     → text → category labels
        4. Embedding    → text chunks → vectors

    current_step is updated at each stage so progress is visible.
    On any stage failure, error_message is set and pipeline continues.
    Re-running is safe — stages with success status are skipped.
    """
    doc = get_document_by_id(db, document_id)
    if doc is None:
        return {"document_id": document_id, "error": "文档不存在"}

    logger.info("Pipeline START for document_id=%d, title=%s, step=%s", doc.id, doc.title, doc.current_step)

    result: dict[str, Any] = {
        "document_id": doc.id,
        "parse_status": doc.parse_status,
        "summary_status": doc.summary_status,
        "classify_status": doc.classify_status,
        "embedding_status": doc.embedding_status,
        "current_step": doc.current_step,
        "summary_text": doc.summary_text,
    }

    # ── Stage 1: Parse ──────────────────────────
    if doc.parse_status != TaskStatus.SUCCESS:
        update_document_status(db, doc, current_step="parsed", error_message=None)
        try:
            doc = await run_parser_task(doc)
            update_document_status(
                db, doc,
                current_step="parsed" if doc.parse_status == TaskStatus.SUCCESS else "failed",
                parse_status=doc.parse_status,
                content_text=doc.content_text,
                page_count=doc.page_count,
                error_message=None if doc.parse_status == TaskStatus.SUCCESS else doc.content_text,
            )
        except Exception as exc:
            msg = str(exc)[:500]
            logger.exception("Parser stage exception: %s", exc)
            update_document_status(
                db, doc,
                current_step="failed",
                parse_status=TaskStatus.FAILED,
                error_message=msg,
            )
    else:
        logger.info("Parser already SUCCESS, skipping")

    result["parse_status"] = doc.parse_status
    result["current_step"] = doc.current_step

    # ── Stage 2: Summary ────────────────────────
    if doc.parse_status == TaskStatus.SUCCESS and doc.summary_status != TaskStatus.SUCCESS:
        update_document_status(db, doc, current_step="summarized", error_message=None)
        try:
            doc = await run_summary_task(doc)
            update_document_status(
                db, doc,
                current_step="summarized" if doc.summary_status == TaskStatus.SUCCESS else doc.current_step,
                summary_status=doc.summary_status,
                summary_text=doc.summary_text,
                error_message=None if doc.summary_status == TaskStatus.SUCCESS else doc.summary_text,
            )
        except Exception as exc:
            msg = str(exc)[:500]
            logger.exception("Summary stage exception: %s", exc)
            update_document_status(
                db, doc,
                current_step="failed",
                summary_status=TaskStatus.FAILED,
                error_message=msg,
            )
    result["summary_status"] = doc.summary_status
    result["summary_text"] = doc.summary_text

    # ── Stage 3: Classify ───────────────────────
    if not skip_classification and doc.summary_status in (TaskStatus.SUCCESS, TaskStatus.WAITING):
        if doc.classify_status != TaskStatus.SUCCESS:
            update_document_status(db, doc, current_step="classified", error_message=None)
            try:
                doc = await run_classification_task(doc, categories)
                update_document_status(
                    db, doc,
                    current_step="classified" if doc.classify_status == TaskStatus.SUCCESS else doc.current_step,
                    classify_status=doc.classify_status,
                    error_message=None if doc.classify_status == TaskStatus.SUCCESS else "分类失败",
                )
            except Exception as exc:
                msg = str(exc)[:500]
                logger.exception("Classify stage exception: %s", exc)
                update_document_status(
                    db, doc,
                    current_step="failed",
                    classify_status=TaskStatus.FAILED,
                    error_message=msg,
                )
    result["classify_status"] = doc.classify_status

    # ── Stage 4: Embedding ──────────────────────
    if doc.embedding_status != TaskStatus.SUCCESS:
        update_document_status(db, doc, current_step="embedded", error_message=None)
        try:
            doc = await run_embedding_task(doc)
            step = "ready" if doc.embedding_status == TaskStatus.SUCCESS else doc.current_step
            update_document_status(
                db, doc,
                current_step=step,
                embedding_status=doc.embedding_status,
                error_message=None if doc.embedding_status == TaskStatus.SUCCESS else "向量化失败",
            )
        except Exception as exc:
            msg = str(exc)[:500]
            logger.exception("Embedding stage exception: %s", exc)
            update_document_status(
                db, doc,
                current_step="failed",
                embedding_status=TaskStatus.FAILED,
                error_message=msg,
            )
    else:
        # Already embedded → mark ready
        if doc.current_step not in ("ready", "failed"):
            update_document_status(db, doc, current_step="ready")
    result["embedding_status"] = doc.embedding_status
    result["current_step"] = doc.current_step

    if all(
        s == TaskStatus.SUCCESS
        for s in [doc.parse_status, doc.summary_status, doc.embedding_status]
    ):
        update_document_status(db, doc, current_step="ready", error_message=None)
        result["current_step"] = "ready"

    logger.info(
        "Pipeline END for document_id=%d step=%s statuses=%s",
        doc.id, doc.current_step,
        {k: v for k, v in result.items() if k.endswith("status")},
    )
    return result


async def run_single_task(
    document_id: int,
    db: Session,
    task_name: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a single task stage independently (for retries)."""
    doc = get_document_by_id(db, document_id)
    if doc is None:
        return {"document_id": document_id, "error": "文档不存在"}

    step_map = {
        "parser": "parsed",
        "summary": "summarized",
        "classify": "classified",
        "embedding": "embedded",
    }
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
    new_step = step_map.get(task_name, doc.current_step)
    update_document_status(db, doc, current_step=new_step, error_message=None)

    try:
        updated_doc = await task_fn(doc, **kwargs)

        status_kwargs: dict[str, Any] = {"current_step": new_step, "error_message": None}
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
            if updated_doc.embedding_status == TaskStatus.SUCCESS:
                status_kwargs["current_step"] = "ready"

        update_document_status(db, doc, **status_kwargs)
        logger.info("Single task '%s' SUCCESS for document_id=%d", task_name, doc.id)

        return {"document_id": doc.id, "task": task_name, "status": "success"}
    except Exception as exc:
        msg = str(exc)[:500]
        logger.exception("Single task '%s' FAILED: %s", task_name, exc)
        update_document_status(
            db, doc,
            current_step="failed",
            error_message=msg,
        )
        return {
            "document_id": doc.id,
            "task": task_name,
            "status": "failed",
            "error": msg,
        }
