"""Seed college data — run once to populate initial colleges."""

from sqlalchemy.orm import Session

from app.models.college import College

SEED_COLLEGES = [
    "计算机科学与技术学院",
    "电子信息工程学院",
    "数学与统计学院",
    "物理学院",
    "化学与化工学院",
    "生物工程学院",
    "经济管理学院",
    "外国语学院",
    "法学院",
    "教育学院",
]


def seed(db: Session) -> int:
    created = 0
    for name in SEED_COLLEGES:
        existing = db.query(College).filter(College.name == name).first()
        if not existing:
            db.add(College(name=name, sort_order=created))
            created += 1
    if created > 0:
        db.commit()
    return created
