"""Parser task — parse uploaded files into plain text."""

import logging
from pathlib import Path

from app.models.knowledge_document import KnowledgeDocument
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)

# File-size threshold for AI context (characters). Documents larger than
# this are truncated before passing downstream to summary/classify.
MAX_CONTENT_LENGTH = 32_000


async def run_parser_task(doc: KnowledgeDocument) -> KnowledgeDocument:
    """Parse a knowledge document's file into plain text.

    Updates doc.parse_status, doc.content_text, doc.page_count in-place
    and returns the same ORM object (caller must commit outside if needed).

    Supported formats (via mime_type detection):
        text/plain          — direct read
        application/pdf     — placeholder (TODO: PyMuPDF / pdfplumber)
        application/ms-word — placeholder (TODO: python-docx)
        text/csv            — direct read
        text/markdown       — direct read
    """
    logger.info("Parser task started for document_id=%d, file=%s", doc.id, doc.file_name)
    doc.parse_status = TaskStatus.PROCESSING

    try:
        file_path = Path(doc.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {doc.file_path}")

        mime = (doc.mime_type or "").lower()
        text = _read_text_file(file_path)

        # Truncate if too large for downstream AI processing
        if len(text) > MAX_CONTENT_LENGTH:
            logger.info(
                "Document content truncated from %d to %d chars",
                len(text),
                MAX_CONTENT_LENGTH,
            )
            text = text[:MAX_CONTENT_LENGTH]

        doc.content_text = text
        doc.page_count = _estimate_page_count(text)
        doc.parse_status = TaskStatus.SUCCESS
        logger.info(
            "Parser task SUCCESS for document_id=%d, chars=%d, pages=%d",
            doc.id,
            len(text),
            doc.page_count,
        )
    except Exception as exc:
        logger.error("Parser task FAILED for document_id=%d: %s", doc.id, exc)
        doc.parse_status = TaskStatus.FAILED
        doc.content_text = f"[解析失败] {exc}"

    return doc


# ── Internal helpers ────────────────────────────────


def _read_text_file(file_path: Path) -> str:
    """Read a text file with encoding detection fallback."""
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding="gbk")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1")


def _estimate_page_count(text: str) -> int:
    """Estimate page count — assumes ~3000 chars per page."""
    CHARS_PER_PAGE = 3000
    return max(1, len(text) // CHARS_PER_PAGE)
