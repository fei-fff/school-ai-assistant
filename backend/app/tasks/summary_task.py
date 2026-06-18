"""Summary task stub — generate AI summaries for uploaded documents."""

import logging

from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_summary_task(document_id: int) -> dict:
    """Generate an AI summary for a knowledge document.

    TODO: Implement actual summarization pipeline:
    1. Fetch document by ID
    2. Extract text content (content_text field)
    3. Call AIClient.summary()
    4. Save result to summary_text field
    5. Update summary_status to SUCCESS or FAILED
    """
    logger.info("Summary task stub called for document_id=%d", document_id)
    return {"status": TaskStatus.WAITING, "document_id": document_id}
