"""Helper functions to build unified API responses."""

from typing import Any

from app.schemas.common import ApiResponse


def ok(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(code=200, message=message, data=data)


def created(data: Any = None, message: str = "创建成功") -> ApiResponse:
    return ApiResponse(code=201, message=message, data=data)


def error(message: str = "服务器内部错误", code: int = 500) -> ApiResponse:
    return ApiResponse(code=code, message=message, data=None)
