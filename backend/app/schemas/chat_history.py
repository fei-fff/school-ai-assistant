"""Chat history Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    session_id: str
    role: str  # user / assistant / system
    content: str
    token_count: int | None = None


class ChatMessageOut(BaseModel):
    id: int
    user_id: int
    session_id: str
    role: str
    content: str
    token_count: int | None
    create_time: datetime

    model_config = {"from_attributes": True}
