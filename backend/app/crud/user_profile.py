"""User profile CRUD."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile


def get_profile(db: Session, user_id: int) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))


def get_or_create_profile(db: Session, user_id: int) -> UserProfile:
    profile = get_profile(db, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_profile(
    db: Session,
    user_id: int,
    *,
    college: str | None = None,
    interests: str | None = None,
    emotion_state: str | None = None,
    frequent_topics: str | None = None,
) -> UserProfile:
    profile = get_or_create_profile(db, user_id)
    if college is not None:
        profile.college = college
    if interests is not None:
        profile.interests = _merge_tags(profile.interests, interests)
    if emotion_state is not None:
        profile.emotion_state = emotion_state
    if frequent_topics is not None:
        profile.frequent_topics = _merge_tags(profile.frequent_topics, frequent_topics)
    db.commit()
    db.refresh(profile)
    return profile


def _merge_tags(existing: str | None, new: str, max_tags: int = 10) -> str:
    if not existing:
        return new
    existing_tags = [t.strip() for t in existing.split(",") if t.strip()]
    new_tags = [t.strip() for t in new.split(",") if t.strip()]
    merged = dict.fromkeys(existing_tags + new_tags)  # dedup preserving order
    return ",".join(list(merged)[:max_tags])
