"""User-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr
    nickname: str | None = None
    avatar: str | None = None


class UserRegister(BaseModel):
    """Schema for user registration."""

    username: str
    email: EmailStr
    password: str
    confirm_password: str
    role: str = "student"  # student / teacher

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("用户名至少3个字符")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码至少6个字符")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    """Public user profile returned in API responses (excludes password)."""

    id: int
    username: str
    nickname: str | None
    email: str
    avatar: str | None
    role: str
    status: int
    create_time: datetime
    update_time: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
