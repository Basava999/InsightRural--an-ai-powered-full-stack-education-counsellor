# ==============================================================================
# InsightRural — Predict API Router
# ==============================================================================
# The core prediction endpoint. Replaces the old Flask /predict/kcet route
# with the new deterministic pipeline.
# ==============================================================================

import logging
from fastapi import APIRouter, HTTPException

from models.schemas import PredictRequest, RecommendationResponse

logger = logging.getLogger("PredictAPI")
router = APIRouter()


@router.post("/predict/kcet", response_model=RecommendationResponse)
async def predict_kcet(request: PredictRequest):
    """
    KCET College Prediction.

    Takes student profile and returns deterministic recommendations
    classified as Safe/Moderate/Ambitious.

    This is the main prediction endpoint that replaces the old Flask route.
    The pipeline is:
        StudentProfile → Cutoff Match → Reservation → Constraint Filter → Rank → Classify
    """
    from main import get_recommendation_service

    try:
        service = get_recommendation_service()
        profile = request.to_student_profile()
        result = service.recommend(profile, top_n=request.top_n)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/quick")
async def predict_quick(
    rank: int,
    branch: str = "CSE",
    category: str = "GM",
    location: str = None,
    budget: int = None,
    hostel: bool = False,
):
    """
    Quick prediction with URL parameters. Convenience endpoint
    for simple queries without full JSON body.
    """
    from main import get_recommendation_service
    from models.schemas import StudentProfile

    try:
        profile = StudentProfile(
            rank=rank,
            category=category,
            preferred_branches=[branch],
            preferred_locations=[location] if location else None,
            budget=budget,
            hostel_required=hostel,
        )
        service = get_recommendation_service()
        result = service.recommend(profile, top_n=10)

        # Return simplified response
        return {
            "success": True,
            "rank": rank,
            "branch": branch,
            "category": category,
            "safe_count": len(result.safe),
            "moderate_count": len(result.moderate),
            "ambitious_count": len(result.ambitious),
            "safe": [
                {
                    "name": c.college_name,
                    "location": c.location,
                    "type": c.college_type,
                    "cutoff": c.cutoff_rank,
                    "fee": c.annual_fee,
                    "score": c.recommendation_score,
                }
                for c in result.safe[:5]
            ],
            "moderate": [
                {
                    "name": c.college_name,
                    "location": c.location,
                    "cutoff": c.cutoff_rank,
                    "score": c.recommendation_score,
                }
                for c in result.moderate[:5]
            ],
            "ambitious": [
                {
                    "name": c.college_name,
                    "location": c.location,
                    "cutoff": c.cutoff_rank,
                    "score": c.recommendation_score,
                }
                for c in result.ambitious[:3]
            ],
        }
    except Exception as e:
        logger.error(f"Quick prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
