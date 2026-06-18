"""Unified AI client — the single entry-point for all AI capabilities.

Business code should ONLY import from here, never from a specific provider.
"""

import logging
from typing import Any

from app.ai.interfaces import AIProvider
from app.ai.provider import get_provider

logger = logging.getLogger(__name__)


class AIClient:
    """Facade over the active AIProvider."""

    def __init__(self, provider: AIProvider | None = None):
        self._provider: AIProvider | None = provider

    @property
    def provider(self) -> AIProvider:
        if self._provider is None:
            self._provider = get_provider()
        return self._provider

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        logger.info("AI generate called, prompt length=%d", len(prompt))
        result = await self.provider.generate(prompt, **kwargs)
        logger.info("AI generate completed, response length=%d", len(result))
        return result

    async def chat(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> str:
        logger.info("AI chat called, %d messages", len(messages))
        result = await self.provider.chat(messages, **kwargs)
        logger.info("AI chat completed, response length=%d", len(result))
        return result

    async def embedding(
        self, texts: list[str], **kwargs: Any
    ) -> list[list[float]]:
        logger.info("AI embedding called, %d texts", len(texts))
        result = await self.provider.embedding(texts, **kwargs)
        logger.info("AI embedding completed")
        return result

    async def classify(
        self, text: str, categories: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        logger.info("AI classify called")
        return await self.provider.classify(text, categories, **kwargs)

    async def summary(self, document: str, **kwargs: Any) -> str:
        logger.info("AI summary called, doc length=%d", len(document))
        return await self.provider.summary(document, **kwargs)


# Convenience singleton — use DI in production
ai_client = AIClient()
