# ==============================================================================
# InsightRural — Constraint Filter Tests
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engines.constraint_filter import ConstraintFilter


class TestConstraintFilter:
    """Test hard constraint enforcement in the recommendation pipeline."""

    def setup_method(self):
        self.filter = ConstraintFilter()

    def test_budget_filter_excludes_expensive(self):
        """Colleges above budget are excluded."""
        colleges = [
            {"name": "Expensive College", "fee": 200000},
            {"name": "Cheap College", "fee": 50000},
        ]
        result = self.filter.apply_budget(colleges, budget=100000)
        assert all(c["fee"] <= 100000 for c in result)

    def test_budget_filter_zero_means_no_filter(self):
        """Budget of 0 should not filter anything."""
        colleges = [
            {"name": "College A", "fee": 200000},
            {"name": "College B", "fee": 50000},
        ]
        result = self.filter.apply_budget(colleges, budget=0)
        assert len(result) == len(colleges)

    def test_branch_filter(self):
        """Only colleges with matching branch are returned."""
        colleges = [
            {"name": "College A", "branches": ["CSE", "ECE"]},
            {"name": "College B", "branches": ["MECH", "CIVIL"]},
        ]
        result = self.filter.apply_branch(colleges, branch="CSE")
        assert len(result) == 1
        assert result[0]["name"] == "College A"

    def test_location_filter(self):
        """Location filter matches correctly."""
        colleges = [
            {"name": "College A", "location": "Bangalore"},
            {"name": "College B", "location": "Mysore"},
        ]
        result = self.filter.apply_location(colleges, location="Bangalore")
        assert len(result) == 1
        assert result[0]["name"] == "College A"

    def test_hostel_filter(self):
        """Hostel filter works."""
        colleges = [
            {"name": "College A", "hostel_available": True},
            {"name": "College B", "hostel_available": False},
        ]
        result = self.filter.apply_hostel(colleges, hostel_required=True)
        assert all(c["hostel_available"] for c in result)

    def test_empty_colleges_returns_empty(self):
        """Empty input returns empty output."""
        result = self.filter.apply_budget([], budget=100000)
        assert result == []

    def test_no_filter_returns_all(self):
        """When no constraints, all colleges pass."""
        colleges = [
            {"name": "A", "fee": 100000, "branches": ["CSE"], "location": "BLR", "hostel_available": True},
        ]
        result = self.filter.apply_budget(colleges, budget=0)
        assert len(result) == len(colleges)
