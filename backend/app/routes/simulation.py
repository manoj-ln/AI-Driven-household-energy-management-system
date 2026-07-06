from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.simulation_service import SimulationService

router = APIRouter()

class SimulationRequest(BaseModel):
    scenario: str
    hours: int = Field(default=24, ge=6, le=168)
    rate_per_kwh: float = Field(default=6.26, ge=0.0, le=100.0)
    optimization_strength: float = Field(default=18.0, ge=0.0, le=60.0)
    solar_offset: float = Field(default=45.0, ge=0.0, le=90.0)
    battery_shift: float = Field(default=12.0, ge=0.0, le=40.0)
    appliance_upgrade: float = Field(default=10.0, ge=0.0, le=40.0)
    demand_response: float = Field(default=8.0, ge=0.0, le=40.0)
    occupancy_mode: str = Field(default="family")

@router.post("/run", response_model=dict)
async def run_simulation(request: SimulationRequest):
    if request.scenario not in {"normal", "optimized", "solar", "battery_backup", "weekend_saver", "green_home", "peak_protection"}:
        raise HTTPException(status_code=400, detail="Invalid simulation scenario")
    if request.occupancy_mode not in {"family", "working_day", "vacation", "guests", "students"}:
        raise HTTPException(status_code=400, detail="Invalid occupancy mode")
    return SimulationService.run_scenario(
        scenario=request.scenario,
        hours=request.hours,
        rate_per_kwh=request.rate_per_kwh,
        optimization_strength=request.optimization_strength,
        solar_offset=request.solar_offset,
        battery_shift=request.battery_shift,
        appliance_upgrade=request.appliance_upgrade,
        demand_response=request.demand_response,
        occupancy_mode=request.occupancy_mode,
    )
