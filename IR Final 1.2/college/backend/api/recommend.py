# ==============================================================================
# InsightRural — Recommend API Router
# ==============================================================================

import logging
from fastapi import APIRouter, HTTPException

from models.schemas import PredictRequest, RecommendationResponse

logger = logging.getLogger("RecommendAPI")
router = APIRouter()


@router.post("/recommend/colleges", response_model=RecommendationResponse)
async def recommend_colleges(request: PredictRequest):
    """
    Full college recommendation with all metadata.
    Alias for /predict/kcet with richer response.
    """
    from main import get_recommendation_service

    try:
        service = get_recommendation_service()
        profile = request.to_student_profile()
        return service.recommend(profile, top_n=request.top_n)
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/strategy")
async def recommend_strategy(request: PredictRequest):
    """
    Get counselling strategy — recommended option entry sequence.
    Returns Dream → Realistic → Safe ordering for KEA choice filling.
    """
    from main import get_recommendation_service

    try:
        service = get_recommendation_service()
        profile = request.to_student_profile()
        result = service.recommend(profile, top_n=15)

        return {
            "success": True,
            "strategy": result.counselling_guidance,
            "option_entry_sequence": result.option_entry_sequence,
            "confidence": result.confidence,
            "total_options": result.total_eligible,
        }
    except Exception as e:
        logger.error(f"Strategy error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/preference-list")
async def generate_preference_list(request: PredictRequest):
    """
    Generate a KEA option entry preference list.
    Returns ordered list ready for direct submission.
    """
    from main import get_recommendation_service

    try:
        service = get_recommendation_service()
        profile = request.to_student_profile()
        result = service.recommend(profile, top_n=20)

        return {
            "success": True,
            "preference_list": result.option_entry_sequence,
            "total": len(result.option_entry_sequence),
            "student": {
                "rank": profile.rank,
                "category": profile.category,
                "branches": profile.preferred_branches,
            },
        }
    except Exception as e:
        logger.error(f"Preference list error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
