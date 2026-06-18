"""Knowledge category Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class KnowledgeCategoryCreate(BaseModel):
    parent_id: int | None = None
    name: str
    level: int = 0
    sort_order: int = 0
    status: int = 1


class KnowledgeCategoryUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    level: int | None = None
    sort_order: int | None = None
    status: int | None = None


class KnowledgeCategoryOut(BaseModel):
    id: int
    parent_id: int | None
    name: str
    level: int
    sort_order: int
    status: int
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}
