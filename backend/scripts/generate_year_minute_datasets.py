import os
import csv
from datetime import datetime, timedelta
import random

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datasets_dir = os.path.join(base_dir, "data", "datasets")
    frontend_datasets_dir = os.path.join(base_dir, "..", "frontend", "public", "datasets")
    
    os.makedirs(datasets_dir, exist_ok=True)
    os.makedirs(frontend_datasets_dir, exist_ok=True)

    start_date = datetime(2023, 11, 1, 0, 0, 0)
    end_date = datetime(2024, 1, 1, 0, 0, 0) # exactly 61 days -> 87840 rows
    
    filename = "energy_dataset_50k_plus.csv"
    
    filepath_backend = os.path.join(datasets_dir, filename)
    filepath_frontend = os.path.join(frontend_datasets_dir, filename)

    print(f"Generating 50000+ rows dataset with 100+ devices: {filename}...")
    
    standard_headers = [
        "Timestamp", "Hour", "DayOfWeek", "IsWeekend", "Temperature",
        "Lighting_LED", "Lighting_Tube", "Cooling_Fan_Ceiling", "Cooling_Fan_Table", "Cooling_AC", "Cooling_Cooler",
        "Electronics_TV", "Electronics_Laptop", "Electronics_Desktop", "Electronics_Charger", "Electronics_WiFi",
        "Kitchen_Microwave", "Kitchen_Induction", "Kitchen_Kettle", "Kitchen_Mixer", "Kitchen_Toaster", "Kitchen_Coffee",
        "Utility_Washing", "Utility_Dishwasher", "Utility_Vacuum", "Utility_Iron",
        "Heating_Water", "Heating_Room",
        "Smart_Speaker", "Smart_CCTV", "Smart_Purifier", "Smart_Humidifier",
        "Others_Refrigerator", "Others_Purifier", "Others_Exhaust"
    ]
    
    # 100 realistic extra device names
    real_device_names = [
        "Smart_Bulb_Living", "Smart_Bulb_Kitchen", "Smart_Bulb_Bed", "Smart_Plug_TV", "Smart_Plug_PC",
        "Air_Purifier_Living", "Air_Purifier_Bed", "Dehumidifier_Basement", "Humidifier_Bed", "Robot_Vacuum",
        "Cordless_Vacuum", "Electric_Mop", "Smart_Speaker_Living", "Smart_Speaker_Bed", "Smart_Display_Kitchen",
        "Security_Camera_Front", "Security_Camera_Back", "Video_Doorbell", "Smart_Lock_Front", "Smart_Thermostat",
        "Gaming_Console_PS", "Gaming_Console_Xbox", "Nintendo_Switch", "VR_Headset_Charger", "Gaming_PC_Monitor",
        "Office_Monitor_1", "Office_Monitor_2", "Laptop_Work", "Laptop_Personal", "Tablet_Charger_1",
        "Tablet_Charger_2", "Phone_Charger_Living", "Phone_Charger_Bed1", "Phone_Charger_Bed2", "Smartwatch_Charger",
        "Electric_Toothbrush_1", "Electric_Toothbrush_2", "Water_Flosser", "Hair_Dryer", "Hair_Straightener",
        "Electric_Shaver", "Curling_Iron", "Treadmill", "Exercise_Bike", "Massage_Chair",
        "Heating_Pad", "Electric_Blanket_1", "Electric_Blanket_2", "Coffee_Grinder", "Espresso_Machine",
        "Milk_Frother", "Electric_Kettle_Tea", "Toaster_Oven", "Waffle_Maker", "Stand_Mixer",
        "Hand_Mixer", "Food_Processor", "Blender_Smoothie", "Juicer", "Slow_Cooker",
        "Pressure_Cooker_Electric", "Rice_Cooker_Smart", "Air_Fryer", "Deep_Fryer", "Bread_Maker",
        "Ice_Cream_Maker", "Popcorn_Machine", "Wine_Cooler", "Mini_Fridge_Drinks", "Chest_Freezer",
        "Water_Dispenser", "Ice_Maker", "Trash_Compactor", "Garage_Door_Opener", "Electric_Gate_Motor",
        "Pool_Pump", "Hot_Tub_Heater", "Sprinkler_System", "Outdoor_Lighting_Landscape", "Patio_Heater",
        "Electric_Grill", "Mosquito_Zapper", "Power_Tool_Charger", "Air_Compressor", "Shop_Vac",
        "Sewing_Machine", "Ironing_Station", "Clothes_Steamer", "Shoe_Polisher", "Aquarium_Filter",
        "Aquarium_Light", "Terrarium_Heater", "Pet_Feeder_Automatic", "Pet_Water_Fountain", "Baby_Monitor_Camera",
        "Bottle_Warmer", "Breast_Pump", "Night_Light_Hallway", "Night_Light_Bath", "White_Noise_Machine",
        "Projector_Home_Theater", "Soundbar", "Subwoofer", "Record_Player", "AV_Receiver",
        "Router_Main", "Mesh_WiFi_Node_1", "Mesh_WiFi_Node_2", "NAS_Storage", "Network_Switch"
    ]
    
    # Ensure exactly 100 devices
    extra_devices = real_device_names[:100]
    
    all_headers = standard_headers + extra_devices + ["Total_Consumption"]
    
    with open(filepath_backend, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(all_headers)
        
        current = start_date
        while current < end_date:
            hour = current.hour
            month = current.month
            day = current.weekday()
            is_weekend = 1 if day >= 5 else 0
            
            temp = random.uniform(15.0, 25.0)
            
            # Base standard loads
            cooling_ac = random.uniform(0.5, 1.2) if temp > 22 and hour > 12 and hour < 18 else 0.0
            heating_room = random.uniform(1.0, 2.0) if temp < 18 and (hour < 7 or hour > 19) else 0.0
            others_refrigerator = random.uniform(0.05, 0.1)
            lighting_led = random.uniform(0.02, 0.06) if (hour < 7 or hour > 17) else 0.0
            utility_washing = random.uniform(0.3, 0.8) if is_weekend and hour == 10 else 0.0
            cooling_fan = random.uniform(0.02, 0.08) if hour > 8 and hour < 22 else random.uniform(0.01, 0.03)
            
            row_dict = {
                "Timestamp": current.isoformat(),
                "Hour": hour,
                "DayOfWeek": day,
                "IsWeekend": is_weekend,
                "Temperature": round(temp, 1),
                "Lighting_LED": round(lighting_led, 3),
                "Lighting_Tube": round(random.uniform(0, 0.05) if lighting_led > 0 else 0, 3),
                "Cooling_Fan_Ceiling": round(cooling_fan, 3),
                "Cooling_Fan_Table": 0,
                "Cooling_AC": round(cooling_ac, 3),
                "Cooling_Cooler": 0,
                "Electronics_TV": round(random.uniform(0.05, 0.15) if hour > 18 else 0, 3),
                "Electronics_Laptop": round(random.uniform(0.02, 0.06) if hour > 8 and hour < 23 else 0, 3),
                "Electronics_Desktop": 0,
                "Electronics_Charger": 0.01,
                "Electronics_WiFi": 0.01,
                "Kitchen_Microwave": round(random.uniform(0.8, 1.2) if hour in [8, 13, 19] else 0, 3),
                "Kitchen_Induction": 0,
                "Kitchen_Kettle": 0,
                "Kitchen_Mixer": 0,
                "Kitchen_Toaster": 0,
                "Kitchen_Coffee": 0,
                "Utility_Washing": round(utility_washing, 3),
                "Utility_Dishwasher": 0,
                "Utility_Vacuum": 0,
                "Utility_Iron": 0,
                "Heating_Water": round(random.uniform(1.5, 2.0) if hour in [7, 8] else 0, 3),
                "Heating_Room": round(heating_room, 3),
                "Smart_Speaker": 0.005,
                "Smart_CCTV": 0.01,
                "Smart_Purifier": 0,
                "Smart_Humidifier": 0,
                "Others_Refrigerator": round(others_refrigerator, 3),
                "Others_Purifier": 0,
                "Others_Exhaust": 0
            }
            
            total_consumption = sum(v for k, v in row_dict.items() if isinstance(v, (int, float)) and k not in ["Hour", "DayOfWeek", "IsWeekend", "Temperature"])
            
            # 100 extra devices
            extra_vals = []
            for i in range(100):
                val = round(random.uniform(0, 0.005), 4) # tiny background load
                extra_vals.append(val)
                total_consumption += val
                
            row = [row_dict[k] for k in standard_headers] + extra_vals + [round(total_consumption, 4)]
            writer.writerow(row)
            
            current += timedelta(minutes=1)
            
    print(f"Dataset generated at {filepath_backend}")
    
    # Copy to frontend for UI selection
    import shutil
    shutil.copy2(filepath_backend, filepath_frontend)
    print(f"Dataset copied to {filepath_frontend}")
    print("Done!")

if __name__ == "__main__":
    main()
