"""Knowledge category API — admin CRUD, public read."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import admin_required, get_current_user
from app.models.user import User
from app.crud.knowledge_category import (
    get_category_by_id,
    list_categories,
    create_category,
    update_category,
    delete_category,
)
from app.schemas.knowledge_category import (
    KnowledgeCategoryCreate,
    KnowledgeCategoryUpdate,
    KnowledgeCategoryOut,
)
from app.schemas.common import PaginatedData
from app.utils.response import ok
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/categories", tags=["知识分类"])


@router.get("", summary="知识分类列表")
def get_categories(
    parent_id: int | None = Query(None, description="父分类 ID，null=顶层"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = list_categories(
        db, parent_id=parent_id, page=page, page_size=page_size
    )
    return ok(
        data=PaginatedData(
            items=[KnowledgeCategoryOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/{category_id}", summary="分类详情")
def get_category_detail(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = get_category_by_id(db, category_id)
    if cat is None:
        raise NotFoundError("分类不存在")
    return ok(data=KnowledgeCategoryOut.model_validate(cat))


@router.post("", summary="创建分类（管理员）")
def create(
    req: KnowledgeCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    cat = create_category(db, req)
    return ok(data=KnowledgeCategoryOut.model_validate(cat), message="分类创建成功")


@router.put("/{category_id}", summary="更新分类（管理员）")
def update(
    category_id: int,
    req: KnowledgeCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    cat = get_category_by_id(db, category_id)
    if cat is None:
        raise NotFoundError("分类不存在")
    cat = update_category(db, cat, req)
    return ok(data=KnowledgeCategoryOut.model_validate(cat), message="分类更新成功")


@router.delete("/{category_id}", summary="删除分类（管理员）")
def delete(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    cat = get_category_by_id(db, category_id)
    if cat is None:
        raise NotFoundError("分类不存在")
    delete_category(db, cat)
    return ok(message="分类已删除")
