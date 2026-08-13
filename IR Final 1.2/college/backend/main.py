# ==============================================================================
# InsightRural — FastAPI Application Entry Point
# ==============================================================================
# Production-ready FastAPI application. Uses the core/ infrastructure for
# configuration, logging, exceptions, and dependency injection.
#
# Run with: uvicorn main:app --reload --port 5000
# ==============================================================================

import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Ensure backend directory is on sys.path ───────────────────────────────────

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ── Core Infrastructure ──────────────────────────────────────────────────────

from core.config import settings
from core.logging import setup_logging, get_logger
from core.exceptions import InsightRuralError
from core.dependencies import (
    get_json_data_service,
    get_recommendation_service,
    get_query_parser,
    get_rag_engine,
    is_rag_available,
)

# Initialize structured logging FIRST
setup_logging()
logger = get_logger("InsightRural")

# ── Backward-Compatible Global Accessors ──────────────────────────────────────
# These functions are imported by api/chat.py and other modules.
# They now delegate to core.dependencies but maintain the same interface.
# ──────────────────────────────────────────────────────────────────────────────

def get_json_data():
    """Backward-compatible accessor. Delegates to core.dependencies."""
    return get_json_data_service()


# Re-export these so existing `from main import ...` statements still work
# (get_recommendation_service and get_query_parser are already imported above)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize engines on startup, cleanup on shutdown."""
    logger.info("=" * 60)
    logger.info("  %s v%s — Starting up", settings.APP_NAME, settings.APP_VERSION)
    logger.info("=" * 60)

    start = time.time()

    # Initialize core data service (loads all JSON data)
    try:
        data = get_json_data_service()
        logger.info(
            "  JSON Data: %d colleges, %d cutoffs, %d scholarships",
            len(data.colleges), len(data.cutoffs), len(data.scholarships),
        )
    except Exception as e:
        logger.error("  CRITICAL: JSONDataService failed to initialize: %s", e)
        raise

    # Initialize recommendation service
    try:
        get_recommendation_service()
        logger.info("  Recommendation Engine: ready")
    except Exception as e:
        logger.error("  Recommendation Engine failed: %s", e)

    # Initialize query parser
    try:
        get_query_parser()
        logger.info("  Query Parser: ready")
    except Exception as e:
        logger.error("  Query Parser failed: %s", e)

    # Try to initialize RAG engine (optional — degrades gracefully)
    if is_rag_available():
        try:
            rag = get_rag_engine()
            if rag.client:
                logger.info("  RAG Engine (ChromaDB): ready")
            else:
                logger.warning("  RAG Engine: ChromaDB client not available")
        except Exception as e:
            logger.warning("  RAG Engine: %s", e)
    else:
        logger.warning("  RAG Engine: not available (will use fallback)")

    elapsed = time.time() - start
    logger.info("  Startup completed in %.2fs", elapsed)
    logger.info("=" * 60)

    yield

    logger.info("InsightRural shutting down...")


# ── Create App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)


# ══════════════════════════════════════════════════════════════════════════════
# Middleware Stack
# ══════════════════════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    Adds request ID tracking and response timing.
    - X-Request-ID: Unique ID for tracing requests through logs
    - X-Response-Time: Wall-clock time for the request
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.request_id = request_id

    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{elapsed:.3f}s"

    # Log slow requests
    if elapsed > 2.0:
        logger.warning(
            "Slow request: %s %s took %.2fs [%s]",
            request.method, request.url.path, elapsed, request_id,
        )

    return response


# ══════════════════════════════════════════════════════════════════════════════
# Exception Handlers
# ══════════════════════════════════════════════════════════════════════════════

@app.exception_handler(InsightRuralError)
async def insight_rural_error_handler(request: Request, exc: InsightRuralError):
    """
    Handle all typed application exceptions.
    Each InsightRuralError subclass carries its own HTTP status code.
    """
    logger.warning(
        "Application error [%s]: %s (path=%s)",
        exc.error_code, exc.message, request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI/Starlette HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_code": "HTTP_ERROR",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected exceptions. Logs full traceback."""
    logger.error(
        "Unhandled error on %s %s: %s",
        request.method, request.url.path, exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal error occurred. Please try again.",
            "error_code": "INTERNAL_ERROR",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# Import & Register Routers
# ══════════════════════════════════════════════════════════════════════════════

from api.predict import router as predict_router
from api.chat import router as chat_router
from api.health import router as health_router

# Always-available routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(predict_router, prefix="/api", tags=["Predict"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# Routers migrated from app.py — loaded with graceful fallback
_new_routers = [
    ("api.simulation", "Simulation"),
    ("api.admissions", "Admissions"),
    ("api.career", "Career"),
    ("api.auth", "Auth"),
    ("api.reports", "Reports"),
    ("api.risk", "Risk"),
    ("api.admin", "Admin"),
    ("api.recommend", "Recommend"),
    ("api.colleges", "Colleges"),
    ("api.scholarships", "Scholarships"),
    ("api.hostels", "Hostels"),
]

for module_name, tag in _new_routers:
    try:
        import importlib
        mod = importlib.import_module(module_name)
        if hasattr(mod, "router"):
            app.include_router(mod.router, prefix="/api", tags=[tag])
            logger.debug("Loaded router: %s", module_name)
    except ImportError:
        logger.debug("Router %s not yet available", module_name)
    except Exception as e:
        logger.warning("Failed to load router %s: %s", module_name, e)


# ── Root Route ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Run with: uvicorn main:app --reload --port 5000
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
