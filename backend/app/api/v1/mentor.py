"""Mentor API — card management + recommendation."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import get_current_user, teacher_required
from app.models.user import User
from app.crud.teacher_profile import (
    get_profile_by_user_id, get_profile_by_id, list_profiles,
    create_profile, update_profile,
)
from app.crud.college import list_colleges
from app.schemas.teacher_profile import (
    TeacherProfileCreate, TeacherProfileUpdate, TeacherProfileOut,
)
from app.schemas.college import CollegeOut
from app.schemas.common import PaginatedData
from app.utils.response import ok, error
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/mentor", tags=["Mentor"])


# ── Static routes first (before /{mentor_id}) ──

@router.get("/me", summary="Get my mentor card")
def get_my_card(db: Session = Depends(get_db), current_user: User = Depends(teacher_required)):
    profile = get_profile_by_user_id(db, current_user.id)
    if profile is None:
        return ok(data=None, message="No card yet")
    return ok(data=TeacherProfileOut.model_validate(profile))


@router.post("/me", summary="Create my mentor card")
def create_my_card(req: TeacherProfileCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(teacher_required)):
    existing = get_profile_by_user_id(db, current_user.id)
    if existing:
        return error("Card already exists. Use PUT to update.", code=409)
    profile = create_profile(db, current_user.id, req)
    return ok(data=TeacherProfileOut.model_validate(profile))


@router.put("/me", summary="Update my mentor card")
def update_my_card(req: TeacherProfileUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(teacher_required)):
    profile = get_profile_by_user_id(db, current_user.id)
    if profile is None:
        raise NotFoundError("No card found. Create one first.")
    profile = update_profile(db, profile, req)
    return ok(data=TeacherProfileOut.model_validate(profile))


@router.get("/colleges", summary="List colleges")
def browse_colleges(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items, _ = list_colleges(db, page=1, page_size=50)
    return ok(data=[CollegeOut.model_validate(i) for i in items])


@router.get("/list", summary="List mentors by college")
def list_mentors(
    college_id: int | None = Query(None),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = list_profiles(db, college_id=college_id, page=page, page_size=page_size)
    return ok(data=PaginatedData(
        items=[TeacherProfileOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
    ).model_dump())


@router.get("/recommend", summary="Recommend mentors by query")
def recommend_mentors(
    query: str = Query(..., description="Search query, e.g. AI, database"),
    college_id: int | None = Query(None, description="Student college for priority"),
    top_k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, _ = list_profiles(db, page=1, page_size=1000)
    query_lower = query.lower()

    results = []
    for p in items:
        college_match = 1.0 if (college_id and p.college_id == college_id) else 0.0
        research = (p.research_direction or "").lower()
        intro = (p.introduction or "").lower()
        kw_in_research = 1.0 if query_lower and query_lower in research else 0.0
        kw_in_intro = 1.0 if query_lower and query_lower in intro else 0.0
        score = college_match * 0.5 + kw_in_research * 0.3 + kw_in_intro * 0.2
        reasons = []
        if college_match: reasons.append("Same college")
        if kw_in_research: reasons.append(f"Research matches '{query}'")
        if kw_in_intro: reasons.append(f"Intro matches '{query}'")
        if score > 0:
            results.append(dict(mentor_id=p.id, name=p.real_name, college_id=p.college_id,
                                 title=p.title, research_direction=p.research_direction,
                                 score=round(score, 2),
                                 match_reason="; ".join(reasons) if reasons else "No match"))
    results.sort(key=lambda x: x["score"], reverse=True)
    return ok(data=results[:top_k])


# ── Path param route LAST ──

@router.get("/{mentor_id}", summary="Mentor detail")
def mentor_detail(mentor_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    profile = get_profile_by_id(db, mentor_id)
    if profile is None:
        raise NotFoundError("Mentor not found")
    return ok(data=TeacherProfileOut.model_validate(profile))
