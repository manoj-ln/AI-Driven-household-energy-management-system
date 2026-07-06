import sys
from pathlib import Path
# Add backend to path
sys.path.append(str(Path("c:/myproject/backend").resolve()))

from app.services.dataset_service import DatasetService
import time

try:
    print("Testing get_device_time_series(24)...")
    start = time.time()
    series = DatasetService.get_device_time_series(1440)
    end = time.time()
    print(f"Success! Found {len(series)} devices in {end - start:.2f}s")
    if series:
        print(f"First device: {series[0]['device_name']} with {len(series[0]['points'])} points")
except Exception as e:
    import traceback
    traceback.print_exc()
