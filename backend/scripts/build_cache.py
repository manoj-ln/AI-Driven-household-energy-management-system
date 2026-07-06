import sys
from pathlib import Path
import json
from datetime import datetime

base_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(base_dir))

from app.services.dataset_cache_service import DatasetCacheService

dataset_path = base_dir / "data" / "datasets" / "energy_dataset_50k_plus.csv"
print(f"Loading {dataset_path}...")
rows = DatasetCacheService.load_csv(dataset_path)
print(f"Loaded {len(rows)} rows.")

hourly_rows = DatasetCacheService.aggregate_rows(rows, 60)
print(f"Aggregated {len(hourly_rows)} hourly rows.")

cache_path = DatasetCacheService.cache_path(dataset_path)

# Prepare recent rows (convert datetime to isoformat)
def serialize_rows(rows_list):
    res = []
    for r in rows_list:
        new_r = r.copy()
        new_r["timestamp"] = new_r["timestamp"].isoformat()
        res.append(new_r)
    return res

payload = {
    "row_count": len(rows),
    "start": rows[0]["timestamp"].isoformat() if rows else None,
    "end": rows[-1]["timestamp"].isoformat() if rows else None,
    "coverage_days": len(hourly_rows) / 24.0,
    "cadence_minutes": 1,
    "device_columns": list(rows[0].get("appliances", {}).keys()) if rows else [],
    "recent_minute_rows": serialize_rows(rows[-1440:]), # last 24 hours
    "recent_hourly_rows": serialize_rows(hourly_rows[-720:]) # last 30 days
}

with cache_path.open("w", encoding="utf-8") as f:
    json.dump(payload, f)

print(f"Cache written to {cache_path}")
