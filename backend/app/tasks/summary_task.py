"""Summary task — generate AI summaries for parsed documents."""

import logging

from app.ai.service import ai_service
from app.models.knowledge_document import KnowledgeDocument
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_summary_task(doc: KnowledgeDocument) -> KnowledgeDocument:
    """Generate an AI summary for a knowledge document.

    Requires doc.content_text to be populated (parser must run first).
    Updates doc.summary_status, doc.summary_text.

    Returns the same ORM object (caller must commit).
    """
    logger.info("Summary task started for document_id=%d", doc.id)
    doc.summary_status = TaskStatus.PROCESSING

    try:
        if not doc.content_text:
            raise ValueError("文档内容为空，可能解析未完成")

        summary = await ai_service.summarize(doc.content_text)
        doc.summary_text = summary
        doc.summary_status = TaskStatus.SUCCESS
        logger.info(
            "Summary task SUCCESS for document_id=%d, len=%d",
            doc.id,
            len(summary),
        )
    except Exception as exc:
        logger.error("Summary task FAILED for document_id=%d: %s", doc.id, exc)
        doc.summary_status = TaskStatus.FAILED
        doc.summary_text = f"[摘要失败] {exc}"

    return doc
