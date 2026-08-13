"""Shared admission probability helpers for rank-based counselling modules."""

from typing import Dict, Optional


CATEGORY_MARGIN = {
    "OPEN": 0,
    "GENERAL": 0,
    "GEN": 0,
    "UR": 0,
    "EWS": 2,
    "OBC": 3,
    "OBC-NCL": 3,
    "SC": 5,
    "ST": 5,
}


def normalize_category(category: Optional[str]) -> str:
    value = (category or "OPEN").strip().upper().replace("_", "-")
    aliases = {
        "GM": "OPEN",
        "GENERAL": "OPEN",
        "GEN": "OPEN",
        "UR": "OPEN",
        "OC": "OPEN",
        "OBC NCL": "OBC-NCL",
        "OBC": "OBC-NCL",
    }
    return aliases.get(value, value)


def calculate_admission_probability(
    rank: int,
    previous_cutoff: int,
    category: Optional[str] = None,
) -> Dict:
    """
    Convert a student rank and previous closing rank into a 0-100 probability.

    Lower ranks are better. The model intentionally stays conservative because
    opening/closing ranks move every round and every year.
    """
    try:
        rank = int(rank)
        previous_cutoff = int(previous_cutoff)
    except (TypeError, ValueError):
        return {
            "probability": 0,
            "admission_chance": "Dream",
            "reason": "Rank and previous cutoff must be valid numbers.",
        }

    if rank <= 0 or previous_cutoff <= 0:
        return {
            "probability": 0,
            "admission_chance": "Dream",
            "reason": "Rank and previous cutoff must be greater than zero.",
        }

    ratio = rank / previous_cutoff
    cat = normalize_category(category)
    bonus = CATEGORY_MARGIN.get(cat, 0)

    if ratio <= 0.60:
        probability = 96
        reason = "Your rank is far better than the previous closing rank."
    elif ratio <= 0.80:
        probability = 90 - int((ratio - 0.60) * 40)
        reason = "Your rank has a comfortable margin over the previous cutoff."
    elif ratio <= 1.00:
        probability = 78 - int((ratio - 0.80) * 90)
        reason = "Your rank is within the previous closing-rank range."
    elif ratio <= 1.15:
        probability = 48 - int((ratio - 1.00) * 120)
        reason = "Your rank is just beyond the previous cutoff, so later rounds may matter."
    elif ratio <= 1.35:
        probability = 28 - int((ratio - 1.15) * 80)
        reason = "This is above the previous cutoff and should be treated as ambitious."
    else:
        probability = max(5, 12 - int((ratio - 1.35) * 10))
        reason = "The rank gap is large compared with the previous closing rank."

    probability = max(1, min(99, probability + bonus))

    if probability >= 80:
        chance = "Safe"
    elif probability >= 45:
        chance = "Moderate"
    else:
        chance = "Dream"

    return {
        "probability": probability,
        "admission_chance": chance,
        "reason": reason,
        "rank_gap": previous_cutoff - rank,
        "rank_to_cutoff_ratio": round(ratio, 3),
    }
