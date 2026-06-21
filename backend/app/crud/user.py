"""User CRUD operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password
from app.utils.exceptions import DuplicateError


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, data: UserRegister) -> User:
    # Uniqueness checks
    if get_user_by_username(db, data.username):
        raise DuplicateError("用户名已被使用")
    if get_user_by_email(db, data.email):
        raise DuplicateError("邮箱已被使用")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        email=data.email,
        nickname=data.username,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
