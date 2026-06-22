"""Emotion AI module — independent, sits on top of RAG."""

from app.emotion.detector import EmotionDetector, EmotionResult, emotion_detector
from app.emotion.persona import PERSONAS, EMOTION_TO_PERSONA, get_persona
from app.emotion.prompt_builder import PromptBuilder, prompt_builder

__all__ = [
    "EmotionDetector", "EmotionResult", "emotion_detector",
    "PERSONAS", "EMOTION_TO_PERSONA", "get_persona",
    "PromptBuilder", "prompt_builder",
]
