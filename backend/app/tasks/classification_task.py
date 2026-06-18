"""Classification task stub — auto-classify documents into categories."""

import logging

from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_classification_task(document_id: int) -> dict:
    """Auto-classify a document into knowledge categories.

    TODO: Implement actual classification pipeline:
    1. Fetch document by ID
    2. Extract text content
    3. Fetch available category tree
    4. Call AIClient.classify()
    5. Assign category_id on the document
    6. Update classify_status to SUCCESS or FAILED
    """
    logger.info("Classification task stub called for document_id=%d", document_id)
    return {"status": TaskStatus.WAITING, "document_id": document_id}
