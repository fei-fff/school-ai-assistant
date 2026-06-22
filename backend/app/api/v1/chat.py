"""Unified Chat API — multi-turn with history + memory."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.chat.router import chat_router
from app.chat.memory import extract_memory_context
from app.utils.response import ok

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[dict] = Field(default_factory=list, description="Previous turns [{role,content},...]")


@router.post("/chat", summary="Unified chat with multi-turn history")
async def unified_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Extract memory context from history
    memory = extract_memory_context(req.history)

    # Route to appropriate backend with history
    result = await chat_router.route(req.message, current_user.id, req.history, memory)
    return ok(data=result)
