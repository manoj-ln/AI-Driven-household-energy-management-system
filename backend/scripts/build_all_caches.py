"""Build cache files for all datasets."""
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(base_dir))

from app.services.dataset_cache_service import DatasetCacheService

datasets_dir = base_dir / "data" / "datasets"

for csv_path in sorted(datasets_dir.glob("*.csv")):
    print(f"Building cache for {csv_path.name}...", flush=True)
    cache_path = DatasetCacheService.cache_path(csv_path)

    rows = DatasetCacheService.load_csv(csv_path)
    if not rows:
        print(f"  No rows loaded for {csv_path.name}", flush=True)
        continue

    hourly_rows = DatasetCacheService.aggregate_rows(rows, 60)

    def serialize_rows(rows_list):
        return [
            {
                "timestamp": r["timestamp"].isoformat(),
                "hour": r["hour"],
                "day_of_week": r["day_of_week"],
                "is_weekend": r["is_weekend"],
                "temperature": r["temperature"],
                "total_consumption": r["total_consumption"],
                "appliances": r["appliances"],
            }
            for r in rows_list
        ]

    source_row_count = sum(1 for _ in csv_path.open("r", encoding="utf-8")) - 1
    with csv_path.open("r", encoding="utf-8") as source_handle:
        source_handle.readline()
        first_source_row = source_handle.readline().strip().split(",")
    source_start = first_source_row[0] if first_source_row else None
    source_end = None
    with csv_path.open("r", encoding="utf-8") as source_handle:
        for source_line in source_handle:
            if source_line.strip():
                source_end = source_line.split(",", 1)[0]

    # Pre-compute daily history from the retained dashboard window
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

    # Pre-compute pattern summary
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
        "cached_row_count": len(rows),
        "start": rows[0]["timestamp"].isoformat(),
        "end": rows[-1]["timestamp"].isoformat(),
        "source_start": source_start,
        "source_end": source_end,
        "coverage_days": (rows[-1]["timestamp"] - rows[0]["timestamp"]).total_seconds() / 86400.0,
        "cadence_minutes": 1,
        "device_columns": list(rows[0].get("appliances", {}).keys()),
        "recent_minute_rows": serialize_rows(rows[-1440:]),
        "recent_hourly_rows": serialize_rows(hourly_rows[-720:]),
        "daily_history": daily_history,
        "pattern_summary": pattern_summary,
    }

    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)

    print(f"  Cache written: {cache_path.name} ({len(rows)} rows, {len(payload['device_columns'])} devices, {len(daily_history)} daily records)", flush=True)

print("All caches built successfully.", flush=True)
