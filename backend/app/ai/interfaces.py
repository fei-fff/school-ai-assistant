"""Abstract interfaces for AI providers — all business code depends on these."""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Unified interface for any LLM / AI backend.

    To add a new model (e.g. Gemini), implement this interface
    without touching any business logic.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Single-turn text generation."""
        ...

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Multi-turn conversation."""
        ...

    @abstractmethod
    async def embedding(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings for one or more texts."""
        ...

    async def classify(
        self, text: str, categories: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """Classify text into predefined categories. Override for custom logic."""
        prompt = f"将以下文本分类到：{', '.join(categories)}。文本：{text}"
        result = await self.generate(prompt, **kwargs)
        return {"primary": result.strip(), "raw": result}

    async def summary(self, document: str, **kwargs: Any) -> str:
        """Summarize a document. Override for custom logic."""
        prompt = f"请对以下文档生成简洁摘要：\n{document}"
        return await self.generate(prompt, **kwargs)

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is configured and reachable."""
        ...
