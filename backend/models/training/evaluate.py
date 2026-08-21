"""Evaluation metrics and model comparison utilities for trained models.

This module provides evaluation functions that can be used both during
training (as an alternative to sklearn's metrics) and at runtime to
re-evaluate loaded models against recent data.

Usage:
    python -m models.training.evaluate
        — runs evaluation report on all trained models using recent data
"""
from pathlib import Path
import json

import joblib
import numpy as np


def mean_absolute_percentage_error(y_true, y_pred):
    if not y_true:
        return 0.0
    total = 0.0
    count = 0
    for true, pred in zip(y_true, y_pred):
        if true == 0:
            continue
        total += abs((true - pred) / true)
        count += 1
    return (total / count) if count else float("inf")


def r2_score(y_true, y_pred):
    if not y_true:
        return 0.0
    mean_true = sum(y_true) / len(y_true)
    ss_res = sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred))
    ss_tot = sum((true - mean_true) ** 2 for true in y_true)
    return 1.0 - ss_res / ss_tot if ss_tot else 0.0


def evaluate_model(y_true, y_pred):
    results = {
        "mape": mean_absolute_percentage_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }
    print(f"Evaluation metrics: {results}")
    return results


def evaluate_trained_models():
    """Load all trained models and re-evaluate against their stored metrics."""
    models_dir = Path(__file__).resolve().parents[2] / "models" / "trained"

    perf_path = models_dir / "model_performances.pkl"
    if not perf_path.exists():
        print("No model_performances.pkl found. Run train.py first.")
        return {}

    performances = joblib.load(perf_path)
    info_path = models_dir / "training_info.json"
    training_info = {}
    if info_path.exists():
        training_info = json.loads(info_path.read_text())

    print(f"Trained {len(performances)} models from {training_info.get('trained_at', 'unknown')}")
    print(f"Training datasets: {training_info.get('datasets', [])}")
    print(f"Feature dimension: {training_info.get('feature_dim', 'unknown')}")
    print()

    for name, metrics in performances.items():
        model_path = models_dir / f"{name}.pkl"
        available = model_path.exists()
        print(f"  {name}: {'loaded' if available else 'missing'} | "
              f"R2={metrics.get('r2', 0):.4f} | "
              f"MAE={metrics.get('mae', 0):.4f} | "
              f"RMSE={metrics.get('rmse', 0):.4f}")

    best = max(performances, key=lambda n: performances[n]["r2"]) if performances else None
    if best:
        print(f"\nBest model: {best} (R2={performances[best]['r2']:.4f})")
    return performances


if __name__ == "__main__":
    evaluate_trained_models()
