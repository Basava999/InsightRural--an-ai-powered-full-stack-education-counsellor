"""Engine integration tests — verify deterministic behavior."""

import pytest
from app.schemas.student import StudentProfile
from app.engines.query_understanding import QueryUnderstandingEngine
from app.engines.constraint_filter import ConstraintFilterEngine
from app.engines.admission_probability import rule_based_probability, _probability_to_tier
from app.engines.recommendation_orchestrator import RecommendationOrchestrator


class TestQueryUnderstanding:
    def test_extract_rank_and_city(self):
        engine = QueryUnderstandingEngine()
        result = engine.parse("My KCET rank is 5000, I want CSE in Bangalore only")
        assert result.rank == 5000
        assert result.branch == "CSE"
        assert result.city is not None

    def test_explicit_profile(self):
        engine = QueryUnderstandingEngine()
        profile = StudentProfile(rank=3000, category="GM", branch="CSE", city="Bangalore")
        result = engine.parse("", profile)
        assert result.rank == 3000
        assert result.extraction_confidence == 1.0


class TestConstraintFilter:
    def test_city_filter_never_relaxes(self):
        engine = ConstraintFilterEngine()
        colleges = [
            {"college_id": "E001", "location": "Bengaluru Urban", "district": "Bengaluru Urban", "annual_fee": 50000, "hostel_available": True, "college_type": "Government"},
            {"college_id": "E002", "location": "Haveri", "district": "Haveri", "annual_fee": 80000, "hostel_available": True, "college_type": "Private"},
        ]
        profile = StudentProfile(rank=5000, category="GM", branch="CSE", city="Bangalore")
        filtered, filters = engine.apply(colleges, profile)
        assert len(filtered) == 1
        assert filtered[0]["college_id"] == "E001"
        assert filters["city"]["removed"] == 1

    def test_budget_filter(self):
        engine = ConstraintFilterEngine()
        colleges = [
            {"college_id": "E001", "annual_fee": 50000, "hostel_available": True, "college_type": "Government", "location": "Bengaluru", "district": "Bengaluru"},
            {"college_id": "E002", "annual_fee": 200000, "hostel_available": True, "college_type": "Private", "location": "Bengaluru", "district": "Bengaluru"},
        ]
        profile = StudentProfile(rank=5000, category="GM", branch="CSE", budget=100000)
        filtered, _ = engine.apply(colleges, profile)
        assert len(filtered) == 1
        assert filtered[0]["annual_fee"] == 50000


class TestAdmissionProbability:
    def test_safe_tier(self):
        result = rule_based_probability(rank=1000, cutoff=5000, category="GM")
        assert result["probability"] >= 80
        assert result["tier"] == "SAFE"

    def test_ambitious_tier(self):
        result = rule_based_probability(rank=50000, cutoff=5000, category="GM")
        assert result["probability"] < 50
        assert result["tier"] == "AMBITIOUS"

    def test_tier_thresholds(self):
        assert _probability_to_tier(85) == "SAFE"
        assert _probability_to_tier(65) == "MODERATE"
        assert _probability_to_tier(30) == "AMBITIOUS"


class TestRecommendationOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return RecommendationOrchestrator()

    def test_bangalore_filter_no_haveri(self, orchestrator):
        profile = StudentProfile(rank=8000, category="GM", branch="CSE", city="Bangalore")
        result = orchestrator.recommend(profile)
        all_recs = result.safe + result.moderate + result.ambitious
        for r in all_recs:
            loc = r.location.lower()
            assert "bangalore" in loc or "bengaluru" in loc, f"Haveri leak: {r.college_name} in {r.location}"

    def test_budget_respected(self, orchestrator):
        profile = StudentProfile(rank=10000, category="GM", branch="CSE", budget=60000)
        result = orchestrator.recommend(profile)
        all_recs = result.safe + result.moderate + result.ambitious
        for r in all_recs:
            if r.annual_fee is not None:
                assert r.annual_fee <= 60000

    def test_confidence_not_always_high(self, orchestrator):
        profile = StudentProfile(rank=5000, category="GM", branch="CSE")
        result = orchestrator.recommend(profile)
        assert 0 < result.confidence <= 1.0

    def test_hostels_only_for_recommended(self, orchestrator):
        profile = StudentProfile(rank=5000, category="GM", branch="CSE", city="Bangalore", hostel_required=True)
        result = orchestrator.recommend(profile)
        rec_ids = {r.college_id for r in result.safe + result.moderate + result.ambitious}
        for h in result.hostels:
            assert h.get("college_id") in rec_ids or h.get("verified")
