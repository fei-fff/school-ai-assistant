"""DeepSeek Provider — chat/summarize/classify via DeepSeek API, embed via hash."""

import logging
from typing import Any

from openai import AsyncOpenAI

from app.ai.base import BaseAIProvider
from app.ai.providers.mock import _simple_embed
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek provider using OpenAI-compatible API."""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self._model = settings.DEEPSEEK_CHAT_MODEL

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Hash-based embedding — DeepSeek has no native embed API."""
        return _simple_embed(texts, dim=settings.EMBEDDING_DIMENSION)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def summarize(self, text: str) -> str:
        from app.ai.prompt_manager import get_summary_prompt
        prompt = get_summary_prompt(document=text)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return response.choices[0].message.content or ""

    async def classify(self, text: str, categories: list[str]) -> dict[str, Any]:
        import json
        from app.ai.prompt_manager import get_classify_prompt
        cat_str = "\n".join(f"- {c}" for c in categories)
        prompt = get_classify_prompt(categories=cat_str, document=text[:8000])
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {"primary": str(parsed), "categories": []}
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse classify response as JSON")
            return {"primary": categories[0] if categories else "unknown", "categories": []}

    def is_available(self) -> bool:
        return bool(settings.DEEPSEEK_API_KEY)
