"""Parser task — parse uploaded files into plain text."""

import logging
from pathlib import Path

from app.core.config import settings
from app.models.knowledge_document import KnowledgeDocument
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_parser_task(doc: KnowledgeDocument) -> KnowledgeDocument:
    """Parse file into plain text."""
    logger.info("Parser task started for document_id=%d, file=%s", doc.id, doc.file_name)
    doc.parse_status = TaskStatus.PROCESSING

    try:
        file_path = Path(doc.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {doc.file_path}")

        text = _read_text_file(file_path)
        max_len = settings.PARSER_MAX_CONTENT_LENGTH
        if len(text) > max_len:
            logger.info("Truncated from %d to %d chars", len(text), max_len)
            text = text[:max_len]

        doc.content_text = text
        doc.page_count = max(1, len(text) // 3000)
        doc.parse_status = TaskStatus.SUCCESS
        logger.info("Parser SUCCESS: %d chars, %d pages", len(text), doc.page_count)
    except Exception as exc:
        logger.error("Parser FAILED: %s", exc)
        doc.parse_status = TaskStatus.FAILED
        doc.content_text = f"[Parse error] {exc}"
    return doc


def _read_text_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding="gbk")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1")
