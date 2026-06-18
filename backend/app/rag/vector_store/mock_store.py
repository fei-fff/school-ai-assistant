"""Mock vector store — in-memory dict implementation for development.

Not suitable for production but allows the full RAG pipeline to run
without any external dependencies.
"""

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
