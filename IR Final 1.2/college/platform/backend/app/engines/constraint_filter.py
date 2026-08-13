"""
Layer 4: Constraint Filtering Engine
Hard filters — constraints are NEVER relaxed automatically.
"""

import logging
from typing import Any, Dict, List, Optional

from app.schemas.student import StudentProfile

logger = logging.getLogger(__name__)

CITY_ALIASES = {
    "bangalore": ["bangalore", "bengaluru", "bengaluru urban", "bengaluru rural"],
    "mysore": ["mysore", "mysuru"],
    "mangalore": ["mangalore", "mangaluru"],
    "hubli": ["hubli", "hubballi"],
    "belgaum": ["belgaum", "belagavi"],
}


class ConstraintFilterEngine:
    """Apply hard constraints. Rejected colleges are removed, not downgraded."""

    def apply(
        self,
        colleges: List[Dict[str, Any]],
        profile: StudentProfile,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        filters_applied = {}
        filtered = colleges

        if profile.city:
            filtered, removed = self._filter_city(filtered, profile.city)
            filters_applied["city"] = {"value": profile.city, "removed": removed}

        if profile.district:
            filtered, removed = self._filter_district(filtered, profile.district)
            filters_applied["district"] = {"value": profile.district, "removed": removed}

        if profile.budget is not None and profile.budget > 0:
            filtered, removed = self._filter_budget(filtered, profile.budget)
            filters_applied["budget"] = {"value": profile.budget, "removed": removed}

        if profile.hostel_required:
            filtered, removed = self._filter_hostel(filtered)
            filters_applied["hostel_required"] = {"value": True, "removed": removed}

        if profile.college_type:
            filtered, removed = self._filter_college_type(filtered, profile.college_type)
            filters_applied["college_type"] = {"value": profile.college_type, "removed": removed}

        return filtered, filters_applied

    def _normalize_location(self, value: str) -> str:
        return value.lower().strip().replace("_", " ")

    def _location_matches(self, constraint: str, location: str, district: str) -> bool:
        c = self._normalize_location(constraint)
        loc = self._normalize_location(location)
        dist = self._normalize_location(district)

        if c in loc or c in dist:
            return True

        for canonical, aliases in CITY_ALIASES.items():
            if c in aliases or c == canonical:
                return any(a in loc or a in dist for a in aliases)

        return False

    def _filter_city(self, colleges: List[Dict], city: str) -> tuple:
        kept, removed = [], 0
        for c in colleges:
            if self._location_matches(city, c.get("location", ""), c.get("district", "")):
                kept.append(c)
            else:
                removed += 1
        return kept, removed

    def _filter_district(self, colleges: List[Dict], district: str) -> tuple:
        kept, removed = [], 0
        for c in colleges:
            if self._location_matches(district, c.get("district", ""), c.get("location", "")):
                kept.append(c)
            else:
                removed += 1
        return kept, removed

    def _filter_budget(self, colleges: List[Dict], budget: int) -> tuple:
        kept, removed = [], 0
        for c in colleges:
            fee = c.get("annual_fee")
            if fee is None:
                kept.append(c)
            elif isinstance(fee, (int, float)) and fee <= budget:
                kept.append(c)
            else:
                removed += 1
        return kept, removed

    def _filter_hostel(self, colleges: List[Dict]) -> tuple:
        kept = [c for c in colleges if c.get("hostel_available")]
        return kept, len(colleges) - len(kept)

    def _filter_college_type(self, colleges: List[Dict], college_type: str) -> tuple:
        ct = college_type.lower()
        kept, removed = [], 0
        for c in colleges:
            t = (c.get("college_type") or "").lower()
            if "government" in ct and "government" in t:
                kept.append(c)
            elif "private" in ct and ("private" in t or "unaided" in t or "deemed" in t):
                kept.append(c)
            elif ct in t:
                kept.append(c)
            else:
                removed += 1
        return kept, removed
