"""Aggregate and register all API routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.teacher import router as teacher_router
from app.api.v1.college import router as college_router
from app.api.v1.knowledge import router as knowledge_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(teacher_router)
api_router.include_router(college_router)
api_router.include_router(knowledge_router)

# TODO: 后续模块在此注册
# api_router.include_router(chat_router)         # AI情感陪聊
# api_router.include_router(rag_router)           # RAG知识库检索
# api_router.include_router(upload_router)        # 文件上传
# api_router.include_router(admin_router)         # 管理员综合接口
# api_router.include_router(log_router)           # 系统日志
