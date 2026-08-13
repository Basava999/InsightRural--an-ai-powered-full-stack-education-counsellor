# ==============================================================================
# InsightRural — KEA Simulation Router
# ==============================================================================
# Endpoints: /v2/simulate, /v2/ml-info
# Migrated from app.py Flask endpoints (lines 1044-1121)
# ==============================================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from core.logging import get_logger
from core.exceptions import ServiceUnavailableError

logger = get_logger("api.simulation")
router = APIRouter()


class SimulationRequest(BaseModel):
    """KEA seat allotment simulation request."""
    kcet_rank: int = Field(..., gt=0, description="KCET CET rank")
    category: str = Field(default="GM")
    gender: str = Field(default="Male")
    branch_preference: List[str] = Field(default=["CSE", "ISE", "ECE"])
    district_preference: Optional[List[str]] = None
    college_preference: Optional[List[str]] = None
    rural_quota: bool = False
    kannada_medium: bool = False
    snq: bool = False
    special_reservation: Optional[str] = None
    hk_371j: bool = Field(default=False, alias="371j_status")
    minority_status: bool = False
    annual_income: int = 0
    hostel_required: bool = False
    budget: Optional[int] = 0
    top_n: int = Field(default=15, le=50)

    class Config:
        populate_by_name = True


@router.post("/v2/simulate")
async def kea_simulate(data: SimulationRequest):
    """
    Full KEA seat allotment simulation.
    Uses ML models + rule-based engine to predict colleges.
    Returns SAFE / MODERATE / AMBITIOUS with confidence scores.
    """
    try:
        from kea_allotment_engine import get_kea_engine
    except ImportError:
        raise ServiceUnavailableError("KEA Allotment Engine")

    try:
        engine = get_kea_engine()
        result = engine.simulate(
            rank=data.kcet_rank,
            category=data.category,
            gender=data.gender,
            branch_preference=data.branch_preference,
            district_preference=data.district_preference,
            college_preference=data.college_preference,
            rural_quota=data.rural_quota,
            kannada_medium=data.kannada_medium,
            snq=data.snq,
            special_reservation=data.special_reservation,
            hk_371j=data.hk_371j,
            minority_status=data.minority_status,
            annual_income=data.annual_income,
            hostel_required=data.hostel_required,
            budget=data.budget or 0,
            top_n=data.top_n,
        )
        return result
    except Exception as e:
        logger.error("KEA simulation error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/v2/ml-info")
async def ml_info():
    """Get information about the trained ML models."""
    try:
        from kea_allotment_engine import get_kea_engine
        engine = get_kea_engine()
        return {
            "ml_model": engine.ml_engine.best_model_name or "Rule-based",
            "is_trained": engine.ml_engine.is_trained,
            "model_comparison": engine.ml_engine.metrics,
            "total_colleges": len(engine.colleges),
            "feature_names": engine.ml_engine.feature_names,
        }
    except ImportError:
        raise ServiceUnavailableError("KEA Engine")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
