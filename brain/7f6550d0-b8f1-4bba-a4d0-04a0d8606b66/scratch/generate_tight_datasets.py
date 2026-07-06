
import csv
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import json

def get_class_definitions():
    # 2021: Low Class (Minimal)
    low_essential = ["Fridge_Main", "TV_Main", "Ceiling_Fan_Living", "Ceiling_Fan_Master", "Phone_Charger_1", "Exhaust_Fan", "Iron_Box", "Geyser_Main"]
    
    # 2025: Middle Class (Comfort)
    middle_essential = low_essential + ["Microwave", "Induction_Stove", "Washing_Machine", "Laptop_Personal", "AC_Master", "Water_Purifier", "Mixer", "Set_Top_Box", "Main_Router", "Monitor_1", "Printer"]
    
    # 2024: High Class (All)
    all_100 = [
        "Fridge_Main", "Fridge_Mini", "Microwave", "Electric_Kettle", "Coffee_Grinder", "Blender", "Toaster", "Dishwasher", "Induction_Stove", "Air_Fryer", "Oven", "Rice_Cooker", "Slow_Cooker", "Juicer", "Food_Processor", "Mixer", "Wine_Cooler", "Water_Purifier", "Ice_Maker", "Exhaust_Fan",
        "TV_Main", "Soundbar", "Home_Theater", "Gaming_PS5", "Gaming_Xbox", "Nintendo_Switch", "Set_Top_Box", "Floor_Lamp_1", "Floor_Lamp_2", "Ceiling_Fan_Living", "AC_Living", "Smart_Speaker_Living", "Robot_Vacuum_Dock", "Air_Purifier_Living",
        "AC_Master", "Ceiling_Fan_Master", "Bedside_Lamp_L", "Bedside_Lamp_R", "TV_Bedroom", "Laptop_Personal", "Phone_Charger_1", "Humidifier", "Electric_Blanket", "Hair_Dryer",
        "AC_Guest", "Ceiling_Fan_Guest", "Lamp_Guest", "Laptop_Guest", "Phone_Charger_Guest", "Heater_Guest",
        "Desktop_PC", "Monitor_1", "Monitor_2", "Printer", "Scanner", "Office_Lighting", "Mesh_WiFi_Node", "UPS_Backup", "Phone_Charger_Office", "Paper_Shredder",
        "Geyser_Main", "Geyser_Guest", "Electric_Toothbrush", "Shaver_Charger", "Hair_Straightener", "Exhaust_Fan_Bath", "Mirror_Light",
        "Washing_Machine", "Clothes_Dryer", "Iron_Box", "Vacuum_Cleaner", "EV_Charger", "Pool_Pump", "Garden_Lights", "Security_Camera_1", "Security_Camera_2", "Security_Camera_3", "Security_Camera_4", "Garage_Door_Opener", "Electric_Gate", "Borewell_Pump", "Sprinkler_System",
        "Main_Router", "Smart_Hub", "CCTV_NVR", "Intercom_System", "Doorbell_Camera", "Smart_Lock", "Emergency_Light_1", "Emergency_Light_2", "Air_Compressor", "Power_Tool_Charger"
    ]
    # Add padding to 100
    while len(all_100) < 100: all_100.append(f"Misc_Device_{len(all_100)}")
    
    return low_essential, middle_essential, all_100

def generate_tight_dataset(year, output_path, devices):
    print(f"Generating tight dataset for {year} with {len(devices)} devices...")
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    current_time = start_date
    delta = timedelta(minutes=10)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature', 'humidity', 'total_consumption'] + devices)
        
        while current_time < end_date:
            hour = current_time.hour
            temp = 22 + 8 * math.sin((current_time.month - 4) * math.pi / 6) + random.uniform(-2, 2)
            hum = 60 + random.uniform(-10, 10)
            
            row_vals, total = [], 0.0
            for name in devices:
                consumption = 0.0
                if "Fridge" in name: consumption = 0.05 if random.random() < 0.2 else 0.01
                elif "AC" in name and temp > 27: consumption = 1.1
                elif "Fan" in name: consumption = 0.06
                elif "TV" in name and 18 <= hour <= 23: consumption = 0.12
                elif "Light" in name and (hour >= 18 or hour <= 6): consumption = 0.02
                elif "Geyser" in name and 6 <= hour <= 9: consumption = 1.8
                elif "EV" in name and 0 <= hour <= 5: consumption = 3.5
                elif random.random() < 0.02: consumption = 0.05
                
                energy = (consumption * 10) / 60
                total += energy
                row_vals.append(round(energy, 4))
            
            writer.writerow([current_time.strftime('%Y-%m-%d %H:%M:%S'), round(temp, 1), round(hum, 1), round(total, 4)] + row_vals)
            current_time += delta

def precalculate_cache(file_path):
    print(f"Caching {file_path.name}...")
    import sys
    sys.path.append(r'c:\myproject\backend')
    from app.services.dataset_cache_service import DatasetCacheService
    rows = DatasetCacheService.load_csv(file_path)
    if not rows: return
    
    # Minimal cache to keep it fast
    metadata = {
        "row_count": len(rows),
        "columns": list(rows[0].keys()),
        "device_count": len(rows[0].keys()) - 4,
        "start": rows[0]['timestamp'].isoformat(),
        "end": rows[-1]['timestamp'].isoformat()
    }
    with open(file_path.with_suffix('.cache.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f)

if __name__ == "__main__":
    out_dir = Path(r'c:\myproject\backend\data\datasets')
    low, mid, high = get_class_definitions()
    
    generate_tight_dataset(2021, out_dir / 'energy_dataset_2021.csv', low)
    precalculate_cache(out_dir / 'energy_dataset_2021.csv')
    
    generate_tight_dataset(2025, out_dir / 'energy_dataset_2025.csv', mid)
    precalculate_cache(out_dir / 'energy_dataset_2025.csv')
    
    generate_tight_dataset(2024, out_dir / 'energy_dataset_2024.csv', high)
    precalculate_cache(out_dir / 'energy_dataset_2024.csv')
    
    print("Tight datasets created. WARNING: Column counts now differ between years.")
