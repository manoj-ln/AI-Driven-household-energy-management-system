import requests
import json

try:
    # First select the 2024 dataset
    requests.post("http://127.0.0.1:8000/analytics/datasets/select", json={"dataset_name": "energy_dataset_2024.csv"})
    
    # Get device series
    response = requests.get("http://127.0.0.1:8000/analytics/device-series/24")
    data = response.json()
    print(f"Number of device series: {len(data)}")
    if data:
        print(f"First device: {data[0]['device_name']}")
        print(f"Last device: {data[-1]['device_name']}")
except Exception as e:
    print(f"Error: {e}")
