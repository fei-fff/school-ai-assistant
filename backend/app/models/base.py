"""Base mixins for SQLAlchemy models — soft-delete, timestamps."""

from datetime import datetime

from sqlalchemy import DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Auto-managed create_time and update_time."""

    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class SoftDeleteMixin:
    """Soft-delete support via is_deleted flag."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0"
    )
    delete_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
