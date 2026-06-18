"""Provider registry — maps provider names to AIProvider implementations."""

import logging

from app.ai.interfaces import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

_registry: dict[str, type[AIProvider]] = {}


def register_provider(name: str, cls: type[AIProvider]) -> None:
    _registry[name] = cls
    logger.info("Registered AI provider: %s", name)


def get_provider(name: str | None = None) -> AIProvider:
    """Return an AIProvider instance for the named (or default) provider."""
    name = name or settings.AI_PROVIDER

    if name == "mock":
        from app.ai.mock_provider import MockProvider

        return MockProvider()

    cls = _registry.get(name)
    if cls is None:
        logger.warning(
            "Provider '%s' not registered, falling back to mock", name
        )
        from app.ai.mock_provider import MockProvider

        return MockProvider()
    return cls()


def list_providers() -> list[str]:
    return ["mock"] + list(_registry.keys())
