"""Emotion record model — stores periodic emotion analysis results."""

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class EmotionRecord(Base):
    __tablename__ = "emotion_record"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    emotion: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="情绪类别: happy/sad/stress/anxiety/angry/confused/neutral",
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="置信度 0.0-1.0"
    )
    ai_persona: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="AI 响应时采用的人格"
    )
    create_time: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), comment="记录时间"
    )
