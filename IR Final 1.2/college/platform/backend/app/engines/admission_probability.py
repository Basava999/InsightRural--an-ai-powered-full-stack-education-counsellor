"""
Layer 3: Admission Probability Engine
Uses historical cutoff trends + ML model comparison (RF, XGBoost, LightGBM).
Falls back to deterministic rank-vs-cutoff formula when ML unavailable.
"""

import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

CATEGORY_MARGIN = {
    "GM": 0, "OPEN": 0, "GENERAL": 0,
    "EWS": 2, "OBC": 3, "OBC-NCL": 3, "SC": 5, "ST": 5,
}

TIER_THRESHOLDS = {"SAFE": 80, "MODERATE": 50}


def normalize_category(category: str) -> str:
    aliases = {
        "GM": "GM", "GENERAL": "GM", "GEN": "GM", "OC": "GM", "UR": "GM",
        "OBC NCL": "OBC", "OBC": "OBC", "SC": "SC", "ST": "ST",
    }
    return aliases.get(category.upper().strip(), category.upper())


def rule_based_probability(rank: int, cutoff: int, category: str = "GM") -> Dict[str, Any]:
    """Deterministic probability from rank vs cutoff ratio."""
    if rank <= 0 or cutoff <= 0:
        return {"probability": 0, "tier": "AMBITIOUS", "reason": "Invalid rank or cutoff", "method": "rule"}

    ratio = rank / cutoff
    cat = normalize_category(category)
    bonus = CATEGORY_MARGIN.get(cat, 0)

    if ratio <= 0.60:
        probability = 96
        reason = "Rank is far better than previous closing rank."
    elif ratio <= 0.80:
        probability = 90 - int((ratio - 0.60) * 40)
        reason = "Comfortable margin over previous cutoff."
    elif ratio <= 1.00:
        probability = 78 - int((ratio - 0.80) * 90)
        reason = "Within previous closing-rank range."
    elif ratio <= 1.15:
        probability = 48 - int((ratio - 1.00) * 120)
        reason = "Just beyond previous cutoff; later rounds may help."
    elif ratio <= 1.35:
        probability = 28 - int((ratio - 1.15) * 80)
        reason = "Above previous cutoff — ambitious choice."
    else:
        probability = max(5, 12 - int((ratio - 1.35) * 10))
        reason = "Large rank gap compared to previous closing rank."

    probability = max(1, min(99, probability + bonus))
    tier = _probability_to_tier(probability)

    return {
        "probability": probability,
        "tier": tier,
        "reason": reason,
        "rank_gap": cutoff - rank,
        "rank_to_cutoff_ratio": round(ratio, 3),
        "method": "rule",
    }


def _probability_to_tier(probability: float) -> str:
    if probability >= TIER_THRESHOLDS["SAFE"]:
        return "SAFE"
    if probability >= TIER_THRESHOLDS["MODERATE"]:
        return "MODERATE"
    return "AMBITIOUS"


def trend_adjusted_cutoff(trends: Dict, branch: str, category: str, base_cutoff: int) -> int:
    """Predict next-year cutoff from historical trends."""
    if not trends:
        return base_cutoff

    values = []
    for year_data in trends.values():
        if isinstance(year_data, dict):
            branch_data = year_data.get(branch, year_data)
            if isinstance(branch_data, dict):
                val = branch_data.get(category) or branch_data.get("GM")
                if val:
                    values.append(int(val))

    if len(values) < 2:
        return base_cutoff

    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    avg_delta = sum(deltas) / len(deltas)
    predicted = int(base_cutoff + avg_delta * 0.7)
    return max(1, predicted)


class AdmissionProbabilityEngine:
    """Score admission probability using ML ensemble or rule-based fallback."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir
        self._ml_models = None
        self._best_model_name = None
        self._load_models()

    def _load_models(self):
        if not self.models_dir:
            return
        model_path = self.models_dir / "ml_models.pkl"
        if not model_path.exists():
            return
        try:
            with open(model_path, "rb") as f:
                self._ml_models = pickle.load(f)
            metrics = self._ml_models.get("metrics", {})
            if metrics:
                self._best_model_name = min(metrics, key=lambda k: metrics[k].get("mae", 999))
            logger.info("Loaded ML models; best: %s", self._best_model_name)
        except Exception as e:
            logger.warning("ML model load failed: %s", e)

    def score_college(
        self,
        rank: int,
        cutoff: int,
        category: str,
        trends: Optional[Dict] = None,
        branch: str = "CSE",
    ) -> Dict[str, Any]:
        adjusted_cutoff = trend_adjusted_cutoff(trends or {}, branch, category, cutoff)

        ml_result = self._ml_predict(rank, adjusted_cutoff, category, branch)
        if ml_result:
            rule = rule_based_probability(rank, adjusted_cutoff, category)
            blended_prob = int(0.6 * ml_result["probability"] + 0.4 * rule["probability"])
            return {
                "probability": blended_prob,
                "tier": _probability_to_tier(blended_prob),
                "reason": f"ML ({ml_result['method']}) + rule blend. {rule['reason']}",
                "predicted_cutoff": adjusted_cutoff,
                "method": "ml+rule",
            }

        result = rule_based_probability(rank, adjusted_cutoff, category)
        result["predicted_cutoff"] = adjusted_cutoff
        return result

    def _ml_predict(self, rank: int, cutoff: int, category: str, branch: str) -> Optional[Dict]:
        if not self._ml_models or not self._best_model_name:
            return None
        try:
            import numpy as np
            model = self._ml_models["models"].get(self._best_model_name)
            if model is None:
                return None

            cat_enc = {"GM": 0, "OBC": 1, "SC": 2, "ST": 3}.get(category, 0)
            branch_enc = {"CSE": 1, "ECE": 2, "ISE": 3, "EEE": 4, "ME": 5, "CIVIL": 6}.get(branch, 0)
            X = np.array([[rank, cutoff, cat_enc, branch_enc]])
            pred_cutoff = max(1, int(model.predict(X)[0]))
            prob_result = rule_based_probability(rank, pred_cutoff, category)
            prob_result["method"] = self._best_model_name
            return prob_result
        except Exception as e:
            logger.debug("ML predict failed: %s", e)
            return None

    def score_batch(
        self,
        rank: int,
        category: str,
        colleges: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        scored = []
        for c in colleges:
            prob = self.score_college(
                rank=rank,
                cutoff=c["cutoff_rank"],
                category=category,
                trends=c.get("cutoff_trends"),
                branch=c.get("branch", "CSE"),
            )
            entry = {**c, **prob}
            scored.append(entry)
        return scored
