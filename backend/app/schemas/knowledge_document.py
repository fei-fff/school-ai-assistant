"""Knowledge document Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocumentCreate(BaseModel):
    category_id: int | None = None
    title: str
    file_name: str
    file_path: str
    file_size: int | None = None
    mime_type: str | None = None


class KnowledgeDocumentUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = None


class DocumentStatusOut(BaseModel):
    """Lightweight status response for polling."""

    id: int
    title: str
    current_step: str
    error_message: str | None
    parse_status: str
    summary_status: str
    classify_status: str
    embedding_status: str

    model_config = {"from_attributes": True}


class KnowledgeDocumentOut(BaseModel):
    """Full document record."""

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
    current_step: str
    error_message: str | None
    parse_status: str
    summary_status: str
    classify_status: str
    embedding_status: str
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}
