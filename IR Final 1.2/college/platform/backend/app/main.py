"""KCET Counselling Platform — FastAPI Application Entry Point."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.rate_limit import RateLimiter
from app.api.v1.router import router as v1_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()
rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)

app = FastAPI(
    title=settings.APP_NAME,
    description="Production KCET Counselling AI Platform — deterministic recommendations, LLM explains only.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        rate_limiter.check(request)
    return await call_next(request)


app.include_router(v1_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "engine_version": settings.ENGINE_VERSION,
        "architecture": "8-layer deterministic pipeline",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    from app.services.data_service import get_data_service
    svc = get_data_service()
    return {
        "status": "healthy",
        "colleges_loaded": len(svc.colleges),
        "engine": settings.ENGINE_VERSION,
        "data_mode": "json" if settings.USE_JSON_DATA else "postgresql",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
