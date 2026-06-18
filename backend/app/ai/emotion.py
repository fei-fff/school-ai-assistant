"""Emotion analysis service — wraps AIService for emotion detection."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """Analyze user emotion from conversation text.

    Delegates all AI calls through AIService — never calls ai_client or AIProvider directly.
    """

    EMOTIONS = ["happy", "sad", "stress", "anxiety", "angry", "confused", "neutral"]

    def __init__(self):
        # Lazy import to avoid circular dependency at module level
        self._service = None

    @property
    def service(self):
        if self._service is None:
            from app.ai.service import ai_service

            self._service = ai_service
        return self._service

    async def analyze(self, conversation: str) -> dict[str, Any]:
        """Analyze emotion from raw conversation text.

        Returns structured result with emotion, confidence, and analysis.
        """
        try:
            result = await self.service.analyze_emotion(conversation)
            emotion = result.get("emotion", "neutral")
            if emotion not in self.EMOTIONS:
                emotion = "neutral"
            return {
                "emotion": emotion,
                "confidence": min(max(float(result.get("confidence", 0.5)), 0.0), 1.0),
                "analysis": result.get("analysis", ""),
            }
        except Exception as exc:
            logger.warning("Emotion analysis failed: %s", exc)
            return {"emotion": "neutral", "confidence": 0.5, "analysis": ""}

    async def get_persona(self, emotion: str) -> str:
        """Map emotion to an AI persona. Returns a persona description."""
        personas = {
            "happy": "温暖鼓励",
            "sad": "温柔共情",
            "stress": "冷静减压",
            "anxiety": "安抚引导",
            "angry": "理性倾听",
            "confused": "清晰解答",
            "neutral": "专业高效",
        }
        return personas.get(emotion, "专业高效")


# Convenience singleton
emotion_analyzer = EmotionAnalyzer()
