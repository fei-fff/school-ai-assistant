"""Parser task stub — parse uploaded files into plain text."""

import logging

from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_parser_task(document_id: int) -> dict:
    """Parse an uploaded document into plain text.

    TODO: Implement actual parsing pipeline:
    1. Fetch document by ID
    2. Detect file type from mime_type
    3. Parse:
       - PDF  → PyMuPDF / pdfplumber
       - DOCX → python-docx
       - TXT  → direct read
       - CSV  → pandas
       - PPTX → python-pptx
    4. Save parsed text to content_text field
    5. Calculate page_count
    6. Update parse_status to SUCCESS or FAILED
    """
    logger.info("Parser task stub called for document_id=%d", document_id)
    return {"status": TaskStatus.WAITING, "document_id": document_id}
