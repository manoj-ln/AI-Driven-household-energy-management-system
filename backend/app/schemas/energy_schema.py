from datetime import datetime
from typing import Optional

class EnergyReading:
    def __init__(self, timestamp: datetime, energy_kwh: float, appliance: Optional[str] = None, location: Optional[str] = None):
        self.timestamp = timestamp
        self.energy_kwh = energy_kwh
        self.appliance = appliance
        self.location = location

    def dict(self):
        return {
            "timestamp": self.timestamp,
            "energy_kwh": self.energy_kwh,
            "appliance": self.appliance,
            "location": self.location
        }
