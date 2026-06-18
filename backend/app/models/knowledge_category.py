"""Knowledge category model — infinite-level tree via parent_id."""

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class KnowledgeCategory(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "knowledge_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("knowledge_category.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="父分类 ID，NULL 表示顶级",
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="分类名称"
    )
    level: Mapped[int] = mapped_column(Integer, default=0, comment="层级深度")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 1=启用, 0=禁用")
