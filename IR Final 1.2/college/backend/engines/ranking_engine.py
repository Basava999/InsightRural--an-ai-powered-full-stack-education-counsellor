# ==============================================================================
# InsightRural — Layer 5: Ranking Engine
# ==============================================================================
# Weighted multi-criteria ranking of filtered colleges. Produces an explainable
# composite score with transparent sub-scores for each dimension.
#
# Weights:
#   40% Admission Probability
#   20% Placements
#   15% Accreditation (NAAC + NBA)
#   10% Hostel Quality
#   10% Fees (lower = better)
#   5%  Location Preference
# ==============================================================================

import logging
from typing import List, Dict, Any, Optional, Tuple

from config import NAAC_SCORE, RANKING_WEIGHTS

logger = logging.getLogger("RankingEngine")


class RankingEngine:
    """
    Weighted multi-criteria ranking engine.
    Produces transparent, explainable scores.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or RANKING_WEIGHTS

    def rank(
        self,
        colleges: List[Dict[str, Any]],
        profile: Any,  # StudentProfile
        admission_probs: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Score and rank colleges.

        Args:
            colleges: Filtered college list from constraint filter.
            profile: StudentProfile with preferences.
            admission_probs: Optional dict mapping college_id → probability.

        Returns:
            Sorted list of colleges with recommendation_score and sub_scores.
        """
        if not colleges:
            return []

        scored = []
        for college in colleges:
            sub_scores = self._compute_sub_scores(
                college, profile, admission_probs
            )
            composite = self._weighted_composite(sub_scores)

            college_copy = dict(college)
            college_copy["recommendation_score"] = round(composite)
            college_copy["sub_scores"] = sub_scores
            scored.append(college_copy)

        # Sort by composite score (descending)
        scored.sort(key=lambda x: x["recommendation_score"], reverse=True)

        return scored

    def classify(
        self,
        scored_colleges: List[Dict[str, Any]],
        rank: int,
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Classify scored colleges into SAFE / MODERATE / AMBITIOUS tiers
        based on cutoff vs student rank relationship.

        Returns:
            Tuple of (safe, moderate, ambitious) lists.
        """
        safe = []
        moderate = []
        ambitious = []

        for college in scored_colleges:
            cutoff = college.get("cutoff_rank") or college.get("effective_cutoff", 0)
            if cutoff == 0:
                ambitious.append(college)
                continue

            # Classification logic using rank-to-cutoff ratio
            # KCET rank: lower = better. Cutoff rank = the last admitted rank.
            # If student's rank < cutoff → easy admission (SAFE)
            # If student's rank ~ cutoff → moderate
            # If student's rank > cutoff → difficult (AMBITIOUS)
            ratio = rank / max(cutoff, 1)

            if ratio <= 0.80:
                # Student rank is 20%+ better than cutoff → SAFE
                college["admission_tier"] = "Safe"
                college["tier_reason"] = (
                    f"Your rank ({rank}) is well within the cutoff ({cutoff})"
                )
                safe.append(college)
            elif ratio <= 1.10:
                # Student rank is close to cutoff → MODERATE
                college["admission_tier"] = "Moderate"
                college["tier_reason"] = (
                    f"Your rank ({rank}) is near the cutoff ({cutoff}) — "
                    f"admission is competitive"
                )
                moderate.append(college)
            else:
                # Student rank exceeds cutoff → AMBITIOUS
                college["admission_tier"] = "Ambitious"
                college["tier_reason"] = (
                    f"Your rank ({rank}) exceeds the cutoff ({cutoff}) — "
                    f"this is a stretch choice"
                )
                ambitious.append(college)

        return safe, moderate, ambitious

    # ══════════════════════════════════════════════════════════════════════════
    # Sub-Score Computation
    # ══════════════════════════════════════════════════════════════════════════

    def _compute_sub_scores(
        self,
        college: Dict[str, Any],
        profile: Any,
        admission_probs: Optional[Dict[str, float]],
    ) -> Dict[str, float]:
        """Compute all sub-scores for a college."""

        return {
            "admission_probability": self._score_admission(
                college, profile, admission_probs
            ),
            "placement_score": self._score_placements(college),
            "accreditation_score": self._score_accreditation(college),
            "hostel_score": self._score_hostel(college),
            "fee_score": self._score_fees(college, profile),
            "location_score": self._score_location(college, profile),
        }

    def _weighted_composite(self, sub_scores: Dict[str, float]) -> float:
        """Compute weighted composite from sub-scores."""
        score = (
            sub_scores["admission_probability"] * self.weights["admission_probability"] +
            sub_scores["placement_score"] * self.weights["placements"] +
            sub_scores["accreditation_score"] * self.weights["accreditation"] +
            sub_scores["hostel_score"] * self.weights["hostel_quality"] +
            sub_scores["fee_score"] * self.weights["fees"] +
            sub_scores["location_score"] * self.weights["location_preference"]
        )
        return max(0.0, min(100.0, score))

    def _score_admission(
        self,
        college: Dict,
        profile: Any,
        admission_probs: Optional[Dict[str, float]],
    ) -> float:
        """Score based on admission probability or cutoff-rank comparison."""
        # If ML probabilities are available, use them
        if admission_probs:
            college_id = college.get("college_id", "")
            if college_id in admission_probs:
                return admission_probs[college_id]

        # Fallback: cutoff-rank ratio scoring
        cutoff = college.get("cutoff_rank") or college.get("effective_cutoff", 0)
        if cutoff == 0:
            return 30.0  # Unknown cutoff → low confidence score

        rank = profile.rank
        ratio = rank / max(cutoff, 1)

        if ratio <= 0.50:
            return 98.0  # Very strong match
        elif ratio <= 0.70:
            return 90.0
        elif ratio <= 0.85:
            return 78.0
        elif ratio <= 1.00:
            return 65.0
        elif ratio <= 1.15:
            return 45.0
        elif ratio <= 1.30:
            return 30.0
        else:
            return 15.0

    def _score_placements(self, college: Dict) -> float:
        """Score based on placement data."""
        avg_lpa = college.get("placement_avg_lpa")
        if avg_lpa is None:
            return 40.0  # No data → neutral score

        try:
            avg_lpa = float(avg_lpa)
        except (ValueError, TypeError):
            return 40.0

        # Scale: 0 LPA → 0 score, 15+ LPA → 100 score
        score = min(100.0, (avg_lpa / 15.0) * 100.0)
        return max(0.0, score)

    def _score_accreditation(self, college: Dict) -> float:
        """Score based on NAAC grade and NBA accreditation."""
        naac = college.get("naac_grade", "N/A") or "N/A"
        naac_score = NAAC_SCORE.get(naac, 50)

        # NBA bonus
        nba = college.get("nba_accredited", False)
        if nba:
            naac_score = min(100, naac_score + 8)

        return float(naac_score)

    def _score_hostel(self, college: Dict) -> float:
        """Score hostel availability and quality."""
        if not college.get("hostel_available", False):
            return 20.0  # No hostel

        # Base score for having a hostel
        score = 70.0

        # Bonus for hostel details being available
        hostel_data = college.get("hostel_details", {})
        if hostel_data:
            if hostel_data.get("boys_hostel") and hostel_data.get("girls_hostel"):
                score += 10
            if hostel_data.get("mess_available"):
                score += 10
            if hostel_data.get("wifi"):
                score += 10

        return min(100.0, score)

    def _score_fees(self, college: Dict, profile: Any) -> float:
        """
        Score fees relative to budget. Lower fees = higher score.
        If no budget, score based on absolute fee level.
        """
        fee_data = college.get("annual_fee", {})
        fee_key = profile.fee_category_key

        # Extract the fee
        fee = None
        if isinstance(fee_data, dict):
            fee = fee_data.get(fee_key) or fee_data.get("gm")
        elif isinstance(fee_data, (int, float)):
            fee = fee_data

        if fee is None or not isinstance(fee, (int, float)):
            return 50.0  # Unknown fee → neutral

        if profile.budget and profile.budget > 0:
            # Score relative to budget: fee at 0% of budget = 100, at 100% = 40
            ratio = fee / profile.budget
            score = max(40.0, 100.0 - (ratio * 60.0))
            return min(100.0, score)
        else:
            # Absolute scoring: < ₹50K = great, > ₹2L = low
            if fee <= 50000:
                return 95.0
            elif fee <= 100000:
                return 80.0
            elif fee <= 150000:
                return 65.0
            elif fee <= 200000:
                return 50.0
            else:
                return 35.0

    def _score_location(self, college: Dict, profile: Any) -> float:
        """Score location preference match."""
        if not profile.preferred_locations:
            return 75.0  # No preference → neutral

        college_location = (college.get("location", "") or "").lower()
        college_district = (college.get("district", "") or "").lower()

        for loc in profile.preferred_locations:
            loc_lower = loc.lower().strip()

            # Handle city name equivalences
            search_terms = [loc_lower]
            equivalences = {
                "bangalore": ["bangalore", "bengaluru"],
                "bengaluru": ["bangalore", "bengaluru"],
                "mysore": ["mysore", "mysuru"],
                "mysuru": ["mysore", "mysuru"],
                "mangalore": ["mangalore", "mangaluru"],
                "mangaluru": ["mangalore", "mangaluru"],
            }
            if loc_lower in equivalences:
                search_terms = equivalences[loc_lower]

            for term in search_terms:
                if term in college_location or term in college_district:
                    return 95.0

        return 30.0  # Not in preferred location
