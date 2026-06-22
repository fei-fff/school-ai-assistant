"""System integration — unified chat routing layer."""

from app.chat.intent import detect_intent
from app.chat.router import ChatRouter, chat_router

__all__ = ["detect_intent", "ChatRouter", "chat_router"]
