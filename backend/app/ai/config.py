"""AI configuration — expose relevant settings in one place."""

from app.core.config import settings


def get_ai_config() -> dict:
    """Return the active AI provider configuration dict."""
    return {
        "provider": settings.AI_PROVIDER,
        "openai": {
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_BASE_URL,
            "chat_model": settings.OPENAI_CHAT_MODEL,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
        },
        "deepseek": {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "chat_model": settings.DEEPSEEK_CHAT_MODEL,
        },
        "qwen": {
            "api_key": settings.QWEN_API_KEY,
            "base_url": settings.QWEN_BASE_URL,
            "chat_model": settings.QWEN_CHAT_MODEL,
        },
        "glm": {
            "api_key": settings.GLM_API_KEY,
            "base_url": settings.GLM_BASE_URL,
            "chat_model": settings.GLM_CHAT_MODEL,
        },
        "gemini": {
            "api_key": settings.GEMINI_API_KEY,
            "chat_model": settings.GEMINI_CHAT_MODEL,
        },
        "embedding": {
            "provider": settings.EMBEDDING_PROVIDER,
            "model": settings.EMBEDDING_MODEL,
            "dimension": settings.EMBEDDING_DIMENSION,
        },
    }
