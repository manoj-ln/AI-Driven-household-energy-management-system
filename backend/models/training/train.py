"""
End-to-end training pipeline for the runtime prediction models (Random Forest,
XGBoost, LightGBM).

RUNTIME CONTRACT
The deployed models must accept exactly the 25-column feature vector produced
by PredictionService._build_features_for_next_hour (hour/weekday/month flags,
1/2/3/6/12/24h lags, 3/6/12/24h rolling stats, seasonal sin/cos cycles,
appliance placeholders). This script therefore generates its training matrix
with that same builder, using full hourly data read directly from the
production CSV datasets (the analytics cache only keeps the last ~10k minute
rows, which is far too little to fit a probabilistic model).

OUTPUTS (written to models/trained/)
  random_forest.pkl / xgboost.pkl / lightgbm.pkl
  model_performances.pkl   {name: {"r2", "mae", "rmse"}}
  training_info.json       provenance (datasets, feature version, timestamp)

RUN (from backend/):
  python -m models.training.train            # default datasets
  $env:TRAIN_DATASETS="energy_dataset_2021.csv,energy_dataset_2025.csv"
  python -m models.training.train
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.services.prediction_service import PredictionService

DATASETS_DIR = Path(__file__).resolve().parents[2] / "data" / "datasets"
MODELS_DIR = Path(__file__).resolve().parents[2] / "models" / "trained"

DEFAULT_DATASETS = [
    "energy_dataset_2021.csv",
    "energy_dataset_2024.csv",
    "energy_dataset_2025.csv",
]


def load_hourly_series(dataset_names):
    """Aggregate each CSV's minute consumption into hourly totals."""
    records = []
    for name in dataset_names:
        path = DATASETS_DIR / name
        if not path.exists():
            print(f"[skip] {name}: file not found")
            continue
        df = pd.read_csv(path, low_memory=False)
        time_col = next((c for c in df.columns if c.lower() in {"timestamp", "time", "datetime"}), None)
        total_col = next(
            (c for c in df.columns if "total" in c.lower() and "consumption" in c.lower()),
            None,
        )
        if time_col is None or total_col is None:
            print(f"[skip] {name}: unexpected columns {list(df.columns[:6])}")
            continue
        df = df[[time_col, total_col]].copy()
        df.columns = ["ts", "total"]
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts", "total"]).set_index("ts").sort_index()
        hourly = df["total"].resample("1h").sum().dropna()
        records.extend(
            {"timestamp": ts.to_pydatetime(), "total_consumption": float(val)}
            for ts, val in hourly.items()
        )
        print(f"[data] {name}: {len(hourly)} hourly rows")
    return sorted(records, key=lambda row: row["timestamp"])


def build_feature_matrix(records):
    """Records -> (X, y) in the exact runtime feature space."""
    X, y = [], []
    for i in range(24, len(records)):
        window = records[max(0, i - 24):i]
        X.append(PredictionService._build_features_for_next_hour(window))
        y.append(float(records[i]["total_consumption"]))
    return np.asarray(X, dtype=float), np.asarray(y, dtype=float)


def _xgboost_model():
    try:
        import xgboost as xgb

        return xgb.XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1
        )
    except ImportError:
        return None


def _lightgbm_model():
    try:
        import lightgbm as lgb

        return lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            verbosity=-1,
        )
    except ImportError:
        return None


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    raw = os.getenv("TRAIN_DATASETS", ",".join(DEFAULT_DATASETS))
    dataset_names = [name.strip() for name in raw.split(",") if name.strip()]
    records = load_hourly_series(dataset_names)
    if len(records) < 24 * 10:
        raise SystemExit(f"Not enough data to train ({len(records)} hourly rows)")

    X, y = build_feature_matrix(records)
    print(f"[features] shape={X.shape} (expect 25 runtime columns)")

    split = int(len(X) * 0.8)
    X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]
    print(f"[split] train={len(X_train)} test={len(X_test)}")

    estimators = {
        "random_forest": RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
        "xgboost": _xgboost_model(),
        "lightgbm": _lightgbm_model(),
    }

    performances = {}
    for name, estimator in estimators.items():
        if estimator is None:
            print(f"[skip] {name}: library unavailable")
            continue
        estimator.fit(X_train, y_train)
        pred = estimator.predict(X_test)
        metrics = {
            "r2": float(r2_score(y_test, pred)),
            "mae": float(mean_absolute_error(y_test, pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
        }
        performances[name] = metrics
        joblib.dump(estimator, MODELS_DIR / f"{name}.pkl")
        print(f"[done] {name}: {metrics}")

    if not performances:
        raise SystemExit("No models could be trained.")

    joblib.dump(performances, MODELS_DIR / "model_performances.pkl")

    info = {
        "datasets": dataset_names,
        "hourly_rows": len(records),
        "samples": len(X),
        "feature_dim": int(X.shape[1]),
        "metrics": performances,
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    (MODELS_DIR / "training_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    best = max(performances, key=lambda name: performances[name]["r2"])
    print(f"\nBest model: {best} (r2={performances[best]['r2']:.4f})")
    print(f"Artifacts written to {MODELS_DIR}")


if __name__ == "__main__":
    main()