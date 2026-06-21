"""Document API — upload, list, status, pipeline trigger (backward-compat)."""

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.core.deps import get_current_user, teacher_required
from app.models.user import User, UserRole
from app.crud.knowledge_document import (
    create_document,
    get_document_by_id,
    list_documents,
    delete_document,
)
from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentOut,
    DocumentStatusOut,
)
from app.schemas.common import PaginatedData
from app.utils.response import ok, error
from app.utils.exceptions import NotFoundError
from app.tasks.pipeline import run_pipeline, run_single_task

router = APIRouter(prefix="/documents", tags=["知识文档(兼容)"])


@router.post("/upload", summary="上传文档(兼容)")
def upload_document(
    file: UploadFile = File(...),
    title: str = Query(default=""),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    allowed = [t.strip() for t in settings.ALLOWED_UPLOAD_TYPES.split(",")]
    ext = Path(file.filename or "unknown").suffix.lower().lstrip(".")
    if ext not in allowed:
        return error(f"不支持的文件类型: .{ext}，允许: {', '.join(allowed)}", code=400)

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}_{file.filename}"
    file_path = upload_dir / safe_name

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as exc:
        return error(f"文件保存失败: {exc}", code=500)

    file_size = file_path.stat().st_size if file_path.exists() else None
    doc_title = title.strip() or (file.filename or "未命名文档")

    doc = create_document(db, uploader_id=current_user.id,
        data=KnowledgeDocumentCreate(
            category_id=category_id, title=doc_title,
            file_name=file.filename or safe_name,
            file_path=str(file_path.resolve()),
            file_size=file_size, mime_type=file.content_type,
        ))
    return ok(data=KnowledgeDocumentOut.model_validate(doc).model_dump(), message="文档上传成功")


@router.get("", summary="文档列表(兼容)")
def list_my_documents(
    category_id: int | None = Query(None),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploader_id = None if current_user.role == UserRole.ADMIN else current_user.id
    items, total = list_documents(db, uploader_id=uploader_id, category_id=category_id,
                                   page=page, page_size=page_size)
    return ok(data=PaginatedData(
        items=[KnowledgeDocumentOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
    ).model_dump())


@router.get("/{document_id}", summary="文档详情(兼容)")
def get_document_detail(document_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    doc = get_document_by_id(db, document_id)
    if doc is None:
        raise NotFoundError("文档不存在")
    return ok(data=KnowledgeDocumentOut.model_validate(doc))


@router.get("/{document_id}/status", summary="获取处理状态(兼容)")
def get_document_status(document_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    doc = get_document_by_id(db, document_id)
    if doc is None:
        raise NotFoundError("文档不存在")
    return ok(data=DocumentStatusOut.model_validate(doc))


@router.post("/{document_id}/pipeline", summary="触发完整流水线(兼容)")
async def trigger_pipeline(
    document_id: int,
    categories: str | None = Query(None),
    skip_classification: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    cat_list = None
    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
    result = await run_pipeline(document_id, db, categories=cat_list,
                                skip_classification=skip_classification)
    return ok(data=result, message="流水线执行完成")


@router.post("/{document_id}/task/{task_name}", summary="触发单个阶段(兼容)")
async def trigger_single_task(
    document_id: int, task_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    result = await run_single_task(document_id, db, task_name)
    if "error" in result:
        return error(result["error"], code=400)
    return ok(data=result, message=f"任务 {task_name} 执行完成")


@router.delete("/{document_id}", summary="删除文档(兼容)")
def delete(document_id: int, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    doc = get_document_by_id(db, document_id)
    if doc is None:
        raise NotFoundError("文档不存在")
    if current_user.role != UserRole.ADMIN and doc.uploader_id != current_user.id:
        return error("无权删除此文档", code=403)
    delete_document(db, doc)
    return ok(message="文档已删除")
