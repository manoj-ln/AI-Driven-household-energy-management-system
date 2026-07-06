import os
import csv

datasets = ["energy_dataset_2021.csv", "energy_dataset_2024.csv", "energy_dataset_2025.csv"]
base_path = "c:/myproject/backend/data/datasets"

for ds in datasets:
    path = os.path.join(base_path, ds)
    if not os.path.exists(path):
        print(f"File {ds} NOT FOUND")
        continue
    
    with open(path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        # First few cols are metadata: timestamp, temperature, humidity, total_consumption
        devices = header[4:]
        print(f"Dataset: {ds}")
        print(f"  Total columns: {len(header)}")
        print(f"  Device columns: {len(devices)}")
        print(f"  Sample devices: {devices[:5]}...")
        
        # Check row count
        row_count = sum(1 for _ in f)
        print(f"  Rows: {row_count}")
