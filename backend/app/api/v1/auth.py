"""Auth endpoints — register, login, get current user."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.user import authenticate_user, create_user
from app.database.database import get_db
from app.schemas.user import TokenResponse, UserLogin, UserOut, UserRegister
from app.core.security import create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.utils.response import ok, created, error

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", summary="用户注册")
def register(req: UserRegister, db: Session = Depends(get_db)):
    """Register a new user (student or teacher only)."""
    if req.role not in ("student", "teacher"):
        return error("仅支持注册学生或教师角色", code=400)
    try:
        user = create_user(db, req)
    except Exception as e:
        return error(str(e), code=409)
    return created(data=UserOut.model_validate(user))


@router.post("/login", summary="用户登录")
def login(req: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, req.username, req.password)
    if user is None:
        return error("用户名或密码错误", code=401)
    if user.status.value == 0:
        return error("账号已被禁用", code=403)

    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return ok(
        data=TokenResponse(
            access_token=token,
            user=UserOut.model_validate(user),
        ).model_dump()
    )


@router.get("/me", summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return ok(data=UserOut.model_validate(current_user))
