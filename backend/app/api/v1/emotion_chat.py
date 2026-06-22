"""Emotion Chat API — emotion-aware conversational AI."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.service import ai_service
from app.database.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.emotion.detector import emotion_detector
from app.emotion.prompt_builder import prompt_builder
from app.rag.retrieval import knowledge_qa
from app.utils.response import ok

router = APIRouter(prefix="/emotion", tags=["Emotion Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message", min_length=1)


@router.post("/chat", summary="Emotion-aware chat")
async def emotion_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Step 1: Detect emotion
    emotion_result = emotion_detector.detect(req.message)

    # Step 2: Try RAG retrieval (non-blocking, may be empty)
    retrieval_trace = None
    rag_context = None
    try:
        rag_result = await knowledge_qa.ask(req.message, top_k=3, similarity_threshold=0.15)
        if rag_result.get("chunk_count", 0) > 0:
            rag_context = rag_result.get("context_used", "")
            retrieval_trace = rag_result.get("retrieval_trace")
    except Exception:
        pass

    # Step 3: Build persona + emotion prompt
    messages = prompt_builder.build(req.message, emotion_result, rag_context)

    # Step 4: Generate response
    answer = await ai_service.chat(messages)

    # Step 5: Return structured result
    return ok(data={
        "emotion": emotion_result.emotion,
        "confidence": emotion_result.confidence,
        "matched_keywords": emotion_result.matched_keywords,
        "persona": prompt_builder.build(req.message, emotion_result, None)[0]["content"][:100],
        "answer": answer,
        "retrieval_trace": retrieval_trace,
    })
