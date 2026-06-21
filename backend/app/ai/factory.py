"""Provider factory — instantiates the configured AI provider."""

import logging

from app.ai.base import BaseAIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory that returns the configured BaseAIProvider instance.

    Backend selection is driven by AI_PROVIDER in .env:
        mock     → MockProvider      (zero-dependency, for development)
        deepseek → DeepSeekProvider   (DeepSeek API)
        openai   → OpenAIProvider     (OpenAI API)
    """

    @staticmethod
    def create() -> BaseAIProvider:
        name = settings.AI_PROVIDER.lower()
        logger.info("Creating AI provider: %s", name)

        if name == "mock":
            from app.ai.providers.mock import MockProvider
            return MockProvider()
        elif name == "deepseek":
            from app.ai.providers.deepseek import DeepSeekProvider
            return DeepSeekProvider()
        elif name == "openai":
            from app.ai.providers.openai import OpenAIProvider
            return OpenAIProvider()
        else:
            logger.warning("Unknown provider '%s', falling back to mock", name)
            from app.ai.providers.mock import MockProvider
            return MockProvider()
