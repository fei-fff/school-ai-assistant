"""Abstract interfaces for AI providers — all business code depends on these."""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Unified interface for any LLM / AI backend.

    To add a new model (e.g. Gemini), implement this interface
    without touching any business logic.

    Default implementations of classify() and summary() delegate
    to PromptManager so that prompts are never hardcoded here.
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
        """Classify text into predefined categories.

        Default implementation uses PromptManager for template-driven prompts.
        Override in provider for custom classification logic.
        """
        from app.ai.prompt_manager import get_classify_prompt

        cat_str = "\n".join(f"- {c}" for c in categories)
        prompt = get_classify_prompt(categories=cat_str, document=text)
        result = await self.generate(prompt, **kwargs)
        return {"primary": result.strip(), "raw": result}

    async def summary(self, document: str, **kwargs: Any) -> str:
        """Summarize a document.

        Default implementation uses PromptManager for template-driven prompts.
        Override in provider for custom summarization logic.
        """
        from app.ai.prompt_manager import get_summary_prompt

        prompt = get_summary_prompt(document=document)
        return await self.generate(prompt, **kwargs)

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether this provider is configured and reachable."""
        ...
