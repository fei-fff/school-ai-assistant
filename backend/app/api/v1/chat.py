"""Unified Chat API — single entry point for all assistant capabilities."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.chat.router import chat_router
from app.utils.response import ok

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


@router.post("/chat", summary="Unified chat (emotion + mentor + knowledge)")
async def unified_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await chat_router.route(req.message, current_user.id)
    return ok(data=result)
