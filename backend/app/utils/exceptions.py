"""Custom application exceptions — hierarchical for unified error handling."""


# ---- Base ----


class AppException(Exception):
    """Base application exception with HTTP status code."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ---- Business ----


class BusinessException(AppException):
    """General business logic exception (400)."""

    def __init__(self, message: str = "业务处理异常"):
        super().__init__(message, status_code=400)


class DuplicateError(AppException):
    """Duplicate resource (409)."""

    def __init__(self, message: str = "数据已存在"):
        super().__init__(message, status_code=409)


class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status_code=404)


# ---- Auth ----


class AuthenticationException(AppException):
    """Authentication failed (401)."""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, status_code=401)


class PermissionException(AppException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status_code=403)


# ---- AI ----


class AIException(AppException):
    """AI service error (502)."""

    def __init__(self, message: str = "AI 服务异常"):
        super().__init__(message, status_code=502)


# ---- Knowledge ----


class KnowledgeException(AppException):
    """Knowledge base error (400)."""

    def __init__(self, message: str = "知识库处理异常"):
        super().__init__(message, status_code=400)
