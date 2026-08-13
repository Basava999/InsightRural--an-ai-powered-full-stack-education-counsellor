"""
Layer 2: Counselling Engine
Deterministic KEA eligibility logic. No LLM.
"""

import logging
from typing import Any, Dict, List, Optional

from app.schemas.student import StudentProfile

logger = logging.getLogger(__name__)

KEA_RESERVATION = {
    "GM": 32, "SC": 15, "ST": 3, "CAT1": 4,
    "2A": 15, "2B": 4, "3A": 4, "3B": 5,
}

HK_DISTRICTS = {
    "bidar", "gulbarga", "kalaburagi", "yadgir", "raichur",
    "koppal", "bellary", "ballari", "vijayanagara", "bagalkot",
}

CATEGORY_MAP = {
    "GENERAL": "GM", "GEN": "GM", "OC": "GM", "UR": "GM",
    "OBC": "OBC", "2A": "OBC", "2B": "OBC", "3A": "OBC", "3B": "OBC",
    "CAT1": "OBC", "CAT-1": "OBC", "CATEGORY-1": "OBC",
    "SC": "SC", "ST": "ST", "EWS": "GM",
}

OBC_RELAXATION = {
    "OBC": 1.00, "2A": 1.12, "2B": 0.95, "3A": 0.95, "3B": 1.00, "CAT1": 0.90,
}


class CounsellingEngine:
    """Apply KEA reservation rules and return eligible college-branch combinations."""

    def __init__(self, data_service):
        self.data = data_service

    def normalize_category(self, category: str) -> str:
        return CATEGORY_MAP.get(category.upper().strip(), category.upper())

    def get_dataset_category(self, category: str) -> str:
        cat = self.normalize_category(category)
        if cat in ("SC", "ST"):
            return cat
        if cat == "OBC":
            return "OBC"
        return "GM"

    def apply_quota_benefits(self, profile: StudentProfile) -> Dict[str, Any]:
        benefits = []
        effective_category = profile.category.upper()

        if profile.rural:
            benefits.append({"quota": "RURAL", "benefit": "15% rural reservation within category"})
        if profile.kannada_medium:
            benefits.append({"quota": "KM", "benefit": "5% Kannada medium reservation"})
        if profile.hk_371j or (profile.district and profile.district.lower() in HK_DISTRICTS):
            benefits.append({"quota": "371J", "benefit": "8% Hyderabad-Karnataka reservation"})
        if profile.snq:
            benefits.append({"quota": "SNQ", "benefit": "Supernumerary quota for special cases"})

        return {
            "effective_category": effective_category,
            "dataset_category": self.get_dataset_category(effective_category),
            "quota_benefits": benefits,
        }

    def get_eligible_colleges(
        self,
        profile: StudentProfile,
        branch: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        branch = (branch or profile.branch).upper().replace(" ", "_")
        quota_info = self.apply_quota_benefits(profile)
        dataset_cat = quota_info["dataset_category"]
        obc_factor = OBC_RELAXATION.get(profile.category.upper(), 1.0)

        eligible = []
        colleges = self.data.get_all_colleges()

        for college in colleges:
            branches = college.get("branches", [])
            if branch not in branches:
                continue

            cutoff_2024 = college.get("cutoff_2024", {})
            branch_cutoff = cutoff_2024.get(branch, {})
            if not isinstance(branch_cutoff, dict):
                continue

            cutoff_rank = branch_cutoff.get(dataset_cat)
            if cutoff_rank is None:
                cutoff_rank = branch_cutoff.get("GM")
            if cutoff_rank is None:
                continue

            adjusted_cutoff = int(cutoff_rank * obc_factor) if dataset_cat == "OBC" else cutoff_rank

            fee = self._get_fee(college, dataset_cat)
            trends = college.get("cutoff_trends", {})

            eligible.append({
                "college_id": college.get("college_id"),
                "college_name": college.get("name"),
                "branch": branch,
                "location": college.get("location", ""),
                "district": college.get("district", college.get("location", "")),
                "college_type": college.get("type", "Unknown"),
                "cutoff_rank": adjusted_cutoff,
                "raw_cutoff_rank": cutoff_rank,
                "category": dataset_cat,
                "annual_fee": fee,
                "hostel_available": college.get("hostel_available", False),
                "placement_avg_lpa": college.get("placement_avg_lpa"),
                "placement_highest_lpa": college.get("placement_highest_lpa"),
                "naac_grade": college.get("naac_grade"),
                "nba_accredited": college.get("nba_accredited", False),
                "cutoff_trends": trends,
                "total_seats": college.get("total_seats", 0),
                "quota_benefits": quota_info["quota_benefits"],
                "data_completeness": self._compute_completeness(college, branch),
            })

        return eligible

    def _get_fee(self, college: Dict, category: str) -> Optional[float]:
        fee = college.get("annual_fee", {})
        if not fee:
            return None
        if category in ("SC", "ST"):
            return fee.get("sc_st", 0)
        if category == "OBC":
            return fee.get("obc")
        return fee.get("gm")

    def _compute_completeness(self, college: Dict, branch: str) -> float:
        score = 0.0
        checks = [
            college.get("cutoff_2024", {}).get(branch),
            college.get("annual_fee"),
            college.get("placement_avg_lpa") is not None,
            college.get("naac_grade"),
            college.get("location"),
        ]
        score = sum(1 for c in checks if c) / len(checks)
        trends = college.get("cutoff_trends", {})
        if len(trends) >= 3:
            score = min(1.0, score + 0.1)
        return round(score, 2)
