# ==============================================================================
# InsightRural — Recommendation Service (Orchestrator)
# ==============================================================================
# This is the central pipeline orchestrator. It chains:
#   Layer 1: Query Parser → StudentProfile
#   Layer 2: Counselling Engine → Eligible colleges (cutoff match)
#   Layer 3: Probability Engine → Admission probabilities (ML)
#   Layer 4: Constraint Filter → Hard-filtered colleges
#   Layer 5: Ranking Engine → Scored + classified results
#
# The LLM is NEVER involved in selection, filtering, or ranking.
# The LLM only receives the final results for explanation (Layer 8).
# ==============================================================================

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from models.schemas import (
    StudentProfile, CollegeRecommendation, RecommendationResponse,
    AdmissionProbability, ReservationResult, SubScores,
)
from engines.constraint_filter import ConstraintFilter
from engines.ranking_engine import RankingEngine
from engines.query_parser import QueryParser
from config import (
    KEA_RESERVATION_POLICY, OBC_RELAXATION, CATEGORY_TO_DATASET,
    TYPE_PRESTIGE, BRANCH_CODES,
)

logger = logging.getLogger("RecommendationService")


class RecommendationService:
    """
    Central orchestrator for the deterministic recommendation pipeline.
    
    Pipeline flow:
    StudentProfile → Data Lookup → Cutoff Match → Constraint Filter → Rank → Classify
    """

    def __init__(self, json_data_service):
        """
        Args:
            json_data_service: JSONDataService instance for database lookups.
        """
        self.data = json_data_service
        self.constraint_filter = ConstraintFilter(json_data_service)
        self.ranking_engine = RankingEngine()
        self.query_parser = QueryParser()

    def recommend(
        self,
        profile: StudentProfile,
        top_n: int = 15,
    ) -> RecommendationResponse:
        """
        Run the full recommendation pipeline.

        Args:
            profile: Validated StudentProfile.
            top_n: Maximum results per tier.

        Returns:
            RecommendationResponse with safe/moderate/ambitious lists.
        """
        start_time = time.time()
        total_checked = len(self.data.colleges)

        # ── Step 1: Find eligible colleges (cutoff-based) ─────────────
        eligible = self._find_eligible_colleges(profile)

        # ── Step 2: Apply reservation adjustments ─────────────────────
        eligible = self._apply_reservations(eligible, profile)

        # ── Step 3: Hard constraint filtering ─────────────────────────
        filtered, filter_report = self.constraint_filter.apply(eligible, profile)

        # ── Step 4: Score and rank ────────────────────────────────────
        scored = self.ranking_engine.rank(filtered, profile)

        # ── Step 5: Classify into tiers ───────────────────────────────
        safe, moderate, ambitious = self.ranking_engine.classify(
            scored, profile.rank
        )

        # ── Step 6: Limit results and build response ──────────────────
        safe = safe[:top_n]
        moderate = moderate[:top_n]
        ambitious = ambitious[:top_n]

        # Build CollegeRecommendation objects
        safe_recs = [self._build_recommendation(c, profile) for c in safe]
        moderate_recs = [self._build_recommendation(c, profile) for c in moderate]
        ambitious_recs = [self._build_recommendation(c, profile) for c in ambitious]

        # Build counselling guidance
        guidance = self._build_guidance(profile, safe_recs, moderate_recs, ambitious_recs)

        # Build option entry sequence (Dream → Realistic → Safe)
        option_sequence = self._build_option_sequence(
            safe_recs, moderate_recs, ambitious_recs
        )

        elapsed = time.time() - start_time
        logger.info(
            f"Recommendation pipeline completed in {elapsed:.2f}s: "
            f"{total_checked} checked → {len(eligible)} eligible → "
            f"{len(filtered)} filtered → "
            f"{len(safe_recs)}S/{len(moderate_recs)}M/{len(ambitious_recs)}A"
        )

        return RecommendationResponse(
            success=True,
            student_profile=profile.model_dump(),
            safe=safe_recs,
            moderate=moderate_recs,
            ambitious=ambitious_recs,
            total_eligible=len(filtered),
            total_colleges_checked=total_checked,
            option_entry_sequence=option_sequence,
            counselling_guidance=guidance,
            confidence={
                "overall": self._compute_confidence(profile, filter_report),
                "filter_report": filter_report,
            },
        )

    def recommend_from_chat(
        self,
        query: str,
        existing_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[RecommendationResponse, Dict[str, Any]]:
        """
        Chat-based recommendation: parse query, then run pipeline.

        Returns:
            Tuple of (RecommendationResponse, parse_metadata)
        """
        profile, metadata = self.query_parser.parse_chat_query(
            query, existing_profile
        )
        result = self.recommend(profile)
        return result, metadata

    # ══════════════════════════════════════════════════════════════════════════
    # Step 1: Find Eligible Colleges
    # ══════════════════════════════════════════════════════════════════════════

    def _find_eligible_colleges(
        self, profile: StudentProfile
    ) -> List[Dict[str, Any]]:
        """
        Find all colleges where the student could potentially get admission,
        based on cutoff data across ALL preferred branches.
        """
        eligible = []
        dataset_cat = profile.dataset_category

        for college in self.data.colleges:
            cutoff_data = college.get("cutoff_2024", {})
            if not cutoff_data:
                continue

            # Check each preferred branch
            for branch in profile.preferred_branches:
                branch_upper = branch.upper().replace(" ", "_")
                branch_cutoff = cutoff_data.get(branch_upper, {})

                if not isinstance(branch_cutoff, dict):
                    continue

                # Get cutoff for student's category
                cutoff_rank = branch_cutoff.get(dataset_cat)
                if cutoff_rank is None:
                    # Fallback to GM cutoff
                    cutoff_rank = branch_cutoff.get("GM")
                if cutoff_rank is None:
                    continue

                # Include if student's rank is within 1.5x of cutoff
                # (generous to include ambitious choices)
                if profile.rank <= cutoff_rank * 1.5:
                    entry = dict(college)
                    entry["matched_branch"] = branch_upper
                    entry["cutoff_rank"] = cutoff_rank
                    entry["gm_cutoff"] = branch_cutoff.get("GM")
                    entry["category_cutoff"] = cutoff_rank
                    entry["original_cutoff"] = cutoff_rank
                    eligible.append(entry)
                    break  # One match per college is enough

        return eligible

    # ══════════════════════════════════════════════════════════════════════════
    # Step 2: Apply Reservation Adjustments
    # ══════════════════════════════════════════════════════════════════════════

    def _apply_reservations(
        self, colleges: List[Dict[str, Any]], profile: StudentProfile
    ) -> List[Dict[str, Any]]:
        """
        Apply KEA reservation policy adjustments to cutoff ranks.
        Categories like SC/ST/OBC get relaxed cutoffs.
        """
        if profile.dataset_category == "GM" and not profile.hk_371j and not profile.rural_quota:
            # No reservation adjustment needed
            for c in colleges:
                c["effective_cutoff"] = c["cutoff_rank"]
                c["reservation_applied"] = False
                c["reservation_benefits"] = []
                c["reservation_multiplier"] = 1.0
            return colleges

        for college in colleges:
            original = college["cutoff_rank"]
            multiplier = 1.0
            benefits = []

            # Category relaxation
            cat = profile.category.upper()
            if cat in OBC_RELAXATION:
                multiplier *= OBC_RELAXATION[cat]
                benefits.append(f"{cat} reservation ({OBC_RELAXATION[cat]*100:.0f}% relaxation)")
            elif cat in ("SC", "ST"):
                multiplier *= 1.30  # 30% relaxation for SC/ST
                benefits.append(f"{cat} reservation (30% cutoff relaxation)")

            # HK 371J
            if profile.hk_371j:
                multiplier *= 1.08
                benefits.append("Hyderabad-Karnataka 371(J) (8% relaxation)")

            # Rural quota
            if profile.rural_quota:
                multiplier *= 1.05
                benefits.append("Rural Quota (5% relaxation)")

            effective = int(original * multiplier)
            college["effective_cutoff"] = effective
            college["cutoff_rank"] = effective  # Use effective for downstream
            college["original_cutoff"] = original
            college["reservation_applied"] = len(benefits) > 0
            college["reservation_benefits"] = benefits
            college["reservation_multiplier"] = multiplier

        return colleges

    # ══════════════════════════════════════════════════════════════════════════
    # Build Response Objects
    # ══════════════════════════════════════════════════════════════════════════

    def _build_recommendation(
        self, college: Dict[str, Any], profile: StudentProfile
    ) -> CollegeRecommendation:
        """Convert a scored college dict into a CollegeRecommendation."""

        sub = college.get("sub_scores", {})
        tier = college.get("admission_tier", "Moderate")

        # Admission probability from sub-scores
        admission_prob = sub.get("admission_probability", 50.0)
        if tier == "Safe":
            pred_round = "Round 1 or 2"
            conf_label = "High"
        elif tier == "Moderate":
            pred_round = "Round 2 or 3"
            conf_label = "Good"
        else:
            pred_round = "Round 3 or later"
            conf_label = "Low"

        # Fee extraction
        fee_data = college.get("annual_fee", {})
        fee_key = profile.fee_category_key
        if isinstance(fee_data, dict):
            annual_fee = fee_data.get(fee_key) or fee_data.get("gm", 0)
            if not isinstance(annual_fee, (int, float)):
                annual_fee = 0
        elif isinstance(fee_data, (int, float)):
            annual_fee = int(fee_data)
        else:
            annual_fee = 0

        # Build reason text
        reason = college.get("tier_reason", "")
        if not reason:
            reason = f"Recommended based on your rank ({profile.rank}) and preferences"

        col_name = college.get("name") or college.get("college_name", "Unknown")
        loc_val = college.get("location", "Unknown")
        if isinstance(loc_val, dict):
            col_loc = loc_val.get("district") or loc_val.get("city") or " ".join(str(v) for v in loc_val.values() if isinstance(v, str)) or "Karnataka"
        else:
            col_loc = str(loc_val or "Unknown")

        matched_br = college.get("matched_branch", profile.preferred_branches[0])
        trends = college.get("cutoff_trends", {})
        hist_cutoffs = {}
        if isinstance(trends, dict):
            for yr, yr_data in trends.items():
                if isinstance(yr_data, dict):
                    br_data = yr_data.get(matched_br, {})
                    if isinstance(br_data, dict):
                        val = br_data.get(profile.dataset_category) or br_data.get("GM")
                        if isinstance(val, (int, float)):
                            hist_cutoffs[str(yr)] = int(val)
                    elif isinstance(br_data, (int, float)):
                        hist_cutoffs[str(yr)] = int(br_data)
                elif isinstance(yr_data, (int, float)):
                    hist_cutoffs[str(yr)] = int(yr_data)

        return CollegeRecommendation(
            college_id=college.get("college_id", ""),
            college_name=col_name,
            location=col_loc,
            college_type=college.get("type", "Unknown"),
            branch=college.get("matched_branch", profile.preferred_branches[0]),
            cutoff_rank=college.get("cutoff_rank", 0),
            original_cutoff=college.get("original_cutoff", 0),
            gm_cutoff=college.get("gm_cutoff"),
            category_cutoff=college.get("category_cutoff"),
            recommendation_score=college.get("recommendation_score", 50),
            sub_scores=SubScores(
                admission_probability=sub.get("admission_probability", 50),
                placement_score=sub.get("placement_score", 40),
                accreditation_score=sub.get("accreditation_score", 50),
                hostel_score=sub.get("hostel_score", 20),
                fee_score=sub.get("fee_score", 50),
                location_score=sub.get("location_score", 75),
            ),
            admission=AdmissionProbability(
                probability=admission_prob,
                tier=tier,
                predicted_round=pred_round,
                confidence_score=int(admission_prob * 0.8),
                confidence_label=conf_label,
            ),
            reservation=ReservationResult(
                effective_cutoff=college.get("cutoff_rank", 0),
                original_cutoff=college.get("original_cutoff", 0),
                multiplier=college.get("reservation_multiplier", 1.0),
                benefits=college.get("reservation_benefits", []),
                has_benefit=college.get("reservation_applied", False),
            ),
            annual_fee=int(annual_fee),
            four_year_cost=int(annual_fee) * 4,
            hostel_available=college.get("hostel_available", False),
            naac_grade=college.get("naac_grade"),
            placement_avg_lpa=college.get("placement_avg_lpa"),
            placement_highest_lpa=college.get("placement_highest_lpa"),
            trend_direction=college.get("trend_direction", "stable"),
            historical_cutoffs=hist_cutoffs,
            reason=reason,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Counselling Guidance
    # ══════════════════════════════════════════════════════════════════════════

    def _build_guidance(
        self,
        profile: StudentProfile,
        safe: List[CollegeRecommendation],
        moderate: List[CollegeRecommendation],
        ambitious: List[CollegeRecommendation],
    ) -> Dict[str, Any]:
        """Build counselling guidance based on results."""

        guidance = {
            "total_options": len(safe) + len(moderate) + len(ambitious),
            "risk_level": "Low",
            "strategy": "",
            "warnings": [],
            "tips": [],
        }

        if not safe and not moderate:
            guidance["risk_level"] = "High"
            guidance["strategy"] = (
                "Your profile is ambitious for the selected constraints. "
                "Consider broadening your branch or location preferences."
            )
            guidance["warnings"].append(
                "No safe or moderate options found. Review your constraints."
            )
        elif len(safe) >= 5:
            guidance["risk_level"] = "Low"
            guidance["strategy"] = (
                "You have strong options. Focus on college quality, "
                "placements, and campus culture to make your choice."
            )
        elif len(safe) >= 2:
            guidance["risk_level"] = "Medium"
            guidance["strategy"] = (
                "You have a few safe options. Include some moderate choices "
                "in your preference list for better variety."
            )

        # Category-specific tips
        if profile.dataset_category in ("SC", "ST"):
            guidance["tips"].append(
                "As an SC/ST student, apply for Post-Matric Scholarship "
                "and check BCM hostel availability."
            )
        if profile.income_lakhs and profile.income_lakhs <= 4.5:
            guidance["tips"].append(
                "You may qualify for CISS (Central Interest Subsidy Scheme) "
                "— government pays your education loan interest."
            )
        if profile.hk_371j:
            guidance["tips"].append(
                "Your HK 371(J) reservation gives you 8% additional "
                "cutoff relaxation."
            )

        return guidance

    def _build_option_sequence(
        self,
        safe: List[CollegeRecommendation],
        moderate: List[CollegeRecommendation],
        ambitious: List[CollegeRecommendation],
    ) -> List[Dict[str, Any]]:
        """
        Build KEA option entry sequence (Dream → Realistic → Safe).
        This is the recommended order for filling choices.
        """
        sequence = []
        order = 1

        # Dream choices first (ambitious, top scored)
        for c in ambitious[:3]:
            sequence.append({
                "order": order,
                "college_name": c.college_name,
                "branch": c.branch,
                "location": c.location,
                "tier": "🎯 Dream",
                "recommendation_score": c.recommendation_score,
                "cutoff": c.cutoff_rank,
            })
            order += 1

        # Realistic choices (moderate)
        for c in moderate[:5]:
            sequence.append({
                "order": order,
                "college_name": c.college_name,
                "branch": c.branch,
                "location": c.location,
                "tier": "⚠️ Realistic",
                "recommendation_score": c.recommendation_score,
                "cutoff": c.cutoff_rank,
            })
            order += 1

        # Safe choices
        for c in safe[:7]:
            sequence.append({
                "order": order,
                "college_name": c.college_name,
                "branch": c.branch,
                "location": c.location,
                "tier": "✅ Safe",
                "recommendation_score": c.recommendation_score,
                "cutoff": c.cutoff_rank,
            })
            order += 1

        return sequence

    def _compute_confidence(
        self, profile: StudentProfile, filter_report: Dict[str, Any]
    ) -> str:
        """
        Compute overall prediction confidence.
        NOT hardcoded — varies based on data quality.
        Fixes Problem #6.
        """
        score = 50  # Base

        # Boost for having a rank
        if profile.rank and profile.rank < 200000:
            score += 15

        # Boost for specific branch preference
        if len(profile.preferred_branches) <= 3:
            score += 10

        # Penalty for too many constraints reducing options
        filtered = filter_report.get("filtered_count", 0)
        original = filter_report.get("original_count", 1)
        retention = filtered / max(original, 1)

        if retention > 0.3:
            score += 15
        elif retention > 0.1:
            score += 5
        else:
            score -= 10  # Very few options → lower confidence

        # Category-specific data quality
        if profile.dataset_category != "GM":
            score -= 5  # Category-specific cutoffs may have less historical data

        if score >= 75:
            return "High"
        elif score >= 55:
            return "Good"
        elif score >= 35:
            return "Medium"
        else:
            return "Low"
