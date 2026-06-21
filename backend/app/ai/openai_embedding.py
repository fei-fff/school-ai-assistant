"""OpenAI embedding provider — uses text-embedding-3-small or similar.

Set EMBEDDING_PROVIDER=openai in .env to activate.
Requires OPENAI_API_KEY to be configured.
"""

import logging
from typing import Any

from openai import AsyncOpenAI

from app.ai.interfaces import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(AIProvider):
    """OpenAI-only provider for text embeddings.

    This provider is specialized for embedding. Chat/generate methods
    fall back to mock since the primary chat provider handles those.
    """

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self._model = settings.OPENAI_EMBEDDING_MODEL
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not set, embedding will use mock fallback")

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        from app.ai.mock_provider import MockProvider
        return await MockProvider().generate(prompt, **kwargs)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        from app.ai.mock_provider import MockProvider
        return await MockProvider().chat(messages, **kwargs)

    async def embedding(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings using OpenAI's embedding API."""
        if not settings.OPENAI_API_KEY:
            logger.warning("No OPENAI_API_KEY, using mock zero vectors")
            from app.ai.mock_provider import MockProvider
            return await MockProvider().embedding(texts)

        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
            )
            vectors = [d.embedding for d in response.data]
            logger.info(
                "OpenAI embedding: %d texts, dim=%d",
                len(vectors),
                len(vectors[0]) if vectors else 0,
            )
            return vectors
        except Exception as exc:
            logger.error("OpenAI embedding failed: %s, falling back to mock", exc)
            from app.ai.mock_provider import MockProvider
            return await MockProvider().embedding(texts)

    def is_available(self) -> bool:
        return bool(settings.OPENAI_API_KEY)
