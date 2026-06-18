"""Knowledge document Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocumentCreate(BaseModel):
    """Schema for creating a knowledge document entry (after file upload)."""

    category_id: int | None = None
    title: str
    file_name: str
    file_path: str
    file_size: int | None = None
    mime_type: str | None = None


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating document metadata."""

    category_id: int | None = None
    title: str | None = None


class KnowledgeDocumentOut(BaseModel):
    """Public document record returned in API responses."""

    id: int
    category_id: int | None
    uploader_id: int
    title: str
    file_name: str
    file_path: str
    file_size: int | None
    mime_type: str | None
    page_count: int | None
    content_text: str | None
    summary_text: str | None
    parse_status: str
    embedding_status: str
    summary_status: str
    classify_status: str
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}


class DocumentStatusOut(BaseModel):
    """Lightweight status-only response for polling."""

    id: int
    title: str
    parse_status: str
    summary_status: str
    classify_status: str
    embedding_status: str

    model_config = {"from_attributes": True}


class PipelineResult(BaseModel):
    """Result returned after running the full RAG pipeline."""

    document_id: int
    parse_status: str
    summary_status: str
    classify_status: str
    embedding_status: str
    summary_text: str | None = None
    classification: dict | None = None
    embedding_dim: int | None = None
