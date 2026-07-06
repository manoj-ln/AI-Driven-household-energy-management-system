import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

DATASETS_DIR = Path("c:/myproject/backend/data/datasets")

def add_spikes(csv_path):
    print(f"Injecting anomalies into {csv_path.name}...")
    rows = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Inject 5 high usage spikes in the last 2 days
    last_idx = len(rows) - 1
    for _ in range(5):
        idx = random.randint(last_idx - 2880, last_idx) # Last 48 hours
        rows[idx]["total_consumption"] = str(float(rows[idx]["total_consumption"]) * 5.5)
        # Also spike a specific device
        devs = [f for f in fieldnames if f not in ["timestamp", "temperature", "humidity", "total_consumption", "hour", "dayofweek", "isweekend"]]
        if devs:
            dev = random.choice(devs)
            rows[idx][dev] = str(float(rows[idx][dev]) + 2.5)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    for csv_file in DATASETS_DIR.glob("energy_dataset_20*.csv"):
        add_spikes(csv_file)
