"""Mock AI provider — returns canned responses for development and testing."""

from app.ai.interfaces import AIProvider
from app.ai.deepseek_provider import _simple_embed


class MockProvider(AIProvider):
    """Returns predictable fake responses so the app runs without a real LLM.

    Embeddings use hash-based vectors instead of zeros so the RAG
    retrieval pipeline works even with AI_PROVIDER=mock.
    """

    async def generate(self, prompt: str, **kwargs) -> str:
        return f"[Mock] 这是对你的问题的模拟回复。提示词长度: {len(prompt)} 字符。"

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        last = messages[-1]["content"] if messages else ""
        return f"[Mock Chat] 收到 {len(messages)} 条消息，最新内容: {last[:50]}..."

    async def embedding(self, texts: list[str], **kwargs) -> list[list[float]]:
        # Use hash-based vectors so retrieval works
        from app.core.config import settings
        return _simple_embed(texts, dim=settings.EMBEDDING_DIMENSION)

    async def classify(self, text: str, categories: list[str], **kwargs) -> dict:
        return {
            "primary": categories[0] if categories else "unknown",
            "categories": [
                {"name": c, "confidence": 0.85}
                for c in (categories[:2] if categories else [])
            ],
        }

    async def summary(self, document: str, **kwargs) -> str:
        preview = document[:200].replace("\n", " ")
        return f"[Mock 摘要] 文档长度: {len(document)} 字符。开头内容: {preview}..."

    def is_available(self) -> bool:
        return True
