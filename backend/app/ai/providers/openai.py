"""OpenAI Provider — chat/embed via OpenAI API.

Requires OPENAI_API_KEY in .env. Set AI_PROVIDER=openai to activate.
"""

import logging
from typing import Any

from openai import AsyncOpenAI

from app.ai.base import BaseAIProvider
from app.ai.providers.mock import _simple_embed
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider for all AI capabilities."""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self._chat_model = settings.OPENAI_CHAT_MODEL
        self._embed_model = settings.OPENAI_EMBEDDING_MODEL

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not settings.OPENAI_API_KEY:
            return _simple_embed(texts, dim=settings.EMBEDDING_DIMENSION)
        try:
            response = await self._client.embeddings.create(
                model=self._embed_model, input=texts,
            )
            return [d.embedding for d in response.data]
        except Exception as exc:
            logger.warning("OpenAI embed failed: %s, fallback to hash", exc)
            return _simple_embed(texts, dim=settings.EMBEDDING_DIMENSION)

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=self._chat_model, messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def summarize(self, text: str) -> str:
        from app.ai.prompt_manager import get_summary_prompt
        prompt = get_summary_prompt(document=text)
        return await self.generate(prompt)

    async def classify(self, text: str, categories: list[str]) -> dict[str, Any]:
        import json
        from app.ai.prompt_manager import get_classify_prompt
        cat_str = "\n".join(f"- {c}" for c in categories)
        prompt = get_classify_prompt(categories=cat_str, document=text[:8000])
        raw = (await self.generate(prompt)).strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {"primary": str(parsed), "categories": []}
        except (json.JSONDecodeError, ValueError):
            return {"primary": categories[0] if categories else "unknown", "categories": []}

    def is_available(self) -> bool:
        return bool(settings.OPENAI_API_KEY)
