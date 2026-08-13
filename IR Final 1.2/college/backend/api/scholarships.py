# ==============================================================================
# InsightRural — Scholarships Router
# ==============================================================================
# Endpoints: /scholarships/list, /scholarships/generate-essay,
#            /scholarships/download-pdf, /v2/scholarships,
#            /recommend/scholarships, /smart-match
# Migrated from app.py Flask endpoints (lines 838-878, 980-1006, 1781-1826,
#   1887-1918, 1973-2075)
# ==============================================================================

import json
import os
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from core.logging import get_logger
from core.config import settings

logger = get_logger("api.scholarships")
router = APIRouter()

DATA_DIR = str(settings.DATA_DIR)


@router.get("/scholarships/list")
async def get_scholarships_list(category: str = ""):
    """Get all scholarships from JSON data with optional category filter."""
    try:
        data_file = os.path.join(DATA_DIR, "scholarships.json")
        with open(data_file, "r", encoding="utf-8") as f:
            all_scholarships = json.load(f)

        if category.strip():
            filtered = []
            for sch in all_scholarships:
                sch_cats = sch.get("eligibility", {}).get("category", [])
                cat_str = str(sch_cats).lower()
                if (
                    category.lower() in cat_str
                    or category.lower() in sch.get("category", "").lower()
                ):
                    filtered.append(sch)
            all_scholarships = filtered

        return {"total": len(all_scholarships), "scholarships": all_scholarships}

    except Exception as e:
        logger.error("Error in get_scholarships_list: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "total": 0, "scholarships": []},
        )


@router.post("/recommend/scholarships")
async def recommend_scholarships(data: Dict[str, Any]):
    """Get scholarship recommendations based on student profile."""
    try:
        category = data.get("category", "General")
        income = int(data.get("income", 500000))

        data_file = os.path.join(DATA_DIR, "scholarships.json")
        with open(data_file, "r", encoding="utf-8") as f:
            all_scholarships = json.load(f)

        scholarships = []
        category_lower = category.lower()
        for sch in all_scholarships:
            eligibility = sch.get("eligibility", {})
            income_limit = eligibility.get("income_limit", float("inf"))
            sch_categories = [c.lower() for c in eligibility.get("category", [])]

            if income <= income_limit:
                if "all categories" in sch_categories or "all" in sch_categories:
                    scholarships.append(sch)
                elif category_lower in ["sc", "st"] and (
                    category_lower in sch_categories or "sc/st" in sch_categories
                ):
                    scholarships.append(sch)
                elif "obc" in category_lower and (
                    "obc" in sch_categories
                    or "2a" in sch_categories
                    or "3a" in sch_categories
                    or "3b" in sch_categories
                ):
                    scholarships.append(sch)
                elif category_lower in ["gm", "general", "ews"] and (
                    "general" in sch_categories
                    or "gm" in sch_categories
                    or "ews" in sch_categories
                    or "all categories" in sch_categories
                ):
                    scholarships.append(sch)

        return {
            "category": category,
            "income": income,
            "total_matches": len(scholarships),
            "scholarships": scholarships,
        }
    except Exception as e:
        logger.error("Error in recommend_scholarships: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/v2/scholarships")
async def get_scholarships_v2(data: Dict[str, Any]):
    """Get verified scholarships from JSON database."""
    try:
        from json_data_service import get_json_data_service
    except ImportError:
        return JSONResponse(
            status_code=500, content={"error": "JSON Data Service not available"}
        )

    try:
        svc = get_json_data_service()
        info = svc.get_scholarships(
            category=data.get("category"),
            income=int(data.get("income")) if data.get("income") else None,
            gender=data.get("gender"),
        )
        if not info:
            return {
                "message": "No matching scholarships found for this profile.",
                "scholarships": [],
            }
        return {"info": info, "source": "Structured JSON Database"}
    except Exception as e:
        logger.error("Error in get_scholarships_v2: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/scholarships/generate-essay")
async def generate_essay_endpoint(data: Dict[str, Any]):
    """Generate scholarship essay using LLM."""
    try:
        from scholarship_service import generate_scholarship_essay
    except ImportError:
        raise HTTPException(status_code=503, detail="Scholarship AI unavailable")

    try:
        essay = generate_scholarship_essay(
            data.get("student_data", {}),
            data.get("scholarship", "Scholarship"),
            data.get("reason", ""),
        )
        return {"essay": essay}
    except Exception as e:
        logger.error("Essay generation error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/scholarships/download-pdf")
async def download_scholarship_pdf(data: Dict[str, Any], request: Request):
    """Generate PDF for scholarship application."""
    try:
        from scholarship_service import create_application_pdf
    except ImportError:
        raise HTTPException(status_code=503, detail="Scholarship AI unavailable")

    try:
        filepath, url = create_application_pdf(
            data.get("student_data", {}), data.get("essay", "")
        )
        if not filepath:
            return JSONResponse(
                status_code=500, content={"error": "PDF generation failed"}
            )

        base_url = str(request.base_url).rstrip("/")
        full_url = f"{base_url}{url}"
        return {"url": full_url, "path": url}
    except Exception as e:
        logger.error("Scholarship PDF error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/smart-match")
async def smart_match(data: Dict[str, Any]):
    """
    Auto-match student profile to eligible scholarships and hostels.
    """
    try:
        category = data.get("category", "").upper()
        raw_income = data.get("income", 500000)
        income_map = {"low": 200000, "medium": 500000, "high": 1000000}
        if isinstance(raw_income, str) and raw_income.lower() in income_map:
            income = income_map[raw_income.lower()]
        else:
            try:
                income = int(raw_income)
            except (ValueError, TypeError):
                income = 500000
        gender = data.get("gender", "").lower()

        # Load data
        sch_file = os.path.join(DATA_DIR, "scholarships.json")
        host_file = os.path.join(DATA_DIR, "hostels.json")

        with open(sch_file, "r", encoding="utf-8") as f:
            all_scholarships = json.load(f)
        with open(host_file, "r", encoding="utf-8") as f:
            all_hostels = json.load(f)

        # Match scholarships
        eligible_scholarships = []
        for sch in all_scholarships:
            elig = sch.get("eligibility", {})
            income_limit = elig.get("income_limit", elig.get("income_max", float("inf")))
            sch_categories = str(elig.get("category", [])).lower()

            if income <= income_limit:
                cat_match = False
                if "all categories" in sch_categories:
                    cat_match = True
                elif category.lower() in sch_categories:
                    cat_match = True
                elif category in ["SC", "ST"] and ("sc" in sch_categories or "st" in sch_categories):
                    cat_match = True
                elif "obc" in category.lower() and ("category" in sch_categories or "obc" in sch_categories):
                    cat_match = True

                gender_req = elig.get("gender", "").lower()
                if gender_req and gender_req != gender:
                    cat_match = False

                if cat_match:
                    eligible_scholarships.append(sch)

        # Match hostels
        eligible_hostels = []
        for hostel in all_hostels:
            hostel_cats = str(hostel.get("category", [])).lower()

            if "bcm" in hostel.get("type", "").lower() or "sc/st" in hostel.get("type", "").lower() or "minority" in hostel.get("type", "").lower():
                cat_match = False
                if category in ["SC", "ST"] and ("sc" in hostel_cats or "st" in hostel_cats):
                    cat_match = True
                elif "obc" in category.lower() and "obc" in hostel_cats:
                    cat_match = True
                elif "category" in hostel_cats:
                    cat_match = True

                if cat_match:
                    fac = hostel.get("facilities", {})
                    if gender == "male" and fac.get("boys_hostel", False):
                        eligible_hostels.append(hostel)
                    elif gender == "female" and fac.get("girls_hostel", False):
                        eligible_hostels.append(hostel)
                    elif not gender:
                        eligible_hostels.append(hostel)
            else:
                eligible_hostels.append(hostel)

        return {
            "scholarships": {"total": len(eligible_scholarships), "items": eligible_scholarships},
            "hostels": {"total": len(eligible_hostels), "items": eligible_hostels},
        }

    except Exception as e:
        logger.error("Smart match error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
