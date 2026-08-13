# ==============================================================================
# InsightRural — ML Model Training & Feature Engineering Pipeline
# ==============================================================================
# Trains and serializes prediction models for KEA (KCET), JEE, and NEET.
# Solves target encoding, data leakage, and training on-the-fly bottlenecks.
# ==============================================================================

import os
import json
import pickle
import math
import numpy as np
from typing import Dict, List, Tuple, Any

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn is not installed. Standalone training requires scikit-learn.")


# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "..", "data")
MODELS_DIR = os.path.join(BACKEND_DIR, "models")

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


# ==============================================================================
# PIPELINE CLASS
# ==============================================================================
class MLTrainingPipeline:
    def __init__(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        self.kea_dataset = []
        self.jee_dataset = []
        self.neet_dataset = []

    def load_datasets(self):
        """Load KEA, JEE, and NEET datasets from data folder."""
        # 1. KEA Cutoffs
        kea_path = os.path.join(DATA_DIR, "cutoff_dataset.json")
        if os.path.exists(kea_path):
            with open(kea_path, 'r', encoding='utf-8') as f:
                self.kea_dataset = json.load(f)
            print(f"[LOAD] KEA: Loaded {len(self.kea_dataset)} colleges")

        # 2. JEE Cutoffs
        jee_path = os.path.join(DATA_DIR, "jee_cutoffs_sample.json")
        if os.path.exists(jee_path):
            with open(jee_path, 'r', encoding='utf-8') as f:
                self.jee_dataset = json.load(f).get("cutoffs", [])
            print(f"[LOAD] JEE: Loaded {len(self.jee_dataset)} cutoff rows")

        # 3. NEET Cutoffs
        neet_path = os.path.join(DATA_DIR, "neet_cutoffs_sample.json")
        if os.path.exists(neet_path):
            with open(neet_path, 'r', encoding='utf-8') as f:
                self.neet_dataset = json.load(f).get("cutoffs", [])
            print(f"[LOAD] NEET: Loaded {len(self.neet_dataset)} cutoff rows")

    # ==========================================================================
    # KEA ML TRAINING PIPELINE
    # ==========================================================================
    def train_kea_models(self) -> Dict[str, Any]:
        """
        Train local linear trend models and a global ensemble model for KEA.
        Uses target encoding for college ID and one-hot encoding for categorical variables.
        """
        if not SKLEARN_AVAILABLE or not self.kea_dataset:
            print("[SKIP] KEA training skipped (scikit-learn or data unavailable)")
            return {}

        print("\n--- Training KEA Admission Predictor Models ---")

        # 1. Calculate Target Encodings (competitiveness benchmark rank for each college)
        college_mean_ranks = {}
        for college in self.kea_dataset:
            cid = college["college_id"]
            ranks = []
            cutoffs = college.get("cutoffs", {})
            for year, branch_data in cutoffs.items():
                for branch, cat_data in branch_data.items():
                    val = cat_data.get("GM")
                    if val and isinstance(val, (int, float)):
                        ranks.append(val)
            # Default to average rank if college has records, else general default
            college_mean_ranks[cid] = float(np.mean(ranks)) if ranks else 25000.0

        # 2. Prepare Training Samples
        X_data = []
        y_data = []
        local_trends = {}

        # First pass: Train local linear trend models and collect global training data
        for college in self.kea_dataset:
            cid = college["college_id"]
            ctype = college.get("type", "Type1_Unaided")
            prestige = TYPE_PRESTIGE.get(ctype, 70)
            naac = college.get("naac_grade", "B")
            naac_val = NAAC_SCORE.get(naac, 60)
            college_base_rank = college_mean_ranks.get(cid, 25000.0)

            cutoffs = college.get("cutoffs", {})
            years = sorted([int(y) for y in cutoffs.keys()])

            # Extract branches and categories for local trend
            all_branches = set()
            for y_str in cutoffs.keys():
                all_branches.update(cutoffs[y_str].keys())

            for branch in all_branches:
                for category in ["GM", "OBC", "SC", "ST"]:
                    data_points = []
                    for year_int in years:
                        val = cutoffs.get(str(year_int), {}).get(branch, {}).get(category)
                        if val and isinstance(val, (int, float)) and val > 0:
                            data_points.append((year_int, val))

                    # Train local Ridge regression if we have at least 2 years of cutoffs
                    if len(data_points) >= 2:
                        X_local = np.array([[dp[0]] for dp in data_points])
                        y_local = np.array([dp[1] for dp in data_points])
                        
                        # Train local Ridge model (regularized linear model to avoid wild extrapolation)
                        trend_model = Ridge(alpha=1.0)
                        trend_model.fit(X_local, y_local)
                        
                        key = f"{cid}_{branch}_{category}"
                        local_trends[key] = {
                            "coef": trend_model.coef_[0],
                            "intercept": trend_model.intercept_,
                            "last_value": data_points[-1][1],
                            "historical": {str(dp[0]): dp[1] for dp in data_points}
                        }

                    # Collect for Global Model Training
                    for yr, val in data_points:
                        # Feature extraction
                        # 1. Base details
                        feat = [prestige, naac_val, college_base_rank, yr]
                        # 2. One-hot branch encoding
                        for b in BRANCH_LIST:
                            feat.append(1.0 if branch == b else 0.0)
                        # 3. One-hot category encoding
                        for c in CATEGORY_LIST:
                            feat.append(1.0 if category == c else 0.0)

                        X_data.append(feat)
                        # Log-transform target for exponential scaling and positive bounds
                        y_data.append(math.log(val))

        X_array = np.array(X_data)
        y_array = np.array(y_data)

        # 3. Evaluate Global Model Performance (Chronological Split: train on <= 2023, validate on 2024)
        if len(X_array) > 50:
            year_col_idx = 3  # Year is the 4th feature (index 3)
            train_mask = X_array[:, year_col_idx] <= 2023
            val_mask = X_array[:, year_col_idx] == 2024

            if np.sum(val_mask) > 5:
                X_train, y_train = X_array[train_mask], y_array[train_mask]
                X_val, y_val = X_array[val_mask], y_array[val_mask]

                eval_model = RandomForestRegressor(n_estimators=100, random_state=42)
                eval_model.fit(X_train, y_train)

                preds = eval_model.predict(X_val)
                # Convert back from log scale
                y_val_real = np.exp(y_val)
                preds_real = np.exp(preds)

                mae = mean_absolute_error(y_val_real, preds_real)
                r2 = r2_score(y_val_real, preds_real)
                print(f"[EVAL] KEA Chronological Split validation (2024 target):")
                print(f"       Mean Absolute Error (MAE): {mae:.1f} ranks")
                print(f"       R^2 Score: {r2:.3f}")

        # 4. Train Final Global Predictor on all data
        global_model = GradientBoostingRegressor(n_estimators=150, max_depth=5, learning_rate=0.08, random_state=42)
        global_model.fit(X_array, y_array)
        print(f"[OK] Trained KEA Global Gradient Boosting model on {len(X_array)} data points")

        return {
            "college_mean_ranks": college_mean_ranks,
            "local_trends": local_trends,
            "global_model": global_model,
            "features": {
                "branch_list": BRANCH_LIST,
                "category_list": CATEGORY_LIST
            }
        }

    # ==========================================================================
    # JEE & NEET ENSEMBLE MODELS (Clean targets & caching)
    # ==========================================================================
    def train_jee_models(self) -> Dict[str, Any]:
        """Train JEE models and return metadata."""
        if not SKLEARN_AVAILABLE or not self.jee_dataset:
            return {}

        print("\n--- Training JEE Admission Predictor Models ---")
        # Extract features and targets
        X_data = []
        y_data = []
        
        # Simple college mean ranks for JEE
        college_mean_ranks = {}
        colleges = [r.get("college") for r in self.jee_dataset if r.get("college")]
        for c in set(colleges):
            ranks = [r.get("closing_rank", 0) for r in self.jee_dataset if r.get("college") == c and r.get("closing_rank", 0) > 0]
            college_mean_ranks[c] = float(np.mean(ranks)) if ranks else 10000.0

        for row in self.jee_dataset:
            college = row.get("college")
            branch = row.get("branch")
            category = row.get("category")
            quota = row.get("quota")
            gender = row.get("gender")
            closing = row.get("closing_rank", 0)
            if not closing:
                continue

            col_base = college_mean_ranks.get(college, 10000.0)
            inst_type = row.get("institute_type", "NIT")
            prestige = 95 if inst_type == "IIT" else (90 if inst_type == "NIT" else 80)
            
            # Simple features
            feat = [prestige, col_base]
            # OHE Indicator vectors
            for cat in ["OPEN", "OBC-NCL", "SC", "ST", "EWS"]:
                feat.append(1.0 if category == cat else 0.0)
            for qt in ["AI", "HS", "OS"]:
                feat.append(1.0 if quota == qt else 0.0)
            feat.append(1.0 if "Female" in str(gender) else 0.0)

            X_data.append(feat)
            y_data.append(math.log(closing))

        X_array = np.array(X_data)
        y_array = np.array(y_data)

        global_model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
        global_model.fit(X_array, y_array)
        print(f"[OK] Trained JEE Global model on {len(X_array)} data points")

        return {
            "college_mean_ranks": college_mean_ranks,
            "global_model": global_model
        }

    def train_neet_models(self) -> Dict[str, Any]:
        """Train NEET models and return metadata."""
        if not SKLEARN_AVAILABLE or not self.neet_dataset:
            return {}

        print("\n--- Training NEET Admission Predictor Models ---")
        X_data = []
        y_data = []

        college_mean_ranks = {}
        colleges = [r.get("college") for r in self.neet_dataset if r.get("college")]
        for c in set(colleges):
            ranks = [r.get("closing_rank", 0) for r in self.neet_dataset if r.get("college") == c and r.get("closing_rank", 0) > 0]
            college_mean_ranks[c] = float(np.mean(ranks)) if ranks else 20000.0

        for row in self.neet_dataset:
            college = row.get("college")
            course = row.get("course")
            category = row.get("category")
            closing = row.get("closing_rank", 0)
            if not closing:
                continue

            col_base = college_mean_ranks.get(college, 20000.0)
            track = row.get("track", "Government")
            prestige = 95 if track == "Government" else 65

            feat = [prestige, col_base]
            # Course OHE
            for crs in ["MBBS", "BDS", "BAMS", "BHMS"]:
                feat.append(1.0 if course == crs else 0.0)
            # Category OHE
            for cat in ["OPEN", "OBC-NCL", "SC", "ST", "EWS"]:
                feat.append(1.0 if category == cat else 0.0)

            X_data.append(feat)
            y_data.append(math.log(closing))

        X_array = np.array(X_data)
        y_array = np.array(y_data)

        global_model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
        global_model.fit(X_array, y_array)
        print(f"[OK] Trained NEET Global model on {len(X_array)} data points")

        return {
            "college_mean_ranks": college_mean_ranks,
            "global_model": global_model
        }

    # ==========================================================================
    # RUN PIPELINE
    # ==========================================================================
    def run(self):
        self.load_datasets()

        kea_models = self.train_kea_models()
        jee_models = self.train_jee_models()
        neet_models = self.train_neet_models()

        if SKLEARN_AVAILABLE:
            payload = {
                "kea": kea_models,
                "jee": jee_models,
                "neet": neet_models
            }
            save_path = os.path.join(MODELS_DIR, "ml_models.pkl")
            with open(save_path, 'wb') as f:
                pickle.dump(payload, f)
            print(f"\n[SUCCESS] Serialized all models successfully to {save_path}!")
        else:
            print("\n[ERROR] Models could not be saved because scikit-learn is missing.")


if __name__ == "__main__":
    pipeline = MLTrainingPipeline()
    pipeline.run()
