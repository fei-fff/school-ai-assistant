"""College Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class CollegeCreate(BaseModel):
    name: str
    description: str | None = None
    logo: str | None = None
    sort_order: int = 0
    status: int = 1


class CollegeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    logo: str | None = None
    sort_order: int | None = None
    status: int | None = None


class CollegeOut(BaseModel):
    id: int
    name: str
    description: str | None
    logo: str | None
    sort_order: int
    status: int
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}
