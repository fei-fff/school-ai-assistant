"""College CRUD operations."""

from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.college import College
from app.schemas.college import CollegeCreate, CollegeUpdate
from app.utils.exceptions import NotFoundError, DuplicateError


def get_college_by_id(db: Session, college_id: int) -> College | None:
    return db.scalar(
        select(College).where(
            College.id == college_id,
            College.is_deleted == False,  # noqa: E712
        )
    )


def list_colleges(
    db: Session, page: int = 1, page_size: int = 50
) -> tuple[list[College], int]:
    base = select(College).where(College.is_deleted == False)  # noqa: E712
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    items = list(
        db.scalars(
            base.order_by(College.sort_order, College.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return items, total


def create_college(db: Session, data: CollegeCreate) -> College:
    existing = db.scalar(
        select(College).where(College.name == data.name)
    )
    if existing:
        raise DuplicateError(f"学院 '{data.name}' 已存在")

    college = College(**data.model_dump())
    db.add(college)
    db.commit()
    db.refresh(college)
    return college


def update_college(db: Session, college: College, data: CollegeUpdate) -> College:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(college, key, value)
    db.commit()
    db.refresh(college)
    return college


def delete_college(db: Session, college: College) -> None:
    college.is_deleted = True
    from datetime import datetime, timezone
    college.delete_time = datetime.now(timezone.utc)
    db.commit()
