"""Teacher profile CRUD operations."""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.teacher_profile import TeacherProfile
from app.schemas.teacher_profile import TeacherProfileCreate, TeacherProfileUpdate
from app.utils.exceptions import NotFoundError, DuplicateError


def get_profile_by_user_id(db: Session, user_id: int) -> TeacherProfile | None:
    return db.scalar(
        select(TeacherProfile).where(
            TeacherProfile.user_id == user_id,
            TeacherProfile.is_deleted == False,  # noqa: E712
        )
    )


def get_profile_by_id(db: Session, profile_id: int) -> TeacherProfile | None:
    return db.scalar(
        select(TeacherProfile).where(
            TeacherProfile.id == profile_id,
            TeacherProfile.is_deleted == False,  # noqa: E712
        )
    )


def list_profiles(
    db: Session,
    college_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[TeacherProfile], int]:
    stmt = select(TeacherProfile).where(
        TeacherProfile.is_deleted == False  # noqa: E712
    )
    if college_id is not None:
        stmt = stmt.where(TeacherProfile.college_id == college_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(
        db.scalars(
            stmt.order_by(TeacherProfile.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return items, total


def create_profile(db: Session, user_id: int, data: TeacherProfileCreate) -> TeacherProfile:
    if get_profile_by_user_id(db, user_id):
        raise DuplicateError("该教师已有名片资料")

    profile = TeacherProfile(user_id=user_id, **data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(
    db: Session, profile: TeacherProfile, data: TeacherProfileUpdate
) -> TeacherProfile:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, profile: TeacherProfile) -> None:
    profile.is_deleted = True
    profile.delete_time = datetime.now(timezone.utc)
    db.commit()
