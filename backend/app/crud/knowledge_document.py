"""Knowledge document CRUD operations."""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument
from app.schemas.knowledge_document import KnowledgeDocumentCreate, KnowledgeDocumentUpdate
from app.utils.exceptions import NotFoundError


def get_document_by_id(db: Session, document_id: int) -> KnowledgeDocument | None:
    return db.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.is_deleted == False,  # noqa: E712
        )
    )


def list_documents(
    db: Session,
    uploader_id: int | None = None,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[KnowledgeDocument], int]:
    base = select(KnowledgeDocument).where(
        KnowledgeDocument.is_deleted == False  # noqa: E712
    )
    if uploader_id is not None:
        base = base.where(KnowledgeDocument.uploader_id == uploader_id)
    if category_id is not None:
        base = base.where(KnowledgeDocument.category_id == category_id)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    items = list(
        db.scalars(
            base.order_by(KnowledgeDocument.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return items, total


def create_document(
    db: Session, uploader_id: int, data: KnowledgeDocumentCreate
) -> KnowledgeDocument:
    doc = KnowledgeDocument(uploader_id=uploader_id, **data.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_document(
    db: Session, doc: KnowledgeDocument, data: KnowledgeDocumentUpdate
) -> KnowledgeDocument:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc


def update_document_status(
    db: Session,
    doc: KnowledgeDocument,
    *,
    current_step: str | None = None,
    error_message: str | None = None,
    parse_status: str | None = None,
    summary_status: str | None = None,
    classify_status: str | None = None,
    embedding_status: str | None = None,
    content_text: str | None = None,
    summary_text: str | None = None,
    page_count: int | None = None,
    category_id: int | None = None,
) -> KnowledgeDocument:
    """Atomically update status fields, lifecycle step, and optional content."""
    if current_step is not None:
        doc.current_step = current_step
    if error_message is not None:
        doc.error_message = error_message
    if parse_status is not None:
        doc.parse_status = parse_status
    if summary_status is not None:
        doc.summary_status = summary_status
    if classify_status is not None:
        doc.classify_status = classify_status
    if embedding_status is not None:
        doc.embedding_status = embedding_status
    if content_text is not None:
        doc.content_text = content_text
    if summary_text is not None:
        doc.summary_text = summary_text
    if page_count is not None:
        doc.page_count = page_count
    if category_id is not None:
        doc.category_id = category_id
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: KnowledgeDocument) -> None:
    doc.is_deleted = True
    doc.delete_time = datetime.now(timezone.utc)
    db.commit()
