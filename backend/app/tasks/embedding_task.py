"""Embedding task — vectorize document text chunks and store in vector DB."""

import logging

from app.ai.service import ai_service
from app.models.knowledge_document import KnowledgeDocument
from app.rag.vector_store import Chunk, vector_store
from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)

# Approximate chunk size in characters (about 512 tokens for Chinese text).
CHUNK_SIZE = 1500


async def run_embedding_task(
    doc: KnowledgeDocument,
    chunk_size: int = CHUNK_SIZE,
) -> KnowledgeDocument:
    """Generate embeddings for a document's text chunks and store in vector DB.

    Requires doc.content_text to be populated.
    Updates doc.embedding_status.

    The chunks are persisted to the global vector_store so they become
    searchable by the KnowledgeQA pipeline.

    Args:
        doc: The KnowledgeDocument ORM object.
        chunk_size: Characters per chunk (default 1500 approx 512 tokens).

    Returns:
        The same ORM object (caller must commit).
    """
    logger.info("Embedding task started for document_id=%d", doc.id)
    doc.embedding_status = TaskStatus.PROCESSING

    try:
        if not doc.content_text:
            raise ValueError("文档内容为空，可能解析未完成")

        # Split text into overlapping chunks
        raw_chunks = _split_text(doc.content_text, chunk_size=chunk_size, overlap=200)
        logger.info(
            "Document_id=%d split into %d chunks (chunk_size=%d)",
            doc.id,
            len(raw_chunks),
            chunk_size,
        )

        # Generate embeddings via AIService
        vectors = await ai_service.embed(raw_chunks)
        logger.info(
            "Generated %d embeddings for document_id=%d (dim=%d)",
            len(vectors),
            doc.id,
            len(vectors[0]) if vectors else 0,
        )

        # Build Chunk objects and store in vector store
        chunks: list[Chunk] = []
        for i, (text, vec) in enumerate(zip(raw_chunks, vectors)):
            chunk = Chunk(
                id=f"doc{doc.id}_chunk{i}",
                document_id=doc.id,
                content=text,
                embedding=vec,
                metadata={
                    "document_id": doc.id,
                    "chunk_index": i,
                    "total_chunks": len(raw_chunks),
                    "title": doc.title,
                    "file_name": doc.file_name,
                },
            )
            chunks.append(chunk)

        added = await vector_store.add(chunks)
        logger.info(
            "Stored %d chunks in vector store for document_id=%d",
            added,
            doc.id,
        )

        doc.embedding_status = TaskStatus.SUCCESS
    except Exception as exc:
        logger.error("Embedding task FAILED for document_id=%d: %s", doc.id, exc)
        doc.embedding_status = TaskStatus.FAILED

    return doc


# ── Internal helpers ────────────────────────────────


def _split_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks of approximately chunk_size chars."""
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
