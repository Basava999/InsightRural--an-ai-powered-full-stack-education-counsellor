"""
Production FastAPI Backend — Karnataka AI Counselling Platform
All counselling decisions are deterministic. LLM only explains.
"""

import json
import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# ── Path setup ─────────────────────────────────────────────────────────────────
PLATFORM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY_DIR   = os.path.join(os.path.dirname(PLATFORM_DIR), "backend")
sys.path.insert(0, PLATFORM_DIR)
sys.path.insert(0, os.path.join(PLATFORM_DIR, "backend"))
sys.path.insert(0, LEGACY_DIR)

# ── Env ────────────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("APIv2")

# ── Core Imports ───────────────────────────────────────────────────────────────
from core.student_profile import get_profile_extractor, StudentProfile
from core.scholarship_engine import get_scholarship_engine
from core.pipeline import get_pipeline

# ── Legacy ML Engine ───────────────────────────────────────────────────────────
try:
    from ml_predictor import get_predictor as get_kcea_predictor, CollegePredictor
    ML_PREDICTOR_AVAILABLE = True
except ImportError:
    ML_PREDICTOR_AVAILABLE = False

# ── LLM Service (explanation only) ────────────────────────────────────────────
try:
    from llm_service import get_llm_service
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Karnataka AI Counselling Platform",
    description="Production-grade deterministic counselling engine",
    version="2.0.0",
    docs_url="/api/v2/docs",
    redoc_url="/api/v2/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store (replace with Redis in production) ─────────────────
SESSION_PROFILES: Dict[str, Dict] = {}


# ══════════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ══════════════════════════════════════════════════════════════════════════════

class RecommendRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    session_id: str = Field(default="default")
    top_n: int = Field(default=15, le=30)

class ProfileRequest(BaseModel):
    rank: Optional[int] = None
    category: str = "GM"
    gender: str = "male"
    preferred_branches: List[str] = []
    preferred_locations: List[str] = []
    budget: Optional[int] = None
    hostel_required: bool = False
    college_type: Optional[str] = None
    rural_quota: bool = False
    kannada_medium: bool = False
    hk_371j: bool = False
    snq: bool = False
    annual_income: Optional[int] = None
    session_id: str = "default"

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    history: List[Dict] = []

class CompareRequest(BaseModel):
    college_ids: List[str]
    session_id: Optional[str] = None

class PredictRequest(BaseModel):
    kcet_rank: int
    category: str = "GM"
    preferred_branches: List[str] = ["CSE"]
    preferred_locations: List[str] = []
    budget: Optional[int] = None
    hostel_required: bool = False
    college_type: Optional[str] = None
    rural_quota: bool = False
    kannada_medium: bool = False
    hk_371j: bool = False
    snq: bool = False
    top_n: int = 15


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _profile_from_session(session_id: str) -> Optional[StudentProfile]:
    """Load profile from session store."""
    data = SESSION_PROFILES.get(session_id)
    if not data:
        return None
    from core.student_profile import StudentProfile
    p = StudentProfile()
    for k, v in data.items():
        if hasattr(p, k):
            setattr(p, k, v)
    return p


def _save_profile(session_id: str, profile: StudentProfile):
    """Persist profile to session."""
    SESSION_PROFILES[session_id] = profile.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH & METADATA
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/health")
def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "pipeline": "deterministic",
        "llm_available": LLM_AVAILABLE,
        "ml_predictor": ML_PREDICTOR_AVAILABLE,
    }

@app.get("/api/v2/stats")
def get_stats():
    pipeline = get_pipeline()
    colleges = pipeline._get_all_colleges()
    locations = list({c.get("location") for c in colleges if c.get("location")})
    branches = list({b for c in colleges for b in c.get("branches", [])})
    return {
        "total_colleges": len(colleges),
        "total_locations": len(locations),
        "total_branches": len(branches),
        "data_source": "Production_Ready_Colleges.json",
    }


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/profile/save")
def save_profile(req: ProfileRequest):
    """Save/update student profile for a session."""
    from core.student_profile import StudentProfile
    profile = StudentProfile(
        rank=req.rank,
        category=req.category.upper(),
        gender=req.gender,
        preferred_branches=req.preferred_branches,
        preferred_locations=req.preferred_locations,
        budget=req.budget,
        hostel_required=req.hostel_required,
        college_type=req.college_type,
        rural_quota=req.rural_quota,
        kannada_medium=req.kannada_medium,
        hk_371j=req.hk_371j,
        snq=req.snq,
        annual_income=req.annual_income,
    )
    extractor = get_profile_extractor()
    profile.extraction_confidence = extractor._confidence(profile)
    profile.missing_fields = extractor._missing(profile)
    _save_profile(req.session_id, profile)
    return {"success": True, "profile": profile.to_dict()}


@app.get("/api/v2/profile/{session_id}")
def get_profile(session_id: str):
    """Retrieve saved profile for session."""
    profile = _profile_from_session(session_id)
    if not profile:
        return {"success": False, "error": "No profile found for this session"}
    return {"success": True, "profile": profile.to_dict()}


# ══════════════════════════════════════════════════════════════════════════════
# COLLEGE RECOMMENDATION (Main Engine)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/recommend")
def recommend_colleges(req: RecommendRequest):
    """
    Full college recommendation pipeline.
    
    Flow: Profile Extraction → Constraint Filter → KEA Engine
    → Ranking → Classification (Safe/Moderate/Ambitious)
    
    LLM is NOT used here. All results are deterministic.
    """
    pipeline = get_pipeline()
    existing = _profile_from_session(req.session_id)

    result = pipeline.run_full_recommendation(
        query=req.query,
        existing_profile=existing,
        top_n=req.top_n,
    )

    # Save updated profile
    if result.get("profile_ready") or result.get("student_profile"):
        extractor = get_profile_extractor()
        profile = extractor.extract(req.query)
        if existing:
            profile = extractor.update(existing, req.query)
        _save_profile(req.session_id, profile)

    return result


@app.post("/api/v2/predict")
def predict_colleges(req: PredictRequest):
    """
    Direct prediction with structured input (no natural language parsing).
    Uses ML predictor for cutoff prediction + KEA rules for probability.
    """
    if ML_PREDICTOR_AVAILABLE:
        predictor: CollegePredictor = get_kcea_predictor()
        result = predictor.predict(
            kcet_rank=req.kcet_rank,
            category=req.category.upper(),
            preferred_branches=req.preferred_branches,
            preferred_locations=req.preferred_locations,
            budget=req.budget,
            college_type_pref=req.college_type,
            reservations={
                "rural": req.rural_quota,
                "kannada": req.kannada_medium,
                "hk_region": req.hk_371j,
                "pwd": req.snq,
            },
            top_n=req.top_n,
        )
        return result
    else:
        # Fallback to pipeline
        from core.student_profile import StudentProfile
        profile = StudentProfile(
            rank=req.kcet_rank,
            category=req.category.upper(),
            preferred_branches=req.preferred_branches,
            preferred_locations=req.preferred_locations,
            budget=req.budget,
            hostel_required=req.hostel_required,
            college_type=req.college_type,
            rural_quota=req.rural_quota,
            kannada_medium=req.kannada_medium,
            hk_371j=req.hk_371j,
            snq=req.snq,
        )
        pipeline = get_pipeline()
        return pipeline.run_full_recommendation(
            query=f"rank {req.kcet_rank} category {req.category}",
            existing_profile=profile,
            top_n=req.top_n,
        )


# ══════════════════════════════════════════════════════════════════════════════
# AI CHAT (LLM explains engine results)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/chat")
def chat(req: ChatRequest):
    """
    AI counselling chat.
    
    Architecture:
    1. Pipeline runs deterministic recommendation
    2. LLM receives ONLY pre-computed results (not raw data)
    3. LLM generates human-readable explanation
    4. LLM CANNOT modify any values from the pipeline
    """
    pipeline = get_pipeline()
    existing = _profile_from_session(req.session_id)

    # Step 1: Run deterministic pipeline
    pipeline_result = pipeline.run_full_recommendation(
        query=req.message,
        existing_profile=existing,
        top_n=10,
    )

    # Step 2: Save updated profile
    if pipeline_result.get("student_profile"):
        sp = pipeline_result["student_profile"]
        from core.student_profile import StudentProfile
        p = StudentProfile()
        for k, v in sp.items():
            if hasattr(p, k):
                setattr(p, k, v)
        _save_profile(req.session_id, p)

    # Step 3: Build context for LLM (LLM sees ONLY pre-computed results)
    llm_context = pipeline.build_llm_context(pipeline_result)

    # Step 4: LLM explains the results (never decides)
    if LLM_AVAILABLE and pipeline_result.get("success"):
        try:
            llm = get_llm_service()
            system_prompt = (
                "You are a Karnataka engineering admission counsellor. "
                "You have been given the OUTPUT of a deterministic counselling engine. "
                "Your ONLY job is to explain these results clearly and helpfully in natural language. "
                "DO NOT add colleges that are not in the results. "
                "DO NOT change any probability values. "
                "DO NOT invent any data. "
                "Stick strictly to the information provided."
            )
            explanation = llm.generate(
                prompt=f"Query: {req.message}\n\n{llm_context}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1500,
            )
            return {
                "success": True,
                "response": explanation,
                "pipeline_data": pipeline_result,
                "context_used": True,
                "model": "deterministic + llm-explanation",
            }
        except Exception as e:
            logger.warning(f"[Chat] LLM explanation failed: {e}")

    # Fallback: Return structured data without LLM
    return {
        "success": True,
        "response": _format_plain_response(pipeline_result),
        "pipeline_data": pipeline_result,
        "context_used": False,
        "model": "deterministic-only",
    }


@app.post("/api/v2/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat endpoint — SSE token stream."""
    pipeline = get_pipeline()
    existing = _profile_from_session(req.session_id)

    # Deterministic pipeline first
    pipeline_result = pipeline.run_full_recommendation(
        query=req.message,
        existing_profile=existing,
        top_n=10,
    )

    # Save profile
    if pipeline_result.get("student_profile"):
        sp = pipeline_result["student_profile"]
        from core.student_profile import StudentProfile
        p = StudentProfile()
        for k, v in sp.items():
            if hasattr(p, k):
                setattr(p, k, v)
        _save_profile(req.session_id, p)

    llm_context = pipeline.build_llm_context(pipeline_result)

    async def generate():
        # First yield the pipeline data
        yield f"data: {json.dumps({'pipeline_data': pipeline_result, 'type': 'data'})}\n\n"

        if LLM_AVAILABLE and pipeline_result.get("success"):
            try:
                llm = get_llm_service()
                system_prompt = (
                    "You are a Karnataka engineering admission counsellor. "
                    "Explain the provided counselling results clearly. "
                    "Do NOT add data not present in the results."
                )
                msgs = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{req.message}\n\n{llm_context}"},
                ]
                for token in llm.groq.stream(msgs, temperature=0.3):
                    yield f"data: {json.dumps({'chunk': token, 'type': 'text'})}\n\n"
            except Exception as e:
                logger.warning(f"[Stream] LLM failed: {e}")
                plain = _format_plain_response(pipeline_result)
                yield f"data: {json.dumps({'chunk': plain, 'type': 'text'})}\n\n"
        else:
            plain = _format_plain_response(pipeline_result)
            yield f"data: {json.dumps({'chunk': plain, 'type': 'text'})}\n\n"

        yield f"data: {json.dumps({'done': True, 'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# ══════════════════════════════════════════════════════════════════════════════
# COLLEGE DATA ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/colleges")
def get_colleges(
    q: str = "",
    branch: str = "",
    location: str = "",
    college_type: str = "",
    page: int = 1,
    limit: int = 12,
):
    """List colleges with filtering."""
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()

    filtered = []
    for c in all_colleges:
        if q and q.lower() not in (c.get("name") or "").lower():
            if q.lower() not in (c.get("location") or "").lower():
                continue
        if branch and branch.upper() not in [b.upper() for b in c.get("branches", [])]:
            continue
        if location and location.lower() not in (c.get("location") or "").lower():
            continue
        if college_type and college_type.lower() not in (c.get("type") or "").lower():
            continue
        filtered.append(c)

    total = len(filtered)
    start = (page - 1) * limit
    items = filtered[start : start + limit]

    # Return compact list
    compact = []
    for c in items:
        fee = c.get("annual_fee", {})
        compact.append({
            "college_id": c.get("college_id"),
            "name": c.get("name"),
            "location": c.get("location"),
            "type": c.get("type"),
            "naac_grade": c.get("naac_grade"),
            "branches": c.get("branches", []),
            "hostel_available": c.get("hostel_available"),
            "annual_fee_gm": fee.get("gm") if isinstance(fee, dict) else fee,
            "placement_avg_lpa": c.get("placement_avg_lpa"),
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "items": compact,
    }


@app.get("/api/v2/colleges/{college_id}")
def get_college(college_id: str):
    """Get full details for a single college."""
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()
    college = next((c for c in all_colleges if c.get("college_id") == college_id), None)
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college


@app.post("/api/v2/colleges/compare")
def compare_colleges(req: CompareRequest):
    """Compare specific colleges side-by-side."""
    pipeline = get_pipeline()
    profile = _profile_from_session(req.session_id) if req.session_id else None
    return pipeline.run_comparison(req.college_ids, profile)


@app.get("/api/v2/branches")
def get_branches():
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()
    branches = sorted({b for c in all_colleges for b in c.get("branches", []) if b})
    return branches


@app.get("/api/v2/locations")
def get_locations():
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()
    locs = sorted({c.get("location") for c in all_colleges if c.get("location")})
    return locs


# ══════════════════════════════════════════════════════════════════════════════
# SCHOLARSHIP ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/scholarships")
def get_all_scholarships():
    """Get all scholarship schemes (no eligibility check)."""
    engine = get_scholarship_engine()
    return {
        "success": True,
        "total": len(engine.SCHOLARSHIP_RULES),
        "scholarships": engine.SCHOLARSHIP_RULES,
    }


@app.post("/api/v2/scholarships/check")
def check_scholarships(req: ProfileRequest):
    """Check scholarship eligibility for a student profile."""
    from core.student_profile import StudentProfile
    profile = StudentProfile(
        rank=req.rank,
        category=req.category.upper(),
        annual_income=req.annual_income,
        rural_quota=req.rural_quota,
        hk_371j=req.hk_371j,
        snq=req.snq,
    )
    pipeline = get_pipeline()
    return pipeline.run_scholarship_check(profile)


# ══════════════════════════════════════════════════════════════════════════════
# HOSTEL ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/hostels")
def get_hostels(location: str = "", budget: int = 0):
    """Get hostel information for colleges."""
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()

    hostels = []
    for c in all_colleges:
        if not c.get("hostel_available"):
            continue
        if location and location.lower() not in (c.get("location") or "").lower():
            continue

        hostel = c.get("hostel_details", {})
        annual_fee = hostel.get("annual_fee", 0)

        if budget > 0 and annual_fee > budget:
            continue

        hostels.append({
            "college_id": c.get("college_id"),
            "college_name": c.get("name"),
            "location": c.get("location"),
            "annual_fee": annual_fee,
            "boys_hostel": hostel.get("boys_hostel", True),
            "girls_hostel": hostel.get("girls_hostel", False),
            "mess_available": hostel.get("mess_available", True),
            "wifi": hostel.get("wifi", False),
            "capacity": hostel.get("capacity"),
        })

    return {"success": True, "total": len(hostels), "hostels": hostels}


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/analytics/cutoff-trends")
def cutoff_trends(branch: str = "CSE", category: str = "GM", limit: int = 20):
    """Get cutoff trend data for analytics dashboard."""
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()

    trends = []
    for c in all_colleges:
        cutoffs = c.get("cutoffs", {})
        historical = {}
        for year in ["2020", "2021", "2022", "2023", "2024"]:
            val = cutoffs.get(year, {}).get(branch, {}).get(category, 0)
            if val:
                historical[year] = val

        if len(historical) >= 2:
            vals = [historical[y] for y in sorted(historical.keys())]
            trend_1yr = vals[-1] - vals[-2] if len(vals) >= 2 else 0

            trends.append({
                "college_id": c.get("college_id"),
                "college_name": c.get("name"),
                "location": c.get("location"),
                "type": c.get("type"),
                "historical_cutoffs": historical,
                "latest_cutoff": vals[-1],
                "trend_1yr": trend_1yr,
                "trend_direction": "↑ Getting harder" if trend_1yr < -500
                                   else ("↓ Getting easier" if trend_1yr > 500 else "→ Stable"),
            })

    trends.sort(key=lambda x: x["latest_cutoff"])
    return {
        "success": True,
        "branch": branch,
        "category": category,
        "total": len(trends),
        "data": trends[:limit],
    }


@app.get("/api/v2/analytics/placement-overview")
def placement_overview():
    """Placement statistics across all colleges."""
    pipeline = get_pipeline()
    all_colleges = pipeline._get_all_colleges()

    by_type: Dict[str, List[float]] = {}
    top_placed = []

    for c in all_colleges:
        lpa = c.get("placement_avg_lpa", 0)
        if lpa:
            ctype = c.get("type", "Unknown")
            by_type.setdefault(ctype, []).append(float(lpa))
            top_placed.append({
                "college": c.get("name"),
                "location": c.get("location"),
                "avg_lpa": float(lpa),
                "highest_lpa": c.get("highest_package_lpa"),
                "type": ctype,
            })

    top_placed.sort(key=lambda x: x["avg_lpa"], reverse=True)
    type_avgs = {
        k: round(sum(v) / len(v), 2)
        for k, v in by_type.items() if v
    }

    return {
        "success": True,
        "top_colleges": top_placed[:20],
        "by_college_type": type_avgs,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/admin/rebuild-index")
def rebuild_index():
    """Reload college data from disk (Admin only)."""
    pipeline = get_pipeline()
    # Force reload by clearing caches
    if pipeline.json_data:
        try:
            pipeline.json_data._reload()
        except Exception:
            pass
    return {"success": True, "message": "Index rebuild triggered"}


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════════════════════════

def _format_plain_response(pipeline_result: Dict) -> str:
    """Format pipeline result as plain text when LLM is unavailable."""
    if not pipeline_result.get("success"):
        return pipeline_result.get("error_message", "I need your KCET rank and branch preference to help you.")

    safe = pipeline_result.get("safe", [])
    moderate = pipeline_result.get("moderate", [])
    profile = pipeline_result.get("student_profile", {})
    rank = profile.get("rank")

    lines = [f"Based on your KCET rank {rank} ({profile.get('category')} category):\n"]

    if safe:
        lines.append("✅ **SAFE OPTIONS** (high probability):")
        for c in safe[:4]:
            lines.append(f"  • {c['name']} ({c['location']}) — {c.get('admission_probability', '~'):.0f}% chance")

    if moderate:
        lines.append("\n🎯 **MODERATE OPTIONS** (competitive but achievable):")
        for c in moderate[:3]:
            lines.append(f"  • {c['name']} ({c['location']}) — {c.get('admission_probability', '~'):.0f}% chance")

    scholarships = pipeline_result.get("scholarships", {})
    eligible_sch = scholarships.get("eligible", [])
    if eligible_sch:
        lines.append(f"\n💰 **Scholarships:** You may be eligible for {len(eligible_sch)} scheme(s)")
        lines.append(f"  → {eligible_sch[0]['name']}")

    return "\n".join(lines)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
