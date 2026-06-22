"""User profile schemas."""

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    college: str | None = None
    interests: str | None = None
    emotion_state: str | None = None
    frequent_topics: str | None = None


class ProfileOut(BaseModel):
    user_id: int
    college: str | None
    interests: str | None
    emotion_state: str | None
    frequent_topics: str | None

    model_config = {"from_attributes": True}
