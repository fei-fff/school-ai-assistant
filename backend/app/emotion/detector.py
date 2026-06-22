"""Emotion detector — keyword-based classification."""

from dataclasses import dataclass

# ── Keyword lexicons ──

NEGATIVE_KEYWORDS = [
    "sad", "depressed", "lonely", "cry", "upset", "angry", "hate",
    "awful", "terrible", "hopeless", "worthless", "tired", "exhausted",
    "fail", "failed", "failure", "can't", "cannot", "never", "nobody",
    "伤心", "难过", "孤独", "哭", "崩溃", "烦", "讨厌", "绝望",
    "失败", "不行", "没救了", "无助", "压抑", "痛苦", "焦虑",
]

STRESS_KEYWORDS = [
    "stress", "anxiety", "anxious", "worried", "nervous", "pressure",
    "overwhelmed", "deadline", "exam", "test", "study", "studying",
    "busy", "too much", "can't sleep", "insomnia",
    "压力", "紧张", "担心", "考试", "复习", "忙", "没时间",
    "睡不着", "学不进去", "赶不上", "太多了", "负担",
]

POSITIVE_KEYWORDS = [
    "happy", "glad", "great", "wonderful", "amazing", "love", "excited",
    "joy", "fantastic", "awesome", "thank", "grateful", "blessed",
    "开心", "高兴", "太棒了", "感谢", "喜欢", "兴奋", "满足",
    "成功", "进步", "解决了", "懂了", "会了",
]


@dataclass
class EmotionResult:
    emotion: str
    confidence: float
    matched_keywords: list[str]


class EmotionDetector:
    """Rule-based emotion detector using keyword matching."""

    @staticmethod
    def detect(text: str) -> EmotionResult:
        text_lower = text.lower()
        matched: dict[str, list[str]] = {}

        for kw in NEGATIVE_KEYWORDS:
            if kw in text_lower:
                matched.setdefault("negative", []).append(kw)
        for kw in STRESS_KEYWORDS:
            if kw in text_lower:
                matched.setdefault("stress", []).append(kw)
        for kw in POSITIVE_KEYWORDS:
            if kw in text_lower:
                matched.setdefault("positive", []).append(kw)

        if not matched:
            return EmotionResult(emotion="neutral", confidence=0.5, matched_keywords=[])

        best = max(matched, key=lambda k: len(matched[k]))
        confidence = min(0.9, 0.5 + 0.1 * len(matched[best]))
        return EmotionResult(emotion=best, confidence=confidence, matched_keywords=matched[best][:8])


emotion_detector = EmotionDetector()
