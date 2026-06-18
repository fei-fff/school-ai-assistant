"""Chat history model — stores multi-turn conversation records."""

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import TimestampMixin


class ChatHistory(Base, TimestampMixin):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id: Mapped[str] = mapped_column(
        String(128), nullable=False, index=True, comment="会话标识"
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="角色: user / assistant / system"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    token_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Token 估算数"
    )
