import csv
import random
import math
import os
from datetime import datetime, timedelta
from pathlib import Path

# --- Configuration ---
DATA_DIR = Path(r'c:\myproject\backend\data\datasets')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 100 Total Devices for High Class
ALL_DEVICES = [
    "Fridge_Main", "Fridge_Mini", "Microwave", "Electric_Kettle", "Coffee_Grinder", "Toaster", 
    "Induction_Stove", "Exhaust_Fan", "Dishwasher", "Water_Purifier", "Mixer", "Food_Processor",
    "TV_Living", "TV_Master", "Home_Theater", "Gaming_PC", "Gaming_Console", "Audio_Receiver",
    "AC_Living", "AC_Master", "AC_Guest", "AC_Study", "Heater_Master", "Geyser_1", "Geyser_2",
    "Ceiling_Fan_Living", "Ceiling_Fan_Master", "Ceiling_Fan_Study", "Ceiling_Fan_Kitchen", "Wall_Fan_1",
    "LED_Strip_Living", "Chandelier", "Balcony_Light", "Porch_Light", "Kitchen_Bulb", "Study_Lamp",
    "Washing_Machine", "Dryer", "Iron_Box", "Vacuum_Cleaner", "Air_Purifier", "Dehumidifier",
    "Laptop_Personal", "Laptop_Work", "Monitor_1", "Monitor_2", "Printer", "Router_Main", "WiFi_Extender",
    "Security_Camera_1", "Security_Camera_2", "Smart_Hub", "Smart_Speaker_1", "Smart_Speaker_2"
]
# Fill up to 100 with Misc devices
ALL_DEVICES += [f"Misc_Device_{i}" for i in range(len(ALL_DEVICES) + 1, 101)]

# Socioeconomic Mapping
CLASS_DEVICES = {
    "low": ["Fridge_Main", "TV_Living", "Ceiling_Fan_Living", "Ceiling_Fan_Master", "Phone_Charger_1", "Exhaust_Fan", "Iron_Box", "Geyser_1"],
    "middle": ["Fridge_Main", "TV_Living", "Ceiling_Fan_Living", "Ceiling_Fan_Master", "Phone_Charger_1", "Exhaust_Fan", "Iron_Box", "Geyser_1",
               "Microwave", "Induction_Stove", "Washing_Machine", "Laptop_Work", "AC_Master", "Water_Purifier", "Mixer", "Router_Main", "Monitor_1", "Printer", "Set_Top_Box"],
    "high": ALL_DEVICES
}

# --- Generation Logic ---
def get_device_consumption(name, hour, is_weekend, temp):
    name_low = name.lower()
    
    # Base load for always-on
    if any(x in name_low for x in ["fridge", "router", "hub", "camera", "purifier"]):
        # Always on with cycling
        base = 0.015 if "fridge" in name_low else 0.005
        # Add random blips
        return base + (0.01 if random.random() < 0.2 else 0)
    
    # Lighting (evening peaks)
    if any(x in name_low for x in ["light", "bulb", "lamp", "led", "chandelier"]):
        if 18 <= hour <= 23:
            return 0.02 + random.uniform(0, 0.01)
        if 6 <= hour <= 8:
            return 0.01 + random.uniform(0, 0.005)
        return 0.0
    
    # Climate (temp dependent)
    if any(x in name_low for x in ["ac", "fan", "cooling"]):
        if temp > 26:
            factor = (temp - 26) / 10
            return 0.15 * factor + random.uniform(0, 0.05)
        if 20 <= hour <= 6: # Fans at night
            return 0.02 + random.uniform(0, 0.01)
        return 0.0
    
    if any(x in name_low for x in ["heater", "geyser"]):
        if temp < 18 or (6 <= hour <= 9): # Morning geyser
            return 0.2 + random.uniform(0, 0.1)
        return 0.0

    # Intermittent Mealtime
    if any(x in name_low for x in ["microwave", "kettle", "toaster", "induction", "mixer", "coffee"]):
        if (7 <= hour <= 9) or (12 <= hour <= 14) or (19 <= hour <= 21):
            if random.random() < 0.15:
                return 0.3 + random.uniform(0, 0.2)
        return 0.0
    
    # Entertainment (evening/weekend)
    if any(x in name_low for x in ["tv", "gaming", "theater", "pc", "console", "audio"]):
        prob = 0.4 if is_weekend else 0.2
        if 18 <= hour <= 23 and random.random() < prob:
            return 0.08 + random.uniform(0, 0.05)
        return 0.0

    # Work/Study
    if any(x in name_low for x in ["laptop", "monitor", "printer", "study"]):
        if 9 <= hour <= 18 and random.random() < 0.7:
            return 0.04 + random.uniform(0, 0.02)
        return 0.0
        
    # Misc/Others
    if random.random() < 0.05:
        return 0.02 + random.uniform(0, 0.05)
    return 0.0

def generate_csv(year, class_type):
    filename = f"energy_dataset_{year}.csv"
    filepath = DATA_DIR / filename
    devices = CLASS_DEVICES[class_type]
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    current_time = start_date
    delta = timedelta(minutes=1)
    
    print(f"Generating {filename} ({class_type} class) with 1-min resolution...")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        headers = ['timestamp', 'temperature', 'humidity', 'total_consumption'] + devices
        writer.writerow(headers)
        
        while current_time < end_date:
            hour = current_time.hour
            minute = current_time.minute
            month = current_time.month
            is_weekend = current_time.weekday() >= 5
            
            # Temp logic
            base_temp = 20 + 10 * math.sin((month - 1) * math.pi / 6)
            diurnal = -5 * math.cos((hour + minute/60) * math.pi / 12)
            temp = round(base_temp + diurnal + random.uniform(-0.5, 0.5), 1)
            humidity = round(60 - 20 * math.sin((month - 1) * math.pi / 6) + random.uniform(-2, 2), 1)
            
            row_data = {}
            total = 0.0
            for d in devices:
                val = get_device_consumption(d, hour, is_weekend, temp)
                row_data[d] = round(val, 4)
                total += val
            
            total_consumption = round(total * 1.05, 4) # Add loss factor
            
            writer.writerow([
                current_time.strftime('%Y-%m-%d %H:%M:%S'),
                temp,
                humidity,
                total_consumption
            ] + [row_data[d] for d in devices])
            
            current_time += delta

if __name__ == "__main__":
    generate_csv(2021, "low")
    generate_csv(2025, "middle")
    generate_csv(2024, "high")
    print("All datasets regenerated with high-fidelity behavior!")
