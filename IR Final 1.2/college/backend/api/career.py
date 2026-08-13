# ==============================================================================
# InsightRural — Career Simulator Router
# ==============================================================================
# Endpoints: /simulate-career
# Migrated from app.py Flask endpoints (lines 1417-1558)
# ==============================================================================

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from core.logging import get_logger
from core.dependencies import is_llm_available

logger = get_logger("api.career")
router = APIRouter()


def _career_simulation_fallback(rank, category, branch, interests):
    """Deterministic career simulation when LLM is unavailable."""
    roadmap = {}
    try:
        from admissions_service import generate_career_roadmap
        roadmap = generate_career_roadmap({"branch": branch, "interests": interests})
    except Exception:
        pass

    branch_label = str(branch or "CSE").upper()
    interest_label = str(interests or "technology").title()

    return {
        "paths": [
            {
                "name": "Placement Track",
                "description": f"Build strong fundamentals in {branch_label}, complete internships, and target campus placements.",
                "color": "#2563eb",
                "probability": 72,
                "milestones": [
                    {"year": 2026, "title": "Admission", "desc": f"Join {branch_label} and finish bridge courses", "salary": None, "icon": "1"},
                    {"year": 2027, "title": "Skill Build", "desc": "Projects, coding/core labs, communication practice", "salary": None, "icon": "2"},
                    {"year": 2028, "title": "Internship", "desc": "Summer internship or hospital/industry exposure", "salary": "Rs. 15K-35K/month", "icon": "3"},
                    {"year": 2029, "title": "Campus Placement", "desc": "Target product/service/core companies", "salary": roadmap.get("expected_salary", "6-12 LPA"), "icon": "4"},
                    {"year": 2030, "title": "Growth", "desc": "Specialize and move to higher-impact roles", "salary": "12-24 LPA", "icon": "5"},
                ],
            },
            {
                "name": "Higher Studies Track",
                "description": "Prepare for GATE/GRE/NEET PG/CAT depending on your course and build a research profile.",
                "color": "#059669",
                "probability": 58,
                "milestones": [
                    {"year": 2026, "title": "Foundation", "desc": "Maintain CGPA and identify target exams", "salary": None, "icon": "1"},
                    {"year": 2027, "title": "Research Start", "desc": "Mini-projects, papers, open-source or clinical audits", "salary": None, "icon": "2"},
                    {"year": 2028, "title": "Exam Prep", "desc": "Structured test preparation and mentorship", "salary": None, "icon": "3"},
                    {"year": 2029, "title": "Admission", "desc": "M.Tech/MS/MD/MBA pathway", "salary": None, "icon": "4"},
                    {"year": 2030, "title": "Specialist Role", "desc": "Research, specialist, or leadership track", "salary": "10-22 LPA", "icon": "5"},
                ],
            },
            {
                "name": "Startup Track",
                "description": f"Use your {interest_label} interest to solve a student, rural, health, or industry problem.",
                "color": "#f97316",
                "probability": 36,
                "milestones": [
                    {"year": 2026, "title": "Problem Discovery", "desc": "Talk to users and validate one real pain point", "salary": None, "icon": "1"},
                    {"year": 2027, "title": "Prototype", "desc": "Build MVP with a small student team", "salary": None, "icon": "2"},
                    {"year": 2028, "title": "Pilot", "desc": "Run pilots through campus/incubation cells", "salary": None, "icon": "3"},
                    {"year": 2029, "title": "Funding/Revenue", "desc": "Apply for grants or earn first revenue", "salary": "Variable", "icon": "4"},
                    {"year": 2030, "title": "Scale", "desc": "Convert project into company or strong portfolio", "salary": "Variable", "icon": "5"},
                ],
            },
        ],
        "future_artifact": {
            "type": "news_headline",
            "date": "2030",
            "source": "InsightRural FutureVision",
            "content": f"Student with rank {rank} turns {branch_label} roadmap into a high-impact {interest_label} career.",
        },
        "roadmap": roadmap,
    }


@router.post("/simulate-career")
async def simulate_career(data: Dict[str, Any]):
    """
    Generative AI Career Simulator.
    Returns 3 career paths + Future Artifact.
    Falls back to deterministic simulation if LLM unavailable.
    """
    rank = data.get("rank")
    category = data.get("category")
    branch = data.get("branch")
    interests = data.get("interests", "Technology, Engineering")

    if not all([rank, category, branch]):
        raise HTTPException(status_code=400, detail="Missing required fields: rank, category, branch")

    if not is_llm_available():
        return {
            "success": True,
            "data": _career_simulation_fallback(rank, category, branch, interests),
            "mode": "deterministic-fallback",
        }

    try:
        from prompt_templates import CAREER_SIMULATION_SYSTEM_PROMPT, CAREER_SIMULATION_USER_PROMPT
        from core.dependencies import get_llm_service

        user_prompt = CAREER_SIMULATION_USER_PROMPT.format(
            rank=rank, category=category, branch=branch, interests=interests
        )

        logger.info("Generating career paths for Rank %s, %s", rank, branch)

        llm_service = get_llm_service()
        response_text = llm_service.generate(
            prompt=user_prompt,
            system_prompt=CAREER_SIMULATION_SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=2000,
        )

        # Clean response for valid JSON
        response_text = response_text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            result = json.loads(response_text)
            return {"success": True, "data": result}
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from LLM, using deterministic fallback")
            return {
                "success": True,
                "data": _career_simulation_fallback(rank, category, branch, interests),
                "mode": "deterministic-fallback",
                "warning": "LLM returned invalid JSON, so a fallback simulation was used.",
            }

    except Exception as e:
        logger.error("Career simulation error: %s", e, exc_info=True)
        return {
            "success": True,
            "data": _career_simulation_fallback(rank, category, branch, interests),
            "mode": "deterministic-fallback",
            "warning": str(e),
        }
