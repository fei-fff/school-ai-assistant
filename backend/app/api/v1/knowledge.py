"""Knowledge API — upload, process, query, and category management."""

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
    create_document, get_document_by_id, list_documents, delete_document,
)
from app.crud.knowledge_category import (
    get_category_by_id, list_categories, create_category, update_category, delete_category,
)
from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate, KnowledgeDocumentOut, DocumentStatusOut,
)
from app.schemas.knowledge_category import (
    KnowledgeCategoryCreate, KnowledgeCategoryUpdate, KnowledgeCategoryOut,
)
from app.schemas.common import PaginatedData
from app.utils.response import ok, error
from app.utils.exceptions import NotFoundError
from app.tasks.pipeline import run_pipeline, run_single_task
from app.rag.retrieval import knowledge_qa

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.post("/upload", summary="上传知识文档")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Query(default=""),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    allowed = [t.strip() for t in settings.ALLOWED_UPLOAD_TYPES.split(",")]
    ext = Path(file.filename or "unknown").suffix.lower().lstrip(".")
    if ext not in allowed:
        return error(f"Unsupported: .{ext}, allowed: {', '.join(allowed)}", code=400)

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}_{file.filename}"
    file_path = upload_dir / safe_name

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as exc:
        return error(f"Save failed: {exc}", code=500)

    file_size = file_path.stat().st_size if file_path.exists() else None
    doc_title = title.strip() or (file.filename or "untitled")

    doc = create_document(db, uploader_id=current_user.id,
        data=KnowledgeDocumentCreate(
            category_id=category_id, title=doc_title,
            file_name=file.filename or safe_name,
            file_path=str(file_path.resolve()),
            file_size=file_size, mime_type=file.content_type,
        ))
    return ok(data=KnowledgeDocumentOut.model_validate(doc).model_dump(),
              message="Uploaded. Call /knowledge/process/{id} to process.")


@router.post("/process/{doc_id}", summary="触发文档处理流水线")
async def process_document(
    doc_id: int,
    categories: str | None = Query(None),
    skip_classification: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    cat_list = None
    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
    result = await run_pipeline(doc_id, db, categories=cat_list, skip_classification=skip_classification)
    return ok(data=result, message="Pipeline complete")


@router.post("/process/{doc_id}/{task_name}", summary="触发单个处理阶段")
async def process_single_task(
    doc_id: int, task_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_required),
):
    result = await run_single_task(doc_id, db, task_name)
    if "error" in result:
        return error(result["error"], code=400)
    return ok(data=result, message=f"Task {task_name} done")


@router.post("/query", summary="知识库问答")
async def query_knowledge(
    question: str = Query(..., description="Question"),
    top_k: int = Query(5, ge=1, le=20),
    similarity_threshold: float = Query(0.3, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ready = await knowledge_qa.is_ready()
    if not ready:
        return ok(data={
            "answer": "Knowledge base not initialized. Upload and process a document first.",
            "sources": [], "scores": [], "chunk_count": 0, "context_used": "",
            "retrieval_trace": {"error": "vector_store_empty"},
        })
    result = await knowledge_qa.ask(query=question, top_k=top_k, similarity_threshold=similarity_threshold)
    return ok(data=result)


@router.get("/documents", summary="文档列表")
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


@router.get("/documents/{doc_id}", summary="文档详情")
def get_document_detail(doc_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    doc = get_document_by_id(db, doc_id)
    if doc is None:
        raise NotFoundError("Not found")
    return ok(data=KnowledgeDocumentOut.model_validate(doc))


@router.get("/documents/{doc_id}/status", summary="获取处理状态")
def get_document_status(doc_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    doc = get_document_by_id(db, doc_id)
    if doc is None:
        raise NotFoundError("Not found")
    return ok(data=DocumentStatusOut.model_validate(doc))


@router.delete("/documents/{doc_id}", summary="删除文档")
def delete_doc(doc_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    doc = get_document_by_id(db, doc_id)
    if doc is None:
        raise NotFoundError("Not found")
    if current_user.role != UserRole.ADMIN and doc.uploader_id != current_user.id:
        return error("Permission denied", code=403)
    delete_document(db, doc)
    return ok(message="Deleted")


category_router = APIRouter(prefix="/categories", tags=["知识分类"])


@category_router.get("", summary="知识分类列表")
def get_categories(parent_id: int | None = Query(None), page: int = Query(1, ge=1),
                   page_size: int = Query(100, ge=1, le=500),
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    items, total = list_categories(db, parent_id=parent_id, page=page, page_size=page_size)
    return ok(data=PaginatedData(
        items=[KnowledgeCategoryOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
    ).model_dump())


@category_router.get("/{category_id}", summary="分类详情")
def get_category_detail(category_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    cat = get_category_by_id(db, category_id)
    if cat is None:
        raise NotFoundError("Not found")
    return ok(data=KnowledgeCategoryOut.model_validate(cat))


@category_router.post("", summary="创建分类（管理员）")
def create_category_endpoint(req: KnowledgeCategoryCreate, db: Session = Depends(get_db),
                               current_user: User = Depends(admin_required)):
    cat = create_category(db, req)
    return ok(data=KnowledgeCategoryOut.model_validate(cat))


@category_router.put("/{category_id}", summary="更新分类（管理员）")
def update_category_endpoint(category_id: int, req: KnowledgeCategoryUpdate,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(admin_required)):
    cat = get_category_by_id(db, category_id)
    if cat is None:
        raise NotFoundError("Not found")
    cat = update_category(db, cat, req)
    return ok(data=KnowledgeCategoryOut.model_validate(cat))


@category_router.delete("/{category_id}", summary="删除分类（管理员）")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db),
                               current_user: User = Depends(admin_required)):
    cat = get_category_by_id(db, category_id)
    if cat is None:
        raise NotFoundError("Not found")
    delete_category(db, cat)
    return ok(message="Deleted")


router.include_router(category_router)
