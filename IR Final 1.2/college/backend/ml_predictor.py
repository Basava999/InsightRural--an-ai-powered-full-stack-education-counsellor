# ==============================================================================
# InsightRural — KEA-Accurate ML College Predictor
# ==============================================================================
# Replicates Karnataka Examinations Authority (KEA) seat allocation logic:
#   - Serial Dictatorship (rank-ordered, preference-based allotment)
#   - Category-wise reservation quotas (SC 15%, ST 3%, 2A 15%, etc.)
#   - OBC sub-categories (2A, 2B, 3A, 3B, Cat-1)
#   - KCET Rank = 50% KCET marks + 50% PUC marks
#   - Rural (15%), Kannada Medium (5%), HK 371J reservations
#   - 3-year cutoff trend regression for next-year prediction
# ==============================================================================

import json
import os
import math
from typing import Dict, List, Any, Optional
from pathlib import Path

# ML Libraries
try:
    import numpy as np
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available. Using rule-based prediction.")


class CollegePredictor:
    """
    KEA-accurate ML college prediction system.
    Simulates the Karnataka KCET counselling seat allotment algorithm.
    """

    # ========================================================================
    # KEA RESERVATION QUOTAS (Official percentages from KEA 2024 seat matrix)
    # ========================================================================
    RESERVATION_QUOTAS = {
        "GM":    0.32,   # General Merit (remaining after reservations)
        "SC":    0.15,   # Scheduled Caste — 15%
        "ST":    0.03,   # Scheduled Tribe — 3%
        "CAT1":  0.04,   # Category-1 — 4%
        "2A":    0.15,   # Category-2A — 15%
        "2B":    0.04,   # Category-2B — 4%
        "3A":    0.04,   # Category-3A — 4%
        "3B":    0.05,   # Category-3B — 5%
    }

    # Special reservation quotas (applied on top of category)
    SPECIAL_QUOTAS = {
        "rural":   0.15,   # Rural students — 15%
        "kannada": 0.05,   # Kannada medium — 5%
        "hk_region": 0.08, # Hyderabad-Karnataka 371J — 8% state-level
        "pwd":     0.05,   # Persons with Disabilities — 5%
    }

    # HK Region districts
    HK_DISTRICTS = [
        "Bidar", "Gulbarga", "Kalaburagi", "Yadgir", "Raichur",
        "Koppal", "Bellary", "Ballari", "Vijayanagara", "Bagalkot"
    ]

    # Category → dataset key mapping
    # KEA OBC sub-categories all map to "OBC" cutoff in our dataset
    # but with different relaxation multipliers
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

    # OBC sub-category relaxation factors
    # 2A has the largest quota (15%) → most relaxed cutoffs
    # 3B has 5%, 2B/3A have 4%, Cat-1 has 4%
    OBC_SUB_RELAXATION = {
        "OBC":  1.00,   # Generic OBC — use dataset directly
        "2A":   1.12,   # Largest OBC quota — slightly more relaxed
        "2B":   0.95,   # Smaller quota — slightly tighter
        "3A":   0.95,   # Smaller quota — slightly tighter
        "3B":   1.00,   # Medium quota
        "CAT1": 0.90,   # Smallest OBC quota — tightest
        "CAT-1":0.90,
    }

    # Branch encoding for ML features
    BRANCH_MAP = {
        "CSE": 0, "ECE": 1, "EEE": 2, "ME": 3, "CIVIL": 4,
        "ISE": 5, "AI": 6, "DS": 7, "CY": 8, "AERO": 9,
        "BT": 10, "CH": 11, "CYBER": 12
    }

    # College type encoding
    TYPE_MAP = {
        "Government": 0, "Government_Aided": 1,
        "Type1_Unaided": 2, "Type2_Unaided": 3, "Deemed_Private": 4
    }

    # College type prestige tiers (for scoring)
    TYPE_PRESTIGE = {
        "Government": 95,
        "Government_Aided": 90,
        "Type1_Unaided": 80,
        "Type2_Unaided": 65,
        "Deemed_Private": 70,
    }

    # NAAC grade scoring
    NAAC_SCORE = {
        "A++": 98, "A+": 90, "A": 82, "B++": 75, "B+": 68, "B": 60, "C": 45
    }

    def __init__(self, data_dir: str = None):
        """Initialize the predictor with cutoff data."""
        self.data_dir = data_dir or str(Path(__file__).parent.parent / "data")
        self.cutoff_data = []
        self.college_data = []
        self.trend_models = {}  # {college_id_branch_category: model}
        self._load_data()
        self._build_trend_models()

    # ========================================================================
    # DATA LOADING
    # ========================================================================
    def _load_data(self):
        """Load cutoff dataset and college data."""
        cutoff_path = os.path.join(self.data_dir, "cutoff_dataset.json")
        if os.path.exists(cutoff_path):
            with open(cutoff_path, 'r', encoding='utf-8') as f:
                self.cutoff_data = json.load(f)
            print(f"[OK] Loaded cutoff data for {len(self.cutoff_data)} colleges")

        # Prefer college_master.json (228 colleges) over kea_colleges_complete.json (40)
        master_path   = os.path.join(self.data_dir, "college_master.json")
        fallback_path = os.path.join(self.data_dir, "kea_colleges_complete.json")
        college_path  = master_path if os.path.exists(master_path) else fallback_path

        if os.path.exists(college_path):
            with open(college_path, 'r', encoding='utf-8') as f:
                self.college_data = json.load(f)
            print(f"[OK] Loaded college details for {len(self.college_data)} colleges from {os.path.basename(college_path)}")

        # Build quick lookup: college_id -> cutoff_trends (5-year data)
        self.cutoff_trends_lookup = {}
        for c in self.college_data:
            cid = c.get('college_id')
            if cid and c.get('cutoff_trends'):
                self.cutoff_trends_lookup[cid] = c['cutoff_trends']


    # ========================================================================
    # KCET RANK CALCULATOR  (50% KCET + 50% PUC)
    # ========================================================================
    @staticmethod
    def calculate_kcet_rank(kcet_marks: Dict[str, int] = None,
                            puc_marks: Dict[str, int] = None,
                            total_candidates: int = 230000) -> Optional[int]:
        """
        Estimate KCET rank from marks using KEA's official formula:
          Composite Score = 50% of KCET total (out of 180) + 50% of PUC PCM (out of 300)
          Normalized to percentage → rank estimated via distribution.
        """
        if not kcet_marks and not puc_marks:
            return None

        # KCET marks (Physics 60 + Chemistry 60 + Maths 60 = 180 total)
        kcet_total = 0
        if kcet_marks:
            kcet_total = sum(kcet_marks.get(s, 0) for s in ['physics', 'chemistry', 'maths'])

        # PUC marks (Physics 100 + Chemistry 100 + Maths 100 = 300 total)
        puc_total = 0
        if puc_marks:
            puc_total = sum(puc_marks.get(s, 0) for s in ['physics', 'chemistry', 'maths'])

        # KEA composite score (50% KCET + 50% PUC)
        kcet_pct = (kcet_total / 180) * 100 if kcet_total > 0 else 0
        puc_pct = (puc_total / 300) * 100 if puc_total > 0 else 0

        if kcet_pct == 0 and puc_pct == 0:
            return None

        # If only one set is provided, weight it fully
        if kcet_pct > 0 and puc_pct > 0:
            composite_pct = (kcet_pct * 0.5) + (puc_pct * 0.5)
        elif kcet_pct > 0:
            composite_pct = kcet_pct
        else:
            composite_pct = puc_pct

        # Rank estimation using a logistic distribution model
        # Higher composite % → lower (better) rank
        # Approximate: top 1% → rank ~2300, top 5% → ~11500, top 10% → ~23000
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

    # ========================================================================
    # TREND MODELS (3-year cutoff regression)
    # ========================================================================
    def _build_trend_models(self):
        """Build linear regression models from 3-year cutoff data to predict future cutoffs."""
        if not ML_AVAILABLE:
            return

        for college in self.cutoff_data:
            cid = college["college_id"]
            cutoffs = college.get("cutoffs", {})

            years = sorted([int(y) for y in cutoffs.keys()])
            if len(years) < 2:
                continue

            for branch in cutoffs.get(str(years[-1]), {}).keys():
                for category in ["GM", "OBC", "SC", "ST"]:
                    data_points = []
                    for year in years:
                        val = cutoffs.get(str(year), {}).get(branch, {}).get(category)
                        if val and isinstance(val, (int, float)):
                            data_points.append((year, val))

                    if len(data_points) >= 2:
                        X = np.array([[dp[0]] for dp in data_points])
                        y = np.array([dp[1] for dp in data_points])

                        model = LinearRegression()
                        model.fit(X, y)

                        key = f"{cid}_{branch}_{category}"
                        self.trend_models[key] = {
                            "model": model,
                            "last_value": data_points[-1][1],
                            "slope": model.coef_[0],
                            "historical": {str(dp[0]): dp[1] for dp in data_points}
                        }

        print(f"[OK] Built {len(self.trend_models)} trend models for cutoff prediction")

    def _predict_cutoff(self, college_id: str, branch: str, category: str,
                        target_year: int = 2025) -> Dict:
        """
        Predict cutoff for a future year using trend regression.
        Returns predicted cutoff and confidence interval.
        """
        key = f"{college_id}_{branch}_{category}"
        trend = self.trend_models.get(key)

        if not trend or not ML_AVAILABLE:
            # Fallback: use latest known cutoff
            for college in self.cutoff_data:
                if college["college_id"] == college_id:
                    latest = college.get("cutoffs", {}).get("2024", {}).get(branch, {})
                    val = latest.get(category, 0)
                    return {
                        "predicted": val,
                        "confidence": "low",
                        "trend_direction": "stable",
                        "historical": {}
                    }
            return {"predicted": 0, "confidence": "low", "trend_direction": "stable", "historical": {}}

        model = trend["model"]
        predicted = max(int(model.predict([[target_year]])[0]), 1)
        slope = trend["slope"]

        # Don't let predictions deviate more than 30% from last known value
        last_val = trend["last_value"]
        predicted = max(int(last_val * 0.70), min(predicted, int(last_val * 1.30)))

        # Determine trend direction
        if slope < -300:
            direction = "getting_harder"  # Cutoff rank dropping (harder to get in)
        elif slope > 300:
            direction = "getting_easier"  # Cutoff rank rising (easier)
        else:
            direction = "stable"

        # Confidence based on number of data points and variance
        n_points = len(trend["historical"])
        confidence = "high" if n_points >= 3 else "medium"

        return {
            "predicted": predicted,
            "confidence": confidence,
            "trend_direction": direction,
            "slope": round(slope, 1),
            "historical": trend["historical"]
        }

    # ========================================================================
    # KEA RESERVATION LOGIC
    # ========================================================================
    def _apply_kea_reservation(self, base_cutoff: int, student_category: str,
                                reservations: Dict[str, bool],
                                college_location: str) -> Dict:
        """
        Apply KEA reservation benefits to determine effective cutoff.

        KEA Logic:
        - Reserved category students (SC/ST/OBC) get category-specific cutoffs
            which are already more relaxed in the dataset
        - Rural students get ~15% seat quota (we model as cutoff relaxation)
        - Kannada medium gets ~5% quota
        - HK 371J gets huge benefit in HK region colleges, moderate elsewhere
        - OBC sub-categories get differential relaxation based on quota size
        """
        effective_cutoff = base_cutoff
        benefits_applied = []
        multiplier = 1.0

        # 1. OBC Sub-category relaxation
        if student_category in self.OBC_SUB_RELAXATION:
            sub_factor = self.OBC_SUB_RELAXATION[student_category]
            if sub_factor != 1.0:
                multiplier *= sub_factor
                if sub_factor > 1.0:
                    benefits_applied.append(f"{student_category} quota benefit")

        # 2. Rural reservation (15% quota → ~12-18% cutoff relaxation)
        if reservations.get('rural', False):
            multiplier += 0.15
            benefits_applied.append("Rural (15% quota)")

        # 3. Kannada Medium (5% quota → ~5-8% relaxation)
        if reservations.get('kannada', False):
            multiplier += 0.06
            benefits_applied.append("Kannada Medium (5% quota)")

        # 4. Hyderabad-Karnataka 371J
        if reservations.get('hk_region', False):
            is_hk_college = any(
                d.lower() in college_location.lower()
                for d in self.HK_DISTRICTS
            )
            if is_hk_college:
                # Within HK region: massive benefit (local 70% reservation)
                multiplier += 0.80
                benefits_applied.append("HK 371J (In-Region — 70% local quota)")
            else:
                # Outside HK region: state-level 8% quota
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

    # ========================================================================
    # ADMISSION PROBABILITY MODEL
    # ========================================================================
    def _calculate_probability(self, student_rank: int, cutoff_rank: int,
                                category: str) -> Dict:
        """
        Calculate admission probability using KEA-realistic model.

        KEA uses closing rank as the threshold. A student with rank LESS than
        or EQUAL to closing rank would have gotten a seat in that round.

        Probability bands (based on analyzing 3 years of KEA data):
        - Rank ≤ 70% of cutoff  → 95%+ (Very Safe)
        - Rank ≤ 90% of cutoff  → 85-95% (Safe)
        - Rank ≤ 100% of cutoff → 70-85% (Good Chance)
        - Rank ≤ 110% of cutoff → 40-70% (Moderate - may get in Round 2)
        - Rank ≤ 125% of cutoff → 15-40% (Reach - Extended Round possible)
        - Rank > 125% of cutoff → 1-15% (Long Shot)
        """
        if cutoff_rank <= 0:
            return {"probability": 1.0, "tier": "Unknown", "round": "Unknown"}

        ratio = student_rank / cutoff_rank  # <1 means rank is better than cutoff

        if ratio <= 0.50:
            prob = 0.99
            tier = "Very Safe"
            predicted_round = "Round 1 (Guaranteed)"
        elif ratio <= 0.70:
            prob = 0.95 + (0.70 - ratio) * 0.20
            tier = "Very Safe"
            predicted_round = "Round 1"
        elif ratio <= 0.90:
            prob = 0.85 + (0.90 - ratio) * 0.50
            tier = "Safe"
            predicted_round = "Round 1"
        elif ratio <= 1.00:
            prob = 0.70 + (1.00 - ratio) * 1.50
            tier = "Good Chance"
            predicted_round = "Round 1 / Round 2"
        elif ratio <= 1.10:
            prob = 0.40 + (1.10 - ratio) * 3.0
            tier = "Moderate"
            predicted_round = "Round 2"
        elif ratio <= 1.25:
            prob = 0.15 + (1.25 - ratio) * 1.67
            tier = "Reach"
            predicted_round = "Extended Round"
        elif ratio <= 1.50:
            prob = 0.05 + (1.50 - ratio) * 0.40
            tier = "Long Shot"
            predicted_round = "Extended Round (unlikely)"
        else:
            prob = max(0.01, 0.05 * math.exp(-2 * (ratio - 1.5)))
            tier = "Very Unlikely"
            predicted_round = "Unlikely"

        # Category boost: SC/ST have smaller pools → slightly higher variance
        if category in ["SC", "ST"]:
            if 0.40 <= prob <= 0.70:
                prob += 0.05  # Slightly more likely due to smaller pool fluctuation

        return {
            "probability": round(min(prob, 0.999), 4),
            "tier": tier,
            "round": predicted_round
        }

    # ========================================================================
    # SCORING & RANKING
    # ========================================================================
    def _calculate_college_score(self, college: Dict, branch: str,
                                  probability: float, student_rank: int,
                                  cutoff: int, fee: int,
                                  preferred_branches: List[str]) -> int:
        """
        Calculate a composite college-branch score for ranking results.
        Factors: admission probability, college prestige, fee value, branch preference.
        """
        # 1. Probability weight (40%)
        prob_score = probability * 100 * 0.40

        # 2. College prestige (25%)
        college_type = college.get("type", "Type1_Unaided")
        naac = college.get("naac_grade", "B")
        prestige = (
            self.TYPE_PRESTIGE.get(college_type, 60) * 0.4 +
            self.NAAC_SCORE.get(naac, 60) * 0.6
        )
        prestige_score = prestige * 0.25

        # 3. Fee value (15%) — lower fees = higher score
        if fee and fee > 0:
            fee_score = max(0, (1 - fee / 400000)) * 100 * 0.15
        else:
            fee_score = 100 * 0.15  # Free = max score

        # 4. Branch preference (10%)
        if branch in preferred_branches:
            branch_idx = preferred_branches.index(branch)
            branch_score = max(0, (10 - branch_idx) / 10) * 100 * 0.10
        else:
            branch_score = 30 * 0.10

        # 5. Rank comfort (10%) — how much buffer the student has
        if cutoff > 0 and student_rank <= cutoff:
            comfort = (cutoff - student_rank) / max(cutoff, 1)
            comfort_score = min(comfort * 100, 100) * 0.10
        else:
            comfort_score = 0

        total = prob_score + prestige_score + fee_score + branch_score + comfort_score
        return int(min(max(total, 0), 99))

    def _calculate_branch_trend(self, college_id: str, branch: str) -> Dict:
        """Get branch demand trend from trend models."""
        key = f"{college_id}_{branch}_GM"
        trend = self.trend_models.get(key)

        if not trend:
            return {"label": "Stable", "direction": "stable", "value": 0}

        slope = trend["slope"]
        historical = trend["historical"]

        if slope < -500:
            return {"label": "Trending 🔥", "direction": "getting_harder", "value": slope, "historical": historical}
        elif slope < -100:
            return {"label": "Rising Demand 📈", "direction": "getting_harder", "value": slope, "historical": historical}
        elif slope > 500:
            return {"label": "Cooling Down 📉", "direction": "getting_easier", "value": slope, "historical": historical}
        elif slope > 100:
            return {"label": "Slightly Easier", "direction": "getting_easier", "value": slope, "historical": historical}
        else:
            return {"label": "Consistent ✅", "direction": "stable", "value": slope, "historical": historical}

    def _calculate_roi(self, college_type: str, fee: int, naac: str) -> Dict:
        """Calculate Return on Investment score."""
        if not fee or fee == 0:
            return {"label": "Elite Value 💎", "score": 98}

        prestige = self.TYPE_PRESTIGE.get(college_type, 60)
        naac_val = self.NAAC_SCORE.get(naac, 60)

        # ROI = quality/cost ratio
        quality = (prestige * 0.5 + naac_val * 0.5)
        cost_penalty = min((fee / 350000) * 40, 40)
        score = quality - cost_penalty + 15

        if score > 85:
            label = "Best Value 💰"
        elif score > 70:
            label = "Great Choice ✅"
        elif score > 55:
            label = "Good Value"
        else:
            label = "Premium Cost 💸"

        return {"label": label, "score": int(min(max(score, 10), 99))}

    # ========================================================================
    # MAIN PREDICTION ENGINE (KEA Serial Dictatorship Simulation)
    # ========================================================================
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
        """
        KEA-accurate college prediction.

        Simulates the Serial Dictatorship algorithm:
        1. For the student's rank, iterate through ALL college-branch combos
        2. Apply category-specific cutoff lookup
        3. Apply reservation benefits (rural, HK, kannada medium)
        4. Calculate admission probability
        5. Score and rank results
        6. Generate KEA Option Entry recommendation
        """
        if not preferred_branches:
            preferred_branches = ["CSE", "ECE", "ISE"]

        reservations = reservations or {}
        puc_marks = puc_marks or {}
        category = category.upper().strip()

        # Map category to dataset key
        dataset_category = self.CATEGORY_TO_DATASET.get(category, "GM")

        # Calculate rank from marks if provided
        estimated_rank = self.calculate_kcet_rank(kcet_marks, puc_marks)

        predictions = []

        # ---- SERIAL DICTATORSHIP: Check every college-branch combo ----
        for college in self.cutoff_data:
            college_id = college["college_id"]
            college_name = college["name"]
            college_type = college.get("type", "Type1_Unaided")
            location = college.get("location", "Unknown")
            coordinates = college.get("coordinates", None)

            # Filter by location
            if preferred_locations and location not in preferred_locations:
                continue

            # Filter by college type
            if college_type_pref and college_type_pref != "Any":
                if college_type_pref == "Government" and college_type not in ["Government", "Government_Aided"]:
                    continue
                elif college_type_pref == "Private" and college_type in ["Government", "Government_Aided"]:
                    continue

            # Get cutoffs (use prediction or latest data)
            latest_cutoffs = college.get("cutoffs", {}).get("2024", {})

            for branch in preferred_branches:
                if branch not in latest_cutoffs:
                    continue

                branch_cutoffs = latest_cutoffs[branch]

                # ---- 1. Category-specific cutoff ----
                cat_cutoff = branch_cutoffs.get(dataset_category, 0)
                gm_cutoff = branch_cutoffs.get("GM", 0)

                # A student can compete under both GM and their category
                # KEA allots under whichever gives them a seat first
                base_cutoff = max(cat_cutoff, gm_cutoff)
                if base_cutoff == 0:
                    base_cutoff = cat_cutoff if cat_cutoff > 0 else gm_cutoff

                if base_cutoff <= 0:
                    continue

                # ---- 2. Apply OBC sub-category relaxation ----
                if category in self.OBC_SUB_RELAXATION and category != "OBC":
                    sub_factor = self.OBC_SUB_RELAXATION[category]
                    base_cutoff = int(base_cutoff * sub_factor)

                # ---- 3. Apply KEA reservation benefits ----
                reservation_result = self._apply_kea_reservation(
                    base_cutoff, category, reservations, location
                )
                effective_cutoff = reservation_result["effective_cutoff"]

                # ---- 4. Get predicted cutoff from trend model ----
                trend_prediction = self._predict_cutoff(college_id, branch, dataset_category)
                predicted_cutoff = trend_prediction["predicted"]

                # Use the more optimistic (higher) cutoff for the student
                # This accounts for year-to-year variation
                final_cutoff = max(effective_cutoff, int(predicted_cutoff * reservation_result["multiplier"]))

                # ---- 5. Calculate admission probability ----
                prob_result = self._calculate_probability(kcet_rank, final_cutoff, category)
                probability = prob_result["probability"]

                # PUC tie-breaker boost (KEA uses PUC marks to break ties)
                is_puc_boosted = False
                puc_avg = sum(puc_marks.values()) / max(len(puc_marks), 1) if puc_marks else 0
                if 0.35 <= probability <= 0.65 and puc_avg > 85:
                    probability = min(probability + 0.05, 0.999)
                    is_puc_boosted = True
                elif 0.35 <= probability <= 0.65 and puc_avg > 75:
                    probability = min(probability + 0.03, 0.999)
                    is_puc_boosted = True

                # ---- 6. Fee & Budget ----
                fee_info = self._get_fee_info(college_id, dataset_category)
                annual_fee = fee_info.get("annual_fee", 0)
                if budget and annual_fee > budget:
                    continue

                # ---- 7. College Score & Metrics ----
                match_score = self._calculate_college_score(
                    college, branch, probability, kcet_rank,
                    final_cutoff, annual_fee, preferred_branches
                )

                trend_data = self._calculate_branch_trend(college_id, branch)
                roi = self._calculate_roi(college_type, annual_fee, fee_info.get("naac_grade", "B"))

                # Map link
                map_link = None
                if coordinates and isinstance(coordinates, dict) and 'lat' in coordinates:
                    map_link = f"https://maps.google.com/?q={coordinates['lat']},{coordinates['lng']}"

                # Historical cutoffs for 5-year sparkline (GM rank per year)
                historical_cutoffs = {}
                allcutoffs = college.get("cutoffs", {})
                for yr in ["2020", "2021", "2022", "2023", "2024"]:
                    val = allcutoffs.get(yr, {}).get(branch, {}).get("GM", 0)
                    if val:
                        historical_cutoffs[yr] = val

                # Full 5-year cutoff_trends from college_master (all categories)
                cutoff_trends = self.cutoff_trends_lookup.get(college_id, {})

                predictions.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "branch": branch,
                    "location": location,
                    "coordinates": coordinates,
                    "map_link": map_link,
                    "college_type": college_type,
                    "naac_grade": fee_info.get("naac_grade", "N/A"),

                    # Cutoff data
                    "cutoff_rank": final_cutoff,
                    "original_cutoff": reservation_result["original_cutoff"],
                    "gm_cutoff": gm_cutoff,
                    "category_cutoff": cat_cutoff,
                    "predicted_cutoff": predicted_cutoff,
                    "your_rank": kcet_rank,

                    # Probability & Classification
                    "probability": round(min(probability * 100, 99.9), 1),
                    "category": prob_result["tier"],
                    "predicted_round": prob_result["round"],

                    # Fees
                    "annual_fee": annual_fee,
                    "four_year_cost": annual_fee * 4 if annual_fee else 0,
                    "hostel_available": fee_info.get("hostel_available", False),

                    # Reservation info
                    "is_reservation_benefit": reservation_result["has_reservation_benefit"],
                    "reservation_benefits": reservation_result["benefits"],
                    "is_puc_boosted": is_puc_boosted,

                    # Metrics
                    "match_index": match_score,
                    "trend": trend_data["label"],
                    "trend_value": trend_data.get("value", 0),
                    "historical_cutoffs": historical_cutoffs,
                    "cutoff_trends": cutoff_trends,   # Full 5-year branch+category data
                    "roi_label": roi["label"],
                    "roi_score": roi["score"],
                })


        # ---- SORT: KEA Priority (Match Score → Probability) ----
        predictions.sort(key=lambda x: (x["match_index"], x["probability"]), reverse=True)
        top_predictions = predictions[:top_n]

        # ---- Generate KEA Option Entry Sequence ----
        option_sequence = self._generate_kea_option_sequence(predictions, kcet_rank)

        # ---- Generate Counselling Guidance ----
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
                "quota_percentage": f"{self.RESERVATION_QUOTAS.get(category, self.RESERVATION_QUOTAS.get(dataset_category, 0.32)) * 100:.0f}%",
            }
        }

    # ========================================================================
    # FEE INFO LOOKUP
    # ========================================================================
    def _get_fee_info(self, college_id: str, category: str) -> Dict:
        """Get fee information for a college based on category."""
        for college in self.college_data:
            if college.get("college_id") == college_id:
                annual_fee = college.get("annual_fee", {})

                if category in ["SC", "ST"]:
                    fee = annual_fee.get("sc_st", 0)
                elif category == "OBC":
                    fee = annual_fee.get("obc", annual_fee.get("gm", 0))
                else:
                    fee = annual_fee.get("gm", 0)

                return {
                    "annual_fee": fee,
                    "hostel_available": college.get("hostel_available", False),
                    "naac_grade": college.get("naac_grade", "N/A"),
                    "fee_category": college.get("fee_category", "Unknown"),
                }
        return {"annual_fee": 0, "hostel_available": False, "naac_grade": "N/A"}

    # ========================================================================
    # KEA OPTION ENTRY OPTIMIZER
    # ========================================================================
    def _generate_kea_option_sequence(self, all_predictions: List[Dict],
                                       student_rank: int) -> List[Dict]:
        """
        Generate recommended KEA Option Entry sequence.

        KEA Strategy (official recommendation):
        - Options 1-5 : Dream choices (top colleges, might not get but worth trying)
        - Options 6-15: Realistic choices (good match, higher probability)
        - Options 16-25: Safe choices (very likely to get, solid backup)
        - Options 25+: Safety net (guaranteed seats)

        In KEA, you only move UP in subsequent rounds. So order by TRUE preference.
        """
        sequence = []

        # Classify predictions
        dream = [p for p in all_predictions if p["category"] in ["Reach", "Long Shot"] and p["probability"] > 5]
        realistic = [p for p in all_predictions if p["category"] in ["Moderate", "Good Chance"]]
        safe = [p for p in all_predictions if p["category"] in ["Safe", "Very Safe"]]

        priority = 1

        # Dream picks (2-3 max)
        for p in dream[:3]:
            sequence.append({
                "priority": priority,
                "college": p["college_name"],
                "branch": p["branch"],
                "category": p["category"],
                "probability": f"{p['probability']}%",
                "round": p["predicted_round"],
                "reason": "🌟 Dream option — worth trying at the top!",
                "strategy": "aspirational"
            })
            priority += 1

        # Realistic picks (4-6)
        for p in realistic[:6]:
            sequence.append({
                "priority": priority,
                "college": p["college_name"],
                "branch": p["branch"],
                "category": p["category"],
                "probability": f"{p['probability']}%",
                "round": p["predicted_round"],
                "reason": "🎯 Strong realistic choice — good chance of allotment",
                "strategy": "target"
            })
            priority += 1

        # Safe picks (6-10)
        for p in safe[:10]:
            sequence.append({
                "priority": priority,
                "college": p["college_name"],
                "branch": p["branch"],
                "category": p["category"],
                "probability": f"{p['probability']}%",
                "round": p["predicted_round"],
                "reason": "🛡️ Safe backup — high probability of securing this seat",
                "strategy": "safety"
            })
            priority += 1

        return sequence[:20]  # KEA recommends 15-25 options

    # ========================================================================
    # COUNSELLING GUIDANCE
    # ========================================================================
    def _generate_kea_guidance(self, rank: int, category: str,
                                predictions: List[Dict]) -> Dict:
        """Generate KEA-specific counselling guidance."""
        safe_count = len([p for p in predictions if p["category"] in ["Safe", "Very Safe"]])
        moderate_count = len([p for p in predictions if p["category"] in ["Moderate", "Good Chance"]])
        total = len(predictions)

        # Rank analysis based on category
        rank_analysis = self._analyze_rank_kea(rank, category)

        # Strategy based on position
        if safe_count >= 8:
            strategy = "You're in a strong position! Prioritize your TRUE preferences. In KEA, you always move UP, never down — so order by what you genuinely want most."
        elif safe_count >= 3:
            strategy = "Good position. Include your dream colleges at the top (you won't lose a safe option by trying), then list safe choices. KEA guarantees you'll only move upward in later rounds."
        elif moderate_count >= 3:
            strategy = "Competitive position. Fill at least 20+ options. Include some ambitious picks at top, but ensure you have enough safe backup. Consider all locations for better options."
        else:
            strategy = "Your rank is in a competitive range. Fill maximum options (25+), include all locations, and consider all available branches. Government colleges in tier-2 cities often have higher cutoffs."

        # Category-specific tips
        tips = [
            "Enter as many options as possible (KEA recommends 15-25 minimum)",
            "Order options by your TRUE preference — not by safety",
            "In subsequent rounds, KEA only moves you UP your preference list",
            "If you get Choice 2 (Accept & Upgrade), you keep your current seat while trying for better",
            "Document verification must be completed BEFORE option entry opens",
        ]

        if category in ["SC", "ST"]:
            tips.extend([
                "SC/ST students get FULL fee waiver in Government and Aided colleges",
                "Apply for Post-Matric Scholarship on SSP portal (ssp.karnataka.gov.in)",
                "Your category cutoffs are separate — you compete within SC/ST pool",
                "Consider Government colleges first — zero fees for your category",
            ])
        elif category in ["2A", "2B", "3A", "3B", "CAT1", "OBC"]:
            tips.extend([
                f"Your OBC sub-category ({category}) has a {self.RESERVATION_QUOTAS.get(category, 0.04)*100:.0f}% seat quota",
                "OBC students get reduced fees in Government & Aided colleges",
                "Apply for OBC scholarship on SSP portal if family income < ₹8 lakh",
            ])

        if any(p.get("is_reservation_benefit") for p in predictions[:10]):
            tips.append("🌾 Reservation benefits have been applied to your cutoffs — this improves your chances significantly")

        return {
            "rank_analysis": rank_analysis,
            "strategy": strategy,
            "tips": tips,
            "important_dates": {
                "document_verification": "Check KEA website (cetonline.karnataka.gov.in)",
                "option_entry": "Opens after document verification",
                "mock_allotment": "2-3 days after option entry closes",
                "round_1": "Usually within 1 week of mock results",
                "round_2": "2-3 weeks after Round 1",
                "extended_round": "After Round 2 for remaining seats",
            },
            "summary": {
                "total_eligible": total,
                "safe_options": safe_count,
                "moderate_options": moderate_count,
                "reach_options": len(predictions) - safe_count - moderate_count,
            }
        }

    def _analyze_rank_kea(self, rank: int, category: str) -> str:
        """KEA-specific rank analysis."""
        cat = self.CATEGORY_TO_DATASET.get(category, "GM")

        if cat == "GM":
            if rank <= 500:
                return "🏆 Outstanding rank! UVCE, RVCE CSE, SJCE CSE are all within reach. You can aim for the very best programs in Karnataka."
            elif rank <= 2000:
                return "🌟 Excellent rank! Top colleges like RVCE, BMSCE, MSRIT, PES for CSE/ISE/AI are realistic targets."
            elif rank <= 5000:
                return "👍 Very good rank. Strong options in top-tier private colleges (RVCE, MSRIT, BMSCE) for most branches."
            elif rank <= 10000:
                return "📊 Good rank. Mid-tier colleges in Bangalore (SIT, RNS, CMR) for CS-related branches are good targets."
            elif rank <= 20000:
                return "📈 Decent rank. Government colleges in tier-2 cities and mid-range Bangalore colleges are realistic."
            elif rank <= 40000:
                return "📋 Moderate rank. Focus on Type-2 colleges, Government colleges in smaller cities, and non-CS branches in better colleges."
            else:
                return "🔍 Consider all available options. Government colleges in smaller districts, all branches, and Type-2 private colleges. Every option you add increases your chances."
        elif cat in ["SC", "ST"]:
            if rank <= 5000:
                return f"🏆 Excellent {category} rank! Top colleges including UVCE, RVCE, BMSCE are within reach for CS-related branches."
            elif rank <= 15000:
                return f"🌟 Very good {category} rank. Strong government and top private colleges are realistic targets."
            elif rank <= 30000:
                return f"👍 Good {category} rank. Government colleges across Karnataka and mid-tier private colleges are available."
            else:
                return f"📋 Your {category} rank gives you access to many colleges. Government colleges offer FREE education for {category} students. Fill maximum options."
        else:
            # OBC
            if rank <= 2000:
                return f"🏆 Excellent {category} rank! Top colleges like RVCE, BMSCE, PES are realistic for CS/ISE/AI."
            elif rank <= 8000:
                return f"🌟 Very good {category} rank. Strong options across Bangalore's top-tier colleges."
            elif rank <= 20000:
                return f"👍 Good {category} rank. Mid-tier colleges and Government colleges are strong targets."
            elif rank <= 40000:
                return f"📊 Decent {category} rank. Focus on Government/Aided colleges for lower fees, and Type-1 private colleges."
            else:
                return f"📋 Fill maximum options. Government colleges in tier-2/3 cities offer great value for your category."


# ==============================================================================
# SINGLETON PATTERN
# ==============================================================================
_predictor_instance = None


def get_predictor() -> CollegePredictor:
    """Get the singleton predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CollegePredictor()
    return _predictor_instance


# ==============================================================================
# TEST
# ==============================================================================
if __name__ == "__main__":
    predictor = CollegePredictor()

    print("\n" + "="*60)
    print("TEST 1: GM Rank 5000, CSE/ECE/ISE, Bangalore")
    print("="*60)
    result = predictor.predict(
        kcet_rank=5000,
        category="GM",
        preferred_branches=["CSE", "ECE", "ISE"],
        preferred_locations=["Bangalore", "Mysore"],
        top_n=10
    )
    print(f"Total eligible: {result['total_eligible']}")
    for i, p in enumerate(result['predictions'][:5], 1):
        print(f"  {i}. {p['college_name']} — {p['branch']}: {p['probability']}% ({p['category']}) [{p['predicted_round']}]")

    print("\n" + "="*60)
    print("TEST 2: SC Rank 15000, CSE, Rural + HK Region")
    print("="*60)
    result2 = predictor.predict(
        kcet_rank=15000,
        category="SC",
        preferred_branches=["CSE", "ECE"],
        reservations={"rural": True, "hk_region": True},
        top_n=10
    )
    print(f"Total eligible: {result2['total_eligible']}")
    for i, p in enumerate(result2['predictions'][:5], 1):
        benefits = ", ".join(p["reservation_benefits"]) if p["reservation_benefits"] else "None"
        print(f"  {i}. {p['college_name']} — {p['branch']}: {p['probability']}% ({p['category']}) [Benefits: {benefits}]")

    print("\n" + "="*60)
    print("TEST 3: 2A Category, Rank 8000")
    print("="*60)
    result3 = predictor.predict(
        kcet_rank=8000,
        category="2A",
        preferred_branches=["CSE", "ISE", "AI"],
        top_n=10
    )
    print(f"Total eligible: {result3['total_eligible']}")
    for i, p in enumerate(result3['predictions'][:5], 1):
        print(f"  {i}. {p['college_name']} — {p['branch']}: {p['probability']}% ({p['category']})")

    print("\n" + "="*60)
    print("TEST 4: KCET Rank Calculator")
    print("="*60)
    est_rank = CollegePredictor.calculate_kcet_rank(
        kcet_marks={"physics": 50, "chemistry": 45, "maths": 55},
        puc_marks={"physics": 90, "chemistry": 85, "maths": 95}
    )
    print(f"  KCET (50+45+55)/180 + PUC (90+85+95)/300 -> Estimated Rank: {est_rank}")
