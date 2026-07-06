
import csv
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import json

def get_100_devices():
    categories = {
        "Kitchen": ["Fridge_Main", "Fridge_Mini", "Microwave", "Electric_Kettle", "Coffee_Grinder", "Blender", "Toaster", "Dishwasher", "Induction_Stove", "Air_Fryer", "Oven", "Rice_Cooker", "Slow_Cooker", "Juicer", "Food_Processor", "Mixer", "Wine_Cooler", "Water_Purifier", "Ice_Maker", "Exhaust_Fan"],
        "Living_Room": ["TV_Main", "Soundbar", "Home_Theater", "Gaming_PS5", "Gaming_Xbox", "Nintendo_Switch", "Set_Top_Box", "Floor_Lamp_1", "Floor_Lamp_2", "Ceiling_Fan_Living", "AC_Living", "Smart_Speaker_Living", "Robot_Vacuum_Dock", "Air_Purifier_Living"],
        "Bedroom_Master": ["AC_Master", "Ceiling_Fan_Master", "Bedside_Lamp_L", "Bedside_Lamp_R", "TV_Bedroom", "Laptop_Personal", "Phone_Charger_1", "Humidifier", "Electric_Blanket", "Hair_Dryer"],
        "Bedroom_Guest": ["AC_Guest", "Ceiling_Fan_Guest", "Lamp_Guest", "Laptop_Guest", "Phone_Charger_Guest", "Heater_Guest"],
        "Home_Office": ["Desktop_PC", "Monitor_1", "Monitor_2", "Printer", "Scanner", "Office_Lighting", "Mesh_WiFi_Node", "UPS_Backup", "Phone_Charger_Office", "Paper_Shredder"],
        "Bathroom": ["Geyser_Main", "Geyser_Guest", "Electric_Toothbrush", "Shaver_Charger", "Hair_Straightener", "Exhaust_Fan_Bath", "Mirror_Light"],
        "Utility_Outdoor": ["Washing_Machine", "Clothes_Dryer", "Iron_Box", "Vacuum_Cleaner", "EV_Charger", "Pool_Pump", "Garden_Lights", "Security_Camera_1", "Security_Camera_2", "Security_Camera_3", "Security_Camera_4", "Garage_Door_Opener", "Electric_Gate", "Borewell_Pump", "Sprinkler_System"],
        "Smart_Home_Misc": ["Main_Router", "Smart_Hub", "CCTV_NVR", "Intercom_System", "Doorbell_Camera", "Smart_Lock", "Emergency_Light_1", "Emergency_Light_2", "Air_Compressor", "Power_Tool_Charger"]
    }
    device_list = []
    for cat, names in categories.items():
        for name in names:
            device_list.append((name, cat))
    extras = [f"Misc_Device_{i}" for i in range(1, 101 - len(device_list))]
    for e in extras:
        device_list.append((e, "Miscellaneous"))
    return device_list

def precalculate_cache(file_path):
    print(f"Precalculating cache for {file_path.name}...")
    import sys
    sys.path.append(r'c:\myproject\backend')
    from app.services.dataset_cache_service import DatasetCacheService
    
    rows = DatasetCacheService.load_csv(file_path)
    if not rows: return
    
    start_ts = rows[0]['timestamp']
    end_ts = rows[-1]['timestamp']
    coverage_days = (end_ts - start_ts).total_seconds() / 86400.0
    
    daily_aggregated = {}
    for row in rows:
        date_str = row['timestamp'].date().isoformat()
        if date_str not in daily_aggregated:
            daily_aggregated[date_str] = {"total": 0.0, "temp": 0.0, "count": 0}
        daily_aggregated[date_str]["total"] += row['total_consumption']
        daily_aggregated[date_str]["temp"] += row['temperature']
        daily_aggregated[date_str]["count"] += 1
    
    daily_history = []
    for date_str in sorted(daily_aggregated.keys()):
        data = daily_aggregated[date_str]
        daily_history.append({
            "date": date_str,
            "total_consumption": round(data["total"], 3),
            "average_temperature": round(data["temp"] / data["count"], 1)
        })

    metadata = {
        "row_count": len(rows),
        "start": start_ts.isoformat(),
        "end": end_ts.isoformat(),
        "coverage_days": round(coverage_days, 2),
        "daily_history": daily_history,
        "pattern_insights": {"dominant_season": "☀️ Summer", "quality_score": 100, "device_count": 100}
    }
    with open(file_path.with_suffix('.cache.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f)

def generate_range(start_year, end_year, output_path):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year + 1, 1, 1)
    current_time = start_date
    delta = timedelta(minutes=10)
    devices = get_100_devices()
    configs = {}
    for name, cat in devices:
        if any(x in name for x in ["Fridge", "Router", "Hub", "Camera", "NVR", "Purifier"]):
            configs[name] = (0.05, 1.0, (10, 10), "Always-On")
        elif "AC" in name: configs[name] = (1.2, 0.1, (60, 240), "Cooling")
        elif "Geyser" in name or "Heater" in name: configs[name] = (2.0, 0.05, (20, 45), "Heating")
        elif any(x in name for x in ["Grinder", "Kettle", "Toaster", "Blender"]): configs[name] = (0.5, 0.05, (1, 5), "Morning")
        elif any(x in name for x in ["TV", "Gaming", "Theater", "Soundbar"]): configs[name] = (0.15, 0.2, (60, 180), "Evening")
        elif "Light" in name or "Lamp" in name: configs[name] = (0.02, 0.5, (120, 360), "Night")
        elif "EV_Charger" in name: configs[name] = (3.5, 0.05, (240, 480), "EV")
        elif any(x in name for x in ["Machine", "Dryer", "Iron"]): configs[name] = (0.8, 0.02, (45, 90), "Weekend")
        else: configs[name] = (0.1, 0.05, (10, 60), "Random")

    active_durations = {n: 0 for n in configs}
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature', 'humidity', 'total_consumption'] + [d[0] for d in devices])
        while current_time < end_date:
            hour, month = current_time.hour, current_time.month
            is_weekend = current_time.weekday() >= 5
            temp = 25 + 5 * math.sin((month - 4) * math.pi / 6) + random.uniform(-2, 2)
            hum = 60 + random.uniform(-10, 10)
            row_vals, total = [], 0.0
            for name, config in configs.items():
                pwr, prob, dur, behavior = config
                consumption = 0.0
                if active_durations[name] > 0:
                    active_durations[name] -= 10
                    consumption = pwr
                else:
                    trigger = False
                    if behavior == "Always-On": consumption = pwr
                    elif behavior == "Cooling" and temp > 27 and random.random() < 0.1: trigger = True
                    elif behavior == "Heating" and temp < 18 and random.random() < 0.1: trigger = True
                    elif behavior == "Morning" and 7 <= hour <= 9 and random.random() < 0.1: trigger = True
                    elif behavior == "Evening" and 18 <= hour <= 23 and random.random() < 0.2: trigger = True
                    elif behavior == "Night" and 18 <= hour <= 24 and random.random() < 0.5: consumption = pwr
                    elif behavior == "EV" and 0 <= hour <= 5 and random.random() < 0.1: trigger = True
                    elif behavior == "Weekend" and is_weekend and random.random() < 0.05: trigger = True
                    elif behavior == "Random" and random.random() < 0.01: trigger = True
                    if trigger:
                        active_durations[name] = random.randint(dur[0], dur[1])
                        consumption = pwr
                energy = (consumption * 10) / 60
                total += energy
                row_vals.append(round(energy, 4))
            writer.writerow([current_time.strftime('%Y-%m-%d %H:%M:%S'), round(temp, 1), round(hum, 1), round(total, 4)] + row_vals)
            current_time += delta
    precalculate_cache(output_path)

if __name__ == "__main__":
    out_dir = Path(r'c:\myproject\backend\data\datasets')
    print("Regenerating 100-device ecosystem...")
    generate_range(2021, 2021, out_dir / 'energy_dataset_2021.csv')
    generate_range(2024, 2024, out_dir / 'energy_dataset_2024.csv')
    generate_range(2025, 2025, out_dir / 'energy_dataset_2025.csv')
    print("Generating 100-device 3-year Master (2023-2025)...")
    generate_range(2023, 2025, out_dir / 'energy_dataset_merged_3years.csv')
    print("All 100-device datasets and caches updated.")
