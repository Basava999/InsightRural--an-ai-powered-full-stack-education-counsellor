"""College prediction endpoints — deterministic engine only."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request

from app.core.audit import log_request
from app.schemas.student import RecommendationResponse, StudentProfile
from app.engines.recommendation_orchestrator import RecommendationOrchestrator

router = APIRouter()
_orchestrator = RecommendationOrchestrator()


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_colleges(profile: StudentProfile, request: Request):
    """Generate SAFE/MODERATE/AMBITIOUS recommendations using deterministic pipeline."""
    log_request("recommend", "/predict/recommend", ip=request.client.host if request.client else None)
    return _orchestrator.recommend(profile)


@router.post("/preference-order")
async def generate_preference_order(profile: StudentProfile, max_options: int = 50):
    """Generate KEA option-entry preference order list."""
    return {"preferences": _orchestrator.generate_preference_order(profile, max_options)}


class CompareRequest(StudentProfile):
    college_ids: List[str]


@router.post("/compare")
async def compare_colleges(body: CompareRequest):
    """Compare multiple colleges for the same student profile."""
    if len(body.college_ids) < 2:
        raise HTTPException(400, "Provide at least 2 college IDs to compare")
    profile = StudentProfile(**body.model_dump(exclude={"college_ids"}))
    return {"comparisons": _orchestrator.compare_colleges(body.college_ids, profile)}


@router.post("/strategy")
async def counselling_strategy(profile: StudentProfile):
    """Generate counselling strategy with tier distribution."""
    result = _orchestrator.recommend(profile)
    return {
        "strategy": {
            "safe_count": len(result.safe),
            "moderate_count": len(result.moderate),
            "ambitious_count": len(result.ambitious),
            "confidence": result.confidence,
            "advice": [
                "Fill SAFE options in top 10 preference slots for guaranteed backup.",
                "Place MODERATE options in slots 11-30 for realistic targets.",
                "Add 5-10 AMBITIOUS options at lower priority for stretch goals.",
            ],
        },
        "top_safe": result.safe[:3],
        "top_moderate": result.moderate[:3],
    }
