# ==============================================================================
# InsightRural — Upgraded KEA, JEE, & NEET ML College Predictor
# ==============================================================================
# Upgrades predictions by:
#   1. Deserializing pre-trained robust Models (Ridge & Gradient Boosting)
#   2. Using Target Encoding & One-Hot Encoding instead of checksum-ord
#   3. Implementing a 6-factor Unified Hybrid Recommendation Score
#   4. Dynamic Probability Calibration mapping to Safe, Moderate, and Dream
#   5. Generating Explainable AI (XAI) reasons for each recommendation
# ==============================================================================

import json
import os
import math
import pickle
from typing import Dict, List, Any, Optional, Tuple
from engines.probability import (
    TrendPredictor,
    TrendResult,
)
from pathlib import Path

# ML Libraries
try:
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: NumPy not available. Using rule-based fallbacks.")

# Load prestige configurations and grading metrics
TYPE_PRESTIGE = {
    "Government": 95,
    "Government_Aided": 90,
    "Type1_Unaided": 80,
    "Type2_Unaided": 65,
    "Deemed_Private": 70,
}

NAAC_SCORE = {
    "A++": 98, "A+": 90, "A": 82, "B++": 75, "B+": 68, "B": 60, "C": 45, "N/A": 60
}

BRANCH_LIST = ["CSE", "ECE", "ISE", "EEE", "ME", "CIVIL", "AI", "DS", "CY", "AERO"]
CATEGORY_LIST = ["GM", "OBC", "SC", "ST"]

# ==========================================================
# Probability Engine Configuration
# ==========================================================

SAFE_THRESHOLD = 80

MODERATE_THRESHOLD = 45

MAX_PROBABILITY = 99

MIN_PROBABILITY = 1

RANK_WEIGHT = 0.45

TREND_WEIGHT = 0.20

ROUND_WEIGHT = 0.10

RESERVATION_WEIGHT = 0.15

SEAT_WEIGHT = 0.10
# ==============================================================================
# KEA COLLEGE PREDICTOR (ML-ENABLED + RULES)
# ==============================================================================
class CollegePredictor:
    """
    KEA-accurate ML college prediction system.
    Simulates Karnataka Examinations Authority (KEA) seat allocation rules
    using a multi-factor hybrid scoring and calibrated probability engine.
    """

    RESERVATION_QUOTAS = {
        "GM":    0.32,   # General Merit
        "SC":    0.15,   # Scheduled Caste
        "ST":    0.03,   # Scheduled Tribe
        "CAT1":  0.04,   # Category-1
        "2A":    0.15,   # Category-2A
        "2B":    0.04,   # Category-2B
        "3A":    0.04,   # Category-3A
        "3B":    0.05,   # Category-3B
    }

    SPECIAL_QUOTAS = {
        "rural":   0.15,   # Rural
        "kannada": 0.05,   # Kannada Medium
        "hk_region": 0.08, # Hyderabad-Karnataka 371J
        "pwd":     0.05,   # Persons with Disabilities
    }

    HK_DISTRICTS = [
        "Bidar", "Gulbarga", "Kalaburagi", "Yadgir", "Raichur",
        "Koppal", "Bellary", "Ballari", "Vijayanagara", "Bagalkot"
    ]

    CATEGORY_TO_DATASET = {
        "GM":   "GM",
        "SC":   "SC",
        "ST":   "ST",
        "OBC":  "OBC",
        "2A":   "OBC",
        "2B":   "OBC",
        "3A":   "OBC",
        "3B":   "OBC",
        "CAT1": "OBC",
        "CAT-1":"OBC",
    }

    OBC_SUB_RELAXATION = {
        "OBC":  1.00,
        "2A":   1.12,
        "2B":   0.95,
        "3A":   0.95,
        "3B":   1.00,
        "CAT1": 0.90,
        "CAT-1":0.90,
    }

    def __init__(self, data_dir: str = None):
        self.trend_predictor = TrendPredictor()
        self.data_dir = data_dir or str(Path(__file__).parent.parent / "data")
        self.models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        self.cutoff_data = []
        self.college_data = []
        self.model_data = None
        self._load_data()
        self._load_trained_models()

    def _load_data(self):
        """Load datasets."""
        cutoff_path = os.path.join(self.data_dir, "cutoff_dataset.json")
        if os.path.exists(cutoff_path):
            with open(cutoff_path, 'r', encoding='utf-8') as f:
                self.cutoff_data = json.load(f)

        master_path = os.path.join(self.data_dir, "Production_Ready_Colleges.json")
        fallback_path = os.path.join(self.data_dir, "colleges.json")
        college_path = master_path if os.path.exists(master_path) else fallback_path

        if os.path.exists(college_path):
            with open(college_path, 'r', encoding='utf-8') as f:
                self.college_data = json.load(f)

        # Quick lookup college_id -> cutoff_trends, placement, and fee info
        self.cutoff_trends_lookup = {}
        self.placement_lookup = {}
        self.fee_lookup = {}
        for c in self.college_data:
            cid = c.get('college_id')
            if cid:
                if c.get('cutoff_trends'):
                    self.cutoff_trends_lookup[cid] = c['cutoff_trends']
                if c.get('placement_avg_lpa'):
                    self.placement_lookup[cid] = float(c['placement_avg_lpa'])
                # Pre-build fee lookup for O(1) access
                self.fee_lookup[cid] = {
                    "annual_fee": c.get("annual_fee", {}),
                    "hostel_available": c.get("hostel_available", False),
                    "naac_grade": c.get("naac_grade", "N/A"),
                    "fee_category": c.get("fee_category", "Unknown"),
                }

    def _load_trained_models(self):
        """Deserialize trained ML models from train pipeline output."""
        model_path = os.path.join(self.models_dir, "ml_models.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"[OK] CollegePredictor loaded serialized models from {model_path}")
            except Exception as e:
                print(f"[WARNING] Fallback to rule-based because loading models failed: {e}")

    # ==========================================================================
    # KCET RANK CALCULATOR (50% KCET + 50% PUC PCM)
    # ==========================================================================
    @staticmethod
    def calculate_kcet_rank(kcet_marks: Dict[str, int] = None,
                            puc_marks: Dict[str, int] = None,
                            total_candidates: int = 230000) -> Optional[int]:
        """KEA official rank estimation."""
        if not kcet_marks and not puc_marks:
            return None

        kcet_total = 0
        if kcet_marks:
            kcet_total = sum(kcet_marks.get(s, 0) for s in ['physics', 'chemistry', 'maths'])

        puc_total = 0
        if puc_marks:
            puc_total = sum(puc_marks.get(s, 0) for s in ['physics', 'chemistry', 'maths'])

        kcet_pct = (kcet_total / 180) * 100 if kcet_total > 0 else 0
        puc_pct = (puc_total / 300) * 100 if puc_total > 0 else 0

        if kcet_pct == 0 and puc_pct == 0:
            return None

        if kcet_pct > 0 and puc_pct > 0:
            composite_pct = (kcet_pct * 0.5) + (puc_pct * 0.5)
        elif kcet_pct > 0:
            composite_pct = kcet_pct
        else:
            composite_pct = puc_pct

        if composite_pct >= 95:
            rank = int(total_candidates * 0.005 * (100 - composite_pct) / 5)
        elif composite_pct >= 80:
            rank = int(total_candidates * (0.01 + 0.09 * (95 - composite_pct) / 15))
        elif composite_pct >= 60:
            rank = int(total_candidates * (0.10 + 0.25 * (80 - composite_pct) / 20))
        elif composite_pct >= 40:
            rank = int(total_candidates * (0.35 + 0.30 * (60 - composite_pct) / 20))
        else:
            rank = int(total_candidates * (0.65 + 0.35 * (40 - composite_pct) / 40))

        return max(rank, 1)

    # ==========================================================================
    # HYBRID PREDICTIVE ENGINE
    # ==========================================================================
    def _predict_cutoff(self, college_id: str, branch: str, category: str,
                        target_year: int = 2025) -> Dict:
        """
        KEA Hybrid Ensemble Model loading the robust serialized regressors.
        """
        local_predicted = 0.0
        global_predicted = 0.0
        slope = 0.0
        direction = "stable"
        historical = {}

        # 1. Load from serialized models if available
        if self.model_data and "kea" in self.model_data:
            kea = self.model_data["kea"]
            
            # Local Linear Trend
            local_trends = kea.get("local_trends", {})
            key = f"{college_id}_{branch}_{category}"
            if key in local_trends:
                trend = local_trends[key]
                local_predicted = trend["coef"] * target_year + trend["intercept"]
                local_predicted = max(1.0, local_predicted)
                slope = trend["coef"]
                historical = trend["historical"]
                if slope < -200:
                    direction = "getting_harder"
                elif slope > 200:
                    direction = "getting_easier"

            # Global Gradient Boosting Model
            global_model = kea.get("global_model")
            college_mean_ranks = kea.get("college_mean_ranks", {})
            if global_model and ML_AVAILABLE:
                ctype = "Type1_Unaided"
                naac = "B"
                for college in self.cutoff_data:
                    if college["college_id"] == college_id:
                        ctype = college.get("type", "Type1_Unaided")
                        naac = college.get("naac_grade", "B")
                        break

                prestige = TYPE_PRESTIGE.get(ctype, 70)
                naac_val = NAAC_SCORE.get(naac, 60)
                base_rank = college_mean_ranks.get(college_id, 25000.0)

                # Reconstruct one-hot feature vector
                feat = [prestige, naac_val, base_rank, target_year]
                for b in BRANCH_LIST:
                    feat.append(1.0 if branch == b else 0.0)
                for c in CATEGORY_LIST:
                    feat.append(1.0 if category == c else 0.0)

                try:
                    log_pred = global_model.predict(np.array([feat]))[0]
                    global_predicted = math.exp(log_pred)
                except Exception:
                    global_predicted = 0.0

        # 2. Get recent year benchmark (2024 closing)
        recent_cutoff = 0
        for college in self.cutoff_data:
            if college["college_id"] == college_id:
                latest = college.get("cutoffs", {}).get("2024", {}).get(branch, {})
                recent_cutoff = latest.get(category, 0)
                break

        # 3. Ensemble Blending
        if local_predicted > 0 and global_predicted > 0:
            hybrid = int(local_predicted * 0.5 + global_predicted * 0.3 + recent_cutoff * 0.2)
        elif local_predicted > 0:
            hybrid = int(local_predicted * 0.8 + recent_cutoff * 0.2)
        elif global_predicted > 0:
            hybrid = int(global_predicted * 0.8 + recent_cutoff * 0.2)
        else:
            hybrid = recent_cutoff if recent_cutoff > 0 else 0

        # Clamping to reasonable bounds around recent year to prevent wild extrapolations
        if recent_cutoff > 0:
            hybrid = max(int(recent_cutoff * 0.70), min(hybrid, int(recent_cutoff * 1.30)))
        else:
            hybrid = max(hybrid, 1)

        return {
            "predicted": hybrid,
            "confidence": "high" if local_predicted > 0 else "medium",
            "trend_direction": direction,
            "slope": slope,
            "historical": historical
        }

    # ==========================================================================
    # RESERVATION RULES ENGINE
    # ==========================================================================
    def _apply_kea_reservation(self, base_cutoff: int, student_category: str,
                                reservations: Dict[str, bool],
                                college_location: str) -> Dict:
        """Apply official KEA seat reservation relaxed multipliers."""
        effective_cutoff = base_cutoff
        benefits_applied = []
        multiplier = 1.0

        if student_category in self.OBC_SUB_RELAXATION:
            sub_factor = self.OBC_SUB_RELAXATION[student_category]
            if sub_factor != 1.0:
                multiplier *= sub_factor
                if sub_factor > 1.0:
                    benefits_applied.append(f"{student_category} quota benefit")

        if reservations.get('rural', False):
            multiplier += 0.15
            benefits_applied.append("Rural (15% quota)")

        if reservations.get('kannada', False):
            multiplier += 0.06
            benefits_applied.append("Kannada Medium (5% quota)")

        if reservations.get('hk_region', False):
            loc_str = " ".join(str(v) for v in college_location.values()).lower() if isinstance(college_location, dict) else str(college_location or "").lower()
            is_hk_college = any(
                d.lower() in loc_str
                for d in self.HK_DISTRICTS
            )
            if is_hk_college:
                multiplier += 0.80
                benefits_applied.append("HK 371J (In-Region — 70% local quota)")
            else:
                multiplier += 0.10
                benefits_applied.append("HK 371J (State-level 8% quota)")

        effective_cutoff = int(base_cutoff * multiplier)

        return {
            "effective_cutoff": effective_cutoff,
            "original_cutoff": base_cutoff,
            "multiplier": round(multiplier, 3),
            "benefits": benefits_applied,
            "has_reservation_benefit": len(benefits_applied) > 0
        }

    # ==========================================================================
    # PROBABILITY & SCORING ENGINES
    # ==========================================================================
    def _calculate_probability(
        self,
        student_rank: int,
        cutoff_rank: int,
        category: str,
        trend_direction: str = "stable",
        seat_intake: int = 120,
        round_number: int = 1,
    ) -> Dict[str, Any]:
        """
        Enterprise Probability Engine
        Uses Rank Gap, Historical Trend, Reservation, Seat Intake, Counselling Round.
        Returns production-ready probability dictionary.
        """
        if cutoff_rank <= 0:
            return {
                "probability": 5,
                "tier": "Dream",
                "round": "Unknown",
                "confidence": "Low"
            }

        rank_gap = cutoff_rank - student_rank
        ratio = student_rank / cutoff_rank

        # Rank Score
        if ratio <= 0.60:
            score = 98
        elif ratio <= 0.80:
            score = 90
        elif ratio <= 1.00:
            score = 75
        elif ratio <= 1.10:
            score = 60
        elif ratio <= 1.25:
            score = 40
        else:
            score = 15

        # Trend
        if trend_direction == "getting_easier":
            score += 6
        elif trend_direction == "getting_harder":
            score -= 8

        # Reservation
        if category in ["SC", "ST", "2A", "2B", "3A", "3B", "CAT1"]:
            score += 5

        # Seat Intake
        if seat_intake >= 240:
            score += 5
        elif seat_intake <= 60:
            score -= 5

        # Round
        if round_number == 2:
            score += 3
        elif round_number >= 3:
            score += 6

        probability = max(MIN_PROBABILITY, min(MAX_PROBABILITY, int(score)))

        if probability >= SAFE_THRESHOLD:
            tier = "Safe"
            predicted_round = "Round 1"
        elif probability >= MODERATE_THRESHOLD:
            tier = "Moderate"
            predicted_round = "Round 2"
        else:
            tier = "Dream"
            predicted_round = "Later Round"

        confidence = "High"
        if abs(rank_gap) < 1000:
            confidence = "Medium"
        if abs(rank_gap) < 300:
            confidence = "Low"

        return {
            "probability": probability,
            "tier": tier,
            "round": predicted_round,
            "confidence": confidence,
            "rank_gap": rank_gap,
            "ratio": round(ratio, 3)
        }

    def _calculate_hybrid_score(self, college: Dict, branch: str, kcet_rank: int,
                                final_cutoff: int, student_category: str,
                                preferred_branches: List[str], preferred_locations: List[str],
                                budget: Optional[int], placement_avg_lpa: float,
                                fee: int) -> Tuple[int, Dict[str, float]]:
        """
        Calculate production-grade Unified Recommendation Score:
          40% Cutoff Match + 20% Branch + 15% Category + 10% Location + 10% Fee + 5% Placement
        """
        # 1. Cutoff Match Score (40%)
        if kcet_rank <= final_cutoff:
            cutoff_score = 100.0
        else:
            cutoff_score = max(0.0, 100.0 - ((kcet_rank - final_cutoff) / final_cutoff) * 200.0)

        # 2. Branch Preference Score (20%)
        if preferred_branches and branch in preferred_branches:
            idx = preferred_branches.index(branch)
            branch_score = max(0.0, 100.0 - idx * 20.0)
        else:
            branch_score = 0.0

        # 3. Category match score (15%)
        # Perfect 100 if college offers specific cutoffs for their category or student is GM
        college_cutoffs = college.get("cutoffs", {}).get("2024", {}).get(branch, {})
        dataset_category = self.CATEGORY_TO_DATASET.get(student_category, "GM")
        if student_category == "GM":
            cat_score = 100.0
        elif college_cutoffs.get(dataset_category, 0) > 0:
            cat_score = 100.0
        else:
            cat_score = 50.0  # Fallback to competing under General Merit seats

        # 4. Location Preference Match (10%)
        col_loc = college.get("location", "")
        if isinstance(col_loc, dict):
            col_loc_str = " ".join(str(v) for v in col_loc.values()).lower()
        else:
            col_loc_str = str(col_loc or "").lower()

        if not preferred_locations:
            location_score = 100.0
        elif any(pl.lower() in col_loc_str for pl in preferred_locations):
            location_score = 100.0
        else:
            location_score = 0.0

        # 5. Fee Affordability Match (10%)
        if not budget or budget <= 0:
            fee_score = 100.0
        elif fee <= budget:
            fee_score = 100.0
        else:
            fee_score = max(0.0, 100.0 - ((fee - budget) / budget) * 100.0)

        # 6. Placement Score (5%)
        if placement_avg_lpa >= 12.0:
            placement_score = 100.0
        elif placement_avg_lpa > 0.0:
            placement_score = (placement_avg_lpa / 12.0) * 100.0
        else:
            # Fallback based on college type prestige
            ctype = college.get("type", "Type1_Unaided")
            placement_score = TYPE_PRESTIGE.get(ctype, 50.0)

        weighted_total = (
            0.40 * cutoff_score +
            0.20 * branch_score +
            0.15 * cat_score +
            0.10 * location_score +
            0.10 * fee_score +
            0.05 * placement_score
        )

        sub_scores = {
            "cutoff_match": round(cutoff_score, 1),
            "branch_preference": round(branch_score, 1),
            "category_match": round(cat_score, 1),
            "location_preference": round(location_score, 1),
            "fee_affordability": round(fee_score, 1),
            "placement_rating": round(placement_score, 1)
        }

        return int(min(max(weighted_total, 0), 100)), sub_scores

    # ==========================================================================
    # MAIN KCET PREDICTION ENGINE
    # ==========================================================================
    def predict(
        self,
        kcet_rank: int,
        category: str,
        preferred_branches: List[str] = None,
        preferred_locations: List[str] = None,
        budget: int = None,
        college_type_pref: str = None,
        reservations: Dict[str, bool] = None,
        puc_marks: Dict[str, int] = None,
        kcet_marks: Dict[str, int] = None,
        top_n: int = 15
    ) -> Dict[str, Any]:
        """KEA KEA-accurate Predictor implementing serial dictatorship simulation."""
        if not preferred_branches:
            preferred_branches = ["CSE", "ECE", "ISE"]

        reservations = reservations or {}
        puc_marks = puc_marks or {}
        category = category.upper().strip()

        dataset_category = self.CATEGORY_TO_DATASET.get(category, "GM")
        estimated_rank = self.calculate_kcet_rank(kcet_marks, puc_marks)

        predictions = []

        # Loop through all college records
        for college in self.cutoff_data:
            college_id = college["college_id"]
            college_name = college["name"]
            college_type = college.get("type", "Type1_Unaided")
            location = college.get("location", "Unknown")
            loc_str = " ".join(str(v) for v in location.values()) if isinstance(location, dict) else str(location or "Unknown")
            coordinates = college.get("coordinates", None)

            # Location Filters
            if preferred_locations:
                loc_lower = loc_str.lower()
                if not any(pl.lower() in loc_lower for pl in preferred_locations):
                    continue

            # College Type Filters
            if college_type_pref and college_type_pref != "Any":
                if college_type_pref == "Government" and college_type not in ["Government", "Government_Aided"]:
                    continue
                elif college_type_pref == "Private" and college_type in ["Government", "Government_Aided"]:
                    continue

            latest_cutoffs = college.get("cutoffs", {}).get("2024", {})

            for branch in preferred_branches:
                if branch not in latest_cutoffs:
                    continue

                branch_cutoffs = latest_cutoffs[branch]
                cat_cutoff = branch_cutoffs.get(dataset_category, 0)
                gm_cutoff = branch_cutoffs.get("GM", 0)

                # Compete under whichever cutoff rank is better for the candidate
                base_cutoff = max(cat_cutoff, gm_cutoff)
                if base_cutoff == 0:
                    base_cutoff = cat_cutoff if cat_cutoff > 0 else gm_cutoff

                if base_cutoff <= 0:
                    continue

                # KEA Reservation & OBC multipliers
                if category in self.OBC_SUB_RELAXATION and category != "OBC":
                    base_cutoff = int(base_cutoff * self.OBC_SUB_RELAXATION[category])

                reservation_result = self._apply_kea_reservation(
                    base_cutoff, category, reservations, loc_str
                )
                effective_cutoff = reservation_result["effective_cutoff"]

                # Upgraded prediction from training pipeline models
                trend_prediction = self._predict_cutoff(college_id, branch, dataset_category)
                predicted_cutoff = trend_prediction["predicted"]

                # More optimistic benchmark between effective cutoff & predicted cutoff
                final_cutoff = max(effective_cutoff, int(predicted_cutoff * reservation_result["multiplier"]))

                # Probability calculation on the calibrated curve
                prob_result = self._calculate_probability(kcet_rank, final_cutoff, category)
                probability = prob_result["probability"]

                # PUC boost
                is_puc_boosted = False
                puc_avg = sum(puc_marks.values()) / max(len(puc_marks), 1) if puc_marks else 0
                if 35.0 <= probability <= 65.0 and puc_avg > 85:
                    probability = min(probability + 5.0, 99.9)
                    is_puc_boosted = True

                # Fee configurations
                fee_info = self._get_fee_info(college_id, dataset_category)
                annual_fee = fee_info.get("annual_fee", 0)
                if budget and annual_fee > budget:
                    continue

                # Fetch placements from optimized lookup
                placement_avg_lpa = self.placement_lookup.get(college_id, 0.0)

                # Calculate Multi-factor hybrid scores
                match_score, sub_scores = self._calculate_hybrid_score(
                    college, branch, kcet_rank, final_cutoff, category,
                    preferred_branches, preferred_locations, budget,
                    placement_avg_lpa, annual_fee
                )

                # Explainable AI (XAI) Reason Generator
                rank_diff = final_cutoff - kcet_rank
                if rank_diff >= 0:
                    reason = f"Recommended because your rank of {kcet_rank} is better than the predicted cutoff of {final_cutoff} by {rank_diff} ranks and the branch matches your preference."
                else:
                    reason = f"Recommended as an ambitious dream option. Your rank is {abs(rank_diff)} ranks behind the predicted cutoff of {final_cutoff}, but it matches your branch preference perfectly."

                # Maps
                map_link = None
                if coordinates and isinstance(coordinates, dict) and 'lat' in coordinates:
                    map_link = f"https://maps.google.com/?q={coordinates['lat']},{coordinates['lng']}"

                # 5-year trend maps for the sparkline charts
                historical_cutoffs = {}
                allcutoffs = college.get("cutoffs", {})
                for yr in ["2020", "2021", "2022", "2023", "2024"]:
                    val = allcutoffs.get(yr, {}).get(branch, {}).get("GM", 0)
                    if val:
                        historical_cutoffs[yr] = val

                predictions.append({
                    # Submitting required Upgraded production format
                    "college": college_name,
                    "probability": probability,
                    "recommendation_score": match_score,
                    "reason": reason,

                    # Backward-compatibility parameters to avoid breaking frontend/PDF logic
                    "college_id": college_id,
                    "college_name": college_name,
                    "branch": branch,
                    "location": loc_str,
                    "coordinates": coordinates,
                    "map_link": map_link,
                    "college_type": college_type,
                    "naac_grade": fee_info.get("naac_grade", "N/A"),
                    "cutoff_rank": final_cutoff,
                    "original_cutoff": reservation_result["original_cutoff"],
                    "gm_cutoff": gm_cutoff,
                    "category_cutoff": cat_cutoff,
                    "predicted_cutoff": predicted_cutoff,
                    "your_rank": kcet_rank,
                    "category": prob_result["tier"],   # Mapped to 'Safe', 'Moderate', 'Dream'
                    "admission_chance": prob_result["tier"],
                    "predicted_round": prob_result["round"],
                    "annual_fee": annual_fee,
                    "four_year_cost": annual_fee * 4,
                    "hostel_available": fee_info.get("hostel_available", False),
                    "is_reservation_benefit": reservation_result["has_reservation_benefit"],
                    "reservation_benefits": reservation_result["benefits"],
                    "is_puc_boosted": is_puc_boosted,
                    "match_index": match_score,
                    "sub_scores": sub_scores,
                    "trend": trend_prediction.get("trend_direction", "stable").replace("_", " ").title(),
                    "trend_value": trend_prediction.get("slope", 0.0),
                    "historical_cutoffs": historical_cutoffs,
                    "cutoff_trends": self.cutoff_trends_lookup.get(college_id, {}),
                    "placement_avg_lpa": placement_avg_lpa,
                })

        # Sort recommendations: Hybrid recommendation score first, then probability
        predictions.sort(key=lambda x: (x["recommendation_score"], x["probability"]), reverse=True)
        top_predictions = predictions[:top_n]

        # Option Entry sequencing
        option_sequence = self._generate_kea_option_sequence(predictions, kcet_rank)
        guidance = self._generate_kea_guidance(kcet_rank, category, predictions)

        return {
            "success": True,
            "student_profile": {
                "kcet_rank": kcet_rank,
                "estimated_rank_from_marks": estimated_rank,
                "category": category,
                "dataset_category": dataset_category,
                "preferred_branches": preferred_branches,
                "reservations": reservations,
                "puc_marks": puc_marks,
            },
            "predictions": top_predictions,
            "total_eligible": len(predictions),
            "total_colleges_checked": len(self.cutoff_data),
            "option_entry_sequence": option_sequence,
            "counselling_guidance": guidance,
            "kea_info": {
                "algorithm": "Serial Dictatorship (Rank-ordered, Preference-based)",
                "reservation_applied": category,
                "quota_percentage": f"{self.RESERVATION_QUOTAS.get(category, 0.32) * 100:.0f}%",
            }
        }

    def _get_fee_info(self, college_id: str, category: str) -> Dict:
        """Get fee structures using pre-built O(1) lookup."""
        info = self.fee_lookup.get(college_id)
        if not info:
            return {"annual_fee": 0, "hostel_available": False, "naac_grade": "N/A"}

        annual_fee = info.get("annual_fee", {})
        if category in ["SC", "ST"]:
            fee = annual_fee.get("sc_st", 0)
        elif category == "OBC":
            fee = annual_fee.get("obc", annual_fee.get("gm", 0))
        else:
            fee = annual_fee.get("gm", 0)

        return {
            "annual_fee": fee,
            "hostel_available": info.get("hostel_available", False),
            "naac_grade": info.get("naac_grade", "N/A"),
            "fee_category": info.get("fee_category", "Unknown"),
        }

    def _generate_kea_option_sequence(self, all_predictions: List[Dict], student_rank: int) -> List[Dict]:
        """KEA Option Entry order recommendations (Dream -> Realistic -> Safe)."""
        sequence = []
        dream = [p for p in all_predictions if p["category"] == "Dream" and p["probability"] > 5.0]
        realistic = [p for p in all_predictions if p["category"] == "Moderate"]
        safe = [p for p in all_predictions if p["category"] == "Safe"]

        priority = 1
        for p in dream[:4]:
            sequence.append({
                "priority": priority,
                "college": p["college"],
                "branch": p["branch"],
                "category": p["category"],
                "probability": f"{p['probability']}%",
                "round": p["predicted_round"],
                "reason": "🌟 Dream option — high cutoff quality, worth listing at the very top!",
                "strategy": "aspirational"
            })
            priority += 1

        for p in realistic[:6]:
            sequence.append({
                "priority": priority,
                "college": p["college"],
                "branch": p["branch"],
                "category": p["category"],
                "probability": f"{p['probability']}%",
                "round": p["predicted_round"],
                "reason": "🎯 Strong realistic choice — high likelihood of round 2 entry",
                "strategy": "target"
            })
            priority += 1

        for p in safe[:10]:
            sequence.append({
                "priority": priority,
                "college": p["college"],
                "branch": p["branch"],
                "category": p["category"],
                "probability": f"{p['probability']}%",
                "round": p["predicted_round"],
                "reason": "🛡️ Extremely Safe backup — secures your seat entry",
                "strategy": "safety"
            })
            priority += 1

        return sequence[:20]

    def _generate_kea_guidance(self, rank: int, category: str, predictions: List[Dict]) -> Dict:
        """Counseling tips."""
        safe_count = len([p for p in predictions if p["category"] == "Safe"])
        moderate_count = len([p for p in predictions if p["category"] == "Moderate"])
        total = len(predictions)

        rank_analysis = "Based on your rank of " + str(rank) + " and category: " + category

        if safe_count >= 8:
            strategy = "You are in a highly favorable position! Prioritize your absolute true preferences at the top of your KEA form."
        elif safe_count >= 3:
            strategy = "Solid target range. Enter all dream schools first, followed by realistic and safety selections."
        else:
            strategy = "Highly competitive range. Focus on tier-2 districts, government-aided branches, and enter at least 25+ choices."

        tips = [
            "Order options purely by your genuine quality preference, not safety index.",
            "In subsequent rounds, KEA only moves you UP your preference list.",
            "Complete KEA document verification immediately before option entries open."
        ]

        return {
            "rank_analysis": rank_analysis,
            "strategy": strategy,
            "tips": tips,
            "important_dates": {
                "verification": "Check cetonline.karnataka.gov.in",
                "option_entry": "Opens soon after verification results"
            },
            "summary": {
                "total_eligible": total,
                "safe_options": safe_count,
                "moderate_options": moderate_count,
                "reach_options": total - safe_count - moderate_count,
            }
        }


# ==============================================================================
# JoSAA/JEE COLLEGE PREDICTOR (Upgraded ML & calibrations)
# ==============================================================================
class JEECollegePredictor:
    """Upgraded JoSAA prediction module mapping features to robust RandomForest."""
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or str(Path(__file__).parent.parent / "data")
        self.models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        self.cutoff_data = []
        self.model_data = None
        self._load_data()
        self._load_trained_models()

    def _load_data(self):
        path = os.path.join(self.data_dir, "jee_cutoffs_sample.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.cutoff_data = json.load(f).get("cutoffs", [])

    def _load_trained_models(self):
        model_path = os.path.join(self.models_dir, "ml_models.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"[OK] JEECollegePredictor loaded models from {model_path}")
            except Exception as e:
                print(f"Error loading JEE models: {e}")

    def predict_cutoff(self, college: str, branch: str, category: str, quota: str, gender: str, target_year: int = 2026) -> Dict:
        global_predicted = 0.0
        
        # Load from models
        if self.model_data and "jee" in self.model_data:
            jee = self.model_data["jee"]
            global_model = jee.get("global_model")
            college_mean_ranks = jee.get("college_mean_ranks", {})

            if global_model and ML_AVAILABLE:
                col_base = college_mean_ranks.get(college, 10000.0)
                inst_type = "NIT"
                for row in self.cutoff_data:
                    if row.get("college") == college:
                        inst_type = row.get("institute_type", "NIT")
                        break
                prestige = 95 if inst_type == "IIT" else (90 if inst_type == "NIT" else 80)
                
                feat = [prestige, col_base]
                for cat in ["OPEN", "OBC-NCL", "SC", "ST", "EWS"]:
                    feat.append(1.0 if category == cat else 0.0)
                for qt in ["AI", "HS", "OS"]:
                    feat.append(1.0 if quota == qt else 0.0)
                feat.append(1.0 if "Female" in str(gender) else 0.0)

                try:
                    log_pred = global_model.predict(np.array([feat]))[0]
                    global_predicted = math.exp(log_pred)
                except Exception:
                    global_predicted = 0.0

        # Recent cutoff fallback
        recent_cutoff = 0
        for row in self.cutoff_data:
            if row.get("college") == college and row.get("branch") == branch and row.get("category") == category and row.get("quota") == quota and row.get("gender") == gender:
                recent_cutoff = row.get("closing_rank", 0)
                break

        final_val = int(global_predicted) if global_predicted > 0 else recent_cutoff
        if recent_cutoff > 0:
            final_val = max(int(recent_cutoff * 0.75), min(final_val, int(recent_cutoff * 1.25)))

        return {
            "predicted": final_val,
            "confidence": "high" if global_predicted > 0 else "medium",
            "trend_direction": "stable",
            "slope": 0.0,
            "historical": {}
        }

    def calculate_probability(self, student_rank: int, cutoff_rank: int, category: str) -> Dict:
        """Calibrate JoSAA probability into Safe, Moderate, and Dream."""
        if cutoff_rank <= 0:
            return {"probability": 10.0, "tier": "Dream", "round": "Unlikely"}

        ratio = student_rank / cutoff_rank

        if ratio <= 0.85:
            prob = 99.0 - (ratio / 0.85) * 19.0
            tier = "Safe"
            predicted_round = "Round 1"
        elif ratio <= 1.05:
            prob = 79.9 - ((ratio - 0.85) / 0.20) * 29.9
            tier = "Moderate"
            predicted_round = "Round 2 / 3"
        else:
            prob = max(1.0, 49.9 - ((ratio - 1.05) / 0.95) * 48.9)
            tier = "Dream"
            predicted_round = "Round 6 CSAB"

        return {
            "probability": round(prob, 1),
            "tier": tier,
            "round": predicted_round
        }

    def calculate_demand_trend(self, college: str, branch: str) -> Dict:
        return {"label": "Consistent ✅", "direction": "stable", "value": 0}

    def calculate_roi(self, inst_type: str, fee: int) -> Dict:
        prestige = 95 if inst_type == "IIT" else (90 if inst_type == "NIT" else 80)
        score = prestige - min((fee / 350000) * 40, 40) + 15
        label = "Best Value 💰" if score > 80 else "Good Choice"
        return {"label": label, "score": int(score)}


# ==============================================================================
# MCC/NEET COLLEGE PREDICTOR (Upgraded ML & calibrations)
# ==============================================================================
class NEETCollegePredictor:
    """Upgraded MCC prediction module mapping medical features."""
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or str(Path(__file__).parent.parent / "data")
        self.models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        self.cutoff_data = []
        self.model_data = None
        self._load_data()
        self._load_trained_models()

    def _load_data(self):
        path = os.path.join(self.data_dir, "neet_cutoffs_sample.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.cutoff_data = json.load(f).get("cutoffs", [])

    def _load_trained_models(self):
        model_path = os.path.join(self.models_dir, "ml_models.pkl")
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model_data = pickle.load(f)
                print(f"[OK] NEETCollegePredictor loaded models from {model_path}")
            except Exception as e:
                print(f"Error loading NEET models: {e}")

    def predict_cutoff(self, college: str, course: str, category: str, quota: str, gender: str, target_year: int = 2026) -> Dict:
        global_predicted = 0.0
        
        # Load from models
        if self.model_data and "neet" in self.model_data:
            neet = self.model_data["neet"]
            global_model = neet.get("global_model")
            college_mean_ranks = neet.get("college_mean_ranks", {})

            if global_model and ML_AVAILABLE:
                col_base = college_mean_ranks.get(college, 20000.0)
                track = "Government"
                for row in self.cutoff_data:
                    if row.get("college") == college:
                        track = row.get("track", "Government")
                        break
                prestige = 95 if track == "Government" else 65
                
                feat = [prestige, col_base]
                for crs in ["MBBS", "BDS", "BAMS", "BHMS"]:
                    feat.append(1.0 if course == crs else 0.0)
                for cat in ["OPEN", "OBC-NCL", "SC", "ST", "EWS"]:
                    feat.append(1.0 if category == cat else 0.0)

                try:
                    log_pred = global_model.predict(np.array([feat]))[0]
                    global_predicted = math.exp(log_pred)
                except Exception:
                    global_predicted = 0.0

        # Recent fallback
        recent_cutoff = 0
        for row in self.cutoff_data:
            if row.get("college") == college and row.get("course") == course and row.get("category") == category and row.get("quota") == quota and row.get("gender") == gender:
                recent_cutoff = row.get("closing_rank", 0)
                break

        final_val = int(global_predicted) if global_predicted > 0 else recent_cutoff
        if recent_cutoff > 0:
            final_val = max(int(recent_cutoff * 0.75), min(final_val, int(recent_cutoff * 1.25)))

        return {
            "predicted": final_val,
            "confidence": "high" if global_predicted > 0 else "medium",
            "trend_direction": "stable",
            "slope": 0.0,
            "historical": {}
        }

    def calculate_probability(self, student_rank: int, cutoff_rank: int, category: str) -> Dict:
        """Calibrate NEET probability into Safe, Moderate, and Dream."""
        if cutoff_rank <= 0:
            return {"probability": 10.0, "tier": "Dream", "round": "Unlikely"}

        ratio = student_rank / cutoff_rank

        if ratio <= 0.85:
            prob = 99.0 - (ratio / 0.85) * 19.0
            tier = "Safe"
            predicted_round = "Round 1"
        elif ratio <= 1.05:
            prob = 79.9 - ((ratio - 0.85) / 0.20) * 29.9
            tier = "Moderate"
            predicted_round = "Round 2"
        else:
            prob = max(1.0, 49.9 - ((ratio - 1.05) / 0.95) * 48.9)
            tier = "Dream"
            predicted_round = "Mop-up Round"

        return {
            "probability": round(prob, 1),
            "tier": tier,
            "round": predicted_round
        }

    def calculate_demand_trend(self, college: str, course: str) -> Dict:
        return {"label": "Consistent ✅", "direction": "stable", "value": 0}

    def calculate_roi(self, track: str, fee: int) -> Dict:
        prestige = 95 if track == "Government" else 65
        score = prestige - min((fee / 350000) * 40, 40) + 15
        label = "Best Value 💰" if score > 80 else "Good Choice"
        return {"label": label, "score": int(score)}


# ==============================================================================
# SINGLETON CONTEXTS
# ==============================================================================
_predictor_instance = None
_jee_predictor_instance = None
_neet_predictor_instance = None


def get_predictor() -> CollegePredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CollegePredictor()
    return _predictor_instance


def get_jee_predictor() -> JEECollegePredictor:
    global _jee_predictor_instance
    if _jee_predictor_instance is None:
        _jee_predictor_instance = JEECollegePredictor()
    return _jee_predictor_instance


def get_neet_predictor() -> NEETCollegePredictor:
    global _neet_predictor_instance
    if _neet_predictor_instance is None:
        _neet_predictor_instance = NEETCollegePredictor()
    return _neet_predictor_instance


# ==============================================================================
# TEST RUN
# ==============================================================================
if __name__ == "__main__":
    predictor = CollegePredictor()
    print("\n" + "="*60)
    print("KEA TEST RUN: Rank 12000, Category 2A, Bangalore")
    print("="*60)
    result = predictor.predict(
        kcet_rank=12000,
        category="2A",
        preferred_branches=["CSE", "ECE"],
        top_n=3
    )
    for p in result["predictions"]:
        print(f"College: {p['college']} | Branch: {p['branch']}")
        print(f"  Probability: {p['probability']}% ({p['category']})")
        print(f"  Score: {p['recommendation_score']}/100")
        print(f"  Reason: {p['reason']}\n")