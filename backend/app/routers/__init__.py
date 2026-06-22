"""Aggregate and register all API routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.teacher import router as teacher_router
from app.api.v1.college import router as college_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.documents import router as documents_router
from app.api.v1.qa import router as qa_router
from app.api.v1.emotion_chat import router as emotion_router
from app.api.v1.mentor import router as mentor_router
from app.api.v1.chat import router as chat_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(teacher_router)
api_router.include_router(college_router)
api_router.include_router(knowledge_router)
api_router.include_router(documents_router)
api_router.include_router(qa_router)
api_router.include_router(emotion_router)
api_router.include_router(mentor_router)
api_router.include_router(chat_router)
