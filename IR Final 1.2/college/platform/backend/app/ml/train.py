"""
ML Training Pipeline — trains RF, XGBoost, LightGBM and auto-selects best.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def build_training_data(data_dir: Path) -> Tuple[List[List[float]], List[float]]:
    """Build feature matrix from cutoff_dataset.json and college trends."""
    cutoff_path = data_dir / "cutoff_dataset.json"
    college_path = data_dir / "Production_Ready_Colleges.json"

    if not cutoff_path.exists():
        raise FileNotFoundError(f"Missing {cutoff_path}")

    with open(cutoff_path, "r", encoding="utf-8") as f:
        cutoffs = json.load(f)

    colleges_by_id = {}
    if college_path.exists():
        with open(college_path, "r", encoding="utf-8") as f:
            for c in json.load(f):
                colleges_by_id[c.get("college_id")] = c

    cat_map = {"GM": 0, "OBC": 1, "SC": 2, "ST": 3}
    branch_map = {"CSE": 1, "ECE": 2, "ISE": 3, "EEE": 4, "ME": 5, "CIVIL": 6, "AI": 7, "DS": 8}

    X, y = [], []
    for record in cutoffs:
        cid = record.get("college_id", "")
        college = colleges_by_id.get(cid, {})
        trends = college.get("cutoff_trends", record.get("cutoff_trends", {}))

        for year_str, year_data in trends.items():
            if not isinstance(year_data, dict):
                continue
            for branch, branch_data in year_data.items():
                if not isinstance(branch_data, dict):
                    continue
                for cat, closing_rank in branch_data.items():
                    if not isinstance(closing_rank, (int, float)):
                        continue
                    cat_enc = cat_map.get(cat, 0)
                    branch_enc = branch_map.get(branch, 0)
                    year = int(year_str) if str(year_str).isdigit() else 2024
                    prestige = {"Government": 95, "Government_Aided": 90}.get(
                        college.get("type", ""), 70
                    )
                    X.append([year, cat_enc, branch_enc, prestige, int(closing_rank)])
                    y.append(float(closing_rank))

    if len(X) < 50:
        logger.warning("Only %d training samples — adding synthetic augmentation", len(X))
        for i in range(max(0, 100 - len(X))):
            X.append([2024, i % 4, (i % 8) + 1, 70 + (i % 25), 1000 + i * 50])
            y.append(1000 + i * 50 + (i % 10) * 20)

    return X, y


def train_and_evaluate(
    data_dir: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    """Train RF, XGBoost, LightGBM; save best model."""
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import mean_absolute_error

    X, y = build_training_data(data_dir)
    X_arr = np.array(X)
    y_arr = np.array(y)

    models = {
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
    }

    try:
        import xgboost as xgb
        models["XGBoost"] = xgb.XGBRegressor(n_estimators=100, max_depth=6, random_state=42, verbosity=0)
    except ImportError:
        logger.info("XGBoost not installed — skipping")

    try:
        import lightgbm as lgb
        models["LightGBM"] = lgb.LGBMRegressor(n_estimators=100, max_depth=6, random_state=42, verbose=-1)
    except ImportError:
        logger.info("LightGBM not installed — skipping")

    metrics = {}
    trained = {}

    for name, model in models.items():
        try:
            cv_scores = cross_val_score(model, X_arr, y_arr, cv=min(5, len(X) // 10 or 2), scoring="neg_mean_absolute_error")
            model.fit(X_arr, y_arr)
            preds = model.predict(X_arr)
            mae = mean_absolute_error(y_arr, preds)
            metrics[name] = {"mae": round(mae, 2), "cv_mae": round(-cv_scores.mean(), 2)}
            trained[name] = model
            logger.info("%s: MAE=%.2f CV_MAE=%.2f", name, mae, -cv_scores.mean())
        except Exception as e:
            logger.error("Failed to train %s: %s", name, e)

    if not trained:
        raise RuntimeError("No models trained successfully")

    best_name = min(metrics, key=lambda k: metrics[k]["mae"])
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "models": trained,
        "metrics": metrics,
        "best_model": best_name,
        "feature_names": ["year", "category", "branch", "prestige", "prev_cutoff"],
    }
    out_path = output_dir / "ml_models.pkl"
    with open(out_path, "wb") as f:
        pickle.dump(artifact, f)

    logger.info("Best model: %s saved to %s", best_name, out_path)
    return {"best_model": best_name, "metrics": metrics, "artifact": str(out_path), "samples": len(X)}


if __name__ == "__main__":
    from app.config import get_settings
    s = get_settings()
    result = train_and_evaluate(s.DATA_DIR, s.ML_MODELS_DIR)
    print(json.dumps(result, indent=2))
