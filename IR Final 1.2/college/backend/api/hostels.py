# ==============================================================================
# InsightRural — Hostels Router
# ==============================================================================
# Endpoints: /hostels, /hostels/apply, /v2/hostel
# Migrated from app.py Flask endpoints (lines 1842-1970, 951-977)
# ==============================================================================

import json
import os
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from core.logging import get_logger
from core.config import settings

logger = get_logger("api.hostels")
router = APIRouter()

DATA_DIR = str(settings.DATA_DIR)


@router.get("/hostels")
async def get_hostels(
    location: str = "",
    type: str = "",
    gender: str = "",
    category: str = "",
):
    """Get all hostels with optional filters."""
    try:
        data_file = os.path.join(DATA_DIR, "hostels.json")
        with open(data_file, "r", encoding="utf-8") as f:
            all_hostels = json.load(f)

        filtered = all_hostels
        loc = location.strip().lower()
        hostel_type = type.strip().lower()
        gen = gender.strip().lower()
        cat = category.strip().lower()

        if loc:
            filtered = [h for h in filtered if h.get("location", "").lower() == loc]
        if hostel_type:
            filtered = [h for h in filtered if hostel_type in h.get("type", "").lower()]
        if gen:
            if gen == "boys":
                filtered = [h for h in filtered if h.get("facilities", {}).get("boys_hostel", False)]
            elif gen == "girls":
                filtered = [h for h in filtered if h.get("facilities", {}).get("girls_hostel", False)]
        if cat:
            filtered = [h for h in filtered if cat.upper() in str(h.get("category", []))]

        return {"total": len(filtered), "hostels": filtered}

    except Exception as e:
        logger.error("Error in get_hostels: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"error": str(e), "total": 0, "hostels": []}
        )


@router.post("/hostels/apply")
async def hostel_apply(data: Dict[str, Any]):
    """Generate AI hostel application letter."""
    try:
        from core.dependencies import get_llm_service, is_llm_available
        if not is_llm_available():
            raise HTTPException(status_code=503, detail="AI modules not available")

        student_data = data.get("student_data", {})
        hostel_name = data.get("hostel_name", "Government Hostel")
        reason = data.get("reason", "")

        llm = get_llm_service()
        prompt = f"""
        You are a professional educational counselor helping a student write a hostel admission application.

        Student Profile:
        - Name: {student_data.get('name', 'Student')}
        - Category: {student_data.get('category', 'Not specified')}
        - KCET Rank: {student_data.get('kcet_rank', 'Not specified')}
        - Family Income: {student_data.get('income', 'Not specified')}
        - Location: {student_data.get('location', 'Karnataka')}
        - College: {student_data.get('college', 'Not specified')}

        Hostel: {hostel_name}
        Personal Reason: {reason}

        Task:
        Write a formal, compelling hostel admission application letter addressed to the Hostel Warden / Department Head.

        Guidelines:
        - Tone: Formal, humble, and sincere.
        - Structure: Subject line, salutation, introduction, need for hostel, family background, academic commitment, conclusion.
        - Length: Around 200-250 words.
        - NO placeholders like [Name]. Use the provided name or "I".
        - Include the student's category and financial situation if relevant.
        - Mention the specific hostel name.
        """

        response = llm.generate(prompt)
        return {"application": response}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Hostel application error: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/v2/hostel")
async def get_hostel_v2(data: Dict[str, Any]):
    """Get hostel information from verified JSON database."""
    try:
        from json_data_service import get_json_data_service
    except ImportError:
        return JSONResponse(
            status_code=500, content={"error": "JSON Data Service not available"}
        )

    try:
        svc = get_json_data_service()
        info = svc.get_hostel_info(
            college_name=data.get("college"),
            location=data.get("location"),
            category=data.get("category"),
        )
        if not info:
            return {
                "message": "Verified hostel information is not currently available for this query.",
                "hostels": [],
            }
        return {"info": info, "source": "Structured JSON Database"}
    except Exception as e:
        logger.error("Error in get_hostel_v2: %s", e, exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
