"""Simple memory — extract user context from conversation history."""


def extract_memory_context(history: list[dict]) -> str:
    """Extract user preferences, college, and emotional state from history."""
    if not history:
        return ""

    user_messages = [m["content"] for m in history if m.get("role") == "user"]
    all_text = " ".join(user_messages[-5:])  # last 5 turns

    context_parts = []

    # Detect college mentions
    college_hints = ["学院", "计算机", "电子", "数学", "物理", "化学", "生物", "经济", "法学", "教育"]
    found = [c for c in college_hints if c in all_text]
    if found:
        context_parts.append(f"User is associated with: {', '.join(found)}")

    # Detect emotional state
    emotion_words = ["焦虑", "压力", "难过", "开心", "兴奋", "紧张", "担心", "抑郁"]
    found_e = [e for e in emotion_words if e in all_text]
    if found_e:
        context_parts.append(f"User's emotional state: {', '.join(found_e)}")

    # Detect topic interests
    topic_words = ["AI", "人工智能", "机器学习", "深度学习", "数据库", "算法", "数据结构",
                   "NLP", "计算机视觉", "python", "java", "c++"]
    found_t = [t for t in topic_words if t.lower() in all_text.lower()]
    if found_t:
        context_parts.append(f"User interests: {', '.join(found_t[:5])}")

    return "; ".join(context_parts) if context_parts else ""
