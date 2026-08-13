"""Hostel endpoints — only verified database records."""

from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.student import StudentProfile
from app.services.data_service import get_data_service
from app.engines.recommendation_orchestrator import RecommendationOrchestrator

router = APIRouter()
_orchestrator = RecommendationOrchestrator()


@router.post("/for-recommendations")
async def hostels_for_recommendations(profile: StudentProfile):
    """Return hostel info ONLY for recommended colleges."""
    result = _orchestrator.recommend(profile, include_scholarships=False)
    return {
        "hostels": result.hostels,
        "count": len(result.hostels),
        "source": "verified_database",
        "note": "Hostel details are never invented — only from official database records.",
    }


@router.get("/college/{college_id}")
async def hostel_by_college(college_id: str):
    svc = get_data_service()
    hostels = svc.get_hostels_for_colleges([college_id])
    if not hostels:
        college = svc.get_college_by_id(college_id)
        if college and college.get("hostel_available"):
            return {
                "hostels": [{"college_id": college_id, "hostel_available": True, "details": "Limited data available"}],
                "verified": True,
            }
        raise HTTPException(404, "No verified hostel data for this college")
    return {"hostels": hostels, "verified": True}
