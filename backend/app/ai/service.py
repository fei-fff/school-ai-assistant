"""AIService — the single entry-point for all AI capabilities in the system.

All business-layer code MUST call AIService instead of importing AIClient or AIProvider directly.
"""

import json
import logging
from typing import Any

from app.ai.client import AIClient, ai_client
from app.ai.prompt_manager import (
    get_classify_prompt,
    get_emotion_prompt,
    get_knowledge_prompt,
    get_mentor_prompt,
    get_summary_prompt,
)
from app.utils.exceptions import AIException

logger = logging.getLogger(__name__)


class AIService:
    """Unified AI service — wraps all AI calls with prompt management and error handling."""

    def __init__(self, client: AIClient | None = None):
        self._client = client or ai_client

    async def chat(
        self, messages: list[dict[str, str]], *, system_prompt: str | None = None,
        temperature: float | None = None, max_tokens: int | None = None,
    ) -> str:
        full_messages = list(messages)
        if system_prompt:
            full_messages.insert(0, {"role": "system", "content": system_prompt})
        kwargs: dict[str, Any] = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        try:
            return await self._client.chat(full_messages, **kwargs)
        except Exception as exc:
            logger.error("AIService.chat failed: %s", exc)
            raise AIException(f"AI 对话失败: {exc}") from exc

    async def knowledge_chat(
        self, question: str, context: str, *, history: list[dict[str, str]] | None = None,
    ) -> str:
        prompt = get_knowledge_prompt(context=context, question=question)
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        try:
            return await self._client.chat(messages)
        except Exception as exc:
            logger.error("AIService.knowledge_chat failed: %s", exc)
            raise AIException(f"知识库问答失败: {exc}") from exc

    async def summarize(self, document: str, *, max_length: int | None = None) -> str:
        prompt = get_summary_prompt(document=document)
        try:
            return await self._client.generate(prompt)
        except Exception as exc:
            logger.error("AIService.summarize failed: %s", exc)
            raise AIException(f"摘要生成失败: {exc}") from exc

    async def classify(self, text: str, categories: list[str]) -> dict[str, Any]:
        """Classify text into predefined categories. Always returns a dict."""
        cat_str = "\n".join(f"- {c}" for c in categories)
        prompt = get_classify_prompt(categories=cat_str, document=text)
        try:
            result = await self._client.generate(prompt)
            parsed = self._parse_json_result(result)
            # Ensure we always return a dict
            if not isinstance(parsed, dict):
                return {"primary": str(parsed), "categories": []}
            return parsed
        except Exception as exc:
            logger.error("AIService.classify failed: %s", exc)
            raise AIException(f"分类失败: {exc}") from exc

    async def analyze_emotion(self, conversation: str) -> dict[str, Any]:
        prompt = get_emotion_prompt(conversation=conversation)
        try:
            result = await self._client.generate(prompt)
            parsed = self._parse_json_result(result)
            if not isinstance(parsed, dict):
                return {"emotion": "neutral", "confidence": 0.5, "analysis": ""}
            return parsed
        except Exception as exc:
            logger.error("AIService.analyze_emotion failed: %s", exc)
            raise AIException(f"情绪分析失败: {exc}") from exc

    async def match_mentors(self, student_info: str, mentor_list: str) -> list[dict[str, Any]]:
        prompt = get_mentor_prompt(student_info=student_info, mentor_list=mentor_list)
        try:
            result = await self._client.generate(prompt)
            parsed = self._parse_json_result(result)
            if isinstance(parsed, list):
                return parsed
            return [parsed] if isinstance(parsed, dict) else []
        except Exception as exc:
            logger.error("AIService.match_mentors failed: %s", exc)
            raise AIException(f"导师匹配失败: {exc}") from exc

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            return await self._client.embedding(texts)
        except Exception as exc:
            logger.error("AIService.embed failed: %s", exc)
            raise AIException(f"向量化失败: {exc}") from exc

    async def generate(self, prompt: str, *, temperature: float | None = None,
                       max_tokens: int | None = None) -> str:
        kwargs: dict[str, Any] = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        try:
            return await self._client.generate(prompt, **kwargs)
        except Exception as exc:
            logger.error("AIService.generate failed: %s", exc)
            raise AIException(f"AI 生成失败: {exc}") from exc

    def is_available(self) -> bool:
        return self._client.provider.is_available()

    @staticmethod
    def _parse_json_result(raw: str) -> Any:
        """Parse AI response as JSON with markdown fence stripping."""
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            inner = lines[1:] if not lines[-1].strip().startswith("```") else lines[1:-1]
            raw = "\n".join(inner)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse JSON from AI response: %s", raw[:200])
            return raw


ai_service = AIService()
