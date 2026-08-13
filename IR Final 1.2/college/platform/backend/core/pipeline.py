"""
Pipeline Orchestrator — Ties every engine together.

Flow:
  Input text → ProfileExtractor → ConstraintEngine → CounsellingEngine
  → AdmissionPredictor → RankingEngine → ScholarshipEngine → HostelEngine
  → LLM Explainer → Final Response

The LLM ONLY explains results. It NEVER decides colleges, probabilities,
rankings, or eligibility.
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("Pipeline")

# Add parent paths for imports
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "backend")

sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, LEGACY_DIR)

from core.student_profile import ProfileExtractor, StudentProfile, get_profile_extractor
from core.scholarship_engine import ScholarshipEngine, get_scholarship_engine

# Legacy engines — reused (already deterministic)
try:
    from engines.constraint_filter import ConstraintFilter
    CONSTRAINT_FILTER_AVAILABLE = True
except ImportError:
    CONSTRAINT_FILTER_AVAILABLE = False

try:
    from engines.ranking_engine import RankingEngine
    RANKING_ENGINE_AVAILABLE = True
except ImportError:
    RANKING_ENGINE_AVAILABLE = False

try:
    from kea_allotment_engine import KEASeatAllotmentEngine, get_kea_engine
    KEA_ENGINE_AVAILABLE = True
except ImportError:
    KEA_ENGINE_AVAILABLE = False

try:
    from json_data_service import get_json_data_service
    JSON_DATA_AVAILABLE = True
except ImportError:
    JSON_DATA_AVAILABLE = False


class CounsellingPipeline:
    """
    Production-grade counselling pipeline.
    
    Architecture invariants:
    1. LLM NEVER decides colleges, probabilities, rankings, or eligibility.
    2. All structured data comes from deterministic engines.
    3. LLM only generates human-readable explanation of engine outputs.
    4. Every recommendation is deterministic and reproducible.
    """

    def __init__(self):
        self.profile_extractor = get_profile_extractor()
        self.scholarship_engine = get_scholarship_engine()
        self.constraint_filter = ConstraintFilter() if CONSTRAINT_FILTER_AVAILABLE else None
        self.ranking_engine = RankingEngine() if RANKING_ENGINE_AVAILABLE else None
        self.kea_engine = None
        self.json_data = None
        self._init_data_services()

    def _init_data_services(self):
        """Initialize data services with graceful fallback."""
        if KEA_ENGINE_AVAILABLE:
            try:
                self.kea_engine = get_kea_engine()
                logger.info("[Pipeline] KEA Engine initialized")
            except Exception as e:
                logger.warning(f"[Pipeline] KEA Engine init failed: {e}")

        if JSON_DATA_AVAILABLE:
            try:
                self.json_data = get_json_data_service()
                logger.info("[Pipeline] JSON Data Service initialized")
            except Exception as e:
                logger.warning(f"[Pipeline] JSON Data Service init failed: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN PIPELINE ENTRY POINTS
    # ══════════════════════════════════════════════════════════════════════════

    def run_full_recommendation(
        self,
        query: str,
        existing_profile: Optional[StudentProfile] = None,
        top_n: int = 15,
    ) -> Dict[str, Any]:
        """
        Full recommendation pipeline.
        Returns structured result with all engine outputs.
        The LLM caller should only use this to generate explanation text.
        """
        start = time.time()
        result = {
            "success": False,
            "pipeline_version": "2.0",
            "timestamp": int(start),
        }

        # ── Step 1: Profile Extraction ─────────────────────────────────────
        if existing_profile:
            profile = self.profile_extractor.update(existing_profile, query)
        else:
            profile = self.profile_extractor.extract(query)

        result["student_profile"] = profile.to_dict()

        # ── Step 2: Validate Profile ───────────────────────────────────────
        if not profile.rank:
            result["error"] = "MISSING_RANK"
            result["error_message"] = (
                "I need your KCET rank to make recommendations. "
                "Please tell me your rank (e.g., 'My KCET rank is 12000')."
            )
            result["missing_fields"] = profile.missing_fields
            result["profile_ready"] = False
            return result

        if not profile.preferred_branches:
            result["error"] = "MISSING_BRANCH"
            result["error_message"] = (
                "Please tell me which branch you're interested in "
                "(e.g., 'CSE', 'ECE', 'AI&DS', 'Mechanical')."
            )
            result["missing_fields"] = profile.missing_fields
            result["profile_ready"] = False
            return result

        result["profile_ready"] = True

        # ── Step 3: Load All Eligible Colleges ────────────────────────────
        all_colleges = self._get_all_colleges()
        if not all_colleges:
            result["error"] = "NO_DATA"
            result["error_message"] = "College database is not available. Please try again."
            return result

        result["total_colleges_in_db"] = len(all_colleges)

        # ── Step 4: Constraint Filtering ──────────────────────────────────
        if self.constraint_filter:
            filtered_colleges, filter_report = self.constraint_filter.apply(all_colleges, profile)
        else:
            filtered_colleges = self._basic_filter(all_colleges, profile)
            filter_report = {"filtered_count": len(filtered_colleges)}

        result["filter_report"] = filter_report

        # ── Step 5: No results check ───────────────────────────────────────
        if not filtered_colleges:
            result["success"] = True
            result["recommendations"] = []
            result["safe"] = []
            result["moderate"] = []
            result["ambitious"] = []
            result["no_results"] = True
            result["no_results_message"] = (
                "No colleges in our database satisfy all your specified constraints. "
                "Constraints applied: " + json.dumps(filter_report.get("constraints_applied", {}))
            )
            result["execution_ms"] = int((time.time() - start) * 1000)
            return result

        # ── Step 6: Admission Probability via KEA Engine ───────────────────
        admission_probs = {}
        kea_results = {}

        if self.kea_engine and profile.rank:
            try:
                kea_result = self.kea_engine.recommend_colleges(
                    rank=profile.rank,
                    category=profile.category,
                    branch=profile.preferred_branches[0] if profile.preferred_branches else "CSE",
                    rural_quota=profile.rural_quota,
                    kannada_medium=profile.kannada_medium,
                    hk_371j=profile.hk_371j,
                    hostel_required=profile.hostel_required,
                    budget=profile.budget or 0,
                )
                # Build probability map
                for rec in kea_result.get("recommendations", []):
                    cid = rec.get("college_id")
                    if cid:
                        admission_probs[cid] = rec.get("probability", 50.0)
                kea_results = kea_result
            except Exception as e:
                logger.warning(f"[Pipeline] KEA Engine failed: {e}")

        # ── Step 7: Ranking ────────────────────────────────────────────────
        if self.ranking_engine:
            ranked = self.ranking_engine.rank(filtered_colleges, profile, admission_probs)
            safe, moderate, ambitious = self.ranking_engine.classify(ranked, profile.rank)
        else:
            ranked = self._basic_rank(filtered_colleges, profile, admission_probs)
            safe, moderate, ambitious = self._basic_classify(ranked, profile.rank)

        # Limit results
        all_ranked = safe[:8] + moderate[:6] + ambitious[:4]
        top_results = all_ranked[:top_n]

        # Enrich with probability data
        for college in top_results:
            cid = college.get("college_id", "")
            if cid in admission_probs:
                college["admission_probability"] = round(admission_probs[cid], 1)

        # ── Step 8: Scholarship Check ──────────────────────────────────────
        scholarship_results = self.scholarship_engine.check_eligibility(profile)
        scholarship_summary = self.scholarship_engine.get_total_benefit(scholarship_results)

        # ── Step 9: Hostel Data ────────────────────────────────────────────
        hostel_data = []
        if profile.hostel_required:
            hostel_data = self._get_hostel_data([c.get("college_id") for c in top_results])

        # ── Step 10: Build final result ────────────────────────────────────
        result.update({
            "success": True,
            "recommendations": top_results,
            "safe": [self._college_summary(c) for c in safe[:8]],
            "moderate": [self._college_summary(c) for c in moderate[:6]],
            "ambitious": [self._college_summary(c) for c in ambitious[:4]],
            "total_eligible": len(filtered_colleges),
            "scholarships": {
                "eligible": [self._scholarship_summary(s) for s in scholarship_results if s.eligibility_met],
                "ineligible": [self._scholarship_summary(s) for s in scholarship_results if not s.eligibility_met],
                "summary": scholarship_summary,
            },
            "hostels": hostel_data,
            "kea_data": kea_results,
            "execution_ms": int((time.time() - start) * 1000),
        })

        return result

    def run_scholarship_check(self, profile: StudentProfile) -> Dict[str, Any]:
        """Run only the scholarship eligibility check."""
        results = self.scholarship_engine.check_eligibility(profile)
        summary = self.scholarship_engine.get_total_benefit(results)
        return {
            "success": True,
            "student_profile": profile.to_dict(),
            "scholarships": {
                "eligible": [self._scholarship_summary(s) for s in results if s.eligibility_met],
                "ineligible": [self._scholarship_summary(s) for s in results if not s.eligibility_met],
                "all": [s.__dict__ for s in results],
                "summary": summary,
            }
        }

    def run_comparison(self, college_ids: List[str], profile: Optional[StudentProfile] = None) -> Dict[str, Any]:
        """Compare specific colleges side-by-side."""
        all_colleges = self._get_all_colleges()
        id_set = set(college_ids)
        selected = [c for c in all_colleges if c.get("college_id") in id_set]

        if not selected:
            return {"success": False, "error": "Colleges not found"}

        comparison = []
        for college in selected:
            prob = 50.0
            if profile and self.kea_engine and profile.rank:
                try:
                    sim = self.kea_engine.simulate_single(
                        rank=profile.rank,
                        category=profile.category,
                        college_id=college["college_id"],
                        branch=college.get("branches", ["CSE"])[0],
                    )
                    prob = sim.get("probability", 50.0)
                except Exception:
                    pass

            comparison.append({
                "college_id": college.get("college_id"),
                "name": college.get("name"),
                "location": college.get("location"),
                "type": college.get("type"),
                "naac_grade": college.get("naac_grade"),
                "nba_accredited": college.get("nba_accredited"),
                "branches": college.get("branches", []),
                "annual_fee": college.get("annual_fee"),
                "hostel_available": college.get("hostel_available"),
                "placement_avg_lpa": college.get("placement_avg_lpa"),
                "highest_package_lpa": college.get("highest_package_lpa"),
                "established": college.get("established"),
                "total_seats": college.get("total_seats"),
                "admission_probability": round(prob, 1),
                "cutoff_2024": college.get("cutoffs", {}).get("2024", {}),
            })

        return {
            "success": True,
            "colleges": comparison,
            "metrics": [
                "annual_fee", "placement_avg_lpa", "hostel_available",
                "naac_grade", "admission_probability", "total_seats"
            ]
        }

    # ══════════════════════════════════════════════════════════════════════════
    # CONTEXT BUILDER FOR LLM (The LLM gets ONLY this — no raw data)
    # ══════════════════════════════════════════════════════════════════════════

    def build_llm_context(self, pipeline_result: Dict[str, Any]) -> str:
        """
        Build the context block that the LLM receives.
        
        CRITICAL: The LLM receives only pre-computed results.
        It CANNOT modify or override any values in this context.
        Its ONLY job is to explain these results in natural language.
        """
        if not pipeline_result.get("success"):
            error = pipeline_result.get("error_message", "Pipeline error")
            return f"[PIPELINE STATUS: INCOMPLETE]\n{error}"

        profile = pipeline_result.get("student_profile", {})
        safe = pipeline_result.get("safe", [])
        moderate = pipeline_result.get("moderate", [])
        ambitious = pipeline_result.get("ambitious", [])
        scholarships = pipeline_result.get("scholarships", {})

        ctx = [
            "=== COUNSELLING ENGINE RESULTS ===",
            f"[These values are FINAL. Do NOT modify, recalculate, or invent any numbers.]\n",
            f"STUDENT PROFILE:",
            f"  Rank: {profile.get('rank')} | Category: {profile.get('category')} | "
            f"Branch: {', '.join(profile.get('preferred_branches', []))}",
            f"  Location: {', '.join(profile.get('preferred_locations', [])) or 'Any'}",
            f"  Budget: ₹{profile.get('budget', 0):,}/year" if profile.get('budget') else "  Budget: Not specified",
            f"  Hostel Required: {'Yes' if profile.get('hostel_required') else 'No'}",
            "",
            f"ELIGIBLE COLLEGES: {pipeline_result.get('total_eligible', 0)} found",
            "",
        ]

        if safe:
            ctx.append("SAFE OPTIONS (High probability of admission):")
            for c in safe[:5]:
                ctx.append(
                    f"  ✅ {c['name']} ({c['location']}) — "
                    f"{c.get('admission_probability', '~'):.0f}% chance | "
                    f"Fee: ₹{c.get('annual_fee_gm', 0):,}"
                )
            ctx.append("")

        if moderate:
            ctx.append("MODERATE OPTIONS (Competitive but achievable):")
            for c in moderate[:4]:
                ctx.append(
                    f"  🎯 {c['name']} ({c['location']}) — "
                    f"{c.get('admission_probability', '~'):.0f}% chance"
                )
            ctx.append("")

        if ambitious:
            ctx.append("AMBITIOUS OPTIONS (Stretch choices):")
            for c in ambitious[:3]:
                ctx.append(
                    f"  🌟 {c['name']} ({c['location']}) — "
                    f"{c.get('admission_probability', '~'):.0f}% chance"
                )
            ctx.append("")

        eligible_scholarships = scholarships.get("eligible", [])
        if eligible_scholarships:
            ctx.append("SCHOLARSHIPS YOU ARE ELIGIBLE FOR:")
            for s in eligible_scholarships[:4]:
                ctx.append(f"  💰 {s['name']} — {s['amount']} ({s['portal']})")
            ctx.append("")

        ctx.append("=== END COUNSELLING RESULTS ===")
        ctx.append("\n[INSTRUCTION: Explain the above results clearly. Do NOT add or change any numbers, college names, or probabilities.]")

        return "\n".join(ctx)

    # ══════════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _get_all_colleges(self) -> List[Dict]:
        """Load all colleges from the JSON database."""
        if self.json_data:
            try:
                return self.json_data.get_all_colleges()
            except Exception:
                pass

        # Fallback: load from file
        data_dir = os.path.join(LEGACY_DIR, "..", "data")
        path = os.path.join(data_dir, "Production_Ready_Colleges.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[Pipeline] Cannot load college data: {e}")
            return []

    def _get_hostel_data(self, college_ids: List[str]) -> List[Dict]:
        """Get hostel data for recommended colleges only."""
        if not college_ids:
            return []

        all_colleges = self._get_all_colleges()
        id_set = set(college_ids)

        hostels = []
        for c in all_colleges:
            if c.get("college_id") in id_set and c.get("hostel_available"):
                hostel_info = c.get("hostel_details", {})
                hostels.append({
                    "college_id": c.get("college_id"),
                    "college_name": c.get("name"),
                    "hostel_available": True,
                    "boys_hostel": hostel_info.get("boys_hostel", True),
                    "girls_hostel": hostel_info.get("girls_hostel", False),
                    "hostel_fee_annual": hostel_info.get("annual_fee"),
                    "mess_available": hostel_info.get("mess_available", True),
                    "wifi": hostel_info.get("wifi", False),
                })

        return hostels

    def _basic_filter(self, colleges: List[Dict], profile: StudentProfile) -> List[Dict]:
        """Basic filtering when ConstraintFilter is not available."""
        result = colleges

        if profile.preferred_branches:
            branches = {b.upper() for b in profile.preferred_branches}
            result = [
                c for c in result
                if any(b.upper() in branches for b in c.get("branches", []))
            ]

        if profile.preferred_locations:
            locs = [l.lower() for l in profile.preferred_locations]
            result = [
                c for c in result
                if any(loc in (c.get("location") or "").lower() for loc in locs)
            ]

        if profile.budget:
            result = [
                c for c in result
                if self._fee_within_budget(c, profile.budget, profile.fee_category_key)
            ]

        if profile.hostel_required:
            result = [c for c in result if c.get("hostel_available")]

        return result

    def _fee_within_budget(self, college: Dict, budget: int, fee_key: str) -> bool:
        fee_data = college.get("annual_fee", {})
        if isinstance(fee_data, dict):
            fee = fee_data.get(fee_key) or fee_data.get("gm")
        elif isinstance(fee_data, (int, float)):
            fee = fee_data
        else:
            return True  # Unknown — don't exclude
        if fee is None:
            return True
        return int(fee) <= budget

    def _basic_rank(self, colleges: List[Dict], profile: StudentProfile, probs: Dict) -> List[Dict]:
        """Basic ranking by probability then fee."""
        for c in colleges:
            cid = c.get("college_id", "")
            c["recommendation_score"] = probs.get(cid, 50.0)
        colleges.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return colleges

    def _basic_classify(self, colleges: List[Dict], rank: int) -> Tuple[List, List, List]:
        """Classify colleges into safe/moderate/ambitious."""
        safe, moderate, ambitious = [], [], []
        for c in colleges:
            cutoff = c.get("cutoff_rank", 0) or c.get("effective_cutoff", 0)
            if cutoff == 0:
                ambitious.append(c)
                continue
            ratio = rank / max(cutoff, 1)
            if ratio <= 0.80:
                c["admission_tier"] = "Safe"
                safe.append(c)
            elif ratio <= 1.10:
                c["admission_tier"] = "Moderate"
                moderate.append(c)
            else:
                c["admission_tier"] = "Ambitious"
                ambitious.append(c)
        return safe, moderate, ambitious

    def _college_summary(self, college: Dict) -> Dict[str, Any]:
        """Compact college summary for API response."""
        fee_data = college.get("annual_fee", {})
        fee_gm = (
            fee_data.get("gm", 0) if isinstance(fee_data, dict)
            else (fee_data if isinstance(fee_data, (int, float)) else 0)
        )
        return {
            "college_id": college.get("college_id"),
            "name": college.get("name"),
            "location": college.get("location"),
            "type": college.get("type"),
            "naac_grade": college.get("naac_grade"),
            "branches": college.get("branches", []),
            "annual_fee_gm": fee_gm,
            "hostel_available": college.get("hostel_available", False),
            "placement_avg_lpa": college.get("placement_avg_lpa"),
            "admission_probability": college.get("admission_probability", 50.0),
            "admission_tier": college.get("admission_tier", "Unknown"),
            "recommendation_score": college.get("recommendation_score", 0),
            "sub_scores": college.get("sub_scores", {}),
            "cutoff_rank": college.get("cutoff_rank"),
        }

    def _scholarship_summary(self, s) -> Dict[str, Any]:
        return {
            "name": s.name,
            "authority": s.authority,
            "amount": s.amount,
            "amount_inr": s.amount_inr,
            "eligibility_met": s.eligibility_met,
            "reasons": s.eligibility_reasons if s.eligibility_met else s.ineligibility_reasons,
            "portal": s.application_portal,
            "url": s.official_url,
            "coverage": s.coverage,
            "deadlines": s.deadlines,
            "documents": s.required_documents,
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
_pipeline: Optional[CounsellingPipeline] = None


def get_pipeline() -> CounsellingPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = CounsellingPipeline()
    return _pipeline
