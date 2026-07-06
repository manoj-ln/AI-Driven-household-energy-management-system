import csv
import random
from datetime import datetime, timedelta

def generate_data():
    header = "Timestamp,Hour,DayOfWeek,IsWeekend,Temperature,Lighting_LED,Lighting_Tube,Cooling_Fan_Ceiling,Cooling_Fan_Table,Cooling_AC,Cooling_Cooler,Electronics_TV,Electronics_Laptop,Electronics_Desktop,Electronics_Charger,Electronics_WiFi,Kitchen_Microwave,Kitchen_Induction,Kitchen_Kettle,Kitchen_Mixer,Kitchen_Toaster,Kitchen_Coffee,Utility_Washing,Utility_Dishwasher,Utility_Vacuum,Utility_Iron,Heating_Water,Heating_Room,Smart_Speaker,Smart_CCTV,Smart_Purifier,Smart_Humidifier,Others_Refrigerator,Others_Purifier,Others_Exhaust,Smart_Bulb_Living,Smart_Bulb_Kitchen,Smart_Bulb_Bed,Smart_Plug_TV,Smart_Plug_PC,Air_Purifier_Living,Air_Purifier_Bed,Dehumidifier_Basement,Humidifier_Bed,Robot_Vacuum,Cordless_Vacuum,Electric_Mop,Smart_Speaker_Living,Smart_Speaker_Bed,Smart_Display_Kitchen,Security_Camera_Front,Security_Camera_Back,Video_Doorbell,Smart_Lock_Front,Smart_Thermostat,Gaming_Console_PS,Gaming_Console_Xbox,Nintendo_Switch,VR_Headset_Charger,Gaming_PC_Monitor,Office_Monitor_1,Office_Monitor_2,Laptop_Work,Laptop_Personal,Tablet_Charger_1,Tablet_Charger_2,Phone_Charger_Living,Phone_Charger_Bed1,Phone_Charger_Bed2,Smartwatch_Charger,Electric_Toothbrush_1,Electric_Toothbrush_2,Water_Flosser,Hair_Dryer,Hair_Straightener,Electric_Shaver,Curling_Iron,Treadmill,Exercise_Bike,Massage_Chair,Heating_Pad,Electric_Blanket_1,Electric_Blanket_2,Coffee_Grinder,Espresso_Machine,Milk_Frother,Electric_Kettle_Tea,Toaster_Oven,Waffle_Maker,Stand_Mixer,Hand_Mixer,Food_Processor,Blender_Smoothie,Juicer,Slow_Cooker,Pressure_Cooker_Electric,Rice_Cooker_Smart,Air_Fryer,Deep_Fryer,Bread_Maker,Ice_Cream_Maker,Popcorn_Machine,Wine_Cooler,Mini_Fridge_Drinks,Chest_Freezer,Water_Dispenser,Ice_Maker,Trash_Compactor,Garage_Door_Opener,Electric_Gate_Motor,Pool_Pump,Hot_Tub_Heater,Sprinkler_System,Outdoor_Lighting_Landscape,Patio_Heater,Electric_Grill,Mosquito_Zapper,Power_Tool_Charger,Air_Compressor,Shop_Vac,Sewing_Machine,Ironing_Station,Clothes_Steamer,Shoe_Polisher,Aquarium_Filter,Aquarium_Light,Terrarium_Heater,Pet_Feeder_Automatic,Pet_Water_Fountain,Baby_Monitor_Camera,Bottle_Warmer,Breast_Pump,Night_Light_Hallway,Night_Light_Bath,White_Noise_Machine,Total_Consumption".split(",")
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31, 23, 59)
    delta = timedelta(minutes=10) # 10-minute intervals for 2 years
    
    output_file = r"c:\myproject\backend\data\datasets\energy_dataset_2024_2025.csv"
    
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        current_date = start_date
        while current_date <= end_date:
            row = []
            ts = current_date.isoformat()
            hour = current_date.hour
            dow = current_date.weekday()
            is_weekend = 1 if dow >= 5 else 0
            
            # Base temperature based on month
            month = current_date.month
            if month in [12, 1, 2]: # Winter
                base_temp = 18 + random.uniform(-2, 2)
            elif month in [3, 4, 5]: # Summer
                base_temp = 28 + random.uniform(-3, 5)
            else:
                base_temp = 24 + random.uniform(-2, 2)
            
            # Hourly temp variation
            temp = base_temp + (hour - 12) * 0.5 + random.uniform(-1, 1)
            
            row.extend([ts, hour, dow, is_weekend, round(temp, 1)])
            
            total_cons = 0
            # Generate values for columns 5 to 134 (devices)
            for i in range(5, len(header) - 1):
                col_name = header[i].lower()
                # Simple logic for device usage
                base_val = 0.01
                if "ac" in col_name and temp > 28:
                    base_val = 1.5 + random.uniform(0, 0.5)
                elif "heater" in col_name and temp < 20:
                    base_val = 1.2 + random.uniform(0, 0.3)
                elif "lighting" in col_name and (hour > 18 or hour < 6):
                    base_val = 0.05 + random.uniform(0, 0.05)
                elif "tv" in col_name and 18 <= hour <= 23:
                    base_val = 0.12 + random.uniform(0, 0.05)
                elif "fridge" in col_name:
                    base_val = 0.08 + random.uniform(-0.01, 0.01)
                else:
                    base_val = random.uniform(0.001, 0.005)
                
                val = round(base_val, 4)
                row.append(val)
                total_cons += val
            
            row.append(round(total_cons, 4))
            writer.writerow(row)
            current_date += delta

    print(f"Generated dataset: {output_file}")

if __name__ == "__main__":
    generate_data()
