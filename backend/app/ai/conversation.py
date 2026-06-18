"""Conversation context manager — builds message history for multi-turn chat."""

from typing import Any

from app.ai.prompt_manager import get_system_prompt


class Conversation:
    """Maintains a multi-turn conversation context."""

    def __init__(self, user_id: int, session_id: str | None = None):
        self.user_id = user_id
        self.session_id = session_id or f"{user_id}_{id(self)}"
        self._messages: list[dict[str, str]] = [
            {"role": "system", "content": get_system_prompt()}
        ]

    def add_user_message(self, content: str) -> None:
        self._messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self._messages.append({"role": "assistant", "content": content})

    @property
    def history(self) -> list[dict[str, str]]:
        return list(self._messages)

    def to_chat_messages(self) -> list[dict[str, str]]:
        """Return the message list suitable for AIProvider.chat()."""
        return self.history

    def trim(self, max_messages: int = 20) -> None:
        """Keep the system prompt and the most recent N messages."""
        if len(self._messages) > max_messages + 1:
            self._messages = [self._messages[0]] + self._messages[-(max_messages):]

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "messages": self._messages,
        }
