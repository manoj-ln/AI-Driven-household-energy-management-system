from pydantic import BaseModel
from datetime import datetime

class EnergyRecord(BaseModel):
    timestamp: datetime
    energy_kwh: float
    appliance: str | None = None
    location: str | None = None
