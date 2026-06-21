"""DeepSeek AI provider — OpenAI-compatible API via deepseek-chat."""

import hashlib
import logging
import math
from typing import Any

from openai import AsyncOpenAI

from app.ai.interfaces import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


def _simple_embed(texts: list[str], dim: int = 1536) -> list[list[float]]:
    """Zero-dependency hash-based text embedding.

    Produces non-zero, content-dependent vectors without external APIs.
    Uses character trigram hashing + L2 normalization.
    Similar texts produce vectors with higher cosine similarity.
    """
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


class DeepSeekProvider(AIProvider):
    """DeepSeek provider using OpenAI-compatible API.

    Chat/generate → DeepSeek API (deepseek-chat)
    Embedding    → hash-based simple embedding (zero-dependency)
    """

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self._chat_model = settings.DEEPSEEK_CHAT_MODEL

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=self._chat_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=self._chat_model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def embedding(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Hash-based embedding — zero dependencies, always works."""
        return _simple_embed(texts)

    def is_available(self) -> bool:
        return bool(settings.DEEPSEEK_API_KEY)
