"""College explorer endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.data_service import get_data_service

router = APIRouter()


@router.get("/search")
async def search_colleges(
    q: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    college_type: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
):
    svc = get_data_service()
    return svc.search_colleges(query=q, city=city, college_type=college_type, limit=limit, offset=offset)


@router.get("/{college_id}")
async def get_college(college_id: str):
    svc = get_data_service()
    college = svc.get_college_by_id(college_id)
    if not college:
        raise HTTPException(404, f"College {college_id} not found")
    return college


@router.get("/{college_id}/cutoff-trends")
async def get_cutoff_trends(
    college_id: str,
    branch: str = Query("CSE"),
    category: str = Query("GM"),
):
    svc = get_data_service()
    trends = svc.get_cutoff_trends(college_id, branch.upper(), category.upper())
    if not trends:
        raise HTTPException(404, "Cutoff trend data not available")
    return {"college_id": college_id, "branch": branch, "category": category, "trends": trends}
