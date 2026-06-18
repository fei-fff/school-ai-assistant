"""Vector store package — backward-compatible re-exports.

Old import (still works):
    from app.rag.vector_store import VectorStore, Chunk, SearchResult, vector_store

New imports (preferred):
    from app.rag.vector_store import get_vector_store
    from app.rag.vector_store.base import VectorStore, Chunk, SearchResult
    from app.rag.vector_store.chroma_store import ChromaDBStore
    from app.rag.vector_store.mock_store import MockDictStore
"""

from app.rag.vector_store.base import Chunk, SearchResult, VectorStore
from app.rag.vector_store.factory import get_vector_store, reset_vector_store
from app.rag.vector_store.mock_store import MockDictStore

# Backward-compatible singleton alias — consumers that import `vector_store`
# will get the real singleton from factory when accessed via this lazy wrapper.
# New code should use get_vector_store() directly for clarity.
vector_store = get_vector_store()

__all__ = [
    "VectorStore",
    "MockDictStore",
    "Chunk",
    "SearchResult",
    "get_vector_store",
    "reset_vector_store",
    "vector_store",          # backward-compat
]
