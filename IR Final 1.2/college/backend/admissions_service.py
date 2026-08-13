"""Unified JEE/NEET admission counselling services."""

import json
import os
import re
from typing import Dict, List, Optional

from admission_probability import calculate_admission_probability, normalize_category
from ml_predictor import get_jee_predictor, get_neet_predictor


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _safe_int(value, default: Optional[int] = None) -> Optional[int]:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _clean(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _branch_matches(branch: str, preferred: List[str]) -> bool:
    if not preferred:
        return True

    branch_text = _clean(branch)
    aliases = {
        "cse": ["computer science", "cse", "cs", "software"],
        "ece": ["electronics", "communication", "ece"],
        "eee": ["electrical", "eee"],
        "mech": ["mechanical", "mech"],
        "civil": ["civil"],
        "ai": ["artificial intelligence", "ai", "machine learning", "aiml"],
        "data": ["data science", "data", "ds"],
        "medical": ["mbbs", "medicine"],
        "dental": ["bds", "dental"],
        "ayush": ["bams", "bhms", "ayush"],
    }

    for raw in preferred:
        pref = _clean(raw)
        terms = aliases.get(pref, [pref])
        if any(term in branch_text for term in terms):
            return True
    return False


def _gender_matches(row_gender: str, requested_gender: str) -> bool:
    row = _clean(row_gender)
    requested = _clean(requested_gender)
    if not requested or "neutral" in row or "all" in row:
        return True
    if requested.startswith("f") and ("female" in row or "women" in row):
        return True
    if requested.startswith("m") and ("male" in row or "neutral" in row):
        return True
    return False


def _category_matches(row_category: str, requested_category: str) -> bool:
    row = normalize_category(row_category)
    requested = normalize_category(requested_category)
    if row == requested:
        return True
    if row == "OPEN":
        return True
    if requested == "OBC-NCL" and row in {"OBC", "OBC-NCL"}:
        return True
    return False


def _build_source_note(dataset: Dict) -> Dict:
    return {
        "dataset_status": dataset.get("dataset_status", "sample"),
        "last_updated": dataset.get("last_updated"),
        "source_note": dataset.get("source_note"),
        "official_sources": dataset.get("official_sources", []),
    }


def get_jee_cutoffs(filters: Optional[Dict] = None) -> Dict:
    filters = filters or {}
    dataset = _load_json("jee_cutoffs_sample.json")
    rows = dataset.get("cutoffs", [])

    institute_type = _clean(filters.get("institute_type"))
    category = filters.get("category")
    branch = filters.get("branch")
    quota = _clean(filters.get("quota"))

    filtered = []
    for row in rows:
        if institute_type and _clean(row.get("institute_type")) != institute_type:
            continue
        if category and not _category_matches(row.get("category"), category):
            continue
        if branch and not _branch_matches(row.get("branch", ""), [branch]):
            continue
        if quota and _clean(row.get("quota")) != quota:
            continue
        filtered.append(row)

    return {
        "success": True,
        "total": len(filtered),
        "cutoffs": filtered,
        "source": _build_source_note(dataset),
    }


def predict_jee(data: Dict) -> Dict:
    dataset = _load_json("jee_cutoffs_sample.json")
    rows = dataset.get("cutoffs", [])

    main_rank = _safe_int(data.get("jee_main_rank"))
    advanced_rank = _safe_int(data.get("jee_advanced_rank"))
    category = data.get("category", "OPEN")
    gender = data.get("gender", "Gender Neutral")
    home_state = _clean(data.get("home_state"))
    preferred_branches = data.get("preferred_branches") or []
    if isinstance(preferred_branches, str):
        preferred_branches = [preferred_branches]

    jee_predictor = get_jee_predictor()
    predictions = []
    skipped_rank = 0

    for row in rows:
        institute_type = row.get("institute_type", "")
        rank = advanced_rank if institute_type == "IIT" else main_rank
        if not rank:
            skipped_rank += 1
            continue

        if not _branch_matches(row.get("branch", ""), preferred_branches):
            continue
        if not _category_matches(row.get("category", "OPEN"), category):
            continue
        if not _gender_matches(row.get("gender", "Gender Neutral"), gender):
            continue

        quota = _clean(row.get("quota"))
        row_state = _clean(row.get("state"))
        if quota == "hs" and row_state and home_state and row_state != home_state:
            continue
        if quota == "os" and row_state and home_state and row_state == home_state:
            continue

        college = row.get("college")
        branch = row.get("branch")
        row_category = row.get("category", "OPEN")
        row_quota = row.get("quota", "AI")
        row_gender = row.get("gender", "Gender Neutral")

        # ML-based prediction
        trend_prediction = jee_predictor.predict_cutoff(
            college, branch, row_category, row_quota, row_gender, target_year=2026
        )
        predicted_cutoff = trend_prediction["predicted"]

        prob_result = jee_predictor.calculate_probability(rank, predicted_cutoff, category)
        probability_pct = prob_result["probability"] # 0 - 100
        probability_dec = probability_pct / 100.0   # 0 - 1

        demand_trend = jee_predictor.calculate_demand_trend(college, branch)
        roi_result = jee_predictor.calculate_roi(institute_type, row.get("annual_fee", 0))

        predictions.append({
            "college": college,
            "branch": branch,
            "category": row.get("category"),
            "quota": row.get("quota"),
            "predicted_probability": probability_dec, # for backward compatibility
            "probability": probability_pct,            # for new ML spotlight gauge
            "admission_chance": prob_result["tier"],
            "predicted_round": prob_result["round"],
            "institute_type": institute_type,
            "exam": row.get("exam"),
            "year": 2026,
            "round": row.get("round"),
            "opening_rank": row.get("opening_rank"),
            "closing_rank": predicted_cutoff,          # ML-predicted cutoff rank
            "predicted_cutoff": predicted_cutoff,
            "annual_fee": row.get("annual_fee"),
            "rank_used": rank,
            "state": row.get("state"),
            "reason": f"ML-predicted cutoff of {predicted_cutoff} gives a {prob_result['tier']} fit in {prob_result['round']}.",
            "trend": demand_trend["label"],
            "trend_direction": trend_prediction["trend_direction"],
            "roi_label": roi_result["label"],
            "roi_score": roi_result["score"],
            "cutoff_trends": trend_prediction["historical"],
        })

    predictions.sort(
        key=lambda item: (
            item["probability"],
            -item["closing_rank"],
        ),
        reverse=True,
    )

    counts = {
        "iit": len([p for p in predictions if p["institute_type"] == "IIT"]),
        "nit": len([p for p in predictions if p["institute_type"] == "NIT"]),
        "iiit": len([p for p in predictions if p["institute_type"] == "IIIT"]),
        "gfti": len([p for p in predictions if p["institute_type"] == "GFTI"]),
        "safe": len([p for p in predictions if p["admission_chance"] in ["Safe", "Very Safe"]]),
        "moderate": len([p for p in predictions if p["admission_chance"] == "Moderate"]),
        "dream": len([p for p in predictions if p["admission_chance"] in ["Dream", "Reach", "Long Shot"]]),
    }

    return {
        "success": True,
        "student_profile": {
            "jee_main_rank": main_rank,
            "jee_advanced_rank": advanced_rank,
            "category": normalize_category(category),
            "gender": gender,
            "home_state": data.get("home_state"),
            "preferred_branches": preferred_branches,
        },
        "predictors": {
            "iit_predictor": counts["iit"],
            "nit_predictor": counts["nit"],
            "iiit_predictor": counts["iiit"],
            "gfti_predictor": counts["gfti"],
        },
        "summary": counts,
        "total": len(predictions),
        "predictions": predictions[: _safe_int(data.get("top_n"), 30)],
        "source": _build_source_note(dataset),
        "note": "OPEN rows use common rank lists. ML models train across all category datasets.",
    }


def get_neet_cutoffs(filters: Optional[Dict] = None) -> Dict:
    filters = filters or {}
    dataset = _load_json("neet_cutoffs_sample.json")
    rows = dataset.get("cutoffs", [])

    course = _clean(filters.get("course"))
    quota = _clean(filters.get("quota"))
    category = filters.get("category")
    state = _clean(filters.get("state"))

    filtered = []
    for row in rows:
        if course and _clean(row.get("course")) != course:
            continue
        if quota and quota not in _clean(row.get("quota")):
            continue
        if category and not _category_matches(row.get("category"), category):
            continue
        if state and _clean(row.get("state")) and _clean(row.get("state")) != state:
            continue
        filtered.append(row)

    return {
        "success": True,
        "total": len(filtered),
        "cutoffs": filtered,
        "source": _build_source_note(dataset),
    }


def predict_neet(data: Dict) -> Dict:
    dataset = _load_json("neet_cutoffs_sample.json")
    rows = dataset.get("cutoffs", [])

    rank = _safe_int(data.get("neet_rank"))
    score = _safe_int(data.get("neet_score"), 0)
    category = data.get("category", "OPEN")
    state = _clean(data.get("state"))
    gender = data.get("gender", "All")
    requested_tracks = data.get("tracks") or []
    if isinstance(requested_tracks, str):
        requested_tracks = [requested_tracks]

    if not rank:
        return {"success": False, "error": "NEET rank is required."}

    neet_predictor = get_neet_predictor()
    predictions = []
    for row in rows:
        if not _category_matches(row.get("category", "OPEN"), category):
            continue
        if not _gender_matches(row.get("gender", "All"), gender):
            continue

        quota = _clean(row.get("quota"))
        row_state = _clean(row.get("state"))
        if "state" in quota and row_state and state and row_state != state:
            continue

        track = _clean(row.get("track"))
        if requested_tracks and not any(_clean(t) in track for t in requested_tracks):
            continue

        college = row.get("college")
        course = row.get("course")
        row_category = row.get("category", "OPEN")
        row_quota = row.get("quota", "AIQ")
        row_gender = row.get("gender", "All")

        # ML-based prediction
        trend_prediction = neet_predictor.predict_cutoff(
            college, course, row_category, row_quota, row_gender, target_year=2026
        )
        predicted_cutoff = trend_prediction["predicted"]

        prob_result = neet_predictor.calculate_probability(rank, predicted_cutoff, category)
        probability_pct = prob_result["probability"]
        probability_dec = probability_pct / 100.0

        if score and score >= row.get("typical_score", 0) and probability_pct < 95.0:
            probability_pct = min(99.0, probability_pct + 4.0)
            probability_dec = probability_pct / 100.0

        demand_trend = neet_predictor.calculate_demand_trend(college, course)
        roi_result = neet_predictor.calculate_roi(row.get("track"), row.get("annual_fee", 0))

        predictions.append({
            "college": college,
            "course": course,
            "quota": row.get("quota"),
            "category": row.get("category"),
            "predicted_probability": probability_dec, # backward compatibility
            "probability": probability_pct,            # circular fit gauge
            "admission_chance": prob_result["tier"],
            "predicted_round": prob_result["round"],
            "track": row.get("track"),
            "state": row.get("state"),
            "year": 2026,
            "round": row.get("round"),
            "opening_rank": row.get("opening_rank"),
            "closing_rank": predicted_cutoff,          # ML predicted cutoff
            "predicted_cutoff": predicted_cutoff,
            "typical_score": row.get("typical_score"),
            "annual_fee": row.get("annual_fee"),
            "reason": f"ML model estimates cutoff rank at {predicted_cutoff} providing a {prob_result['tier']} chance in {prob_result['round']}.",
            "trend": demand_trend["label"],
            "trend_direction": trend_prediction["trend_direction"],
            "roi_label": roi_result["label"],
            "roi_score": roi_result["score"],
            "cutoff_trends": trend_prediction["historical"],
        })

    predictions.sort(key=lambda item: item["probability"], reverse=True)
    summary = {
        "aiq": len([p for p in predictions if "AIQ" in p["quota"]]),
        "state_quota": len([p for p in predictions if "State" in p["quota"]]),
        "government": len([p for p in predictions if p["track"] == "Government"]),
        "private": len([p for p in predictions if p["track"] == "Private"]),
        "dental": len([p for p in predictions if p["track"] == "Dental"]),
        "ayush": len([p for p in predictions if p["track"] == "AYUSH"]),
        "safe": len([p for p in predictions if p["admission_chance"] in ["Safe", "Very Safe"]]),
        "moderate": len([p for p in predictions if p["admission_chance"] == "Moderate"]),
        "dream": len([p for p in predictions if p["admission_chance"] in ["Dream", "Reach", "Long Shot"]]),
    }

    return {
        "success": True,
        "student_profile": {
            "neet_rank": rank,
            "neet_score": score,
            "category": normalize_category(category),
            "state": data.get("state"),
            "gender": gender,
        },
        "features": {
            "aiq_college_predictor": summary["aiq"],
            "state_quota_predictor": summary["state_quota"],
            "government_college_predictor": summary["government"],
            "private_medical_college_predictor": summary["private"],
            "dental_college_predictor": summary["dental"],
            "ayush_predictor": summary["ayush"],
        },
        "summary": summary,
        "total": len(predictions),
        "predictions": predictions[: _safe_int(data.get("top_n"), 30)],
        "source": _build_source_note(dataset),
    }


def build_neet_counseling_plan(data: Dict) -> Dict:
    prediction = predict_neet(data)
    if not prediction.get("success"):
        return prediction

    rank = prediction["student_profile"]["neet_rank"]
    safe = [p for p in prediction["predictions"] if p["admission_chance"] == "Safe"]
    moderate = [p for p in prediction["predictions"] if p["admission_chance"] == "Moderate"]
    dream = [p for p in prediction["predictions"] if p["admission_chance"] == "Dream"]

    if safe:
        strategy = "Put dream AIQ options first, then moderate choices, then safe state/government options."
    elif moderate:
        strategy = "Fill a broad list across AIQ, state quota, BDS, and AYUSH. Do not rely on one round."
    else:
        strategy = "Treat MBBS government seats as ambitious. Add private, BDS, and AYUSH backups early."

    return {
        "success": True,
        "rank": rank,
        "strategy": strategy,
        "rounds": [
            "MCC AIQ Round 1: register, fill choices, lock choices, check allotment.",
            "MCC AIQ Round 2: upgrade or re-enter with improved preference list.",
            "Mop-up / stray vacancy: use for remaining AIQ, deemed, BDS, and AYUSH seats.",
            "State quota rounds: follow the official state counselling authority schedule.",
        ],
        "documents": [
            "NEET UG score card and admit card",
            "Class 10 and Class 12 marks cards",
            "Aadhaar or government ID",
            "Category / EWS / PwD certificate if applicable",
            "Domicile certificate for state quota",
            "Passport photos and fee payment receipts",
        ],
        "choice_buckets": {
            "dream": dream[:8],
            "moderate": moderate[:10],
            "safe": safe[:10],
        },
        "prediction_summary": prediction["summary"],
        "source": prediction["source"],
    }


def compare_colleges(data: Dict) -> Dict:
    profiles = _load_json("college_comparison_profiles.json")
    requested = data.get("colleges") or data.get("college_names") or []
    if isinstance(requested, str):
        requested = [name.strip() for name in requested.split(",") if name.strip()]

    selected = []
    for name in requested:
        needle = _clean(name)
        match = next(
            (
                profile
                for profile in profiles
                if needle in _clean(profile["college"]) or _clean(profile["college"]) in needle
            ),
            None,
        )
        if match:
            selected.append(match)

    if not selected:
        selected = profiles[:3]

    def score(profile):
        avg = float(profile.get("average_package_lpa") or 0)
        fee = float(profile.get("annual_fee") or 0)
        hostel = 8 if profile.get("hostel") else 0
        return (avg * 8) + hostel - (fee / 100000)

    selected.sort(key=score, reverse=True)
    best = selected[0]

    return {
        "success": True,
        "total": len(selected),
        "comparison": selected,
        "recommendation": {
            "best_fit": best["college"],
            "reason": "Best combined placement, fee, hostel, and location score among the selected colleges.",
        },
        "metrics": ["fees", "placement", "hostel", "location", "average_package", "highest_package"],
    }


def compare_jee_options(data: Dict) -> Dict:
    if data.get("colleges") or data.get("college_names"):
        return compare_colleges(data)

    profile = {
        "jee_main_rank": data.get("jee_main_rank"),
        "jee_advanced_rank": data.get("jee_advanced_rank"),
        "category": data.get("category", "OPEN"),
        "gender": data.get("gender", "Gender Neutral"),
        "home_state": data.get("home_state"),
        "preferred_branches": data.get("preferred_branches", []),
        "top_n": 8,
    }
    prediction = predict_jee(profile)
    return {
        "success": True,
        "comparison": prediction.get("predictions", [])[:8],
        "summary": prediction.get("summary", {}),
        "source": prediction.get("source", {}),
    }


def generate_career_roadmap(data: Dict) -> Dict:
    branch = (data.get("branch") or data.get("course") or "CSE").upper()
    interest = _clean(data.get("interests") or data.get("interest") or "technology")

    branch_profiles = {
        "CSE": {
            "salary": "8-24 LPA",
            "placements": ["Software Engineer", "Data Engineer", "AI/ML Engineer"],
            "higher_studies": ["M.Tech CSE", "MS Computer Science", "MBA Product Management"],
            "skills": ["Python", "DSA", "Databases", "System design", "AI tools"],
        },
        "ECE": {
            "salary": "6-18 LPA",
            "placements": ["Embedded Engineer", "VLSI Engineer", "IoT Developer"],
            "higher_studies": ["M.Tech VLSI", "MS Robotics", "M.Tech Communication Systems"],
            "skills": ["C/C++", "Signals", "Embedded C", "PCB basics", "IoT"],
        },
        "MBBS": {
            "salary": "8-20 LPA after internship/residency",
            "placements": ["Junior Resident", "Medical Officer", "Hospital Resident"],
            "higher_studies": ["MD", "MS", "DNB", "Public Health"],
            "skills": ["Clinical diagnosis", "Patient communication", "Research basics"],
        },
        "BDS": {
            "salary": "4-12 LPA",
            "placements": ["Dental Surgeon", "Clinic Associate", "Hospital Dental Officer"],
            "higher_studies": ["MDS", "Public Health", "Hospital Administration"],
            "skills": ["Clinical dentistry", "Digital dentistry", "Practice management"],
        },
    }
    profile = branch_profiles.get(branch, branch_profiles["CSE"])

    roadmap = [
        {"year": 1, "focus": "Foundation", "actions": ["Master core subjects", "Build study routine", "Join one technical or clinical club"]},
        {"year": 2, "focus": "Skill Stack", "actions": profile["skills"][:3]},
        {"year": 3, "focus": "Projects and exposure", "actions": ["Complete 2 portfolio projects", "Apply for internships", "Start competitive preparation"]},
        {"year": 4, "focus": "Career launch", "actions": ["Placement or internship conversion", "Interview preparation", "Higher-studies exam plan"]},
        {"year": 5, "focus": "Growth track", "actions": ["Specialize in one domain", "Build professional network", "Plan startup/research/PG path"]},
    ]

    if "startup" in interest:
        startup = "Build a student venture, validate with 20 users, and apply to college incubation cells."
    else:
        startup = "Explore a campus startup only after building a strong skill or clinical problem insight."

    return {
        "success": True,
        "branch": branch,
        "five_year_roadmap": roadmap,
        "expected_salary": profile["salary"],
        "placement_opportunities": profile["placements"],
        "higher_studies_opportunities": profile["higher_studies"],
        "startup_opportunities": startup,
    }


def answer_admission_query(message: str, profile: Optional[Dict] = None, llm=None) -> Dict:
    profile = profile or {}
    msg = message or ""
    lower = msg.lower()
    rank_match = re.search(r"(air|rank)\s*(?:is|:)?\s*(\d+)|\b(\d{1,7})\b", lower)
    rank = _safe_int(rank_match.group(2) or rank_match.group(3)) if rank_match else None

    context_lines = []
    if any(term in lower for term in ["iit", "nit", "iiit", "gfti", "jee"]):
        jee_data = {
            "jee_main_rank": rank or profile.get("jee_main_rank"),
            "jee_advanced_rank": rank or profile.get("jee_advanced_rank"),
            "category": profile.get("category", "OPEN"),
            "gender": profile.get("gender", "Gender Neutral"),
            "home_state": profile.get("home_state"),
            "preferred_branches": [profile.get("branch")] if profile.get("branch") else [],
            "top_n": 5,
        }
        result = predict_jee(jee_data)
        context_lines = [
            f"{p['college']} {p['branch']}: {p['admission_chance']} ({p['predicted_probability']}%) cutoff {p['closing_rank']}"
            for p in result.get("predictions", [])[:5]
        ]
    elif any(term in lower for term in ["aiims", "neet", "mbbs", "bds", "medical"]):
        neet_data = {
            "neet_rank": rank or profile.get("neet_rank"),
            "neet_score": profile.get("neet_score"),
            "category": profile.get("category", "OPEN"),
            "state": profile.get("state"),
            "gender": profile.get("gender", "All"),
            "top_n": 5,
        }
        result = predict_neet(neet_data) if neet_data.get("neet_rank") else {"predictions": []}
        context_lines = [
            f"{p['college']} {p['course']}: {p['admission_chance']} ({p['probability']}%) cutoff {p['closing_rank']}"
            for p in result.get("predictions", [])[:5]
        ]

    context = "\n".join(context_lines) or "No exact local cutoff match was found. Ask with exam, rank, branch/course, category, and state for a sharper answer."

    if llm:
        prompt = (
            "You are an admission counselor. Use only this retrieved cutoff context. "
            "Give a short, honest answer with Safe/Moderate/Dream language.\n\n"
            f"Question: {msg}\n\nContext:\n{context}"
        )
        try:
            response = llm.generate(prompt, temperature=0.3, max_tokens=500)
            return {"success": True, "response": response, "retrieved_context": context_lines}
        except Exception:
            pass

    return {
        "success": True,
        "response": (
            "Based on the local cutoff knowledge base:\n"
            f"{context}\n\n"
            "Use this as counselling guidance, then verify final ranks on JoSAA/MCC before locking choices."
        ),
        "retrieved_context": context_lines,
    }
