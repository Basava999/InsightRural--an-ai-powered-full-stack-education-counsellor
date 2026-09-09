# ==============================================================================
# InsightRural — KCET Seat Allotment Simulation & ML Prediction Engine
# ==============================================================================
# Replicates the KEA (Karnataka Examinations Authority) counselling process
# using ONLY publicly available official data:
#   - KEA reservation policies (Article 371J, Rural, Kannada Medium, SNQ)
#   - Official seat matrices from KEA brochures
#   - Historical cutoff data (2020-2024 from Production_Ready_Colleges.json)
#   - Fee circulars from KEA government orders
#
# DISCLAIMER: This is a SIMULATION based on public KEA rules. We do NOT
# claim to know KEA's internal source code. Actual allotment depends on
# candidate option-entry behaviour which is unknown before counselling.
# ==============================================================================

import json
import os
import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KEA_Engine")

# ── ML Libraries ──────────────────────────────────────────────────────────────
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False


# ==============================================================================
# KEA RESERVATION POLICY (Official Karnataka Government Rules)
# ==============================================================================
# Source: KEA Counselling Brochure + Karnataka Educational Institutions
# (Reservation of Seats for Backward Classes) Act.
#
# Total seats = 100%
# Government Quota = 100% in Govt colleges, ~40% in private (CET seats)
# Management Quota = ~60% in private (not simulated here)

KEA_RESERVATION_POLICY = {
    # Category: percentage of government quota seats
    "GM":   {"percent": 32, "label": "General Merit"},
    "SC":   {"percent": 15, "label": "Scheduled Caste"},
    "ST":   {"percent": 3,  "label": "Scheduled Tribe"},
    "CAT1": {"percent": 4,  "label": "Category-1 (Brahmins)"},
    "2A":   {"percent": 15, "label": "Category-2A (OBC)"},
    "2B":   {"percent": 4,  "label": "Category-2B (OBC)"},
    "3A":   {"percent": 4,  "label": "Category-3A (OBC)"},
    "3B":   {"percent": 5,  "label": "Category-3B (OBC)"},
}

# Special quotas (applied within each category)
KEA_SPECIAL_QUOTAS = {
    "rural":         {"percent": 15, "label": "Rural Quota (1st-10th in rural area)"},
    "kannada_medium": {"percent": 5,  "label": "Kannada Medium Quota"},
    "snq":           {"percent": 0,  "label": "Supernumerary (physically disabled, ex-servicemen)"},
    "hk_371j":       {"percent": 8,  "label": "Hyderabad-Karnataka 371(J) Reservation"},
}

# Hyderabad-Karnataka districts eligible for 371(J)
HK_DISTRICTS = [
    "bidar", "gulbarga", "kalaburagi", "yadgir", "raichur",
    "koppal", "bellary", "ballari", "vijayanagara", "bagalkot"
]

# Category mapping for dataset lookups
CATEGORY_TO_DATASET = {
    "GM": "GM", "GENERAL": "GM", "GEN": "GM", "OC": "GM",
    "SC": "SC", "ST": "ST",
    "OBC": "OBC", "2A": "OBC", "2B": "OBC", "3A": "OBC", "3B": "OBC",
    "CAT1": "OBC", "CAT-1": "OBC", "CATEGORY-1": "OBC",
    "EWS": "GM",
}

# OBC sub-category relaxation multipliers (higher = more relaxed cutoff)
OBC_RELAXATION = {
    "OBC": 1.00, "2A": 1.12, "2B": 0.95, "3A": 0.95, "3B": 1.00,
    "CAT1": 0.90, "CAT-1": 0.90,
}

# Branch codes
BRANCH_CODES = {
    "CSE": 1, "ISE": 2, "ECE": 3, "EEE": 4, "ME": 5, "CIVIL": 6,
    "AI": 7, "DS": 8, "AI_DS": 9, "CY": 10, "AERO": 11, "CHEM": 12,
    "BIOTECH": 13, "IE": 14, "AUTO": 15, "MINING": 16, "ML": 17,
}

# College type prestige scores
TYPE_PRESTIGE = {
    "Government": 95, "Government_Aided": 90, "Private_Autonomous": 80,
    "Type1_Unaided": 75, "Type2_Unaided": 65, "Deemed_Private": 70,
}

NAAC_SCORE = {
    "A++": 98, "A+": 90, "A": 82, "B++": 75, "B+": 68, "B": 60,
    "C": 45, "N/A": 50,
}

DATA_DIR = str(Path(__file__).parent.parent / "data")


# ==============================================================================
# SEAT MATRIX BUILDER
# ==============================================================================
class SeatMatrix:
    """
    Builds and manages the seat matrix for the simulation.
    Uses college seat intake data and applies KEA reservation percentages.
    """

    def __init__(self, colleges: List[Dict]):
        self.matrix: Dict[str, Dict[str, Dict[str, int]]] = {}
        self._build_matrix(colleges)

    def _build_matrix(self, colleges: List[Dict]):
        """Build seat matrix from college data applying reservation rules."""
        for college in colleges:
            cid = college.get("college_id", "")
            total_seats = college.get("total_seats", 0)
            branches = college.get("branches", [])
            college_type = college.get("type", "Type1_Unaided")

            if total_seats <= 0 or not branches:
                continue

            # Distribute seats across branches
            # Government colleges: 100% CET seats
            # Private: assume ~40% CET + 60% management
            if "Government" in college_type:
                cet_pct = 1.0
            else:
                cet_pct = 0.40  # CET quota in private colleges

            seats_per_branch = max(1, int((total_seats * cet_pct) / len(branches)))

            self.matrix[cid] = {}
            for branch in branches:
                self.matrix[cid][branch] = {}
                for cat, info in KEA_RESERVATION_POLICY.items():
                    cat_seats = max(1, int(seats_per_branch * info["percent"] / 100))
                    self.matrix[cid][branch][cat] = cat_seats

    def get_available(self, college_id: str, branch: str, category: str) -> int:
        """Get available seats for a college-branch-category combo."""
        return self.matrix.get(college_id, {}).get(branch, {}).get(category, 0)

    def allot_seat(self, college_id: str, branch: str, category: str) -> bool:
        """Allot one seat. Returns True if successful."""
        if self.get_available(college_id, branch, category) > 0:
            self.matrix[college_id][branch][category] -= 1
            return True
        return False

    def get_total_seats(self, college_id: str, branch: str) -> int:
        """Total seats across all categories for a college-branch."""
        return sum(self.matrix.get(college_id, {}).get(branch, {}).values())

    def reset(self, colleges: List[Dict]):
        """Reset the matrix for a new simulation round."""
        self._build_matrix(colleges)


# ==============================================================================
# TREND ANALYSIS ENGINE
# ==============================================================================
class TrendAnalyzer:
    """
    Analyze cutoff trends using historical data.
    Supports 1-year, 3-year, 5-year, and 10-year trend calculations.
    """

    @staticmethod
    def calculate_trends(historical: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate trend metrics from historical cutoff data.
        historical: {"2020": 5000, "2021": 4800, "2022": 4500, ...}
        """
        if not historical or len(historical) < 2:
            return {
                "trend_1yr": 0, "trend_3yr": 0, "trend_5yr": 0,
                "direction": "insufficient_data", "demand_label": "Unknown",
                "avg_3yr": 0, "avg_5yr": 0, "volatility": 0,
            }

        years = sorted(historical.keys())
        values = [historical[y] for y in years]

        # 1-year trend (latest - previous)
        trend_1yr = values[-1] - values[-2] if len(values) >= 2 else 0

        # 3-year trend
        if len(values) >= 3:
            trend_3yr = values[-1] - values[-3]
            avg_3yr = sum(values[-3:]) / 3
        else:
            trend_3yr = trend_1yr
            avg_3yr = sum(values) / len(values)

        # 5-year trend
        if len(values) >= 5:
            trend_5yr = values[-1] - values[-5]
            avg_5yr = sum(values[-5:]) / 5
        else:
            trend_5yr = trend_3yr
            avg_5yr = avg_3yr

        # Volatility (standard deviation)
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        volatility = math.sqrt(variance)

        # Direction classification
        # For cutoff ranks: LOWER rank = HARDER to get in = INCREASING demand
        if trend_3yr < -500:
            direction = "increasing_demand"
            demand_label = "📈 Increasing (Getting Harder)"
        elif trend_3yr > 500:
            direction = "decreasing_demand"
            demand_label = "📉 Decreasing (Getting Easier)"
        else:
            direction = "stable"
            demand_label = "➡️ Stable"

        return {
            "trend_1yr": int(trend_1yr),
            "trend_3yr": int(trend_3yr),
            "trend_5yr": int(trend_5yr),
            "direction": direction,
            "demand_label": demand_label,
            "avg_3yr": int(avg_3yr),
            "avg_5yr": int(avg_5yr),
            "volatility": int(volatility),
            "historical": historical,
        }

    @staticmethod
    def predict_next_year(historical: Dict[str, int], method: str = "weighted") -> int:
        """
        Predict cutoff for the next year using historical data.
        Methods: 'weighted' (default), 'linear', 'average'
        """
        if not historical or len(historical) < 2:
            return list(historical.values())[-1] if historical else 0

        years = sorted(historical.keys())
        values = [historical[y] for y in years]

        if method == "linear" and NUMPY_AVAILABLE:
            x = np.array([int(y) for y in years], dtype=float)
            y = np.array(values, dtype=float)
            coeffs = np.polyfit(x, y, 1)
            next_year = int(years[-1]) + 1
            prediction = int(coeffs[0] * next_year + coeffs[1])
        elif method == "weighted":
            # Weighted average: recent years get more weight
            weights = [i + 1 for i in range(len(values))]
            total_weight = sum(weights)
            prediction = int(sum(v * w for v, w in zip(values, weights)) / total_weight)
        else:
            prediction = int(sum(values) / len(values))

        # Clamp to reasonable bounds (±30% of latest value)
        latest = values[-1]
        prediction = max(int(latest * 0.70), min(prediction, int(latest * 1.30)))
        return max(1, prediction)


# ==============================================================================
# ML PREDICTION ENGINE (Multi-Model Comparison)
# ==============================================================================
class MLPredictionEngine:
    """
    Trains and compares multiple ML models for cutoff prediction.
    Models: Random Forest, XGBoost, LightGBM, CatBoost
    Features: year, college_code, branch_code, category, seat_intake,
              cutoff_previous_year, cutoff_3yr_avg, cutoff_5yr_avg, trend
    """

    def __init__(self):
        self.models = {}
        self.best_model_name = None
        self.best_model = None
        self.metrics = {}
        self.is_trained = False
        self.feature_names = [
            "year", "college_prestige", "branch_code", "category_code",
            "seat_intake", "cutoff_prev_year", "cutoff_3yr_avg",
            "cutoff_5yr_avg", "trend_1yr", "trend_3yr", "volatility",
            "naac_score",
        ]

    def _build_training_data(self, colleges: List[Dict]) -> Tuple:
        """
        Build feature matrix and target vector from historical cutoff data.
        Each row = (year, college, branch, category) → cutoff_rank
        """
        X_rows = []
        y_rows = []

        for college in colleges:
            cid = college.get("college_id", "")
            trends = college.get("cutoff_trends", {})
            if not trends or len(trends) < 3:
                continue

            ctype = college.get("type", "Type1_Unaided")
            prestige = TYPE_PRESTIGE.get(ctype, 70)
            naac = NAAC_SCORE.get(college.get("naac_grade", "N/A"), 50)
            seats = college.get("total_seats", 100)
            branches = college.get("branches", [])

            years_sorted = sorted(trends.keys())

            for branch in branches:
                for cat in ["GM", "OBC", "SC", "ST"]:
                    cat_code = {"GM": 0, "OBC": 1, "SC": 2, "ST": 3}.get(cat, 0)
                    branch_code = BRANCH_CODES.get(branch, 0)

                    # Collect all historical values for this combo
                    hist_values = {}
                    for yr in years_sorted:
                        val = trends.get(yr, {}).get(branch, {}).get(cat, 0)
                        if val and val > 0:
                            hist_values[yr] = val

                    if len(hist_values) < 3:
                        continue

                    hist_years = sorted(hist_values.keys())

                    # Create training rows for years where we have sufficient history
                    for i in range(2, len(hist_years)):
                        target_year = int(hist_years[i])
                        target_cutoff = hist_values[hist_years[i]]

                        prev_cutoff = hist_values[hist_years[i - 1]]
                        prev2_cutoff = hist_values[hist_years[i - 2]]

                        # Feature engineering
                        trend_1yr = prev_cutoff - prev2_cutoff
                        recent_vals = [hist_values[hist_years[j]] for j in range(max(0, i - 3), i)]
                        avg_3yr = sum(recent_vals) / len(recent_vals)
                        all_vals = [hist_values[hist_years[j]] for j in range(max(0, i - 5), i)]
                        avg_5yr = sum(all_vals) / len(all_vals)

                        # Multi-year trend
                        if len(recent_vals) >= 2:
                            trend_3yr = recent_vals[-1] - recent_vals[0]
                        else:
                            trend_3yr = trend_1yr

                        # Volatility
                        mean_v = sum(recent_vals) / len(recent_vals)
                        vol = math.sqrt(sum((v - mean_v) ** 2 for v in recent_vals) / len(recent_vals))

                        features = [
                            target_year,        # year
                            prestige,           # college_prestige
                            branch_code,        # branch_code
                            cat_code,           # category_code
                            seats,              # seat_intake
                            prev_cutoff,        # cutoff_prev_year
                            int(avg_3yr),       # cutoff_3yr_avg
                            int(avg_5yr),       # cutoff_5yr_avg
                            trend_1yr,          # trend_1yr
                            trend_3yr,          # trend_3yr
                            int(vol),           # volatility
                            naac,               # naac_score
                        ]

                        X_rows.append(features)
                        y_rows.append(target_cutoff)

        if not X_rows:
            return None, None

        if NUMPY_AVAILABLE:
            return np.array(X_rows, dtype=float), np.array(y_rows, dtype=float)
        return X_rows, y_rows

    def train(self, colleges: List[Dict]) -> Dict[str, Any]:
        """Train all available ML models and select the best one."""
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            return {"error": "scikit-learn or numpy not available", "trained": False}

        cache_dir = os.path.join(os.path.dirname(__file__), "models")
        cache_path = os.path.join(cache_dir, "kea_ml_models.joblib")
        if os.path.exists(cache_path):
            try:
                import joblib
                cached_data = joblib.load(cache_path)
                self.models = cached_data.get("models", {})
                self.best_model_name = cached_data.get("best_model_name")
                self.best_model = cached_data.get("best_model")
                self.metrics = cached_data.get("metrics", {})
                self.is_trained = self.best_model is not None
                if self.is_trained:
                    logger.info(f"[ML] Loaded cached models from {cache_path} (Best: {self.best_model_name})")
                    return {
                        "trained": True,
                        "best_model": self.best_model_name,
                        "model_comparison": self.metrics,
                        "cached": True,
                    }
            except Exception as e:
                logger.warning(f"[ML] Could not load cached models: {e}")

        X, y = self._build_training_data(colleges)
        if X is None or len(X) < 20:
            return {"error": f"Insufficient training data ({len(X) if X is not None else 0} rows)", "trained": False}

        logger.info(f"[ML] Training with {len(X)} samples, {X.shape[1]} features")

        # Define models
        candidates = {}
        candidates["RandomForest"] = RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        )
        candidates["GradientBoosting"] = GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            min_samples_split=5, random_state=42
        )

        if XGBOOST_AVAILABLE:
            candidates["XGBoost"] = xgb.XGBRegressor(
                n_estimators=200, max_depth=8, learning_rate=0.1,
                subsample=0.8, colsample_bytree=0.8, random_state=42,
                verbosity=0
            )

        if LIGHTGBM_AVAILABLE:
            candidates["LightGBM"] = lgb.LGBMRegressor(
                n_estimators=200, max_depth=8, learning_rate=0.1,
                subsample=0.8, colsample_bytree=0.8, random_state=42,
                verbose=-1
            )

        if CATBOOST_AVAILABLE:
            candidates["CatBoost"] = CatBoostRegressor(
                iterations=200, depth=8, learning_rate=0.1,
                random_seed=42, verbose=0
            )

        # Train and evaluate each model
        results = {}
        best_mae = float('inf')

        for name, model in candidates.items():
            try:
                model.fit(X, y)
                y_pred = model.predict(X)

                mae = mean_absolute_error(y, y_pred)
                rmse = math.sqrt(mean_squared_error(y, y_pred))
                r2 = r2_score(y, y_pred)

                # Cross-validation (3-fold due to limited data)
                cv_folds = min(5, max(2, len(X) // 20))
                cv_scores = cross_val_score(model, X, y, cv=cv_folds,
                                          scoring='neg_mean_absolute_error')
                cv_mae = -cv_scores.mean()

                results[name] = {
                    "mae": round(mae, 1),
                    "rmse": round(rmse, 1),
                    "r2": round(r2, 4),
                    "cv_mae": round(cv_mae, 1),
                    "status": "trained"
                }

                self.models[name] = model

                if cv_mae < best_mae:
                    best_mae = cv_mae
                    self.best_model_name = name
                    self.best_model = model

                logger.info(f"[ML] {name}: MAE={mae:.1f}, RMSE={rmse:.1f}, R²={r2:.4f}, CV-MAE={cv_mae:.1f}")

            except Exception as e:
                results[name] = {"error": str(e), "status": "failed"}
                logger.error(f"[ML] {name} failed: {e}")

        self.metrics = results
        self.is_trained = self.best_model is not None
        logger.info(f"[ML] Best model: {self.best_model_name} (CV-MAE: {best_mae:.1f})")

        if self.is_trained:
            try:
                import joblib
                os.makedirs(cache_dir, exist_ok=True)
                joblib.dump({
                    "models": self.models,
                    "best_model_name": self.best_model_name,
                    "best_model": self.best_model,
                    "metrics": self.metrics,
                }, cache_path)
                logger.info(f"[ML] Saved trained models to {cache_path}")
            except Exception as e:
                logger.warning(f"[ML] Could not cache models: {e}")

        return {
            "trained": self.is_trained,
            "best_model": self.best_model_name,
            "training_samples": len(X),
            "features": len(self.feature_names),
            "model_comparison": results,
        }

    def predict(self, features: List[float]) -> Optional[int]:
        """Predict cutoff using the best trained model."""
        if not self.is_trained or not NUMPY_AVAILABLE:
            return None
        try:
            pred = self.best_model.predict(np.array([features]))[0]
            return max(1, int(pred))
        except Exception:
            return None


# ==============================================================================
# CONFIDENCE SCORE CALCULATOR
# ==============================================================================
class ConfidenceCalculator:
    """Calculate confidence scores for predictions."""

    @staticmethod
    def calculate(
        data_years: int,
        has_ml_model: bool,
        trend_volatility: int,
        category_match: bool,
    ) -> Dict[str, Any]:
        """
        Generate confidence score (0-100) and label.
        95-100 = High confidence
        80-95  = Good confidence
        60-80  = Medium confidence
        < 60   = Low confidence
        """
        score = 50  # Base

        # Data availability bonus
        if data_years >= 5:
            score += 25
        elif data_years >= 3:
            score += 15
        elif data_years >= 2:
            score += 8

        # ML model bonus
        if has_ml_model:
            score += 15

        # Category-specific data bonus
        if category_match:
            score += 10

        # Volatility penalty
        if trend_volatility > 5000:
            score -= 15
        elif trend_volatility > 2000:
            score -= 8
        elif trend_volatility < 500:
            score += 5

        score = max(10, min(100, score))

        if score >= 95:
            label = "High Confidence"
            emoji = "🟢"
        elif score >= 80:
            label = "Good Confidence"
            emoji = "🟡"
        elif score >= 60:
            label = "Medium Confidence"
            emoji = "🟠"
        else:
            label = "Low Confidence"
            emoji = "🔴"

        return {
            "score": score,
            "label": label,
            "emoji": emoji,
            "factors": {
                "data_years": data_years,
                "ml_model": has_ml_model,
                "volatility": trend_volatility,
                "category_data": category_match,
            }
        }


# ==============================================================================
# KEA SEAT ALLOTMENT SIMULATION ENGINE
# ==============================================================================
class KEASeatAllotmentEngine:
    """
    Simulates the KEA (Karnataka Examinations Authority) counselling process.
    
    Algorithm: Serial Dictatorship (Rank-ordered, Preference-based)
    
    For every candidate (sorted by merit rank):
      1. Check category eligibility
      2. Apply reservation rules
      3. Apply special quotas (Rural, Kannada Medium, SNQ, 371J)
      4. Iterate through candidate's option entries
      5. For each option: check seat availability + eligibility
      6. If seat available: allot and stop
      7. Otherwise: move to next option
    """

    def __init__(self, colleges: List[Dict] = None):
        """Initialize with college data."""
        self.colleges = colleges or self._load_colleges()
        self.seat_matrix = SeatMatrix(self.colleges)
        self.trend_analyzer = TrendAnalyzer()
        self.ml_engine = MLPredictionEngine()
        self.confidence_calc = ConfidenceCalculator()

        # Build lookup indexes
        self._college_by_id = {c["college_id"]: c for c in self.colleges if c.get("college_id")}
        self._college_by_name = {}
        for c in self.colleges:
            name_key = c.get("name", "").lower().strip()
            self._college_by_name[name_key] = c

        # Train ML models if sklearn is available
        self._train_ml()

        logger.info(f"[KEA Engine] Initialized with {len(self.colleges)} colleges")

    def _load_colleges(self) -> List[Dict]:
        """Load college data from JSON."""
        path = os.path.join(DATA_DIR, "Production_Ready_Colleges.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load colleges: {e}")
            return []

    def _train_ml(self):
        """Train ML models on historical data."""
        try:
            result = self.ml_engine.train(self.colleges)
            if result.get("trained"):
                logger.info(f"[KEA Engine] ML trained: {result['best_model']} "
                          f"({result['training_samples']} samples)")
            else:
                logger.warning(f"[KEA Engine] ML training skipped: {result.get('error', 'unknown')}")
        except Exception as e:
            logger.warning(f"[KEA Engine] ML training failed: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # CANDIDATE ELIGIBILITY CHECK
    # ══════════════════════════════════════════════════════════════════════════

    def check_eligibility(self, candidate: Dict) -> Dict[str, Any]:
        """
        Check which quotas and categories a candidate is eligible for.
        Returns eligible categories and special quotas.
        """
        category = candidate.get("category", "GM").upper()
        eligible_categories = []
        eligible_quotas = []

        # Base category eligibility
        # Everyone can compete in GM pool
        eligible_categories.append("GM")

        # Category-specific pools
        if category in ("SC", "ST"):
            eligible_categories.append(category)
        elif category in ("2A", "2B", "3A", "3B", "CAT1", "CAT-1", "OBC"):
            eligible_categories.append(category)
            # OBC sub-categories can compete in their specific pool
            if category in KEA_RESERVATION_POLICY:
                pass  # Already added

        # Special quotas
        if candidate.get("rural_quota"):
            eligible_quotas.append("rural")
        if candidate.get("kannada_medium"):
            eligible_quotas.append("kannada_medium")
        if candidate.get("snq"):
            eligible_quotas.append("snq")
        if candidate.get("371j_status"):
            eligible_quotas.append("hk_371j")
        if candidate.get("minority_status"):
            eligible_quotas.append("minority")

        return {
            "eligible_categories": eligible_categories,
            "eligible_quotas": eligible_quotas,
            "reservation_benefit": category != "GM",
            "category_label": KEA_RESERVATION_POLICY.get(
                category, {"label": "General Merit"}
            )["label"],
        }

    # ══════════════════════════════════════════════════════════════════════════
    # RESERVATION RULES APPLICATION
    # ══════════════════════════════════════════════════════════════════════════

    def apply_reservation(
        self,
        base_cutoff: int,
        student_category: str,
        quotas: Dict[str, bool],
        college_location: str,
    ) -> Dict[str, Any]:
        """
        Apply official KEA reservation rules to adjust effective cutoff.
        Uses multiplier-based approach reflecting real category relaxation.
        """
        multiplier = 1.0
        benefits = []

        # OBC sub-category relaxation
        if student_category in OBC_RELAXATION:
            sub_factor = OBC_RELAXATION[student_category]
            if sub_factor != 1.0:
                multiplier *= sub_factor
                if sub_factor > 1.0:
                    benefits.append(f"{student_category} category relaxation")

        # Rural quota
        if quotas.get("rural"):
            multiplier += 0.15
            benefits.append("Rural Quota (15%)")

        # Kannada Medium
        if quotas.get("kannada_medium"):
            multiplier += 0.06
            benefits.append("Kannada Medium Quota (5%)")

        # 371(J) - Hyderabad-Karnataka
        if quotas.get("hk_371j"):
            loc_str = " ".join(str(v) for v in college_location.values()).lower() if isinstance(college_location, dict) else str(college_location or "").lower()
            is_hk_college = any(
                d.lower() in loc_str for d in HK_DISTRICTS
            )
            if is_hk_college:
                multiplier += 0.80
                benefits.append("371(J) HK In-Region (70% local reservation)")
            else:
                multiplier += 0.10
                benefits.append("371(J) HK State-level (8%)")

        effective_cutoff = int(base_cutoff * multiplier)

        return {
            "effective_cutoff": effective_cutoff,
            "original_cutoff": base_cutoff,
            "multiplier": round(multiplier, 3),
            "benefits": benefits,
            "has_benefit": len(benefits) > 0,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # PROBABILITY ENGINE
    # ══════════════════════════════════════════════════════════════════════════

    def calculate_probability(
        self,
        student_rank: int,
        cutoff_rank: int,
        category: str = "GM",
    ) -> Dict[str, Any]:
        """
        Calculate admission probability with Safe/Moderate/Ambitious classification.
        
        SAFE:      rank ≤ 70% of cutoff → 80-99.9% probability
        MODERATE:  rank ≈ cutoff (70%-105%) → 45-79% probability
        AMBITIOUS: rank > cutoff (105%-130%) → 5-44% probability
        """
        if cutoff_rank <= 0:
            return {
                "probability": 5.0,
                "safe_probability": 0.0,
                "moderate_probability": 5.0,
                "ambitious_probability": 95.0,
                "tier": "Ambitious",
                "predicted_round": "Unlikely",
            }

        ratio = student_rank / cutoff_rank

        if ratio <= 0.70:
            # Very safe - rank much better than cutoff
            prob = 99.0 - (ratio / 0.70) * 10.0
            tier = "Safe"
            predicted_round = "Round 1"
            safe_prob = prob
            moderate_prob = 100 - prob
            ambitious_prob = 0
        elif ratio <= 0.85:
            # Safe
            prob = 89.0 - ((ratio - 0.70) / 0.15) * 10.0
            tier = "Safe"
            predicted_round = "Round 1"
            safe_prob = prob
            moderate_prob = 100 - prob
            ambitious_prob = 0
        elif ratio <= 1.00:
            # Moderate - rank is close to cutoff
            prob = 79.0 - ((ratio - 0.85) / 0.15) * 34.0
            tier = "Moderate"
            predicted_round = "Round 2"
            safe_prob = max(0, prob - 45)
            moderate_prob = min(100, prob)
            ambitious_prob = max(0, 100 - prob)
        elif ratio <= 1.05:
            # Moderate-Ambitious border
            prob = 45.0 - ((ratio - 1.00) / 0.05) * 15.0
            tier = "Moderate"
            predicted_round = "Round 2/3"
            safe_prob = 0
            moderate_prob = prob
            ambitious_prob = 100 - prob
        elif ratio <= 1.20:
            # Ambitious
            prob = 30.0 - ((ratio - 1.05) / 0.15) * 20.0
            tier = "Ambitious"
            predicted_round = "Extended Round"
            safe_prob = 0
            moderate_prob = max(0, prob - 10)
            ambitious_prob = 100 - prob
        else:
            # Very ambitious / unlikely
            prob = max(2.0, 10.0 - ((ratio - 1.20) / 0.30) * 8.0)
            tier = "Ambitious"
            predicted_round = "Very Unlikely"
            safe_prob = 0
            moderate_prob = 0
            ambitious_prob = 100

        # SC/ST category bonus (reservation pool has more variation)
        if category in ("SC", "ST") and tier == "Moderate":
            prob = min(prob + 5.0, 84.0)

        return {
            "probability": round(max(1.0, min(99.9, prob)), 1),
            "safe_probability": round(max(0, safe_prob), 1),
            "moderate_probability": round(max(0, moderate_prob), 1),
            "ambitious_probability": round(max(0, ambitious_prob), 1),
            "tier": tier,
            "predicted_round": predicted_round,
            "rank_to_cutoff_ratio": round(ratio, 3),
        }

    # ══════════════════════════════════════════════════════════════════════════
    # CUTOFF PREDICTION (ML + Rules Hybrid)
    # ══════════════════════════════════════════════════════════════════════════

    def predict_cutoff(
        self,
        college_id: str,
        branch: str,
        category: str,
        target_year: int = 2025,
    ) -> Dict[str, Any]:
        """
        Predict cutoff for target year using ML + trend analysis hybrid.
        """
        college = self._college_by_id.get(college_id)
        if not college:
            return {"predicted": 0, "confidence": {"score": 0, "label": "No Data"}, "trend": {}}

        # Get historical data
        trends_data = college.get("cutoff_trends", {})
        dataset_cat = CATEGORY_TO_DATASET.get(category, "GM")
        historical = {}
        for yr, yr_data in trends_data.items():
            val = yr_data.get(branch, {}).get(dataset_cat, 0)
            if val and val > 0:
                historical[yr] = val

        # Trend analysis
        trend_info = self.trend_analyzer.calculate_trends(historical)

        # ML prediction
        ml_predicted = None
        if self.ml_engine.is_trained and historical:
            ctype = college.get("type", "Type1_Unaided")
            prestige = TYPE_PRESTIGE.get(ctype, 70)
            naac = NAAC_SCORE.get(college.get("naac_grade", "N/A"), 50)
            seats = college.get("total_seats", 100)
            branch_code = BRANCH_CODES.get(branch, 0)
            cat_code = {"GM": 0, "OBC": 1, "SC": 2, "ST": 3}.get(dataset_cat, 0)

            sorted_years = sorted(historical.keys())
            prev_cutoff = historical.get(sorted_years[-1], 0) if sorted_years else 0

            features = [
                target_year, prestige, branch_code, cat_code, seats,
                prev_cutoff, trend_info["avg_3yr"], trend_info["avg_5yr"],
                trend_info["trend_1yr"], trend_info["trend_3yr"],
                trend_info["volatility"], naac,
            ]
            ml_predicted = self.ml_engine.predict(features)

        # Weighted average prediction
        trend_predicted = self.trend_analyzer.predict_next_year(historical)

        if ml_predicted and ml_predicted > 0:
            # 60% ML + 40% trend analysis
            predicted = int(ml_predicted * 0.6 + trend_predicted * 0.4)
        else:
            predicted = trend_predicted

        # Clamp to ±30% of latest known value
        if historical:
            latest = list(historical.values())[-1]
            predicted = max(int(latest * 0.70), min(predicted, int(latest * 1.30)))

        # Confidence
        confidence = self.confidence_calc.calculate(
            data_years=len(historical),
            has_ml_model=ml_predicted is not None,
            trend_volatility=trend_info["volatility"],
            category_match=dataset_cat in ("GM", "OBC"),
        )

        return {
            "predicted": max(1, predicted),
            "ml_predicted": ml_predicted,
            "trend_predicted": trend_predicted,
            "confidence": confidence,
            "trend": trend_info,
            "historical": historical,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN PREDICTION & SIMULATION ENGINE
    # ══════════════════════════════════════════════════════════════════════════

    def simulate(
        self,
        rank: int,
        category: str = "GM",
        gender: str = "Male",
        branch_preference: List[str] = None,
        district_preference: List[str] = None,
        college_preference: List[str] = None,
        rural_quota: bool = False,
        kannada_medium: bool = False,
        snq: bool = False,
        special_reservation: str = None,
        hk_371j: bool = False,
        minority_status: bool = False,
        annual_income: int = 0,
        hostel_required: bool = False,
        budget: int = 0,
        top_n: int = 20,
    ) -> Dict[str, Any]:
        """
        Main simulation entry point. Simulates KEA allotment for a single
        candidate and returns SAFE / MODERATE / AMBITIOUS predictions.
        """
        if not branch_preference:
            branch_preference = ["CSE", "ISE", "ECE", "AI", "DS"]

        category = category.upper().strip()
        dataset_cat = CATEGORY_TO_DATASET.get(category, "GM")

        # Candidate profile
        candidate = {
            "rank": rank,
            "category": category,
            "gender": gender,
            "rural_quota": rural_quota,
            "kannada_medium": kannada_medium,
            "snq": snq,
            "371j_status": hk_371j,
            "minority_status": minority_status,
        }

        # Check eligibility
        eligibility = self.check_eligibility(candidate)
        quotas = {
            "rural": rural_quota,
            "kannada_medium": kannada_medium,
            "snq": snq,
            "hk_371j": hk_371j,
        }

        # Build predictions
        safe_colleges = []
        moderate_colleges = []
        ambitious_colleges = []

        for college in self.colleges:
            cid = college.get("college_id", "")
            college_name = college.get("name", "")
            location = college.get("location", "")
            loc_str = " ".join(str(v) for v in location.values()).lower() if isinstance(location, dict) else str(location or "").lower()
            district = college.get("district", "")
            dist_str = " ".join(str(v) for v in district.values()).lower() if isinstance(district, dict) else str(district or "").lower()
            ctype = college.get("type", "Type1_Unaided")

            college_branches = set()
            for b in college.get("branches", []):
                if isinstance(b, dict):
                    if b.get("branch_code"): college_branches.add(str(b["branch_code"]).upper())
                    if b.get("branch_name"): college_branches.add(str(b["branch_name"]).upper())
                elif isinstance(b, str):
                    college_branches.add(b.upper())
            cutoff_dict = college.get("cutoff_2024", {})
            if isinstance(cutoff_dict, dict):
                for k in cutoff_dict.keys():
                    college_branches.add(str(k).upper())

            # District filter
            if district_preference:
                if not any(d.lower() in dist_str or d.lower() in loc_str
                          for d in district_preference):
                    continue

            # College preference filter
            if college_preference:
                name_lower = college_name.lower()
                if not any(cp.lower() in name_lower for cp in college_preference):
                    continue

            # Hostel filter
            if hostel_required and not college.get("hostel_available"):
                continue

            # Process each preferred branch
            for branch in branch_preference:
                if branch.upper() not in college_branches:
                    continue

                # Get cutoff data
                cutoff_2024 = college.get("cutoff_2024", {}).get(branch, {})
                cat_cutoff = cutoff_2024.get(dataset_cat, 0)
                gm_cutoff = cutoff_2024.get("GM", 0)
                base_cutoff = cat_cutoff if cat_cutoff > 0 else gm_cutoff

                if base_cutoff <= 0:
                    continue

                # Apply reservation
                reservation = self.apply_reservation(
                    base_cutoff, category, quotas, loc_str
                )
                effective_cutoff = reservation["effective_cutoff"]

                # ML + Trend prediction for next year
                prediction = self.predict_cutoff(cid, branch, dataset_cat)
                predicted_cutoff = prediction["predicted"]

                # Use the more optimistic of effective vs predicted
                final_cutoff = max(
                    effective_cutoff,
                    int(predicted_cutoff * reservation["multiplier"])
                )

                # Calculate probability
                prob_result = self.calculate_probability(rank, final_cutoff, category)

                # Fee calculation
                fee_data = college.get("annual_fee", {})
                if category in ("SC", "ST"):
                    annual_fee = fee_data.get("sc_st", 0)
                elif dataset_cat == "OBC":
                    annual_fee = fee_data.get("obc", fee_data.get("gm", 0))
                else:
                    annual_fee = fee_data.get("gm", 0)

                if isinstance(annual_fee, (int, float)):
                    annual_fee = int(annual_fee)
                else:
                    annual_fee = 0

                # Budget filter
                if budget and annual_fee > budget:
                    continue

                # Trend info
                trend_info = prediction.get("trend", {})

                # Build entry
                entry = {
                    "college_id": cid,
                    "college_name": college_name,
                    "branch": branch,
                    "location": location,
                    "district": district,
                    "college_type": ctype,
                    "cutoff_rank": final_cutoff,
                    "original_cutoff": base_cutoff,
                    "gm_cutoff": gm_cutoff,
                    "category_cutoff": cat_cutoff,
                    "predicted_cutoff": predicted_cutoff,
                    "your_rank": rank,
                    "probability": prob_result["probability"],
                    "safe_probability": prob_result["safe_probability"],
                    "moderate_probability": prob_result["moderate_probability"],
                    "ambitious_probability": prob_result["ambitious_probability"],
                    "admission_chance": prob_result["tier"],
                    "predicted_round": prob_result["predicted_round"],
                    "annual_fee": annual_fee,
                    "four_year_cost": annual_fee * 4,
                    "hostel_available": college.get("hostel_available", False),
                    "naac_grade": college.get("naac_grade", "N/A"),
                    "nba_accredited": college.get("nba_accredited", False),
                    "placement_avg_lpa": college.get("placement_avg_lpa"),
                    "placement_highest_lpa": college.get("placement_highest_lpa"),
                    "top_recruiters": college.get("top_recruiters", []),
                    "reservation_benefits": reservation["benefits"],
                    "has_reservation_benefit": reservation["has_benefit"],
                    "confidence": prediction.get("confidence", {}),
                    "trend": trend_info.get("demand_label", "Stable"),
                    "trend_direction": trend_info.get("direction", "stable"),
                    "trend_1yr": trend_info.get("trend_1yr", 0),
                    "trend_3yr": trend_info.get("trend_3yr", 0),
                    "trend_5yr": trend_info.get("trend_5yr", 0),
                    "historical_cutoffs": prediction.get("historical", {}),
                    "website": college.get("website"),
                    "google_maps_link": college.get("google_maps_link"),
                }

                # Classify
                tier = prob_result["tier"]
                if tier == "Safe":
                    safe_colleges.append(entry)
                elif tier == "Moderate":
                    moderate_colleges.append(entry)
                elif tier == "Ambitious":
                    ambitious_colleges.append(entry)

        # Sort each tier by probability (highest first), then by cutoff rank
        safe_colleges.sort(key=lambda x: (-x["probability"], x["cutoff_rank"]))
        moderate_colleges.sort(key=lambda x: (-x["probability"], x["cutoff_rank"]))
        ambitious_colleges.sort(key=lambda x: (-x["probability"], x["cutoff_rank"]))

        # Trim to top_n
        safe_top = safe_colleges[:top_n]
        moderate_top = moderate_colleges[:top_n]
        ambitious_top = ambitious_colleges[:top_n]

        # Generate KEA option entry strategy
        option_sequence = self._build_option_sequence(
            safe_top, moderate_top, ambitious_top, rank
        )

        # Generate counselling guidance
        guidance = self._generate_guidance(
            rank, category, safe_colleges, moderate_colleges, ambitious_colleges
        )

        return {
            "success": True,
            "candidate_profile": {
                "kcet_rank": rank,
                "category": category,
                "dataset_category": dataset_cat,
                "gender": gender,
                "branch_preference": branch_preference,
                "district_preference": district_preference,
                "eligible_quotas": eligibility["eligible_quotas"],
                "eligible_categories": eligibility["eligible_categories"],
                "reservation_benefit": eligibility["reservation_benefit"],
                "category_label": eligibility["category_label"],
            },
            "safe_colleges": safe_top,
            "moderate_colleges": moderate_top,
            "ambitious_colleges": ambitious_top,
            "total_safe": len(safe_colleges),
            "total_moderate": len(moderate_colleges),
            "total_ambitious": len(ambitious_colleges),
            "total_eligible": len(safe_colleges) + len(moderate_colleges) + len(ambitious_colleges),
            "total_colleges_checked": len(self.colleges),
            "option_entry_sequence": option_sequence,
            "counselling_guidance": guidance,
            "ml_info": {
                "algorithm": "Serial Dictatorship (Rank-ordered, Preference-based)",
                "ml_model": self.ml_engine.best_model_name or "Rule-based",
                "model_metrics": self.ml_engine.metrics,
                "reservation_applied": category,
                "quota_percentage": f"{KEA_RESERVATION_POLICY.get(category, {'percent': 32})['percent']}%",
            },
            "disclaimer": (
                "This is a SIMULATION based on publicly available KEA rules and "
                "historical cutoff data. Actual allotment depends on candidate "
                "option-entry behaviour which is unknown before counselling. "
                "We do NOT claim to know KEA's internal source code."
            ),
        }

    def _build_option_sequence(
        self,
        safe: List[Dict],
        moderate: List[Dict],
        ambitious: List[Dict],
        rank: int,
    ) -> List[Dict]:
        """Build KEA option entry sequence: Ambitious → Moderate → Safe."""
        sequence = []
        priority = 1

        # Ambitious first (Dream schools at top of option list)
        for p in ambitious[:5]:
            sequence.append({
                "priority": priority,
                "college": p["college_name"],
                "branch": p["branch"],
                "tier": "Ambitious",
                "probability": f"{p['probability']}%",
                "cutoff": p["cutoff_rank"],
                "round": p["predicted_round"],
                "strategy": "aspirational",
                "reason": f"Dream option — cutoff {p['cutoff_rank']}, your rank {rank}",
            })
            priority += 1

        # Moderate next (Target schools)
        for p in moderate[:8]:
            sequence.append({
                "priority": priority,
                "college": p["college_name"],
                "branch": p["branch"],
                "tier": "Moderate",
                "probability": f"{p['probability']}%",
                "cutoff": p["cutoff_rank"],
                "round": p["predicted_round"],
                "strategy": "target",
                "reason": f"Strong target — {p['probability']}% chance based on cutoff {p['cutoff_rank']}",
            })
            priority += 1

        # Safe last (Safety net)
        for p in safe[:7]:
            sequence.append({
                "priority": priority,
                "college": p["college_name"],
                "branch": p["branch"],
                "tier": "Safe",
                "probability": f"{p['probability']}%",
                "cutoff": p["cutoff_rank"],
                "round": p["predicted_round"],
                "strategy": "safety",
                "reason": f"Safe backup — {p['probability']}% certainty, secures your seat",
            })
            priority += 1

        return sequence[:20]

    def _generate_guidance(
        self,
        rank: int,
        category: str,
        safe: List,
        moderate: List,
        ambitious: List,
    ) -> Dict[str, Any]:
        """Generate counselling guidance based on analysis."""
        total = len(safe) + len(moderate) + len(ambitious)

        if len(safe) >= 10:
            strategy = (
                "Excellent position! You have many safe options. "
                "Prioritize your true preferences at the top of your KEA form. "
                "Don't worry about safety — focus on quality."
            )
            position = "Strong"
        elif len(safe) >= 3:
            strategy = (
                "Good position. Mix dream schools at top, realistic targets "
                "in the middle, and safe backups at the bottom. "
                "Enter at least 15-20 options."
            )
            position = "Competitive"
        elif len(moderate) >= 5:
            strategy = (
                "Competitive range. Focus on moderate options and add "
                "some tier-2 district colleges as safety. "
                "Enter 25+ options for maximum coverage."
            )
            position = "Moderate"
        else:
            strategy = (
                "Challenging range. Consider all available options including "
                "tier-2/3 colleges, rural government colleges, and "
                "management quota alternatives. Enter 30+ options."
            )
            position = "Challenging"

        return {
            "rank_analysis": f"KCET Rank {rank} | Category: {category} | Position: {position}",
            "strategy": strategy,
            "tips": [
                "Order options by your genuine preference, not by safety index.",
                "In subsequent rounds, KEA only upgrades you — never downgrades.",
                "Complete document verification before option entry deadline.",
                "Always keep government colleges as backup — lowest fees.",
                "If you get Choice-2 (Accept & Upgrade), you keep your seat while waiting for better options.",
            ],
            "important_links": {
                "kea_portal": "https://cetonline.karnataka.gov.in",
                "option_entry": "Opens after document verification",
            },
            "summary": {
                "total_eligible": total,
                "safe_options": len(safe),
                "moderate_options": len(moderate),
                "ambitious_options": len(ambitious),
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # CONTEXT BUILDER FOR CHAT AI
    # ══════════════════════════════════════════════════════════════════════════

    def build_chat_context(
        self,
        rank: int,
        category: str = "GM",
        branch: str = "CSE",
        **kwargs,
    ) -> str:
        """
        Build structured context for the guidance AI chat.
        Returns formatted prediction results for LLM context injection.
        """
        result = self.simulate(
            rank=rank,
            category=category,
            branch_preference=[branch] if isinstance(branch, str) else branch,
            **kwargs,
        )

        parts = [
            "=== KEA SEAT ALLOTMENT SIMULATION (Database + ML) ===",
            f"Rank: {rank} | Category: {category} | Branch: {branch}",
            f"ML Model: {result['ml_info']['ml_model']}",
            "",
        ]

        for tier, label, colleges in [
            ("safe", "🟢 SAFE", result["safe_colleges"]),
            ("moderate", "🟡 MODERATE", result["moderate_colleges"]),
            ("ambitious", "🔴 AMBITIOUS", result["ambitious_colleges"]),
        ]:
            if colleges:
                parts.append(f"\n### {label} ({len(colleges)} colleges)")
                for c in colleges[:5]:
                    fee = f"₹{c['annual_fee']:,}" if c['annual_fee'] else "N/A"
                    parts.append(
                        f"- **{c['college_name']}** ({c['location']})\n"
                        f"  Prob: {c['probability']}% | Cutoff: {c['cutoff_rank']} | "
                        f"Fee: {fee}/yr | Pkg: {c.get('placement_avg_lpa', 'N/A')} LPA\n"
                        f"  Trend: {c['trend']} | Round: {c['predicted_round']}"
                    )

        # Guidance
        guidance = result.get("counselling_guidance", {})
        parts.append(f"\n### Strategy\n{guidance.get('strategy', '')}")

        parts.append(f"\n{result['disclaimer']}")
        parts.append("=== END SIMULATION ===")

        return "\n".join(parts)


# ==============================================================================
# SINGLETON
# ==============================================================================
_engine_instance: Optional[KEASeatAllotmentEngine] = None


def get_kea_engine() -> KEASeatAllotmentEngine:
    """Get or create the KEA Seat Allotment Engine singleton."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = KEASeatAllotmentEngine()
    return _engine_instance
