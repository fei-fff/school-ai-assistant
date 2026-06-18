"""AIService — the single entry-point for all AI capabilities in the system.

All business-layer code (API handlers, background tasks, CRUD services)
MUST call AIService instead of importing AIClient or AIProvider directly.

Call chain:
    Business Layer
         |
    AIService  (this module — the only import business code should use)
         |
    AIClient   (internal facade, not imported by business code)
         |
    AIProvider (abstract, swappable — Mock / OpenAI / DeepSeek / Qwen / GLM / Gemini)
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
    get_system_prompt,
)
from app.utils.exceptions import AIException

logger = logging.getLogger(__name__)


class AIService:
    """Unified AI service — wraps all AI calls with prompt management and error handling.

    Usage:
        from app.ai.service import ai_service

        reply = await ai_service.chat(messages)
        summary = await ai_service.summarize(document)
        classification = await ai_service.classify(text, categories)
        vectors = await ai_service.embed(texts)
    """

    def __init__(self, client: AIClient | None = None):
        self._client = client or ai_client

    # ── Chat ────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Multi-turn chat with optional system prompt override.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts.
            system_prompt: If provided, prepended as a system message.
            temperature: Sampling temperature (provider-dependent).
            max_tokens: Token limit (provider-dependent).

        Returns:
            Assistant reply string.

        Raises:
            AIException: On AI provider failure.
        """
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

    # ── Knowledge-base RAG chat ─────────────────────────

    async def knowledge_chat(
        self,
        question: str,
        context: str,
        *,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """RAG-based Q&A — answer a question using retrieved knowledge context.

        Args:
            question: User question.
            context: Retrieved knowledge base context.
            history: Optional conversation history.

        Returns:
            Answer grounded in the provided context.
        """
        prompt = get_knowledge_prompt(context=context, question=question)
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        try:
            return await self._client.chat(messages)
        except Exception as exc:
            logger.error("AIService.knowledge_chat failed: %s", exc)
            raise AIException(f"知识库问答失败: {exc}") from exc

    # ── Summary ─────────────────────────────────────────

    async def summarize(
        self,
        document: str,
        *,
        max_length: int | None = None,
    ) -> str:
        """Generate a summary for a document.

        Args:
            document: Full document text.
            max_length: Optional hint for max summary length.

        Returns:
            Summary string.
        """
        prompt = get_summary_prompt(document=document)
        try:
            return await self._client.generate(prompt)
        except Exception as exc:
            logger.error("AIService.summarize failed: %s", exc)
            raise AIException(f"摘要生成失败: {exc}") from exc

    # ── Classification ──────────────────────────────────

    async def classify(
        self,
        text: str,
        categories: list[str],
    ) -> dict[str, Any]:
        """Classify text into predefined categories.

        Args:
            text: Text to classify.
            categories: List of category names.

        Returns:
            Dict with primary_category and category confidence scores.
        """
        cat_str = "\n".join(f"- {c}" for c in categories)
        prompt = get_classify_prompt(categories=cat_str, document=text)
        try:
            result = await self._client.generate(prompt)
            return self._parse_json_result(result, fallback={"primary": categories[0] if categories else "unknown"})
        except Exception as exc:
            logger.error("AIService.classify failed: %s", exc)
            raise AIException(f"分类失败: {exc}") from exc

    # ── Emotion analysis ────────────────────────────────

    async def analyze_emotion(self, conversation: str) -> dict[str, Any]:
        """Analyze the emotional tone of a conversation.

        Args:
            conversation: The conversation text to analyze.

        Returns:
            Dict with keys: emotion, confidence, analysis.
        """
        prompt = get_emotion_prompt(conversation=conversation)
        try:
            result = await self._client.generate(prompt)
            return self._parse_json_result(
                result,
                fallback={"emotion": "neutral", "confidence": 0.5, "analysis": ""},
            )
        except Exception as exc:
            logger.error("AIService.analyze_emotion failed: %s", exc)
            raise AIException(f"情绪分析失败: {exc}") from exc

    # ── Mentor matching ─────────────────────────────────

    async def match_mentors(
        self,
        student_info: str,
        mentor_list: str,
    ) -> list[dict[str, Any]]:
        """Match students with suitable mentors based on research fit.

        Args:
            student_info: Student background and interests.
            mentor_list: Serialized mentor profiles.

        Returns:
            List of match results with mentor_id, name, score, reason.
        """
        prompt = get_mentor_prompt(student_info=student_info, mentor_list=mentor_list)
        try:
            result = await self._client.generate(prompt)
            parsed = self._parse_json_result(result, fallback=[])
            return parsed if isinstance(parsed, list) else [parsed]
        except Exception as exc:
            logger.error("AIService.match_mentors failed: %s", exc)
            raise AIException(f"导师匹配失败: {exc}") from exc

    # ── Embedding ───────────────────────────────────────

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for text chunks.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of float vectors.
        """
        try:
            return await self._client.embedding(texts)
        except Exception as exc:
            logger.error("AIService.embed failed: %s", exc)
            raise AIException(f"向量化失败: {exc}") from exc

    # ── Low-level generate (for custom use) ─────────────

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Single-turn raw generation — use sparingly; prefer semantic methods above.

        Args:
            prompt: Raw prompt string.
            temperature: Sampling temperature.
            max_tokens: Token limit.

        Returns:
            Generated text.
        """
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

    # ── Helpers ─────────────────────────────────────────

    @staticmethod
    def _parse_json_result(raw: str, fallback: Any = None) -> Any:
        """Attempt to parse a JSON response; return fallback on failure."""
        raw = raw.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from AI response, using fallback")
            return fallback

    # ── Health ──────────────────────────────────────────

    def is_available(self) -> bool:
        """Check whether the underlying AI provider is available."""
        return self._client.provider.is_available()


# Module-level singleton — the canonical import for all business code
ai_service = AIService()
