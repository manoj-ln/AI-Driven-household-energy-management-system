from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.schemas.energy_schema import EnergyReading
from app.services.data_service import DataService

router = APIRouter()

@router.post("/ingest", response_model=dict)
async def ingest_energy_reading(data: dict):
    try:
        reading = EnergyReading(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            energy_kwh=float(data["energy_kwh"]),
            appliance=data.get("appliance"),
            location=data.get("location")
        )
        DataService.save_reading(reading)
        return {"status": "success", "message": "Energy reading ingested"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
