# ==============================================================================
# InsightRural — Colleges Router
# ==============================================================================
# Endpoints: /colleges, /colleges/<cid>, /fees/<category>
# Migrated from app.py Flask endpoints (lines 337-464)
# ==============================================================================

import json
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func

from core.logging import get_logger

logger = get_logger("api.colleges")
router = APIRouter()


def _college_to_dict(col):
    """Convert SQLAlchemy College model to dict."""
    return {
        "college_id": col.id,
        "name": col.name,
        "type": col.type,
        "location": col.location,
        "affiliation": col.affiliation,
        "hostel_available": bool(col.hostel_available),
        "branches": col.branches or [],
        "fee_category": col.fee_category,
        "cutoff_data": col.cutoff_data or {},
    }


def _fee_to_dict(fee):
    """Convert SQLAlchemy FeeStructure model to dict."""
    if not fee:
        return None
    return {
        "category": fee.category,
        "gm_and_others_above_income_limit": fee.gm_and_others_above_income_limit,
        "snq_quota": fee.snq_quota,
        "sc_st_concession": fee.sc_st_concession,
        "cat1_upto_2_5_lakhs": fee.cat1_upto_2_5_lakhs,
        "others_upto_10_lakhs": fee.others_upto_10_lakhs,
        "cat1_above_2_5_lakhs": fee.cat1_above_2_5_lakhs,
    }


@router.get("/colleges")
async def get_colleges(
    q: str = "",
    branch: str = "",
    location: str = "",
    type: str = "",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=100),
):
    """Get colleges with search, branch, location, and type filters."""
    from db import SessionLocal
    from db_models import College

    session = SessionLocal()
    try:
        q = q.strip().lower()
        branch = branch.strip()
        location_filter = location.strip()
        type_filter = type.strip()

        all_colleges = session.query(College).all()
        filtered = []

        for col in all_colleges:
            # Search query
            if q:
                def normalize(text):
                    return "".join(e for e in str(text).lower() if e.isalnum())

                norm_q = normalize(q)
                norm_name = normalize(col.name)

                if not (
                    (q in col.name.lower())
                    or (norm_q in norm_name)
                    or (col.location and q in col.location.lower())
                    or (col.affiliation and q in col.affiliation.lower())
                ):
                    continue

            if branch and (not col.branches or branch not in col.branches):
                continue
            if location_filter and (
                not col.location or location_filter.lower() not in col.location.lower()
            ):
                continue
            if type_filter and (
                not col.type or type_filter.lower() != col.type.lower()
            ):
                continue

            filtered.append(col)

        total = len(filtered)
        start = (page - 1) * limit
        paginated = filtered[start : start + limit]
        results = [_college_to_dict(c) for c in paginated]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "items": results,
        }

    except Exception as e:
        logger.error("Error in get_colleges: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "total": 0, "page": 1, "limit": 12, "pages": 0, "items": []},
        )
    finally:
        session.close()


@router.get("/colleges/{cid}")
async def get_college(cid: str):
    """Get single college details with fee info."""
    from db import SessionLocal
    from db_models import College, FeeStructure

    session = SessionLocal()
    try:
        col = session.query(College).filter(College.id == cid).first()
        if not col:
            raise HTTPException(status_code=404, detail="College not found")

        result = _college_to_dict(col)
        if col.fee_category:
            fee = session.query(FeeStructure).filter(
                FeeStructure.category == col.fee_category
            ).first()
            if fee:
                result["fee_details"] = _fee_to_dict(fee)

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_college: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        session.close()


@router.get("/fees/{category:path}")
async def get_fee(category: str):
    """Get fee structure by category."""
    from db import SessionLocal
    from db_models import FeeStructure

    session = SessionLocal()
    try:
        fee = session.query(FeeStructure).filter(
            FeeStructure.category == category
        ).first()
        if not fee:
            raise HTTPException(status_code=404, detail="Fee category not found")
        return _fee_to_dict(fee)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_fee: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        session.close()


@router.post("/v2/cutoff-trends")
async def get_cutoff_trends_post(data: dict):
    """Get multi-year cutoff trends for a specific college (POST)."""
    try:
        from json_data_service import get_json_data_service
    except ImportError:
        return JSONResponse(
            status_code=500, content={"error": "JSON Data Service not available"}
        )

    college = data.get("college", "")
    branch = data.get("branch", "CSE")
    category = data.get("category", "GM")

    if not college:
        raise HTTPException(status_code=400, detail="College name is required")

    try:
        svc = get_json_data_service()
        info = svc.get_cutoff_trends(college, branch, category)
        if not info:
            return {"message": "Cutoff trend data not available for this college."}
        return {"info": info, "source": "Structured JSON Database"}
    except Exception as e:
        logger.error("Error in get_cutoff_trends: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
