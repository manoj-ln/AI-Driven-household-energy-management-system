import sys
from pathlib import Path
# Add backend to path
sys.path.append(str(Path("c:/myproject/backend").resolve()))

from app.services.dataset_service import DatasetService

def test_dataset_direct(name, expected_min_devices):
    print(f"\n--- Testing Dataset DIRECT: {name} ---")
    DatasetService.select_dataset(name)
    
    series = DatasetService.get_device_time_series(1440)
    breakdown = DatasetService.get_device_breakdown()
    
    print(f"Device Series count: {len(series)}")
    print(f"Device Breakdown count: {len(breakdown)}")
    
    if len(series) >= expected_min_devices:
        print(f"VERIFIED: {name} code works!")
    else:
        print(f"FAILED: Expected {expected_min_devices}, got {len(series)}")

test_dataset_direct("energy_dataset_2021.csv", 8)
test_dataset_direct("energy_dataset_2025.csv", 19)
test_dataset_direct("energy_dataset_2024.csv", 100)
