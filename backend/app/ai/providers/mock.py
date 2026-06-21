"""Mock Provider — hash-based embedding + canned responses for development."""

import hashlib
import logging
import math
from typing import Any

from app.ai.base import BaseAIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


def _simple_embed(texts: list[str], dim: int = 1536) -> list[list[float]]:
    """Zero-dependency hash-based text embedding."""
    results: list[list[float]] = []
    for text in texts:
        vec = [0.0] * dim
        for i in range(len(text) - 2):
            trigram = text[i:i + 3]
            h = int(hashlib.md5(trigram.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        results.append(vec)
    return results


class MockProvider(BaseAIProvider):
    """Mock AI provider — works without any external API key."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return _simple_embed(texts, dim=settings.EMBEDDING_DIMENSION)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        last = messages[-1]["content"] if messages else ""
        return f"[Mock Chat] {len(messages)} messages, last: {last[:80]}..."

    async def summarize(self, text: str) -> str:
        preview = text[:200].replace("\n", " ")
        return f"[Mock Summary] {len(text)} chars. Preview: {preview}..."

    async def classify(self, text: str, categories: list[str]) -> dict[str, Any]:
        return {
            "primary_category": categories[0] if categories else "unknown",
            "categories": [
                {"name": c, "confidence": 0.85}
                for c in (categories[:2] if categories else [])
            ],
        }

    def is_available(self) -> bool:
        return True
