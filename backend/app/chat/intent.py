"""Intent detection — keyword-based classification for unified chat routing."""

EMOTION_KEYWORDS = [
    "anxiety", "stress", "lonely", "sad", "depressed", "cry", "upset",
    "angry", "hopeless", "worthless", "tired", "exhausted", "worry",
    "anxious", "nervous", "pressure", "overwhelmed",
    "焦虑", "压力", "难受", "孤独", "抑郁", "不开心",
    "难过", "崩溃", "烦躁", "失眠", "睡不着", "担心",
    "紧张", "伤心", "绝望", "无助", "压抑",
]

MENTOR_KEYWORDS = [
    "mentor", "professor", "导师", "老师", "教授", "研究方向", "推荐",
    "课题", "研究生", "博士", "硕士", "招生", "实验室",
    "科研", "学术", "学院", "选导师", "找导师",
    "tutor", "supervisor", "advise",
]


def detect_intent(message: str) -> tuple[str, float]:
    """Detect intent from message. Returns (intent, confidence)."""
    msg_lower = message.lower()

    emotion_hits = [kw for kw in EMOTION_KEYWORDS if kw in msg_lower]
    mentor_hits = [kw for kw in MENTOR_KEYWORDS if kw in msg_lower]

    if emotion_hits:
        return ("emotion", min(0.95, 0.5 + 0.1 * len(emotion_hits)))
    if mentor_hits:
        return ("mentor", min(0.95, 0.5 + 0.1 * len(mentor_hits)))

    return ("knowledge", 0.7)
