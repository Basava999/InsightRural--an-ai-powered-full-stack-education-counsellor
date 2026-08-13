"""
Layer 5: Ranking Engine
Weighted composite score for final ordering.
"""

from typing import Any, Dict, List, Optional

NAAC_SCORES = {
    "A++": 98, "A+": 90, "A": 82, "B++": 75, "B+": 68, "B": 60, "C": 45,
}

WEIGHTS = {
    "admission_probability": 0.40,
    "placements": 0.20,
    "accreditation": 0.15,
    "hostel_quality": 0.10,
    "fees": 0.10,
    "location": 0.05,
}


class RankingEngine:
    """Rank colleges by weighted composite score."""

    def rank(
        self,
        colleges: List[Dict[str, Any]],
        profile_location: Optional[str] = None,
        budget: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        for c in colleges:
            c["composite_score"] = self._compute_score(c, profile_location, budget)
            c["explanation"] = self._build_explanation(c, profile_location, budget)

        return sorted(colleges, key=lambda x: x["composite_score"], reverse=True)

    def _compute_score(
        self,
        college: Dict,
        profile_location: Optional[str],
        budget: Optional[int],
    ) -> float:
        prob = college.get("probability", 0)
        prob_score = (prob / 100) * 100 * WEIGHTS["admission_probability"]

        avg_lpa = college.get("placement_avg_lpa")
        if avg_lpa:
            placement_score = min(100, (float(avg_lpa) / 15.0) * 100) * WEIGHTS["placements"]
        else:
            placement_score = 25 * WEIGHTS["placements"]

        naac = college.get("naac_grade", "N/A")
        acc_score = (NAAC_SCORES.get(naac, 50) / 100) * 100 * WEIGHTS["accreditation"]

        hostel_score = (100 if college.get("hostel_available") else 20) * WEIGHTS["hostel_quality"]

        fee = college.get("annual_fee")
        if isinstance(fee, (int, float)) and budget and budget > 0:
            fee_ratio = 1 - min(1, fee / budget)
            fee_score = fee_ratio * 100 * WEIGHTS["fees"]
        elif isinstance(fee, (int, float)) and fee <= 50000:
            fee_score = 80 * WEIGHTS["fees"]
        else:
            fee_score = 40 * WEIGHTS["fees"]

        loc_score = 0
        if profile_location:
            loc = (college.get("location") or "").lower()
            dist = (college.get("district") or "").lower()
            pref = profile_location.lower()
            if pref in loc or pref in dist:
                loc_score = 100 * WEIGHTS["location"]

        return round(prob_score + placement_score + acc_score + hostel_score + fee_score + loc_score, 2)

    def _build_explanation(
        self,
        college: Dict,
        profile_location: Optional[str],
        budget: Optional[int],
    ) -> List[str]:
        reasons = []
        prob = college.get("probability", 0)
        tier = college.get("tier", "MODERATE")

        reasons.append(f"{tier} tier with {prob}% admission probability based on cutoff trends.")
        reasons.append(college.get("reason", "Rank compared against historical closing rank."))

        if college.get("placement_avg_lpa"):
            reasons.append(f"Average placement: {college['placement_avg_lpa']} LPA.")
        if college.get("naac_grade"):
            reasons.append(f"NAAC accreditation: {college['naac_grade']}.")
        if college.get("hostel_available"):
            reasons.append("Hostel facility available on campus.")
        if isinstance(college.get("annual_fee"), (int, float)):
            reasons.append(f"Annual tuition fee: ₹{college['annual_fee']:,.0f}.")
        if profile_location and profile_location.lower() in (college.get("location") or "").lower():
            reasons.append(f"Matches your preferred location: {profile_location}.")

        return reasons

    def bucket_by_tier(self, ranked: List[Dict]) -> Dict[str, List[Dict]]:
        return {
            "safe": [c for c in ranked if c.get("tier") == "SAFE"],
            "moderate": [c for c in ranked if c.get("tier") == "MODERATE"],
            "ambitious": [c for c in ranked if c.get("tier") == "AMBITIOUS"],
        }
