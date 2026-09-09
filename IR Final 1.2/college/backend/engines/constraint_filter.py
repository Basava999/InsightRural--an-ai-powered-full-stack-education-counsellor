# ==============================================================================
# InsightRural — Layer 4: Hard Constraint Filtering Engine
# ==============================================================================
# This is the CRITICAL fix for Problems #2 (Bangalore→Haveri), #3 (budget
# ignored), and #4 (hostel mismatch).
#
# ARCHITECTURAL RULE:
# Hard constraints are NEVER relaxed. If a college fails ANY hard constraint,
# it is removed from the pipeline. The system does NOT suggest "close matches"
# that violate user constraints.
#
# This engine runs AFTER the counselling engine identifies eligible colleges
# and BEFORE the ranking engine scores them.
# ==============================================================================

import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("ConstraintFilter")


class ConstraintFilter:
    """
    Hard constraint filtering engine. Removes colleges that violate any
    user-specified constraint. Never relaxes constraints automatically.
    """

    def __init__(self, json_data_service=None):
        """
        Args:
            json_data_service: Optional reference to JSONDataService for
                              hostel/fee lookups. Can be None for standalone usage.
        """
        self.json_data_service = json_data_service

    def apply_budget(self, colleges: List[Dict[str, Any]], budget: int) -> List[Dict[str, Any]]:
        """Public wrapper for testing budget filtering."""
        if budget == 0:
            return colleges
        for c in colleges:
            if "fee" in c and "annual_fee" not in c:
                c["annual_fee"] = c["fee"]
        return self._filter_by_budget(colleges, budget, "gm")


    def apply_branch(self, colleges: List[Dict[str, Any]], branch: str) -> List[Dict[str, Any]]:
        """Public wrapper for testing branch filtering."""
        return self._filter_by_branch(colleges, [branch] if branch else [])

    def apply_location(self, colleges: List[Dict[str, Any]], location: str) -> List[Dict[str, Any]]:
        """Public wrapper for testing location filtering."""
        return self._filter_by_location(colleges, [location] if location else [])

    def apply_hostel(self, colleges: List[Dict[str, Any]], hostel_required: bool) -> List[Dict[str, Any]]:
        """Public wrapper for testing hostel filtering."""
        if hostel_required:
            return self._filter_by_hostel(colleges)
        return colleges


    def apply(
        self,
        colleges: List[Dict[str, Any]],
        profile: Any,  # StudentProfile
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply all hard constraints to the college list.

        Args:
            colleges: List of college dicts from the counselling engine.
                     Each must have: college_id, name, location, type,
                     branches, hostel_available, annual_fee (dict or int),
                     cutoff_2024, etc.
            profile: StudentProfile Pydantic model with user constraints.

        Returns:
            Tuple of (filtered_colleges, filter_report)
        """
        original_count = len(colleges)
        filtered = list(colleges)
        removed = {}

        # ── 1. Branch Constraint ──────────────────────────────────────────
        before = len(filtered)
        filtered = self._filter_by_branch(filtered, profile.preferred_branches)
        removed["branch"] = before - len(filtered)

        # ── 2. Location Constraint (Fixes Problem #2) ─────────────────────
        if profile.preferred_locations:
            before = len(filtered)
            filtered = self._filter_by_location(
                filtered, profile.preferred_locations
            )
            removed["location"] = before - len(filtered)

        # ── 3. Budget Constraint (Fixes Problem #3) ───────────────────────
        if profile.budget is not None and profile.budget > 0:
            before = len(filtered)
            filtered = self._filter_by_budget(
                filtered, profile.budget, profile.fee_category_key
            )
            removed["budget"] = before - len(filtered)

        # ── 4. Hostel Constraint (Fixes Problem #4) ───────────────────────
        if profile.hostel_required:
            before = len(filtered)
            filtered = self._filter_by_hostel(filtered)
            removed["hostel"] = before - len(filtered)

        # ── 5. College Type Constraint ────────────────────────────────────
        if profile.college_type and profile.college_type.lower() not in ("any", "all", ""):
            before = len(filtered)
            filtered = self._filter_by_type(filtered, profile.college_type)
            removed["college_type"] = before - len(filtered)

        # ── Generate Filter Report ────────────────────────────────────────
        report = {
            "original_count": original_count,
            "filtered_count": len(filtered),
            "removed_count": original_count - len(filtered),
            "removed_by_constraint": {
                k: v for k, v in removed.items() if v > 0
            },
            "constraints_applied": self._describe_constraints(profile),
        }

        if len(filtered) == 0 and original_count > 0:
            report["warning"] = (
                "No college in the current database satisfies all specified "
                "constraints. Consider relaxing one or more constraints."
            )
            logger.warning(
                f"All {original_count} colleges filtered out. "
                f"Constraints: {report['constraints_applied']}"
            )

        logger.info(
            f"Constraint filter: {original_count} → {len(filtered)} colleges "
            f"(removed: {report['removed_by_constraint']})"
        )

        return filtered, report

    # ══════════════════════════════════════════════════════════════════════════
    # Individual Filter Methods
    # ══════════════════════════════════════════════════════════════════════════

    def _filter_by_branch(
        self, colleges: List[Dict], branches: List[str]
    ) -> List[Dict]:
        """Keep only colleges offering at least one preferred branch."""
        if not branches:
            return colleges

        branches_upper = {b.upper().replace(" ", "_") for b in branches}

        result = []
        for college in colleges:
            college_branches = college.get("branches", [])
            college_branches_upper = set()
            for b in college_branches:
                if isinstance(b, dict):
                    if b.get("branch_code"):
                        college_branches_upper.add(str(b["branch_code"]).upper().replace(" ", "_"))
                    if b.get("branch_name"):
                        college_branches_upper.add(str(b["branch_name"]).upper().replace(" ", "_"))
                elif isinstance(b, str):
                    college_branches_upper.add(b.upper().replace(" ", "_"))

            if college.get("matched_branch"):
                college_branches_upper.add(str(college["matched_branch"]).upper().replace(" ", "_"))
            cutoff_dict = college.get("cutoff_2024")
            if isinstance(cutoff_dict, dict):
                for k in cutoff_dict.keys():
                    college_branches_upper.add(str(k).upper().replace(" ", "_"))

            if not college_branches_upper:
                continue

            # Check if any preferred branch is offered
            if branches_upper.intersection(college_branches_upper):
                result.append(college)

        return result

    def _filter_by_location(
        self, colleges: List[Dict], locations: List[str]
    ) -> List[Dict]:
        """
        HARD FILTER: Keep only colleges in the specified locations.
        Matches on city, district, or region (case-insensitive substring).

        This fixes Problem #2: "User asks for Bangalore → system shows Haveri"
        """
        if not locations:
            return colleges

        locations_lower = [loc.lower().strip() for loc in locations]

        result = []
        for college in colleges:
            loc_val = college.get("location", "")
            if isinstance(loc_val, dict):
                college_location = " ".join(str(v) for v in loc_val.values()).lower().strip()
            else:
                college_location = str(loc_val or "").lower().strip()

            dist_val = college.get("district", "")
            if isinstance(dist_val, dict):
                college_district = " ".join(str(v) for v in dist_val.values()).lower().strip()
            else:
                college_district = str(dist_val or "").lower().strip()

            city_val = college.get("city", "")
            if isinstance(city_val, dict):
                college_city = " ".join(str(v) for v in city_val.values()).lower().strip()
            else:
                college_city = str(city_val or "").lower().strip()

            # Check all location fields
            match = False
            for loc in locations_lower:
                # Handle Bangalore/Bengaluru equivalence
                search_terms = [loc]
                if loc in ("bangalore", "bengaluru"):
                    search_terms = ["bangalore", "bengaluru"]
                elif loc in ("mysore", "mysuru"):
                    search_terms = ["mysore", "mysuru"]
                elif loc in ("hubli", "hubballi"):
                    search_terms = ["hubli", "hubballi"]
                elif loc in ("dharwad", "dharwar"):
                    search_terms = ["dharwad", "dharwar"]
                elif loc in ("mangalore", "mangaluru"):
                    search_terms = ["mangalore", "mangaluru"]
                elif loc in ("belgaum", "belagavi"):
                    search_terms = ["belgaum", "belagavi"]
                elif loc in ("bellary", "ballari"):
                    search_terms = ["bellary", "ballari"]
                elif loc in ("gulbarga", "kalaburagi"):
                    search_terms = ["gulbarga", "kalaburagi"]

                for term in search_terms:
                    if (term in college_location or
                        term in college_district or
                        term in college_city):
                        match = True
                        break

                if match:
                    break

            if match:
                result.append(college)

        return result

    def _filter_by_budget(
        self, colleges: List[Dict], budget: int, fee_key: str
    ) -> List[Dict]:
        """
        HARD FILTER: Remove colleges whose annual fee exceeds budget.
        Uses the correct fee tier based on student's category.

        This fixes Problem #3: "Budget constraint ignored"
        """
        result = []
        for college in colleges:
            fee_data = college.get("annual_fee", {})

            if isinstance(fee_data, dict):
                # Structured fee: lookup by category
                fee = fee_data.get(fee_key)
                if fee is None:
                    # Fallback to GM fee
                    fee = fee_data.get("gm")
                if fee is None:
                    # Unknown fee — include by default (don't penalize missing data)
                    result.append(college)
                    continue

                if isinstance(fee, (int, float)):
                    if fee <= budget:
                        result.append(college)
                else:
                    # Fee is not numeric — include to be safe
                    result.append(college)

            elif isinstance(fee_data, (int, float)):
                # Simple numeric fee
                if fee_data <= budget:
                    result.append(college)

            else:
                # No fee data — include by default
                result.append(college)

        return result

    def _filter_by_hostel(self, colleges: List[Dict]) -> List[Dict]:
        """
        HARD FILTER: Keep only colleges with hostel facilities.

        This contributes to fixing Problem #4: "Hostel for wrong colleges"
        """
        return [
            c for c in colleges
            if c.get("hostel_available", False) is True
        ]

    def _filter_by_type(
        self, colleges: List[Dict], college_type: str
    ) -> List[Dict]:
        """Filter by college type (Government, Private, Aided, etc.)."""
        type_lower = college_type.lower().strip()

        result = []
        for college in colleges:
            col_type = (college.get("type", "") or "").lower()

            if type_lower in ("government", "govt"):
                if "government" in col_type and "aided" not in col_type:
                    result.append(college)
            elif type_lower in ("private", "pvt"):
                if "private" in col_type or "unaided" in col_type:
                    result.append(college)
            elif type_lower in ("aided", "government_aided"):
                if "aided" in col_type:
                    result.append(college)
            else:
                # Substring match as fallback
                if type_lower in col_type:
                    result.append(college)

        return result

    # ══════════════════════════════════════════════════════════════════════════
    # Utility
    # ══════════════════════════════════════════════════════════════════════════

    def _describe_constraints(self, profile) -> Dict[str, Any]:
        """Generate human-readable constraint description."""
        constraints = {}
        if profile.preferred_branches:
            constraints["branches"] = profile.preferred_branches
        if profile.preferred_locations:
            constraints["locations"] = profile.preferred_locations
        if profile.budget:
            constraints["budget"] = f"≤ ₹{profile.budget:,}/year"
        if profile.hostel_required:
            constraints["hostel"] = "Required"
        if profile.college_type:
            constraints["college_type"] = profile.college_type
        return constraints


# ── Hostel Filter for Post-Recommendation ────────────────────────────────────

def filter_hostel_to_recommended(
    hostel_results: List[Dict], recommended_college_ids: List[str]
) -> List[Dict]:
    """
    CRITICAL: Only return hostel information for colleges that were recommended.
    This prevents the mismatch where hostel data for unrelated colleges appears.
    
    This fixes Problem #4: "Hostel data for wrong colleges"
    """
    if not recommended_college_ids:
        return []

    recommended_ids_set = set(recommended_college_ids)

    return [
        h for h in hostel_results
        if h.get("college_id") in recommended_ids_set or
           h.get("hostel_id") in recommended_ids_set
    ]
