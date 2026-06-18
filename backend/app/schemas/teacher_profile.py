"""Teacher profile Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class TeacherProfileCreate(BaseModel):
    college_id: int | None = None
    avatar: str | None = None
    real_name: str
    title: str | None = None
    research_direction: str | None = None
    laboratory: str | None = None
    email: str | None = None
    phone: str | None = None
    introduction: str | None = None
    student_requirement: str | None = None
    homepage: str | None = None
    tags: str | None = None


class TeacherProfileUpdate(BaseModel):
    college_id: int | None = None
    avatar: str | None = None
    real_name: str | None = None
    title: str | None = None
    research_direction: str | None = None
    laboratory: str | None = None
    email: str | None = None
    phone: str | None = None
    introduction: str | None = None
    student_requirement: str | None = None
    homepage: str | None = None
    tags: str | None = None


class TeacherProfileOut(BaseModel):
    id: int
    user_id: int
    college_id: int | None
    avatar: str | None
    real_name: str
    title: str | None
    research_direction: str | None
    laboratory: str | None
    email: str | None
    phone: str | None
    introduction: str | None
    student_requirement: str | None
    homepage: str | None
    tags: str | None
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}
