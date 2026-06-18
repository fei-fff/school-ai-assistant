"""College model — organizational unit for tutors."""

from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class College(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "college"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True, comment="学院名称"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="学院简介"
    )
    logo: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="Logo URL"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="排序"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=1, comment="状态: 1=启用, 0=禁用"
    )
