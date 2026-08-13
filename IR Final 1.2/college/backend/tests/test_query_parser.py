# ==============================================================================
# InsightRural — Query Parser Tests
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engines.query_parser import QueryParser


class TestQueryParser:
    """Test the regex-based intent extraction engine."""

    def setup_method(self):
        self.parser = QueryParser()

    def test_rank_extraction_simple(self):
        """Extract rank from simple statement."""
        result = self.parser.parse("My rank is 5000")
        assert result.get("rank") == 5000 or result.get("kcet_rank") == 5000

    def test_rank_extraction_with_text(self):
        """Extract rank from conversational text."""
        result = self.parser.parse("I got kcet rank 12500, what are my options?")
        rank = result.get("rank") or result.get("kcet_rank")
        assert rank == 12500

    def test_category_extraction_sc(self):
        """Detect SC category."""
        result = self.parser.parse("I am SC category with rank 8000")
        cat = result.get("category", "").upper()
        assert cat in ("SC", "SC/ST")

    def test_category_extraction_gm(self):
        """Detect general/GM category."""
        result = self.parser.parse("general category student rank 3000")
        cat = result.get("category", "").upper()
        assert cat in ("GM", "GENERAL", "OPEN", "GEN")

    def test_branch_extraction(self):
        """Detect preferred branch."""
        result = self.parser.parse("I want CSE in Bangalore")
        branch = result.get("branch") or result.get("preferred_branch", "")
        assert "CSE" in str(branch).upper() or "COMPUTER" in str(branch).upper()

    def test_location_extraction(self):
        """Detect location preference."""
        result = self.parser.parse("best colleges in Mysore for ECE")
        location = result.get("location", "") or result.get("city", "")
        assert "mysore" in str(location).lower() or "mysuru" in str(location).lower()

    def test_scholarship_intent(self):
        """Detect scholarship-related query."""
        result = self.parser.parse("What scholarships are available for SC students?")
        intent = result.get("intent", "")
        assert "scholarship" in str(intent).lower() or result.get("is_scholarship_query", False)

    def test_hostel_intent(self):
        """Detect hostel-related query."""
        result = self.parser.parse("Does RV College have hostel facility?")
        intent = result.get("intent", "")
        assert "hostel" in str(intent).lower() or result.get("is_hostel_query", False)

    def test_empty_query(self):
        """Empty query doesn't crash."""
        result = self.parser.parse("")
        assert isinstance(result, dict)

    def test_returns_dict(self):
        """Parser always returns a dict."""
        result = self.parser.parse("random text with no intent")
        assert isinstance(result, dict)
