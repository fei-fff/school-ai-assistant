"""Shared enumerations used across the application."""

from enum import Enum


class TaskStatus(str, Enum):
    """Async task processing status."""

    WAITING = "waiting"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class EmotionType(str, Enum):
    """Emotion classification labels."""

    HAPPY = "happy"
    SAD = "sad"
    STRESS = "stress"
    ANXIETY = "anxiety"
    ANGRY = "angry"
    CONFUSED = "confused"
    NEUTRAL = "neutral"
