"""Emotion analysis service — uses AIService for emotion detection."""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """Analyze user emotion from conversation text."""

    EMOTIONS = ["happy", "sad", "stress", "anxiety", "angry", "confused", "neutral"]

    def __init__(self):
        self._service = None

    @property
    def service(self):
        if self._service is None:
            from app.ai.service import ai_service
            self._service = ai_service
        return self._service

    async def analyze(self, conversation: str) -> dict[str, Any]:
        from app.ai.prompt_manager import get_emotion_prompt
        try:
            prompt = get_emotion_prompt(conversation=conversation)
            result = await self.service.generate(prompt)
            if result.startswith("```"):
                lines = result.split("\n")
                result = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            parsed = json.loads(result)
            emotion = parsed.get("emotion", "neutral")
            if emotion not in self.EMOTIONS:
                emotion = "neutral"
            return {
                "emotion": emotion,
                "confidence": min(max(float(parsed.get("confidence", 0.5)), 0.0), 1.0),
                "analysis": parsed.get("analysis", ""),
            }
        except Exception as exc:
            logger.warning("Emotion analysis failed: %s", exc)
            return {"emotion": "neutral", "confidence": 0.5, "analysis": ""}

    async def get_persona(self, emotion: str) -> str:
        personas = {
            "happy": "温暖鼓励", "sad": "温柔共情", "stress": "冷静减压",
            "anxiety": "安抚引导", "angry": "理性倾听", "confused": "清晰解答",
            "neutral": "专业高效",
        }
        return personas.get(emotion, "专业高效")


emotion_analyzer = EmotionAnalyzer()
