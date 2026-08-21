"""Preprocess raw CSV datasets into a feature-rich training format.

Reads a wide-format energy dataset CSV, derives time-based features
(hour, day_of_week, month, is_weekend, is_peak_hour), and writes a
processed CSV suitable for model training.

Usage:
    python -m models.training.preprocess <input_csv> <output_csv>

If no arguments are given, it processes all production datasets
(energy_dataset_2021.csv, energy_dataset_2024.csv, energy_dataset_2025.csv)
from the data/datasets/ directory.
"""
from pathlib import Path

import pandas as pd


def preprocess_energy_data(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)

    time_col = next((c for c in df.columns if c.lower() in {"timestamp", "time", "datetime"}), None)
    if time_col is None:
        raise ValueError(f"No timestamp column found in {input_path}. Columns: {list(df.columns[:6])}")

    total_col = next(
        (c for c in df.columns if "total" in c.lower() and "consumption" in c.lower()),
        None,
    )
    if total_col is None:
        total_cols = [c for c in df.columns if "consumption" in c.lower() or "energy" in c.lower()]
        if not total_cols:
            raise ValueError(f"No total consumption column found in {input_path}")
        total_col = total_cols[0]

    df["timestamp"] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()

    if time_col != "timestamp":
        df = df.drop(columns=[time_col])

    df["hour"] = df.index.hour
    df["day_of_week"] = df.index.dayofweek
    df["month"] = df.index.month
    df["is_weekend"] = (df.index.dayofweek >= 5).astype(int)
    df["is_peak_hour"] = ((df.index.hour >= 18) & (df.index.hour <= 22)).astype(int)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=True, index_label="timestamp")
    print(f"Processed data saved to {output_path}, shape: {df.shape}")


def _default_datasets():
    base_dir = Path(__file__).resolve().parents[2]
    datasets_dir = base_dir / "data" / "datasets"
    names = ["energy_dataset_2021.csv", "energy_dataset_2024.csv", "energy_dataset_2025.csv"]
    return [(name, datasets_dir / name) for name in names if (datasets_dir / name).exists()]


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if len(args) >= 2:
        preprocess_energy_data(args[0], args[1])
    else:
        base_dir = Path(__file__).resolve().parents[2]
        processed_dir = base_dir / "data" / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        for name, path in _default_datasets():
            output_path = processed_dir / f"processed_{name}"
            try:
                preprocess_energy_data(str(path), str(output_path))
            except Exception as e:
                print(f"[skip] {name}: {e}")
        print(f"All datasets processed into {processed_dir}")
