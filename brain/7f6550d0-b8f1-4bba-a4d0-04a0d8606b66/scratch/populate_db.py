
from app.services.db_service import DatabaseService

def populate_initial_devices():
    DatabaseService.init_db()
    devices = [
        {"id": 1, "name": "Smart Bulb", "category": "Lighting", "ratedPower": "12W", "status": "active", "description": "High-efficiency LED bulb with RGB support.", "smartFeatures": ["Remote Control", "Scheduling"]},
        {"id": 2, "name": "Ceiling Fan", "category": "Cooling", "ratedPower": "75W", "status": "active", "description": "Energy-star rated silent fan.", "smartFeatures": ["Speed Control"]},
        {"id": 3, "name": "Air Conditioner", "category": "Cooling", "ratedPower": "1500W", "status": "inactive", "description": "Inverter AC with fast cooling technology.", "smartFeatures": ["Temp Sensing", "Energy Save Mode"]},
        {"id": 4, "name": "Refrigerator", "category": "Appliances", "ratedPower": "250W", "status": "active", "description": "Double-door fridge with smart defrost.", "smartFeatures": ["Door Alarm", "Holiday Mode"]},
        {"id": 5, "name": "Microwave Oven", "category": "Kitchen", "ratedPower": "1200W", "status": "inactive", "description": "Convection microwave for fast cooking.", "smartFeatures": ["Auto-cook"]},
        {"id": 6, "name": "Washing Machine", "category": "Laundry", "ratedPower": "500W", "status": "active", "description": "Front-load washing machine.", "smartFeatures": ["Load Sensing"]},
        {"id": 7, "name": "LED TV", "category": "Entertainment", "ratedPower": "150W", "status": "active", "description": "4K Smart TV.", "smartFeatures": ["App Integration"]},
        {"id": 8, "name": "Laptop", "category": "Computing", "ratedPower": "65W", "status": "active", "description": "High-performance workstation.", "smartFeatures": ["Battery Tracking"]},
        {"id": 9, "name": "Water Heater", "category": "Utility", "ratedPower": "2000W", "status": "inactive", "description": "Instant water heater.", "smartFeatures": ["Temp Limit"]},
        {"id": 10, "name": "Electric Kettle", "category": "Kitchen", "ratedPower": "1500W", "status": "active", "description": "Rapid boil kettle.", "smartFeatures": ["Auto-shutoff"]},
    ]
    # Add more to reach 30
    for i in range(11, 31):
        devices.append({
            "id": i, "name": f"Device {i}", "category": "General", "ratedPower": "100W", "status": "inactive", "description": "Generic smart device.", "smartFeatures": ["Monitoring"]
        })
    
    DatabaseService.sync_devices(devices)
    print("30 devices synced to SQLite.")

if __name__ == "__main__":
    populate_initial_devices()
