"""User model — SQLAlchemy ORM mapping."""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Enum, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class UserRole(str, PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserStatus(int, PyEnum):
    ACTIVE = 1
    DISABLED = 0


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
