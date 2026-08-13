"""
Unified data service — JSON-first with PostgreSQL-ready interface.
Reads from existing college/data/*.json files.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Failed to load %s: %s", path, e)
        return []


class DataService:
    """Priority-1 structured data access. Never hallucinates values."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self._load()

    def _load(self):
        self.colleges: List[Dict] = _load_json(self.data_dir / "Production_Ready_Colleges.json")
        self.cutoffs: List[Dict] = _load_json(self.data_dir / "cutoff_dataset.json")
        self.hostels: List[Dict] = _load_json(self.data_dir / "hostels.json")
        self.scholarships: List[Dict] = _load_json(self.data_dir / "scholarships.json")
        self.fees: List[Dict] = _load_json(self.data_dir / "Fee.json")
        self.counseling: Dict = _load_json(self.data_dir / "counseling_guide.json") or {}

        self._college_by_id = {c.get("college_id"): c for c in self.colleges if c.get("college_id")}
        self._hostel_by_college: Dict[str, List[Dict]] = {}
        for h in self.hostels:
            name = (h.get("college") or h.get("name") or "").lower().strip()
            if name:
                self._hostel_by_college.setdefault(name, []).append(h)

        logger.info(
            "DataService loaded: %d colleges, %d hostels, %d scholarships",
            len(self.colleges), len(self.hostels), len(self.scholarships),
        )

    def get_all_colleges(self) -> List[Dict]:
        return self.colleges

    def get_college_by_id(self, college_id: str) -> Optional[Dict]:
        return self._college_by_id.get(college_id)

    def find_college(self, query: str) -> Optional[Dict]:
        q = query.strip()
        if q.upper() in self._college_by_id:
            return self._college_by_id[q.upper()]
        q_lower = q.lower()
        for c in self.colleges:
            if q_lower in c.get("name", "").lower():
                return c
        return None

    def get_hostels_for_colleges(self, college_ids: List[str]) -> List[Dict]:
        """Return hostel data ONLY for specified recommended colleges."""
        results = []
        for cid in college_ids:
            college = self._college_by_id.get(cid)
            if not college:
                continue
            name = college.get("name", "").lower().strip()
            hostels = self._hostel_by_college.get(name, [])
            for h in hostels:
                results.append({
                    **h,
                    "college_id": cid,
                    "college_name": college.get("name"),
                    "verified": True,
                    "source": "official_database",
                })
            if not hostels and college.get("hostel_available"):
                results.append({
                    "college_id": cid,
                    "college_name": college.get("name"),
                    "hostel_available": True,
                    "details": "Hostel available — detailed fee data not in database.",
                    "verified": True,
                    "source": "college_profile",
                })
        return results

    def get_eligible_scholarships(
        self,
        category: Optional[str] = None,
        income: Optional[int] = None,
        gender: Optional[str] = None,
    ) -> List[Dict]:
        results = []
        for s in self.scholarships:
            elig = s.get("eligibility", {})
            if category:
                cats = [c.lower() for c in elig.get("category", [])]
                if cats and not any(
                    category.lower() in c or c in category.lower() or "all" in c
                    for c in cats
                ):
                    continue
            if income and elig.get("income_limit") and income > elig["income_limit"]:
                continue
            results.append({**s, "verified": True, "source": "official_database"})
        return results

    def get_cutoff_trends(self, college_id: str, branch: str, category: str) -> Dict:
        college = self._college_by_id.get(college_id)
        if not college:
            return {}
        trends = college.get("cutoff_trends", {})
        result = {}
        for year, data in trends.items():
            if isinstance(data, dict):
                branch_data = data.get(branch, data)
                if isinstance(branch_data, dict):
                    val = branch_data.get(category) or branch_data.get("GM")
                    if val:
                        result[year] = val
        return result

    def search_colleges(
        self,
        query: Optional[str] = None,
        city: Optional[str] = None,
        college_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        results = self.colleges
        if query:
            q = query.lower()
            results = [c for c in results if q in c.get("name", "").lower()]
        if city:
            c_lower = city.lower()
            results = [
                c for c in results
                if c_lower in (c.get("location") or "").lower()
                or c_lower in (c.get("district") or "").lower()
            ]
        if college_type:
            ct = college_type.lower()
            results = [c for c in results if ct in (c.get("type") or "").lower()]
        total = len(results)
        return {"total": total, "colleges": results[offset:offset + limit]}


@lru_cache
def get_data_service() -> DataService:
    return DataService()
