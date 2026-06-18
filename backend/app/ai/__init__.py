"""AI module — public API surface.

Business code should import from here or from app.ai.service:

    from app.ai.service import ai_service          # preferred
    from app.ai import ai_service, AIService       # also works

Internal modules (client, provider, interfaces, prompt_manager)
should NOT be imported directly by business-layer code.
"""

from app.ai.service import AIService, ai_service

__all__ = ["AIService", "ai_service"]
