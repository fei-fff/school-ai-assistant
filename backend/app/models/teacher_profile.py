"""Teacher profile model — extended tutor information."""

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class TeacherProfile(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "teacher_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="关联用户 ID",
    )
    college_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("college.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="所属学院 ID",
    )
    avatar: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="头像 URL"
    )
    real_name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="真实姓名"
    )
    title: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="职称: 教授/副教授/讲师等"
    )
    research_direction: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="研究方向"
    )
    laboratory: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="所属实验室"
    )
    email: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="联系邮箱"
    )
    phone: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="联系电话"
    )
    introduction: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="个人简介"
    )
    student_requirement: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="招生要求"
    )
    homepage: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="个人主页 URL"
    )
    tags: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="标签，逗号分隔"
    )
