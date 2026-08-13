"""
Recommendation Orchestrator — chains all deterministic layers.
LLM is NOT involved in college selection.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.schemas.student import (
    CollegeRecommendation,
    RecommendationResponse,
    StudentProfile,
)
from app.engines.query_understanding import QueryUnderstandingEngine
from app.engines.counselling_engine import CounsellingEngine
from app.engines.admission_probability import AdmissionProbabilityEngine
from app.engines.constraint_filter import ConstraintFilterEngine
from app.engines.ranking_engine import RankingEngine
from app.services.data_service import DataService

logger = logging.getLogger(__name__)
settings = get_settings()


class RecommendationOrchestrator:
    """End-to-end deterministic recommendation pipeline."""

    def __init__(self, data_service: Optional[DataService] = None):
        self.data = data_service or DataService()
        self.query_engine = QueryUnderstandingEngine()
        self.counselling = CounsellingEngine(self.data)
        self.probability = AdmissionProbabilityEngine(settings.ML_MODELS_DIR)
        self.filter_engine = ConstraintFilterEngine()
        self.ranking = RankingEngine()

    def recommend(
        self,
        profile: StudentProfile,
        top_n: int = 10,
        include_hostels: bool = True,
        include_scholarships: bool = True,
    ) -> RecommendationResponse:
        start = time.time()

        eligible = self.counselling.get_eligible_colleges(profile)
        total_eligible = len(eligible)

        filtered, filters_applied = self.filter_engine.apply(eligible, profile)
        total_after_filters = len(filtered)

        scored = self.probability.score_batch(
            rank=profile.rank,
            category=self.counselling.get_dataset_category(profile.category),
            colleges=filtered,
        )

        ranked = self.ranking.rank(
            scored,
            profile_location=profile.city or profile.district,
            budget=profile.budget,
        )
        buckets = self.ranking.bucket_by_tier(ranked)

        avg_completeness = (
            sum(c.get("data_completeness", 0.5) for c in ranked) / len(ranked)
            if ranked else 0.0
        )
        confidence = self._compute_confidence(profile, total_after_filters, avg_completeness)

        hostels = []
        if include_hostels and ranked:
            college_ids = {c["college_id"] for c in ranked[:top_n * 2]}
            hostels = self.data.get_hostels_for_colleges(list(college_ids))

        scholarships = []
        if include_scholarships:
            scholarships = self.data.get_eligible_scholarships(
                category=profile.category,
                gender=profile.gender,
            )

        response = RecommendationResponse(
            profile=profile,
            safe=[self._to_recommendation(c) for c in buckets["safe"][:top_n]],
            moderate=[self._to_recommendation(c) for c in buckets["moderate"][:top_n]],
            ambitious=[self._to_recommendation(c) for c in buckets["ambitious"][:top_n]],
            total_eligible=total_eligible,
            total_after_filters=total_after_filters,
            confidence=confidence,
            data_completeness=round(avg_completeness, 2),
            engine_version=settings.ENGINE_VERSION,
            filters_applied=filters_applied,
            hostels=hostels,
            scholarships=scholarships[:10],
        )

        elapsed = int((time.time() - start) * 1000)
        logger.info(
            "Recommendation complete: eligible=%d filtered=%d confidence=%.2f (%dms)",
            total_eligible, total_after_filters, confidence, elapsed,
        )
        return response

    def recommend_from_query(
        self,
        query: str,
        profile: Optional[StudentProfile] = None,
        **kwargs,
    ) -> tuple[Optional[RecommendationResponse], Optional[str]]:
        parsed = self.query_engine.parse(query, profile)
        resolved = self.query_engine.to_profile(parsed)
        if not resolved:
            return None, "Could not extract a valid KCET rank from the query. Please provide your rank."
        return self.recommend(resolved, **kwargs), None

    def _to_recommendation(self, c: Dict[str, Any]) -> CollegeRecommendation:
        return CollegeRecommendation(
            college_id=c.get("college_id", ""),
            college_name=c.get("college_name", ""),
            branch=c.get("branch", ""),
            location=c.get("location", ""),
            district=c.get("district"),
            college_type=c.get("college_type", ""),
            cutoff_rank=c.get("raw_cutoff_rank", c.get("cutoff_rank", 0)),
            predicted_cutoff=c.get("predicted_cutoff"),
            admission_probability=c.get("probability", 0),
            tier=c.get("tier", "MODERATE"),
            composite_score=c.get("composite_score", 0),
            annual_fee=c.get("annual_fee"),
            hostel_available=c.get("hostel_available", False),
            placement_avg_lpa=c.get("placement_avg_lpa"),
            naac_grade=c.get("naac_grade"),
            explanation=c.get("explanation", []),
            data_completeness=c.get("data_completeness", 0.5),
        )

    def _compute_confidence(
        self,
        profile: StudentProfile,
        matches: int,
        data_completeness: float,
    ) -> float:
        score = 0.3
        if profile.rank:
            score += 0.2
        if matches > 0:
            score += min(0.3, matches / 50)
        score += data_completeness * 0.2
        return round(min(1.0, score), 2)

    def generate_preference_order(
        self,
        profile: StudentProfile,
        max_options: int = 50,
    ) -> List[Dict[str, Any]]:
        """Feature 3: Generate KEA option-entry preference order."""
        result = self.recommend(profile, top_n=max_options, include_hostels=False, include_scholarships=False)
        all_recs = result.safe + result.moderate + result.ambitious
        all_recs.sort(key=lambda x: x.composite_score, reverse=True)
        return [
            {
                "sequence": i + 1,
                "college_id": r.college_id,
                "college_name": r.college_name,
                "branch": r.branch,
                "tier": r.tier,
                "probability": r.admission_probability,
                "score": r.composite_score,
            }
            for i, r in enumerate(all_recs[:max_options])
        ]

    def compare_colleges(
        self,
        college_ids: List[str],
        profile: StudentProfile,
    ) -> List[Dict[str, Any]]:
        """Feature 1: Compare multiple colleges side-by-side."""
        comparisons = []
        for cid in college_ids:
            college = self.data.get_college_by_id(cid)
            if not college:
                continue
            eligible = self.counselling.get_eligible_colleges(profile, branch=profile.branch)
            match = next((c for c in eligible if c["college_id"] == cid), None)
            if match:
                scored = self.probability.score_batch(profile.rank, profile.category, [match])
                comparisons.append(scored[0] if scored else match)
            else:
                comparisons.append({"college_id": cid, "error": "Branch not available"})
        return comparisons
