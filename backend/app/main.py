"""FastAPI application initialization."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    ai_provider,
    auth,
    coach,
    photos,
    plans,
    progress,
    roadmap,
    users,
    wellness,
)
from app.core.config import settings
from app.core.database import check_db_connection
from app.core.errors import AarogyaError, aarogya_exception_handler
from app.core.logging_config import setup_logging
from app.core.redis_client import check_redis_connection
from app.rag.vector_store import check_qdrant_connection, ensure_collections

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Aarogya API...")
    ensure_collections()
    yield
    # Shutdown
    logger.info("Shutting down Aarogya API...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AarogyaError, aarogya_exception_handler)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wellness.router)
app.include_router(progress.router)
app.include_router(plans.router)
app.include_router(photos.router)
app.include_router(ai_provider.router)
app.include_router(coach.router)
app.include_router(roadmap.router)


@app.get("/health")
async def health():
    """System health check endpoint."""
    return {
        "status": "ok",
        "service": "aarogya-api",
        "database": check_db_connection(),
        "redis": check_redis_connection(),
        "qdrant": check_qdrant_connection(),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback exception handler to avoid exposing internals."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
