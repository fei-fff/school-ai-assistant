"""User Profile API."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.crud.user_profile import get_or_create_profile, update_profile
from app.schemas.user_profile import ProfileUpdate, ProfileOut
from app.utils.response import ok

router = APIRouter(prefix="/user/profile", tags=["User Profile"])


@router.get("/{user_id}", summary="Get user profile")
def get(user_id: int, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    profile = get_or_create_profile(db, user_id)
    return ok(data=ProfileOut.model_validate(profile))


@router.post("/update", summary="Update user profile")
def update(req: ProfileUpdate, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    profile = update_profile(db, current_user.id, **req.model_dump(exclude_unset=True))
    return ok(data=ProfileOut.model_validate(profile))
