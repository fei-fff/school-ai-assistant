"""RAG module — vector store and retrieval-augmented generation.

Public API:
    from app.rag import vector_store, KnowledgeQA, knowledge_qa
    from app.rag.vector_store import get_vector_store, VectorStore, Chunk, SearchResult

To swap vector store backend:
    Set VECTOR_DB=chroma in .env — no code changes needed.
"""

from app.rag.vector_store import (
    Chunk,
    MockDictStore,
    SearchResult,
    VectorStore,
    get_vector_store,
    vector_store,
)
from app.rag.retrieval import KnowledgeQA, knowledge_qa

__all__ = [
    "VectorStore",
    "MockDictStore",
    "Chunk",
    "SearchResult",
    "get_vector_store",
    "vector_store",
    "KnowledgeQA",
    "knowledge_qa",
]
