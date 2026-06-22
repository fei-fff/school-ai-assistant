"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.core.config import settings
from app.database.database import SessionLocal
from app.crud.seed_colleges import seed
from app.middleware.exceptions import (
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.routers import api_router
from app.utils.exceptions import AppException

logging.basicConfig(level=logging.INFO,
                     format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s v%s starting", settings.APP_NAME, settings.APP_VERSION)
    db = SessionLocal()
    try:
        n = seed(db)
        if n > 0:
            logger.info("Seeded %d colleges", n)
    finally:
        db.close()
    yield
    logger.info("%s shutting down", settings.APP_NAME)


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}
