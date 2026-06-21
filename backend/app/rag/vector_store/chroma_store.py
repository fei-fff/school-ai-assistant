"""ChromaDB vector store — persistent production-ready implementation."""

import logging
from typing import Any

from app.core.config import settings
from app.rag.vector_store.base import Chunk, SearchResult, VectorStore

logger = logging.getLogger(__name__)


class ChromaDBStore(VectorStore):
    """ChromaDB-backed vector store with persistent storage."""

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str = "campus_knowledge",
    ):
        self._persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self._collection_name = collection_name
        self._client = None
        self._collection = None

    async def _ensure_client(self):
        if self._client is not None:
            return
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb is not installed. Run: pip install chromadb\n"
                "Or switch to mock: set VECTOR_DB=mock in .env"
            )
        self._client = chromadb.PersistentClient(path=self._persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB initialized at %s, collection=%s, count=%d",
            self._persist_dir, self._collection_name, self._collection.count(),
        )

    async def add(self, chunks: list[Chunk]) -> int:
        await self._ensure_client()
        if not chunks:
            return 0
        ids = [c.id for c in chunks]
        embeddings = [c.embedding for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [{**c.metadata, "document_id": c.document_id} for c in chunks]
        self._collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        logger.info("ChromaDB added %d chunks", len(chunks))
        return len(chunks)

    async def search(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[SearchResult]:
        await self._ensure_client()
        if self._collection is None or self._collection.count() == 0:
            return []
        chroma_results = self._collection.query(
            query_embeddings=[query_embedding], n_results=top_k,
            include=["embeddings", "documents", "metadatas", "distances"],
        )
        results: list[SearchResult] = []
        if not chroma_results["ids"] or not chroma_results["ids"][0]:
            return results
        for i, chunk_id in enumerate(chroma_results["ids"][0]):
            distance = chroma_results["distances"][0][i]
            score = 1.0 - distance
            chunk = Chunk(
                id=chunk_id,
                document_id=chroma_results["metadatas"][0][i].get("document_id", 0),
                content=chroma_results["documents"][0][i] or "",
                embedding=chroma_results["embeddings"][0][i] if chroma_results["embeddings"] else [],
                metadata=chroma_results["metadatas"][0][i],
            )
            results.append(SearchResult(chunk=chunk, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    async def delete_by_document(self, document_id: int) -> int:
        await self._ensure_client()
        if self._collection is None:
            return 0
        existing = self._collection.get(where={"document_id": document_id}, include=["metadatas"])
        if not existing["ids"]:
            return 0
        self._collection.delete(ids=existing["ids"])
        deleted = len(existing["ids"])
        logger.info("ChromaDB deleted %d chunks for document_id=%d", deleted, document_id)
        return deleted

    async def count(self) -> int:
        await self._ensure_client()
        if self._collection is None:
            return 0
        return self._collection.count()

    async def get_details(self) -> dict[str, Any]:
        await self._ensure_client()
        c = self._collection.count() if self._collection else 0
        return {
            "backend": "chroma",
            "total_chunks": c,
            "collection_name": self._collection_name,
            "persist_dir": self._persist_dir,
            "provider_type": self.__class__.__name__,
        }
