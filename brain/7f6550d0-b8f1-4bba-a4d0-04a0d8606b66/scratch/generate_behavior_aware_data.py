
import csv
import random
import math
from datetime import datetime, timedelta
from pathlib import Path

def generate_data():
    output_dir = Path(r'c:\myproject\backend\data\datasets')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'energy_dataset_merged_3years.csv'

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 1, 1)
    
    current_time = start_date
    delta = timedelta(minutes=10) # 10-minute resolution for performance/fidelity balance

    # Device Configuration
    # (base_power_kw, usage_probability, duration_mins_range, category)
    device_configs = {
        "Fridge": (0.15, 1.0, (10, 10), "Always-On-Cycle"), # Cycles internally but always connected
        "WiFi_Router": (0.015, 1.0, (10, 10), "Always-On"),
        "Smart_Speaker": (0.005, 0.4, (10, 10), "Idle"),
        
        "AC_Main": (1.5, 0.0, (60, 240), "Season-Cooling"), # Temp dependent
        "Heater": (1.2, 0.0, (30, 120), "Season-Heating"), # Temp dependent
        
        "Coffee_Grinder": (0.4, 0.05, (1, 2), "Intermittent-Morning"), 
        "Microwave": (0.8, 0.1, (2, 5), "Intermittent-Mealtime"),
        "Washing_Machine": (0.5, 0.02, (45, 90), "Duration-Weekend"),
        "Electric_Kettle": (1.8, 0.08, (3, 6), "Intermittent"),
        
        "Living_Room_TV": (0.12, 0.3, (60, 180), "Evening"),
        "LED_Lights": (0.06, 0.0, (180, 360), "Temporal-Evening"),
        "Gaming_PC": (0.35, 0.15, (60, 300), "Night-Weekend"),
        "Electric_Vehicle": (3.3, 0.05, (240, 480), "Night-Charge")
    }

    active_durations = {name: 0 for name in device_configs}

    print(f"Generating behavior-aware data to {output_file}...")

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        headers = ['timestamp', 'temperature', 'humidity', 'total_consumption'] + list(device_configs.keys())
        writer.writerow(headers)

        while current_time < end_date:
            # 1. Contextual Factors
            month = current_time.month
            hour = current_time.hour
            day_of_week = current_time.weekday() # 0-6
            is_weekend = day_of_week >= 5
            
            # Base Temperature Logic (Bangalore/India approximation)
            # Base: 20-30 range. Summer (Mar-May): +5. Winter (Dec-Jan): -5.
            base_temp = 22 + 5 * math.sin((month - 1) * math.pi / 6)
            # Diurnal temp variation
            hourly_variation = -5 * math.cos(hour * math.pi / 12)
            temp = base_temp + hourly_variation + random.uniform(-1, 1)
            humidity = 50 - 15 * math.sin((month - 1) * math.pi / 6) + random.uniform(-5, 5)

            row_consumption = {}
            total = 0.0

            for name, config in device_configs.items():
                base_p, prob, dur_range, cat = config
                
                # Update remaining duration
                if active_durations[name] > 0:
                    active_durations[name] -= 10
                    consumption = base_p + random.uniform(-0.01, 0.01)
                else:
                    consumption = 0.0
                    
                    # Logic to START device
                    start_trigger = False
                    
                    if cat == "Always-On":
                        consumption = base_p
                    elif cat == "Always-On-Cycle":
                        # Simulate compressor cycling (on 30% of the time)
                        if random.random() < 0.3:
                            consumption = base_p
                    elif cat == "Intermittent-Morning" and 7 <= hour <= 9:
                        if random.random() < 0.1: # 10% chance per 10 mins in morning
                            start_trigger = True
                    elif cat == "Intermittent-Mealtime":
                        if (7<=hour<=9 or 12<=hour<=14 or 19<=hour<=21):
                            if random.random() < 0.15: start_trigger = True
                    elif cat == "Season-Cooling" and temp > 28:
                        # Higher chance as temp increases
                        if random.random() < (temp - 28) / 15: start_trigger = True
                    elif cat == "Season-Heating" and temp < 18:
                        if random.random() < (18 - temp) / 10: start_trigger = True
                    elif cat == "Duration-Weekend" and is_weekend:
                        if 8 <= hour <= 16 and random.random() < 0.05: start_trigger = True
                    elif cat == "Temporal-Evening" and 18 <= hour <= 23:
                        consumption = base_p # Lights are usually on fixed duration
                    elif cat == "Evening" and 18 <= hour <= 23:
                        if random.random() < 0.3: start_trigger = True
                    elif cat == "Night-Charge" and 0 <= hour <= 5:
                        if random.random() < 0.1: start_trigger = True # Start charging EV
                    
                    if start_trigger:
                        active_durations[name] = random.randint(dur_range[0], dur_range[1])
                        consumption = base_p

                # Convert Power (kW) to Energy (kWh) for 10-minute interval
                energy_kwh = (consumption * 10) / 60
                
                # Weekend usage boost (1.2x)
                if is_weekend:
                    energy_kwh *= 1.2
                    
                row_consumption[name] = round(energy_kwh, 4)
                total += energy_kwh

            # Write row
            writer.writerow([
                current_time.strftime('%Y-%m-%d %H:%M:%S'),
                round(temp, 1),
                round(humidity, 1),
                round(total, 4)
            ] + [row_consumption[n] for n in device_configs])

            current_time += delta

    print("Generation complete. 3 Years of high-fidelity data created.")

if __name__ == "__main__":
    generate_data()
