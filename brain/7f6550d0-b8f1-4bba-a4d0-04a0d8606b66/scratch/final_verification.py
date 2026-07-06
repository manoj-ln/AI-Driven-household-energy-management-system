import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_dataset(name, expected_min_devices):
    print(f"\n--- Testing Dataset: {name} ---")
    # Select dataset
    sel_resp = requests.post(f"{BASE_URL}/analytics/datasets/select", json={"dataset_name": name})
    if sel_resp.status_code != 200:
        print(f"FAILED to select {name}: {sel_resp.text}")
        return
    
    # Get device series
    series_resp = requests.get(f"{BASE_URL}/analytics/device-series/24")
    series_data = series_resp.json()
    
    # Get breakdown
    breakdown_resp = requests.get(f"{BASE_URL}/analytics/device-breakdown")
    breakdown_data = breakdown_resp.json()
    
    print(f"Device Series count: {len(series_data)}")
    print(f"Device Breakdown count: {len(breakdown_data)}")
    
    if len(series_data) >= expected_min_devices and len(breakdown_data) >= expected_min_devices:
        print(f"VERIFIED: {name} shows at least {expected_min_devices} devices.")
        if series_data:
            print(f"Top device in series: {series_data[0]['device_name']} ({series_data[0]['total_energy_kwh']} kWh)")
    else:
        print(f"WARNING: Expected at least {expected_min_devices}, but got {len(series_data)} series and {len(breakdown_data)} breakdown items.")

# Test all three socioeconomic profiles
test_dataset("energy_dataset_2021.csv", 8)   # Low Class
test_dataset("energy_dataset_2025.csv", 19)  # Middle Class
test_dataset("energy_dataset_2024.csv", 100) # High Class
