"""Global exception handlers."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas.common import ApiResponse
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("AppException: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(code=exc.status_code, message=exc.message).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.warning("ValidationError: %s", exc.errors())
    messages = [
        ".".join(str(loc) for loc in err["loc"]) + ": " + err["msg"]
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=ApiResponse(code=422, message="; ".join(messages)).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content=ApiResponse(code=500, message="服务器内部错误").model_dump(),
    )
