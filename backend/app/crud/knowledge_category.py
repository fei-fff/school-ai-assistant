"""Knowledge category CRUD operations."""

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.knowledge_category import KnowledgeCategory
from app.schemas.knowledge_category import (
    KnowledgeCategoryCreate,
    KnowledgeCategoryUpdate,
)
from app.utils.exceptions import NotFoundError, DuplicateError


def get_category_by_id(db: Session, category_id: int) -> KnowledgeCategory | None:
    return db.scalar(
        select(KnowledgeCategory).where(
            KnowledgeCategory.id == category_id,
            KnowledgeCategory.is_deleted == False,  # noqa: E712
        )
    )


def list_categories(
    db: Session,
    parent_id: int | None = None,
    page: int = 1,
    page_size: int = 100,
) -> tuple[list[KnowledgeCategory], int]:
    base = select(KnowledgeCategory).where(
        KnowledgeCategory.is_deleted == False  # noqa: E712
    )
    if parent_id is not None:
        base = base.where(KnowledgeCategory.parent_id == parent_id)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    items = list(
        db.scalars(
            base.order_by(KnowledgeCategory.sort_order, KnowledgeCategory.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return items, total


def create_category(
    db: Session, data: KnowledgeCategoryCreate
) -> KnowledgeCategory:
    cat = KnowledgeCategory(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(
    db: Session,
    category: KnowledgeCategory,
    data: KnowledgeCategoryUpdate,
) -> KnowledgeCategory:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: KnowledgeCategory) -> None:
    category.is_deleted = True
    from datetime import datetime, timezone
    category.delete_time = datetime.now(timezone.utc)
    db.commit()
