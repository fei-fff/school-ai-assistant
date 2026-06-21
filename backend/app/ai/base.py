"""Base AI Provider — abstract interface for all AI backends.

Every provider (Mock, DeepSeek, OpenAI) MUST implement this interface.
AIService delegates all calls through this abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAIProvider(ABC):
    """Unified interface for AI capabilities.

    To add a new provider:
    1. Subclass BaseAIProvider and implement all abstract methods.
    2. Register in factory.py.
    3. Set AI_PROVIDER in .env.
    No other code changes needed.
    """

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Multi-turn chat completion."""
        ...

    @abstractmethod
    async def summarize(self, text: str) -> str:
        """Generate a summary for the given text."""
        ...

    @abstractmethod
    async def classify(self, text: str, categories: list[str]) -> dict[str, Any]:
        """Classify text into predefined categories."""
        ...

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Single-turn text generation. Default delegates to chat."""
        return await self.chat([{"role": "user", "content": prompt}], **kwargs)

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is configured and reachable."""
        ...
