# ==============================================================================
# InsightRural — Full Recommendation Pipeline Integration Test
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from engines.query_parser import QueryParser
from engines.constraint_filter import ConstraintFilter
from engines.ranking_engine import RankingEngine
from models.schemas import StudentProfile


# ── Query Parser Tests ────────────────────────────────────────────────────────

class TestQueryParser:
    @pytest.fixture
    def parser(self):
        return QueryParser()

    def test_extract_rank(self, parser):
        profile, meta = parser.parse_chat_query("My KCET rank is 15000")
        assert profile.rank == 15000

    def test_extract_rank_inline(self, parser):
        profile, _ = parser.parse_chat_query("rank 8500 CSE Bangalore")
        assert profile.rank == 8500

    def test_extract_category(self, parser):
        profile, _ = parser.parse_chat_query("I am SC category with rank 20000")
        assert profile.category == "SC"

    def test_extract_branch(self, parser):
        profile, _ = parser.parse_chat_query("I want computer science, rank 5000")
        assert "CSE" in profile.preferred_branches

    def test_extract_location(self, parser):
        profile, _ = parser.parse_chat_query("colleges in Bangalore for rank 5000")
        assert profile.preferred_locations is not None
        assert any("Bangalore" in loc or "bangalore" in loc.lower()
                   for loc in profile.preferred_locations)

    def test_extract_budget(self, parser):
        profile, _ = parser.parse_chat_query("budget under 1 lakh, rank 5000")
        assert profile.budget == 100000

    def test_extract_hostel(self, parser):
        profile, _ = parser.parse_chat_query("need hostel, rank 10000 CSE")
        assert profile.hostel_required is True

    def test_extract_govt_college(self, parser):
        profile, _ = parser.parse_chat_query("government college only, rank 5000")
        assert profile.college_type == "Government"

    def test_extract_371j(self, parser):
        profile, _ = parser.parse_chat_query("I am from Hyderabad Karnataka 371j region")
        assert profile.hk_371j is True

    def test_merge_with_existing_profile(self, parser):
        existing = {"rank": 5000, "category": "SC"}
        profile, _ = parser.parse_chat_query(
            "show me Bangalore colleges", existing
        )
        assert profile.rank == 5000  # From existing
        assert profile.category == "SC"  # From existing
        assert profile.preferred_locations is not None  # From query

    def test_form_input(self, parser):
        data = {
            "kcet_rank": 15000,
            "category": "OBC",
            "branch": "CSE,ECE",
            "location": "Bangalore",
            "budget": 100000,
            "hostel_required": True,
        }
        profile = parser.parse_form_input(data)
        assert profile.rank == 15000
        assert profile.category == "OBC"
        assert "CSE" in profile.preferred_branches
        assert profile.budget == 100000
        assert profile.hostel_required is True

    def test_intent_detection(self, parser):
        assert parser.detect_intent("best college for rank 5000 CSE") == "recommendation"
        assert parser.detect_intent("what scholarships am I eligible for") == "scholarship"
        assert parser.detect_intent("education loan from SBI") == "loan"
        assert parser.detect_intent("hostel facility at RVCE") == "hostel"
        assert parser.detect_intent("fee structure of BMSCE") == "fee"
        assert parser.detect_intent("KEA counseling process steps") == "counseling"
        assert parser.detect_intent("compare RVCE vs BMSCE") == "comparison"


# ── Ranking Engine Tests ──────────────────────────────────────────────────────

class TestRankingEngine:
    @pytest.fixture
    def engine(self):
        return RankingEngine()

    def test_ranking_order(self, engine):
        """Higher scored colleges should appear first."""
        colleges = [
            {"college_id": "A", "name": "Bad College", "location": "X", "type": "Private",
             "branches": ["CSE"], "hostel_available": False,
             "annual_fee": {"gm": 200000}, "naac_grade": "B",
             "placement_avg_lpa": 3.0, "cutoff_rank": 50000},
            {"college_id": "B", "name": "Good College", "location": "Bangalore", "type": "Government",
             "branches": ["CSE"], "hostel_available": True,
             "annual_fee": {"gm": 50000}, "naac_grade": "A++",
             "placement_avg_lpa": 12.0, "cutoff_rank": 8000},
        ]
        profile = StudentProfile(rank=5000, preferred_locations=["Bangalore"])

        scored = engine.rank(colleges, profile)
        assert scored[0]["college_id"] == "B", "Better college should rank first"

    def test_tier_classification(self, engine):
        """Verify tier classification logic."""
        colleges = [
            {"college_id": "SAFE", "cutoff_rank": 10000,
             "sub_scores": {"admission_probability": 90, "placement_score": 60,
                           "accreditation_score": 70, "hostel_score": 50,
                           "fee_score": 60, "location_score": 75}},
            {"college_id": "AMB", "cutoff_rank": 3000,
             "sub_scores": {"admission_probability": 30, "placement_score": 80,
                           "accreditation_score": 90, "hostel_score": 80,
                           "fee_score": 50, "location_score": 75}},
        ]
        safe, moderate, ambitious = engine.classify(colleges, rank=5000)

        safe_ids = [c["college_id"] for c in safe]
        amb_ids = [c["college_id"] for c in ambitious]

        assert "SAFE" in safe_ids, "Rank 5000 vs cutoff 10000 should be SAFE"
        assert "AMB" in amb_ids, "Rank 5000 vs cutoff 3000 should be AMBITIOUS"


# ── StudentProfile Schema Tests ───────────────────────────────────────────────

class TestStudentProfile:
    def test_category_normalization(self):
        p = StudentProfile(rank=5000, category="GENERAL")
        assert p.category == "GM"

    def test_branch_normalization_string(self):
        p = StudentProfile(rank=5000, preferred_branches="cse, ece")
        assert "CSE" in p.preferred_branches
        assert "ECE" in p.preferred_branches

    def test_dataset_category(self):
        p1 = StudentProfile(rank=5000, category="2A")
        assert p1.dataset_category == "OBC"

        p2 = StudentProfile(rank=5000, category="SC")
        assert p2.dataset_category == "SC"

    def test_fee_category_key(self):
        p1 = StudentProfile(rank=5000, category="SC")
        assert p1.fee_category_key == "sc_st"

        p2 = StudentProfile(rank=5000, category="GM")
        assert p2.fee_category_key == "gm"

        p3 = StudentProfile(rank=5000, category="2A")
        assert p3.fee_category_key == "obc"

    def test_location_none_normalization(self):
        p = StudentProfile(rank=5000, preferred_locations="")
        assert p.preferred_locations is None

        p2 = StudentProfile(rank=5000, preferred_locations=[])
        assert p2.preferred_locations is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
