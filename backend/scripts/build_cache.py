"""Build cache file for one or all energy datasets.

Usage:
    python -m scripts.build_cache              # default dataset
    python -m scripts.build_cache energy_dataset_2024.csv
    python -m scripts.build_cache --all        # all production CSVs

If no dataset is specified, it falls back to the default set used by the
training pipeline so the script always has a valid target.
"""
import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.services.dataset_cache_service import DatasetCacheService
from app.services.dataset_service import DatasetService

DEFAULT_DATASETS = [
    "energy_dataset_2021.csv",
    "energy_dataset_2024.csv",
    "energy_dataset_2025.csv",
]


def build_one(dataset_name: str):
    dataset_path = BASE_DIR / "data" / "datasets" / dataset_name
    if not dataset_path.exists():
        print(f"  [skip] {dataset_name}: file not found")
        return

    print(f"  Loading {dataset_name}...", flush=True)
    rows = DatasetCacheService.load_csv(dataset_path)
    cached_row_count = len(rows)
    print(f"  Loaded {cached_row_count} cached rows.", flush=True)

    source_row_count = sum(1 for _ in dataset_path.open("r", encoding="utf-8")) - 1
    with dataset_path.open("r", encoding="utf-8") as source_handle:
        source_handle.readline()
        source_first = source_handle.readline().strip().split(",")
    source_start = source_first[0] if source_first else None
    source_end = None
    with dataset_path.open("r", encoding="utf-8") as source_handle:
        for source_line in source_handle:
            if source_line.strip():
                source_end = source_line.split(",", 1)[0]

    hourly_rows = DatasetCacheService.aggregate_rows(rows, 60)
    print(f"  Aggregated {len(hourly_rows)} hourly rows.", flush=True)

    cache_path = DatasetCacheService.cache_path(dataset_path)

    def serialize_rows(rows_list):
        res = []
        for r in rows_list:
            new_r = r.copy()
            new_r["timestamp"] = new_r["timestamp"].isoformat()
            res.append(new_r)
        return res

    from collections import Counter
    from datetime import datetime

    daily_history = []
    if rows:
        day_buckets = {}
        for row in rows:
            date_key = row["timestamp"].date().isoformat()
            if date_key not in day_buckets:
                day_buckets[date_key] = {"total": 0.0, "temp_sum": 0.0, "count": 0}
            day_buckets[date_key]["total"] += row["total_consumption"]
            day_buckets[date_key]["temp_sum"] += row["temperature"]
            day_buckets[date_key]["count"] += 1

        for date_key in sorted(day_buckets.keys()):
            b = day_buckets[date_key]
            daily_history.append({
                "date": date_key,
                "total_consumption": round(b["total"], 3),
                "average_temperature": round(b["temp_sum"] / b["count"], 1) if b["count"] else 24.0,
            })

    month_distribution = Counter()
    season_distribution = Counter()
    day_period_distribution = Counter()
    temperatures = []
    invalid_records = 0

    for row in rows:
        ts = row["timestamp"]
        if not ts or row.get("total_consumption", 0) < 0:
            invalid_records += 1
            continue
        month_distribution[ts.strftime("%b")] += 1
        season = "Winter" if ts.month in (12, 1, 2) else "Summer" if ts.month in (3, 4, 5) else "Monsoon" if ts.month in (6, 7, 8, 9) else "Post-Monsoon"
        season_distribution[season] += 1
        if 4 <= ts.hour < 7:
            period = "early_morning"
        elif 7 <= ts.hour < 12:
            period = "morning"
        elif 12 <= ts.hour < 17:
            period = "afternoon"
        elif 17 <= ts.hour < 21:
            period = "evening"
        elif 21 <= ts.hour < 24:
            period = "night"
        else:
            period = "late_night"
        day_period_distribution[period] += 1
        temp = row.get("temperature")
        if temp is not None:
            temperatures.append(float(temp))
            if temp < -10 or temp > 60:
                invalid_records += 1

    score_penalty = min(60, invalid_records * 5)
    quality_score = max(40, 100 - score_penalty)
    notes = []
    if invalid_records == 0:
        notes.append("No invalid timestamps or negative energy values were found in the normalized dataset.")
    else:
        notes.append(f"{invalid_records} records look suspicious and should be reviewed.")

    if len(month_distribution) < 2:
        notes.append("Month coverage is narrow, so season-level conclusions are limited.")
    else:
        notes.append("Month and season coverage is wide enough for a presentation-level pattern summary.")

    pattern_summary = {
        "record_count": len(rows),
        "quality_score": quality_score,
        "invalid_records": invalid_records,
        "temperature_range": f"{min(temperatures):.1f} C to {max(temperatures):.1f} C" if temperatures else "No temperature data",
        "dominant_season": season_distribution.most_common(1)[0][0] if season_distribution else "Unknown",
        "dominant_day_period": day_period_distribution.most_common(1)[0][0] if day_period_distribution else "Unknown",
        "month_distribution": dict(month_distribution),
        "season_distribution": dict(season_distribution),
        "day_period_distribution": dict(day_period_distribution),
        "notes": notes,
    }

    payload = {
        "row_count": source_row_count,
        "source_row_count": source_row_count,
        "cached_row_count": cached_row_count,
        "start": rows[0]["timestamp"].isoformat(),
        "end": rows[-1]["timestamp"].isoformat(),
        "source_start": source_start,
        "source_end": source_end,
        "coverage_days": (rows[-1]["timestamp"] - rows[0]["timestamp"]).total_seconds() / 86400.0,
        "cadence_minutes": 1,
        "device_columns": list(rows[0].get("appliances", {}).keys()) if rows else [],
        "recent_minute_rows": serialize_rows(rows[-1440:]),
        "recent_hourly_rows": serialize_rows(hourly_rows[-720:]),
        "daily_history": daily_history,
        "pattern_summary": pattern_summary,
    }

    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)

    print(f"  Cache written: {cache_path.name} ({len(rows)} rows, {len(payload['device_columns'])} devices, {len(daily_history)} daily records)", flush=True)


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--all":
        datasets = DatasetService.list_datasets()
        for name in datasets:
            build_one(name)
    else:
        build_one(args[0])
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
