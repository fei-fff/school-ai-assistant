"""Document API — upload, list, status, pipeline trigger."""

import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.core.deps import get_current_user, teacher_required, admin_required
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

router = APIRouter(prefix="/documents", tags=["知识文档"])


@router.post("/upload", summary="上传文档")
def upload_document(
    file: UploadFile = File(...),
    title: str = Query(default="", description="文档标题，留空则使用文件名"),
    category_id: int | None = Query(None, description="所属分类 ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    """Upload a knowledge document.

    Teachers can upload; the file is saved to UPLOAD_DIR.
    Returns the created document record (status = waiting for all stages).
    """
    # Validate file type
    allowed = [t.strip() for t in settings.ALLOWED_UPLOAD_TYPES.split(",")]
    ext = Path(file.filename or "unknown").suffix.lower().lstrip(".")
    if ext not in allowed:
        return error(f"不支持的文件类型: .{ext}，允许: {', '.join(allowed)}", code=400)

    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}_{file.filename}"
    file_path = upload_dir / safe_name

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as exc:
        return error(f"文件保存失败: {exc}", code=500)

    file_path_str = str(file_path.resolve())
    file_size = file_path.stat().st_size if file_path.exists() else None
    doc_title = title.strip() or (file.filename or "未命名文档")

    doc = create_document(
        db,
        uploader_id=current_user.id,
        data=KnowledgeDocumentCreate(
            category_id=category_id,
            title=doc_title,
            file_name=file.filename or safe_name,
            file_path=file_path_str,
            file_size=file_size,
            mime_type=file.content_type,
        ),
    )

    return ok(
        data=KnowledgeDocumentOut.model_validate(doc).model_dump(),
        message="文档上传成功",
    )


@router.get("", summary="文档列表")
def list_my_documents(
    category_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List documents. Teachers see own; admins see all."""
    uploader_id = None if current_user.role == UserRole.ADMIN else current_user.id
    items, total = list_documents(
        db,
        uploader_id=uploader_id,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )
    return ok(
        data=PaginatedData(
            items=[KnowledgeDocumentOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        ).model_dump()
    )


@router.get("/{document_id}", summary="文档详情")
def get_document_detail(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = get_document_by_id(db, document_id)
    if doc is None:
        raise NotFoundError("文档不存在")
    return ok(data=KnowledgeDocumentOut.model_validate(doc))


@router.get("/{document_id}/status", summary="获取处理状态")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lightweight endpoint for polling processing progress."""
    doc = get_document_by_id(db, document_id)
    if doc is None:
        raise NotFoundError("文档不存在")
    return ok(data=DocumentStatusOut.model_validate(doc))


@router.post("/{document_id}/pipeline", summary="触发完整处理流水线")
def trigger_pipeline(
    document_id: int,
    categories: str | None = Query(None, description="自定义分类列表，逗号分隔"),
    skip_classification: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    """Run the full RAG pipeline on an uploaded document.

    Stages: parser → summary → classify → embedding

    This is synchronous — the API waits for all stages to complete.
    For large documents, consider triggering via a background worker.
    """
    import asyncio

    cat_list = None
    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            run_pipeline(
                document_id,
                db,
                categories=cat_list,
                skip_classification=skip_classification,
            )
        )
    finally:
        loop.close()

    return ok(data=result, message="流水线执行完成")


@router.post("/{document_id}/task/{task_name}", summary="触发单个处理阶段")
def trigger_single_task(
    document_id: int,
    task_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    """Run a single pipeline stage (for retries).

    task_name: parser / summary / classify / embedding
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            run_single_task(document_id, db, task_name)
        )
    finally:
        loop.close()

    if "error" in result:
        return error(result["error"], code=400)
    return ok(data=result, message=f"任务 {task_name} 执行完成")


@router.delete("/{document_id}", summary="删除文档（管理员/上传者）")
def delete(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = get_document_by_id(db, document_id)
    if doc is None:
        raise NotFoundError("文档不存在")
    if current_user.role != UserRole.ADMIN and doc.uploader_id != current_user.id:
        return error("无权删除此文档", code=403)
    delete_document(db, doc)
    return ok(message="文档已删除")
