"""Vector store factory — returns the configured backend based on .env settings.

Supported backends:
    mock   → MockDictStore  (in-memory, zero-dependency)
    chroma → ChromaDBStore   (persistent, requires `pip install chromadb`)
"""

import logging

from app.core.config import settings
from app.rag.vector_store.base import VectorStore

logger = logging.getLogger(__name__)

# Module-level singleton — set once at startup.
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Return the configured VectorStore singleton.

    Reads VECTOR_DB from .env / settings:
        VECTOR_DB=mock   → MockDictStore  (default)
        VECTOR_DB=chroma → ChromaDBStore

    Set once and reused across all requests.
    """
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    backend = settings.VECTOR_DB.lower()
    logger.info("Initializing vector store backend: %s", backend)

    if backend == "chroma":
        from app.rag.vector_store.chroma_store import ChromaDBStore

        _vector_store = ChromaDBStore()
    else:
        # Default to mock
        from app.rag.vector_store.mock_store import MockDictStore

        _vector_store = MockDictStore()

    logger.info("Vector store initialized: %s", type(_vector_store).__name__)
    return _vector_store


def reset_vector_store() -> None:
    """Reset the singleton (useful for testing or runtime reconfiguration)."""
    global _vector_store
    _vector_store = None
    logger.info("Vector store singleton reset")
