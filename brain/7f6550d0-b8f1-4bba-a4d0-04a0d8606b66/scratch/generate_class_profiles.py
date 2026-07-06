
import csv
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import json

def get_device_profiles():
    # 100 total devices categorized by class ownership
    all_devices = {
        "Kitchen": ["Fridge_Main", "Fridge_Mini", "Microwave", "Electric_Kettle", "Coffee_Grinder", "Blender", "Toaster", "Dishwasher", "Induction_Stove", "Air_Fryer", "Oven", "Rice_Cooker", "Slow_Cooker", "Juicer", "Food_Processor", "Mixer", "Wine_Cooler", "Water_Purifier", "Ice_Maker", "Exhaust_Fan"],
        "Living_Room": ["TV_Main", "Soundbar", "Home_Theater", "Gaming_PS5", "Gaming_Xbox", "Nintendo_Switch", "Set_Top_Box", "Floor_Lamp_1", "Floor_Lamp_2", "Ceiling_Fan_Living", "AC_Living", "Smart_Speaker_Living", "Robot_Vacuum_Dock", "Air_Purifier_Living"],
        "Bedroom_Master": ["AC_Master", "Ceiling_Fan_Master", "Bedside_Lamp_L", "Bedside_Lamp_R", "TV_Bedroom", "Laptop_Personal", "Phone_Charger_1", "Humidifier", "Electric_Blanket", "Hair_Dryer"],
        "Bedroom_Guest": ["AC_Guest", "Ceiling_Fan_Guest", "Lamp_Guest", "Laptop_Guest", "Phone_Charger_Guest", "Heater_Guest"],
        "Home_Office": ["Desktop_PC", "Monitor_1", "Monitor_2", "Printer", "Scanner", "Office_Lighting", "Mesh_WiFi_Node", "UPS_Backup", "Phone_Charger_Office", "Paper_Shredder"],
        "Bathroom": ["Geyser_Main", "Geyser_Guest", "Electric_Toothbrush", "Shaver_Charger", "Hair_Straightener", "Exhaust_Fan_Bath", "Mirror_Light"],
        "Utility_Outdoor": ["Washing_Machine", "Clothes_Dryer", "Iron_Box", "Vacuum_Cleaner", "EV_Charger", "Pool_Pump", "Garden_Lights", "Security_Camera_1", "Security_Camera_2", "Security_Camera_3", "Security_Camera_4", "Garage_Door_Opener", "Electric_Gate", "Borewell_Pump", "Sprinkler_System"],
        "Smart_Home_Misc": ["Main_Router", "Smart_Hub", "CCTV_NVR", "Intercom_System", "Doorbell_Camera", "Smart_Lock", "Emergency_Light_1", "Emergency_Light_2", "Air_Compressor", "Power_Tool_Charger"]
    }
    
    # Flat list for CSV headers
    device_list = []
    for cat in all_devices.values():
        device_list.extend(cat)
    while len(device_list) < 100:
        device_list.append(f"Misc_Device_{len(device_list)}")

    # Ownership Filters
    low_class_owns = ["Fridge_Main", "TV_Main", "Ceiling_Fan_Living", "Ceiling_Fan_Master", "Phone_Charger_1", "Exhaust_Fan", "Iron_Box", "Geyser_Main"] + [f"Misc_Device_{i}" for i in range(1, 5)]
    middle_class_owns = low_class_owns + ["Microwave", "Induction_Stove", "Washing_Machine", "Laptop_Personal", "AC_Master", "Water_Purifier", "Mixer", "Set_Top_Box", "WiFi_Router", "Monitor_1", "Printer"] + [f"Misc_Device_{i}" for i in range(5, 15)]
    # High class owns all 100

    return device_list, low_class_owns, middle_class_owns

def precalculate_cache(file_path):
    print(f"Precalculating cache for {file_path.name}...")
    import sys
    sys.path.append(r'c:\myproject\backend')
    from app.services.dataset_cache_service import DatasetCacheService
    rows = DatasetCacheService.load_csv(file_path)
    if not rows: return
    start_ts, end_ts = rows[0]['timestamp'], rows[-1]['timestamp']
    daily_aggregated = {}
    for row in rows:
        date_str = row['timestamp'].date().isoformat()
        if date_str not in daily_aggregated:
            daily_aggregated[date_str] = {"total": 0.0, "temp": 0.0, "count": 0}
        daily_aggregated[date_str]["total"] += row['total_consumption']
        daily_aggregated[date_str]["temp"] += row['temperature']
        daily_aggregated[date_str]["count"] += 1
    daily_history = [{"date": d, "total_consumption": round(v["total"], 3), "average_temperature": round(v["temp"]/v["count"], 1)} for d, v in sorted(daily_aggregated.items())]
    metadata = {"row_count": len(rows), "start": start_ts.isoformat(), "end": end_ts.isoformat(), "daily_history": daily_history}
    with open(file_path.with_suffix('.cache.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f)

def generate_profile(year, output_path, profile_type):
    device_list, low_owns, mid_owns = get_device_profiles()
    owned_list = []
    if profile_type == "low": owned_list = low_owns
    elif profile_type == "middle": owned_list = mid_owns
    else: owned_list = device_list # high class

    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    current_time = start_date
    delta = timedelta(minutes=10)

    # Simple behavior rules
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature', 'humidity', 'total_consumption'] + device_list)
        
        while current_time < end_date:
            hour = current_time.hour
            is_weekend = current_time.weekday() >= 5
            temp = 24 + 6 * math.sin((current_time.month - 4) * math.pi / 6) + random.uniform(-2, 2)
            hum = 55 + random.uniform(-10, 10)
            
            row_vals, total = [], 0.0
            for name in device_list:
                consumption = 0.0
                if name in owned_list:
                    # Generic behavior
                    if "Fridge" in name: consumption = 0.05 if random.random() < 0.3 else 0.01
                    elif "AC" in name and temp > 28: consumption = 1.2
                    elif "Fan" in name: consumption = 0.06
                    elif "TV" in name and 18 <= hour <= 23: consumption = 0.15
                    elif "Light" in name and (hour >= 18 or hour <= 6): consumption = 0.02
                    elif "Geyser" in name and 6 <= hour <= 9: consumption = 2.0
                    elif "EV" in name and 0 <= hour <= 5: consumption = 3.5
                    elif "Microwave" in name and random.random() < 0.05: consumption = 0.8
                    elif "Washing" in name and is_weekend and 8 <= hour <= 12: consumption = 0.5
                    elif random.random() < 0.01: consumption = 0.1 # Random idle
                
                energy = (consumption * 10) / 60
                total += energy
                row_vals.append(round(energy, 4))
            
            writer.writerow([current_time.strftime('%Y-%m-%d %H:%M:%S'), round(temp, 1), round(hum, 1), round(total, 4)] + row_vals)
            current_time += delta
    precalculate_cache(output_path)

if __name__ == "__main__":
    out_dir = Path(r'c:\myproject\backend\data\datasets')
    print("Generating Low Class Profile (2021)...")
    generate_profile(2021, out_dir / 'energy_dataset_2021.csv', "low")
    print("Generating High Class Profile (2024)...")
    generate_profile(2024, out_dir / 'energy_dataset_2024.csv', "high")
    print("Generating Middle Class Profile (2025)...")
    generate_profile(2025, out_dir / 'energy_dataset_2025.csv', "middle")
    print("Process Complete.")
