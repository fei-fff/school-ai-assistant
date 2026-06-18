"""College API — admin CRUD, public read."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import admin_required, get_current_user
from app.models.user import User
from app.crud.college import (
    get_college_by_id,
    list_colleges,
    create_college,
    update_college,
    delete_college,
)
from app.schemas.college import CollegeCreate, CollegeUpdate, CollegeOut
from app.schemas.common import PaginatedData
from app.utils.response import ok
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/colleges", tags=["学院管理"])


@router.get("", summary="学院列表")
def get_colleges(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = list_colleges(db, page=page, page_size=page_size)
    return ok(
        data=PaginatedData(
            items=[CollegeOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/{college_id}", summary="学院详情")
def get_college_detail(
    college_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    college = get_college_by_id(db, college_id)
    if college is None:
        raise NotFoundError("学院不存在")
    return ok(data=CollegeOut.model_validate(college))


@router.post("", summary="创建学院（管理员）")
def create(
    req: CollegeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    college = create_college(db, req)
    return ok(data=CollegeOut.model_validate(college), message="学院创建成功")


@router.put("/{college_id}", summary="更新学院（管理员）")
def update(
    college_id: int,
    req: CollegeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    college = get_college_by_id(db, college_id)
    if college is None:
        raise NotFoundError("学院不存在")
    college = update_college(db, college, req)
    return ok(data=CollegeOut.model_validate(college), message="学院更新成功")


@router.delete("/{college_id}", summary="删除学院（管理员）")
def delete(
    college_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    college = get_college_by_id(db, college_id)
    if college is None:
        raise NotFoundError("学院不存在")
    delete_college(db, college)
    return ok(message="学院已删除")
