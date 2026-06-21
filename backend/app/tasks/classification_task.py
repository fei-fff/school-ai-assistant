"""Classification task — auto-classify documents into knowledge categories."""

import json
import logging

from app.ai.service import ai_service
from app.models.knowledge_document import KnowledgeDocument
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_classification_task(
    doc: KnowledgeDocument,
    categories: list[str] | None = None,
) -> KnowledgeDocument:
    """Auto-classify a document into knowledge categories.

    Requires doc.content_text to be populated.
    Updates doc.classify_status.
    """
    DEFAULT_CATEGORIES = [
        "计算机科学", "数学", "物理学", "化学", "生物学",
        "经济学", "管理学", "文学", "历史学", "哲学",
        "法学", "教育学", "心理学", "医学", "工程技术",
    ]

    cats = categories or DEFAULT_CATEGORIES
    logger.info("Classification task started for document_id=%d, categories=%d", doc.id, len(cats))
    doc.classify_status = TaskStatus.PROCESSING

    try:
        if not doc.content_text:
            raise ValueError("文档内容为空，可能解析未完成")

        snippet = doc.content_text[:8000]
        result = await ai_service.classify(snippet, cats)

        # result is guaranteed to be a dict from AIService.classify
        classification_json = json.dumps(result, ensure_ascii=False)
        logger.info(
            "Classification task SUCCESS for document_id=%d: %s",
            doc.id,
            classification_json[:300],
        )
        doc.classify_status = TaskStatus.SUCCESS
    except Exception as exc:
        logger.error("Classification task FAILED for document_id=%d: %s", doc.id, exc)
        doc.classify_status = TaskStatus.FAILED

    return doc
