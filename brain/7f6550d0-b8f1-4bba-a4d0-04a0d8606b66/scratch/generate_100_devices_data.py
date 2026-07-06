
import csv
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import json

def get_100_devices():
    # Define categories and their devices
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
    
    # Fill up to 100 if needed (currently ~95)
    extras = [f"Misc_Device_{i}" for i in range(1, 101 - len(device_list))]
    for e in extras:
        device_list.append((e, "Miscellaneous"))
        
    return device_list

def generate_behavior_aware_100(year, output_path):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    current_time = start_date
    delta = timedelta(minutes=10)

    devices = get_100_devices()
    
    # Assign behavioral properties to each device
    # (base_power_kw, start_prob, duration_range)
    configs = {}
    for name, cat in devices:
        if "Fridge" in name or "Router" in name or "Hub" in name or "Camera" in name or "NVR" in name:
            configs[name] = (0.05, 1.0, (10, 10), "Always-On")
        elif "AC" in name:
            configs[name] = (1.2, 0.1, (60, 240), "Cooling")
        elif "Geyser" in name or "Heater" in name:
            configs[name] = (2.0, 0.05, (20, 45), "Heating")
        elif "Grinder" in name or "Kettle" in name or "Toaster" in name or "Blender" in name:
            configs[name] = (0.5, 0.05, (1, 5), "Morning")
        elif "TV" in name or "Gaming" in name or "Theater" in name or "Soundbar" in name:
            configs[name] = (0.15, 0.2, (60, 180), "Evening")
        elif "Light" in name or "Lamp" in name:
            configs[name] = (0.02, 0.5, (120, 360), "Night")
        elif "EV_Charger" in name:
            configs[name] = (3.5, 0.05, (240, 480), "EV")
        elif "Machine" in name or "Dryer" in name or "Iron" in name:
            configs[name] = (0.8, 0.02, (45, 90), "Weekend")
        else:
            configs[name] = (0.1, 0.05, (10, 60), "Random")

    active_durations = {n: 0 for n in configs}

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        headers = ['timestamp', 'temperature', 'humidity', 'total_consumption'] + [d[0] for d in devices]
        writer.writerow(headers)

        while current_time < end_date:
            hour = current_time.hour
            month = current_time.month
            is_weekend = current_time.weekday() >= 5
            
            temp = 25 + 5 * math.sin((month - 4) * math.pi / 6) + random.uniform(-2, 2)
            hum = 60 + random.uniform(-10, 10)
            
            row_vals = []
            total = 0.0
            
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

def sync_100_devices_db():
    import sys
    sys.path.append(r'c:\myproject\backend')
    from app.services.db_service import DatabaseService
    
    devices = get_100_devices()
    db_list = []
    for i, (name, cat) in enumerate(devices):
        db_list.append({
            "id": i + 1,
            "name": name,
            "category": cat,
            "ratedPower": "RandomW",
            "status": "Running" if random.random() < 0.3 else "Standby",
            "description": f"A realistic {cat} appliance.",
            "smartFeatures": ["AI Optimized", "Remote Control"]
        })
    DatabaseService.sync_devices(db_list)
    print(f"Synced {len(db_list)} devices to DB.")

if __name__ == "__main__":
    out_dir = Path(r'c:\myproject\backend\data\datasets')
    
    # 1. Generate 100-Device Master (3 years)
    print("Generating 100-device Master dataset...")
    # For speed, we'll make the master 2023-2025
    master_file = out_dir / 'energy_dataset_merged_3years.csv'
    # We'll just generate it by combining years
    
    for y in [2021, 2024, 2025]:
        print(f"Generating 100-device dataset for {y}...")
        generate_behavior_aware_100(y, out_dir / f'energy_dataset_{y}.csv')
    
    # 2. Update DB
    sync_100_devices_db()
    
    print("Regeneration complete.")
