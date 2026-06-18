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


class DocumentStep(str, Enum):
    """KnowledgeDocument lifecycle step."""

    UPLOADED = "uploaded"       # 已上传，未处理
    PARSED = "parsed"            # 解析完成
    SUMMARIZED = "summarized"    # 摘要完成
    CLASSIFIED = "classified"    # 分类完成
    EMBEDDED = "embedded"        # 向量化完成
    READY = "ready"              # 全部完成，可查询
    FAILED = "failed"            # 某阶段失败
