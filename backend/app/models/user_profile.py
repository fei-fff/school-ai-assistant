"""User profile model — lightweight user memory system."""

from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import TimestampMixin


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    college: Mapped[str | None] = mapped_column(String(128), nullable=True)
    interests: Mapped[str | None] = mapped_column(String(512), nullable=True)
    emotion_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    frequent_topics: Mapped[str | None] = mapped_column(String(512), nullable=True)
