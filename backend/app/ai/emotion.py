"""Emotion analysis service — wraps AI classify for emotion detection."""

import json
import logging
from typing import Any

from app.ai.client import ai_client
from app.ai.prompt_manager import get_emotion_prompt

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """Analyze user emotion from conversation text."""

    EMOTIONS = ["happy", "sad", "stress", "anxiety", "angry", "confused", "neutral"]

    def __init__(self):
        self._client = ai_client

    async def analyze(self, conversation: str) -> dict[str, Any]:
        """Analyze emotion from raw conversation text. Returns structured result."""
        prompt = get_emotion_prompt(conversation=conversation)
        try:
            result = await self._client.generate(prompt)
            parsed = json.loads(result)
            emotion = parsed.get("emotion", "neutral")
            confidence = float(parsed.get("confidence", 0.5))
            analysis = parsed.get("analysis", "")

            if emotion not in self.EMOTIONS:
                emotion = "neutral"
            return {
                "emotion": emotion,
                "confidence": min(max(confidence, 0.0), 1.0),
                "analysis": analysis,
            }
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Failed to parse emotion result: %s", exc)
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
