from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.energy_schema import EnergyReading
from app.services.data_service import DataService
import httpx

router = APIRouter()

@router.post("/ingest", response_model=dict)
async def ingest_energy_reading(
    reading: EnergyReading,
    user: dict = Depends(get_current_user),
):
    try:
        DataService.save_reading(reading)
        return {"status": "success", "message": "Energy reading ingested"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/weather", response_model=dict)
async def get_current_weather(
    lat: float = 12.9716,
    lon: float = 77.5946,
    user: dict = Depends(get_current_user),
):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            temp = data.get("current_weather", {}).get("temperature")
            return {"status": "success", "temperature": temp}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch weather", "temperature": 25.0}
