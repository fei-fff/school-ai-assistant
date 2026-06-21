"""AIService — the single entry-point for all AI capabilities.

All business code MUST import from here.
AIService is a thin wrapper that delegates to the configured BaseAIProvider.
No business logic, no prompt building, no JSON parsing — pure delegation.
"""

import logging
from typing import Any

from app.ai.base import BaseAIProvider
from app.ai.factory import ProviderFactory

logger = logging.getLogger(__name__)


class AIService:
    """Thin wrapper over a BaseAIProvider — the ONLY import for business code.

    Usage:
        from app.ai.service import ai_service
        vectors = await ai_service.embed(["hello world"])
        reply   = await ai_service.chat([{"role": "user", "content": "hi"}])
        summary = await ai_service.summarize("long text...")
        labels  = await ai_service.classify("text", ["cat1", "cat2"])
    """

    def __init__(self, provider: BaseAIProvider | None = None):
        self._provider = provider

    @property
    def provider(self) -> BaseAIProvider:
        if self._provider is None:
            self._provider = ProviderFactory.create()
        return self._provider

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self.provider.embed(texts)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        return await self.provider.chat(messages, **kwargs)

    async def summarize(self, text: str) -> str:
        return await self.provider.summarize(text)

    async def classify(self, text: str, categories: list[str]) -> dict[str, Any]:
        return await self.provider.classify(text, categories)

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        return await self.provider.generate(prompt, **kwargs)

    async def knowledge_chat(self, question: str, context: str, *,
                             history: list[dict[str, str]] | None = None) -> str:
        """RAG knowledge Q&A — build prompt then delegate to chat."""
        from app.ai.prompt_manager import get_knowledge_prompt
        prompt = get_knowledge_prompt(context=context, question=question)
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages)

    def is_available(self) -> bool:
        return self.provider.is_available()


# Module-level singleton
ai_service = AIService()
