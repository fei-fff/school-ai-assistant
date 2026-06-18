"""Teacher profile API — CRUD with role-based access."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import get_current_user, teacher_required, admin_required, student_required
from app.models.user import User
from app.crud.teacher_profile import (
    get_profile_by_user_id,
    get_profile_by_id,
    list_profiles,
    create_profile,
    update_profile,
    delete_profile,
)
from app.schemas.teacher_profile import (
    TeacherProfileCreate,
    TeacherProfileUpdate,
    TeacherProfileOut,
)
from app.schemas.common import PaginatedData
from app.utils.response import ok, error
from app.utils.exceptions import NotFoundError, PermissionException

router = APIRouter(prefix="/teachers", tags=["导师名片"])


@router.get("", summary="导师列表（学生/管理员可查看）")
def list_teacher_profiles(
    college_id: int | None = Query(None, description="学院 ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List teacher profiles. Available to all authenticated users."""
    items, total = list_profiles(db, college_id=college_id, page=page, page_size=page_size)
    return ok(
        data=PaginatedData(
            items=[TeacherProfileOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/me", summary="获取我的导师名片")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    profile = get_profile_by_user_id(db, current_user.id)
    if profile is None:
        return ok(data=None, message="尚未创建导师名片")
    return ok(data=TeacherProfileOut.model_validate(profile))


@router.post("/me", summary="创建我的导师名片")
def create_my_profile(
    req: TeacherProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    try:
        profile = create_profile(db, current_user.id, req)
        return ok(data=TeacherProfileOut.model_validate(profile), message="名片创建成功")
    except Exception as e:
        return error(str(e), code=409)


@router.put("/me", summary="更新我的导师名片")
def update_my_profile(
    req: TeacherProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    profile = get_profile_by_user_id(db, current_user.id)
    if profile is None:
        raise NotFoundError("尚未创建导师名片，请先创建")
    profile = update_profile(db, profile, req)
    return ok(data=TeacherProfileOut.model_validate(profile), message="名片更新成功")


@router.get("/{profile_id}", summary="查看导师详情")
def get_profile_detail(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_profile_by_id(db, profile_id)
    if profile is None:
        raise NotFoundError("导师名片不存在")
    return ok(data=TeacherProfileOut.model_validate(profile))


# TODO: 管理员删除导师名片接口
# TODO: 导师智能匹配接口
