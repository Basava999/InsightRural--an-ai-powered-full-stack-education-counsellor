# ==============================================================================
# InsightRural — Admissions Router (JEE + NEET + Unified)
# ==============================================================================
# Endpoints: /admission-probability, /jee/*, /neet/*, /compare,
#            /career/roadmap, /admission-counselor
# Migrated from app.py Flask endpoints (lines 1172-1355)
# ==============================================================================

import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from core.logging import get_logger
from core.exceptions import ServiceUnavailableError

logger = get_logger("api.admissions")
router = APIRouter()


def _require_admissions():
    """Import admissions service or raise 503."""
    try:
        from admission_probability import calculate_admission_probability
        from admissions_service import (
            answer_admission_query,
            build_neet_counseling_plan,
            compare_colleges as compare_colleges_service,
            compare_jee_options,
            generate_career_roadmap,
            get_jee_cutoffs,
            get_neet_cutoffs,
            predict_jee,
            predict_neet,
        )
        return {
            "calculate_admission_probability": calculate_admission_probability,
            "answer_admission_query": answer_admission_query,
            "build_neet_counseling_plan": build_neet_counseling_plan,
            "compare_colleges_service": compare_colleges_service,
            "compare_jee_options": compare_jee_options,
            "generate_career_roadmap": generate_career_roadmap,
            "get_jee_cutoffs": get_jee_cutoffs,
            "get_neet_cutoffs": get_neet_cutoffs,
            "predict_jee": predict_jee,
            "predict_neet": predict_neet,
        }
    except ImportError as e:
        raise ServiceUnavailableError("Admissions Service", {"detail": str(e)})


# ── Admission Probability ────────────────────────────────────────────────────

@router.post("/admission-probability")
async def admission_probability_endpoint(data: Dict[str, Any]):
    """Calculate rank-vs-cutoff admission probability from 0 to 100."""
    svc = _require_admissions()
    calc = svc["calculate_admission_probability"]

    rank = data.get("rank")
    previous_cutoff = data.get("previous_cutoff") or data.get("cutoff")
    category = data.get("category", "OPEN")

    if data.get("colleges"):
        results = []
        for college in data.get("colleges", []):
            cutoff = college.get("cutoff") or college.get("previous_cutoff")
            probability = calc(rank, cutoff, category)
            results.append({
                "college": college.get("college") or college.get("name"),
                "branch": college.get("branch") or college.get("course"),
                "previous_cutoff": cutoff,
                **probability,
            })
        return {"success": True, "results": results}

    if not rank or not previous_cutoff:
        raise HTTPException(status_code=400, detail="rank and previous_cutoff are required")

    return {
        "success": True,
        "rank": rank,
        "previous_cutoff": previous_cutoff,
        "category": category,
        **calc(rank, previous_cutoff, category),
    }


# ── JEE Endpoints ────────────────────────────────────────────────────────────

@router.post("/jee/predict")
async def jee_predict_endpoint(data: Dict[str, Any]):
    """Predict IIT, NIT, IIIT, and GFTI options from JEE ranks."""
    svc = _require_admissions()
    if not data.get("jee_main_rank") and not data.get("jee_advanced_rank"):
        raise HTTPException(status_code=400, detail="Provide JEE Main rank or JEE Advanced rank")
    try:
        return svc["predict_jee"](data)
    except Exception as e:
        logger.error("JEE prediction error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/jee/compare")
async def jee_compare_endpoint(data: Dict[str, Any]):
    """Compare JEE options or named colleges."""
    svc = _require_admissions()
    try:
        return svc["compare_jee_options"](data)
    except Exception as e:
        logger.error("JEE compare error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.get("/jee/cutoffs")
async def jee_cutoffs_endpoint(
    institute_type: Optional[str] = None,
    category: Optional[str] = None,
    branch: Optional[str] = None,
    quota: Optional[str] = None,
):
    """Return JEE cutoff rows with optional filters."""
    svc = _require_admissions()
    filters = {}
    if institute_type: filters["institute_type"] = institute_type
    if category: filters["category"] = category
    if branch: filters["branch"] = branch
    if quota: filters["quota"] = quota
    try:
        return svc["get_jee_cutoffs"](filters)
    except Exception as e:
        logger.error("JEE cutoffs error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ── NEET Endpoints ────────────────────────────────────────────────────────────

@router.post("/neet/predict")
async def neet_predict_endpoint(data: Dict[str, Any]):
    """Predict AIQ, state, government, private, dental, and AYUSH options."""
    svc = _require_admissions()
    if not data.get("neet_rank"):
        raise HTTPException(status_code=400, detail="NEET rank is required")
    try:
        return svc["predict_neet"](data)
    except Exception as e:
        logger.error("NEET prediction error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/neet/cutoffs")
async def neet_cutoffs_endpoint(data: Dict[str, Any]):
    """Return NEET cutoff rows with optional filters."""
    svc = _require_admissions()
    try:
        return svc["get_neet_cutoffs"](data)
    except Exception as e:
        logger.error("NEET cutoffs error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/neet/counseling")
async def neet_counseling_endpoint(data: Dict[str, Any]):
    """Generate a NEET counseling plan with choice buckets and documents."""
    svc = _require_admissions()
    if not data.get("neet_rank"):
        raise HTTPException(status_code=400, detail="NEET rank is required")
    try:
        return svc["build_neet_counseling_plan"](data)
    except Exception as e:
        logger.error("NEET counseling error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ── Unified Compare ───────────────────────────────────────────────────────────

@router.post("/compare")
async def unified_compare_endpoint(data: Dict[str, Any]):
    """Compare fees, placement, hostel, location for multiple colleges."""
    svc = _require_admissions()
    try:
        return svc["compare_colleges_service"](data)
    except Exception as e:
        logger.error("Unified compare error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ── Career Roadmap ────────────────────────────────────────────────────────────

@router.post("/career/roadmap")
async def career_roadmap_endpoint(data: Dict[str, Any]):
    """Generate a deterministic 5-year roadmap and opportunity summary."""
    svc = _require_admissions()
    try:
        return svc["generate_career_roadmap"](data)
    except Exception as e:
        logger.error("Career roadmap error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ── Admission Counselor (RAG) ─────────────────────────────────────────────────

@router.post("/admission-counselor")
async def admission_counselor_endpoint(data: Dict[str, Any]):
    """RAG-style admission counselor for JEE/NEET questions."""
    svc = _require_admissions()
    message = (data.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    try:
        from core.dependencies import get_llm_service, is_llm_available
        llm = get_llm_service() if is_llm_available() else None
        return svc["answer_admission_query"](message, data.get("profile", {}), llm=llm)
    except Exception as e:
        logger.error("Admission counselor error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})
