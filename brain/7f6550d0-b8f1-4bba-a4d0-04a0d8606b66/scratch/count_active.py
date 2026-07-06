import csv
from pathlib import Path

path = Path("c:/myproject/backend/data/datasets/energy_dataset_2024.csv")
with path.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    # Last 144 rows (24 hours at 10-min cadence)
    recent = rows[-144:]
    all_active = set()
    for row in recent:
        for k, v in row.items():
            if k not in ["timestamp", "temperature", "humidity", "total_consumption", "hour", "day_of_week", "is_weekend"]:
                try:
                    if float(v) > 0:
                        all_active.add(k)
                except:
                    pass
    print(f"Active devices in last 24h: {len(all_active)}")
    print(f"Sample active: {list(all_active)[:5]}")
