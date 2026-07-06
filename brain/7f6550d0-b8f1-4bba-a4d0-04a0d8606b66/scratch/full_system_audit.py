import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

def audit_endpoint(name, url, method="GET", json_data=None):
    print(f"Testing {name} ({url})...", end=" ")
    try:
        # Increase timeout to 15s for the initial large file load
        if method == "GET":
            r = requests.get(f"{BASE_URL}{url}", timeout=15)
        else:
            r = requests.post(f"{BASE_URL}{url}", json=json_data, timeout=15)
        
        if r.status_code == 200:
            print("OK")
            return r.json()
        else:
            print(f"FAILED (Status {r.status_code})")
            print(f"Error: {r.text}")
            return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

def full_audit():
    print("=== STARTING FULL SYSTEM AUDIT ===\n")
    
    # 1. Basic Health
    audit_endpoint("Datasets List", "/analytics/datasets")
    
    # 2. Socioeconomic Profiles Verification
    profiles = [
        ("Low Class", "energy_dataset_2021.csv", 8),
        ("Middle Class", "energy_dataset_2025.csv", 19),
        ("High Class", "energy_dataset_2024.csv", 100)
    ]
    
    for label, ds, expected_devs in profiles:
        print(f"\nVerifying {label}...")
        sel = audit_endpoint(f"Select {ds}", "/analytics/datasets/select", "POST", {"dataset_name": ds})
        if sel:
            series = audit_endpoint("Device Series", "/analytics/device-series/24")
            if series:
                # Count only devices that aren't metadata fallbacks
                actual_devs = len([d for d in series if d.get('category') != 'Essentials' or d.get('device_id') not in ['total_consumption', 'temperature', 'humidity']])
                if actual_devs >= expected_devs:
                    print(f"  SUCCESS: Found {actual_devs} devices for {label}.")
                else:
                    print(f"  CRITICAL: Found only {actual_devs} devices for {label}. Expected {expected_devs}!")

    # 3. Analytics Summary & Insights
    audit_endpoint("Summary", "/analytics/summary")
    audit_endpoint("Pattern Insights", "/analytics/pattern-insights")
    
    # 4. Predictions (Explainability)
    audit_endpoint("Explain Next", "/predictions/explain-next")
    
    print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    # Note: This assumes the server IS running.
    full_audit()
