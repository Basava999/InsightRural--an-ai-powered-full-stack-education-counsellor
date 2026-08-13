# ==============================================================================
# InsightRural — Health & Metadata Router
# ==============================================================================
# Endpoints: /health, /branches, /locations, /statistics, /ai/status, /debug
# Migrated from app.py Flask endpoints (lines 487-645, 1148-1169)
# ==============================================================================

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import func

from core.logging import get_logger
from core.dependencies import (
    get_json_data_service,
    is_llm_available,
    is_rag_available,
    is_kea_available,
    is_ml_available,
)

logger = get_logger("api.health")
router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check with service availability matrix."""
    try:
        from db import SessionLocal
        from db_models import College, FeeStructure

        session = SessionLocal()
        try:
            college_count = session.query(func.count(College.id)).scalar() or 0
            fee_count = session.query(func.count(FeeStructure.category)).scalar() or 0
        finally:
            session.close()

        return {
            "status": "healthy",
            "message": "API is running",
            "database": {
                "colleges": college_count,
                "fee_structures": fee_count,
            },
            "services": {
                "llm": is_llm_available(),
                "rag": is_rag_available(),
                "kea_engine": is_kea_available(),
                "ml_predictor": is_ml_available(),
            },
        }
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "message": str(e)},
        )


@router.get("/branches")
async def get_branches():
    """Get all unique branches from SQLite database."""
    try:
        from db import SessionLocal
        from db_models import College

        session = SessionLocal()
        try:
            colleges = session.query(College).all()
            branches_set = set()
            for college in colleges:
                if college.branches:
                    for branch in college.branches:
                        if branch:
                            branches_set.add(branch)
            return sorted(list(branches_set))
        finally:
            session.close()
    except Exception as e:
        logger.error("Error in get_branches: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content=[])


@router.get("/locations")
async def get_locations():
    """Get all unique locations."""
    try:
        from db import SessionLocal
        from db_models import College

        session = SessionLocal()
        try:
            locations = (
                session.query(func.distinct(College.location))
                .filter(College.location.isnot(None))
                .order_by(College.location)
                .all()
            )
            return [loc[0] for loc in locations if loc[0]]
        finally:
            session.close()
    except Exception as e:
        logger.error("Error in get_locations: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content=[])


@router.get("/statistics")
async def get_statistics():
    """Get platform statistics."""
    try:
        from db import SessionLocal
        from db_models import College

        session = SessionLocal()
        try:
            total_colleges = session.query(func.count(College.id)).scalar() or 0
            total_locations = session.query(
                func.count(func.distinct(College.location))
            ).scalar() or 0

            colleges = session.query(College).all()
            branches_set = set()
            for college in colleges:
                if college.branches:
                    for branch in college.branches:
                        if branch:
                            branches_set.add(branch)

            return {
                "total_colleges": total_colleges,
                "total_locations": total_locations,
                "total_branches": len(branches_set),
            }
        finally:
            session.close()
    except Exception as e:
        logger.error("Error in get_statistics: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"total_colleges": 0, "total_locations": 0, "total_branches": 0},
        )


@router.get("/ai/status")
async def ai_status():
    """Check AI system status (LLM + RAG)."""
    status = {
        "ai_modules_available": is_llm_available(),
        "ollama_connected": False,
        "ollama_model": "llama3",
        "rag_indexed": False,
        "pipeline": "local-ollama-llama3-chromadb-rag",
    }

    if status["ai_modules_available"]:
        try:
            from core.dependencies import get_llm_service
            counselor = get_llm_service()
            detail = counselor.get_status()
            status["ollama_connected"] = detail.get("ollama", {}).get("available", False)
            status["ollama_model"] = detail.get("ollama", {}).get("model", "llama3")
            status["rag_indexed"] = detail.get("rag_engine", {}).get("available", False)
        except Exception:
            pass

    return status


@router.get("/search/suggestions")
async def get_suggestions(q: str = ""):
    """Autocomplete search suggestions."""
    if len(q.strip()) < 2:
        return []

    try:
        from db import SessionLocal
        from db_models import College

        session = SessionLocal()
        try:
            results = (
                session.query(College.name, College.location)
                .filter(College.name.ilike(f"%{q}%"))
                .limit(5)
                .all()
            )
            return [{"name": r[0], "location": r[1] or ""} for r in results]
        finally:
            session.close()
    except Exception as e:
        logger.error("Error in get_suggestions: %s", e)
        return []
