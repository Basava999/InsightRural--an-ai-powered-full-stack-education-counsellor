"""Scholarship eligibility checker."""

from typing import Optional

from fastapi import APIRouter, Query

from app.services.data_service import get_data_service

router = APIRouter()


@router.get("/eligible")
async def eligible_scholarships(
    category: Optional[str] = Query(None),
    income: Optional[int] = Query(None),
    gender: Optional[str] = Query(None),
):
    svc = get_data_service()
    results = svc.get_eligible_scholarships(category=category, income=income, gender=gender)
    return {"scholarships": results, "count": len(results), "source": "verified_database"}
