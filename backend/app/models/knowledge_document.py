"""Knowledge document model — uploaded files with async processing status."""

from sqlalchemy import String, Integer, BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin


class KnowledgeDocument(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "knowledge_document"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("knowledge_category.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="所属分类 ID",
    )
    uploader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="上传者 ID",
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False, comment="文档标题")
    file_name: Mapped[str] = mapped_column(String(512), nullable=False, comment="原始文件名")
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, comment="存储路径")
    file_size: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="文件大小（字节）"
    )
    mime_type: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="MIME 类型"
    )
    page_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="页数"
    )
    content_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="解析后的文本内容"
    )
    summary_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="AI 摘要"
    )
    # Lifecycle tracking
    current_step: Mapped[str] = mapped_column(
        String(16),
        default="uploaded",
        comment="当前阶段: uploaded/parsed/summarized/classified/embedded/ready/failed",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="最近一次失败的错误信息"
    )
    # Per-stage status (backward-compatible)
    parse_status: Mapped[str] = mapped_column(
        String(16), default="waiting", comment="解析状态: waiting/processing/success/failed"
    )
    summary_status: Mapped[str] = mapped_column(
        String(16), default="waiting", comment="摘要状态"
    )
    classify_status: Mapped[str] = mapped_column(
        String(16), default="waiting", comment="分类状态"
    )
    embedding_status: Mapped[str] = mapped_column(
        String(16), default="waiting", comment="向量化状态"
    )
