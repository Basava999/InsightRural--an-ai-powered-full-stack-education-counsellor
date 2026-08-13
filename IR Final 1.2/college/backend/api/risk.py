# ==============================================================================
# InsightRural — Risk Analyzer Router
# ==============================================================================
# Endpoints: /analyze/risk
# Migrated from app.py Flask endpoints (lines 2295-2372)
# ==============================================================================

from typing import Dict, Any
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core.logging import get_logger
from core.exceptions import ServiceUnavailableError

logger = get_logger("api.risk")
router = APIRouter()


@router.post("/analyze/risk")
async def analyze_risk_endpoint(data: Dict[str, Any]):
    """
    AI Student Success & Counseling Risk Analyzer.
    Returns 11-dimensional risk analysis with AI explanation.
    """
    try:
        from risk_analyzer import analyze_risk, generate_ai_explanation
    except ImportError:
        raise ServiceUnavailableError("Risk Analyzer")

    try:
        risk_analysis = analyze_risk(data)
        ai_explanation = generate_ai_explanation(data, risk_analysis)

        # Save to database (non-blocking, errors are logged but not raised)
        _save_risk_profile(data, risk_analysis, ai_explanation)

        return {
            "success": True,
            "risk_analysis": risk_analysis,
            "ai_explanation": ai_explanation,
        }
    except Exception as e:
        logger.error("Risk analysis error: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Risk analysis encountered an issue. Please try again.",
            },
        )


def _save_risk_profile(data: Dict, risk_analysis: Dict, ai_explanation: str):
    """Persist risk profile to database. Non-critical — errors are logged only."""
    db_session = None
    try:
        from db import SessionLocal
        from db_models import StudentRiskProfile

        db_session = SessionLocal()

        interests = data.get("interests", "")
        if isinstance(interests, list):
            interests = ", ".join(interests)
        skills = data.get("skills", "")
        if isinstance(skills, list):
            skills = ", ".join(skills)

        income_raw = float(data.get("income", 0))
        income_lakhs = income_raw / 100000 if income_raw > 100 else income_raw

        preferred_colleges = data.get("preferred_colleges", "")
        if isinstance(preferred_colleges, list):
            preferred_colleges = ", ".join(preferred_colleges)

        risk_profile = StudentRiskProfile(
            exam=data.get("exam", "KCET"),
            rank=int(data.get("rank", 0)) if data.get("rank") else None,
            category=data.get("category", "GM"),
            income_lakhs=income_lakhs,
            interests=interests,
            career_goals=data.get("career_goals", ""),
            preferred_branches=data.get("branch", ""),
            preferred_colleges=preferred_colleges,
            success_score=risk_analysis["success_score"],
            academic_risk=risk_analysis["academic_risk"],
            financial_risk=risk_analysis["financial_risk"],
            placement_risk=risk_analysis["placement_risk"],
            regret_probability=risk_analysis["regret_probability"],
            branch_compatibility_score=risk_analysis["branch_compatibility_score"],
            roi_score=risk_analysis["roi_label"],
            ai_explanation=ai_explanation,
        )
        db_session.add(risk_profile)
        db_session.commit()
    except Exception as db_err:
        logger.warning("Could not save risk profile: %s", db_err)
        if db_session:
            db_session.rollback()
    finally:
        if db_session:
            db_session.close()
