"""AI module — public API.

Import from here:
    from app.ai.service import ai_service, AIService
    from app.ai.base import BaseAIProvider
    from app.ai.factory import ProviderFactory
"""

from app.ai.service import AIService, ai_service
from app.ai.base import BaseAIProvider
from app.ai.factory import ProviderFactory

__all__ = ["AIService", "ai_service", "BaseAIProvider", "ProviderFactory"]
