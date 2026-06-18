"""Embedding task stub — vectorize document text chunks."""

import logging

from app.utils.enums import TaskStatus

logger = logging.getLogger(__name__)


async def run_embedding_task(document_id: int) -> dict:
    """Generate embeddings for a knowledge document.

    TODO: Implement actual embedding pipeline:
    1. Fetch document by ID
    2. Split text into chunks (e.g. 512 tokens each)
    3. Call AIClient.embedding() for each chunk
    4. Store vectors in ChromaDB / Milvus / Pinecone
    5. Update embedding_status to SUCCESS or FAILED
    """
    logger.info("Embedding task stub called for document_id=%d", document_id)
    # Placeholder
    return {"status": TaskStatus.WAITING, "document_id": document_id}
