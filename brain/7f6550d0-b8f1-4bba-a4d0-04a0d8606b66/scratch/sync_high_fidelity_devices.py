
import sys
import json
from pathlib import Path

sys.path.append(r'c:\myproject\backend')
from app.services.db_service import DatabaseService

def sync_devices():
    # Devices from our high-fidelity generator
    devices = [
        {"id": 1, "name": "Fridge", "category": "Kitchen", "ratedPower": "150W", "status": "Running", "description": "Continuous cooling appliance with intermittent compressor cycles.", "smartFeatures": ["Temp Monitor", "Door Alert"]},
        {"id": 2, "name": "WiFi_Router", "category": "Electronics", "ratedPower": "15W", "status": "Running", "description": "Always-on network hub.", "smartFeatures": ["Traffic Monitor"]},
        {"id": 3, "name": "Smart_Speaker", "category": "Electronics", "ratedPower": "5W", "status": "Standby", "description": "Voice assistant device.", "smartFeatures": ["Voice Control"]},
        {"id": 4, "name": "AC_Main", "category": "Cooling", "ratedPower": "1500W", "status": "Eco Mode", "description": "Main living room air conditioner, sensitive to outside temperature.", "smartFeatures": ["Thermostat Logic", "Sleep Mode"]},
        {"id": 5, "name": "Heater", "category": "Heating", "ratedPower": "1200W", "status": "Off", "description": "Room heater for winter months.", "smartFeatures": ["Auto-cut"]},
        {"id": 6, "name": "Coffee_Grinder", "category": "Kitchen", "ratedPower": "400W", "status": "Off", "description": "Intermittent appliance used typically for 1-2 minutes in the morning.", "smartFeatures": ["Pulse Mode"]},
        {"id": 7, "name": "Microwave", "category": "Kitchen", "ratedPower": "800W", "status": "Off", "description": "Used for short bursts during mealtimes.", "smartFeatures": ["Quick Start"]},
        {"id": 8, "name": "Washing_Machine", "category": "Utility", "ratedPower": "500W", "status": "Off", "description": "High-usage duration device, active mostly on weekends.", "smartFeatures": ["Delay Start"]},
        {"id": 9, "name": "Electric_Kettle", "category": "Kitchen", "ratedPower": "1800W", "status": "Off", "description": "High-power intermittent heater.", "smartFeatures": ["Auto-boil"]},
        {"id": 10, "name": "Living_Room_TV", "category": "Electronics", "ratedPower": "120W", "status": "Standby", "description": "Evening entertainment center.", "smartFeatures": ["Smart Hub"]},
        {"id": 11, "name": "LED_Lights", "category": "Lighting", "ratedPower": "60W", "status": "Running", "description": "Automated lighting, active during evening hours.", "smartFeatures": ["Dimmable"]},
        {"id": 12, "name": "Gaming_PC", "category": "Electronics", "ratedPower": "350W", "status": "Off", "description": "High-performance PC, used heavily during weekends/nights.", "smartFeatures": ["RGB Sync"]},
        {"id": 13, "name": "Electric_Vehicle", "category": "Charging", "ratedPower": "3300W", "status": "Charging", "description": "Night-charging EV module.", "smartFeatures": ["Fast Charge"]}
    ]
    
    DatabaseService.sync_devices(devices)
    print(f"Synchronized {len(devices)} behavior-aware devices to SQLite.")

if __name__ == "__main__":
    sync_devices()
