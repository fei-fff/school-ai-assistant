"""Vector store abstract base — data classes and abstract interface."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """A single text chunk with its embedding and metadata."""

    id: str
    document_id: int
    content: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    """A single search hit returned by vector search."""

    chunk: Chunk
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk.id,
            "document_id": self.chunk.document_id,
            "content": self.chunk.content,
            "score": round(self.score, 4),
            "metadata": self.chunk.metadata,
        }


class VectorStore(ABC):
    """Abstract interface for vector storage and retrieval.

    Implement this interface to swap backends:
        - MockDictStore (in-memory dict, for development)
        - ChromaDBStore  (persistent, production-ready)
        - MilvusStore    (distributed, large-scale)
        - PineconeStore  (cloud-hosted)
    """

    @abstractmethod
    async def add(self, chunks: list[Chunk]) -> int:
        """Store chunks with their embeddings. Returns number of chunks added."""
        ...

    @abstractmethod
    async def search(
        self, query_embedding: list[float], top_k: int = 5
    ) -> list[SearchResult]:
        """Return the top_k most similar chunks to the query embedding."""
        ...

    @abstractmethod
    async def delete_by_document(self, document_id: int) -> int:
        """Remove all chunks belonging to a document. Returns count deleted."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Total number of chunks in the store."""
        ...


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        raise ValueError(f"Vector dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
