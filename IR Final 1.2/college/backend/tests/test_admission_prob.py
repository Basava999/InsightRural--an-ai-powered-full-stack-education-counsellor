# ==============================================================================
# InsightRural — Admission Probability Tests
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from admission_probability import calculate_admission_probability, normalize_category


class TestNormalizeCategory:
    """Test category normalization."""

    def test_gm_to_open(self):
        assert normalize_category("GM") == "OPEN"

    def test_general_to_open(self):
        assert normalize_category("GENERAL") == "OPEN"

    def test_gen_to_open(self):
        assert normalize_category("GEN") == "OPEN"

    def test_ur_to_open(self):
        assert normalize_category("UR") == "OPEN"

    def test_obc_to_obc_ncl(self):
        assert normalize_category("OBC") == "OBC-NCL"

    def test_sc_stays_sc(self):
        assert normalize_category("SC") == "SC"

    def test_st_stays_st(self):
        assert normalize_category("ST") == "ST"

    def test_none_defaults_to_open(self):
        assert normalize_category(None) == "OPEN"

    def test_empty_defaults_to_open(self):
        assert normalize_category("") == "OPEN"

    def test_case_insensitive(self):
        assert normalize_category("gm") == "OPEN"
        assert normalize_category("Sc") == "SC"


class TestAdmissionProbability:
    """Test probability calculation across different rank/cutoff ratios."""

    def test_safe_admission(self):
        """Rank much better than cutoff → high probability."""
        result = calculate_admission_probability(rank=3000, previous_cutoff=10000)
        assert result["probability"] >= 80
        assert result["admission_chance"] == "Safe"

    def test_moderate_admission(self):
        """Rank near cutoff → moderate probability."""
        result = calculate_admission_probability(rank=9000, previous_cutoff=10000)
        assert 30 <= result["probability"] <= 85
        # Could be Moderate or Safe depending on exact threshold

    def test_dream_admission(self):
        """Rank far above cutoff → low probability."""
        result = calculate_admission_probability(rank=50000, previous_cutoff=10000)
        assert result["probability"] <= 30
        assert result["admission_chance"] == "Dream"

    def test_exact_cutoff_match(self):
        """Rank equals cutoff → borderline."""
        result = calculate_admission_probability(rank=10000, previous_cutoff=10000)
        assert 40 <= result["probability"] <= 80

    def test_category_bonus_sc(self):
        """SC category gets probability bonus."""
        base = calculate_admission_probability(rank=10000, previous_cutoff=10000, category="OPEN")
        sc = calculate_admission_probability(rank=10000, previous_cutoff=10000, category="SC")
        assert sc["probability"] >= base["probability"]

    def test_category_bonus_obc(self):
        """OBC category gets probability bonus."""
        base = calculate_admission_probability(rank=10000, previous_cutoff=10000, category="OPEN")
        obc = calculate_admission_probability(rank=10000, previous_cutoff=10000, category="OBC")
        assert obc["probability"] >= base["probability"]

    def test_zero_rank_returns_dream(self):
        """Zero rank is invalid → Dream."""
        result = calculate_admission_probability(rank=0, previous_cutoff=10000)
        assert result["admission_chance"] == "Dream"

    def test_negative_rank_returns_dream(self):
        """Negative rank is invalid → Dream."""
        result = calculate_admission_probability(rank=-100, previous_cutoff=10000)
        assert result["admission_chance"] == "Dream"

    def test_string_rank_handled(self):
        """String rank gets converted."""
        result = calculate_admission_probability(rank="5000", previous_cutoff="10000")
        assert result["probability"] > 0

    def test_result_has_all_fields(self):
        """Result contains all expected fields."""
        result = calculate_admission_probability(rank=5000, previous_cutoff=10000)
        assert "probability" in result
        assert "admission_chance" in result
        assert "reason" in result
        assert "rank_gap" in result
        assert "rank_to_cutoff_ratio" in result

    def test_probability_bounded(self):
        """Probability is always between 1 and 99."""
        for rank in [1, 100, 1000, 10000, 100000]:
            result = calculate_admission_probability(rank=rank, previous_cutoff=10000)
            assert 1 <= result["probability"] <= 99

    def test_rank_gap_computed(self):
        """Rank gap = cutoff - rank."""
        result = calculate_admission_probability(rank=3000, previous_cutoff=10000)
        assert result["rank_gap"] == 7000

    def test_ratio_computed(self):
        """Ratio = rank / cutoff."""
        result = calculate_admission_probability(rank=5000, previous_cutoff=10000)
        assert result["rank_to_cutoff_ratio"] == 0.5
