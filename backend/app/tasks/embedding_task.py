"""Embedding task — vectorize document text chunks and store in vector DB."""

import logging

from app.ai.service import ai_service
from app.core.config import settings
from app.models.knowledge_document import KnowledgeDocument
from app.rag.vector_store import Chunk, vector_store
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_embedding_task(
    doc: KnowledgeDocument,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> KnowledgeDocument:
    """Generate embeddings and store in vector DB."""
    chunk_size = chunk_size or settings.EMBEDDING_CHUNK_SIZE
    overlap = overlap or settings.EMBEDDING_CHUNK_OVERLAP

    logger.info("Embedding task started for document_id=%d", doc.id)
    doc.embedding_status = TaskStatus.PROCESSING

    try:
        if not doc.content_text:
            raise ValueError("Content is empty")

        raw_chunks = _split_text(doc.content_text, chunk_size=chunk_size, overlap=overlap)
        logger.info("Document_id=%d split into %d chunks (chunk_size=%d)", doc.id, len(raw_chunks), chunk_size)

        vectors = await ai_service.embed(raw_chunks)
        logger.info("Generated %d embeddings (dim=%d)", len(vectors), len(vectors[0]) if vectors else 0)

        chunks = [
            Chunk(id=f"doc{doc.id}_chunk{i}", document_id=doc.id, content=text, embedding=vec,
                  metadata={"document_id": doc.id, "chunk_index": i, "total_chunks": len(raw_chunks),
                            "title": doc.title, "file_name": doc.file_name})
            for i, (text, vec) in enumerate(zip(raw_chunks, vectors))
        ]
        added = await vector_store.add(chunks)
        logger.info("Stored %d chunks in vector store", added)
        doc.embedding_status = TaskStatus.SUCCESS
    except Exception as exc:
        logger.error("Embedding FAILED: %s", exc)
        doc.embedding_status = TaskStatus.FAILED
    return doc


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
