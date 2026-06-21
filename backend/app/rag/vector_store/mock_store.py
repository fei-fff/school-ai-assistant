"""Mock vector store — in-memory dict implementation for development."""

from typing import Any

from app.rag.vector_store.base import (
    Chunk,
    SearchResult,
    VectorStore,
    _cosine_similarity,
)


class MockDictStore(VectorStore):
    """In-memory vector store backed by a Python dict.

    Uses cosine similarity for search. All data is lost on restart.
    """

    def __init__(self):
        self._chunks: dict[str, Chunk] = {}

    async def add(self, chunks: list[Chunk]) -> int:
        added = 0
        for chunk in chunks:
            self._chunks[chunk.id] = chunk
            added += 1
        return added

    async def search(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[SearchResult]:
        if not self._chunks:
            return []

        results: list[SearchResult] = []
        for chunk in self._chunks.values():
            score = _cosine_similarity(query_embedding, chunk.embedding)
            results.append(SearchResult(chunk=chunk, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    async def delete_by_document(self, document_id: int) -> int:
        to_delete = [
            cid
            for cid, chunk in self._chunks.items()
            if chunk.document_id == document_id
        ]
        for cid in to_delete:
            del self._chunks[cid]
        return len(to_delete)

    async def count(self) -> int:
        return len(self._chunks)

    async def get_details(self) -> dict[str, Any]:
        chunk_ids = list(self._chunks.keys())[:10]
        norms = [c.vector_norm() for c in list(self._chunks.values())[:5]]
        return {
            "backend": "mock",
            "total_chunks": len(self._chunks),
            "chunk_ids_sample": chunk_ids,
            "vector_norms_sample": [round(n, 4) for n in norms],
            "has_zero_vectors": any(n == 0.0 for n in norms),
            "provider_type": self.__class__.__name__,
        }
