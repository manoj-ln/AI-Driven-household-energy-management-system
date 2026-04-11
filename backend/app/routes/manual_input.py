"""
API Routes for Manual Data Input

This module provides REST API endpoints for manual home-usage input
for software-only operation.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from app.database.manual_input import manual_input

router = APIRouter()


@router.post("/manual-reading", response_model=Dict[str, Any])
async def add_manual_reading(
    device_id: str = Body(..., description="Device identifier"),
    voltage: Optional[float] = Body(None, description="Voltage in volts"),
    current: Optional[float] = Body(None, description="Current in amperes"),
    power: Optional[float] = Body(None, description="Power in watts"),
    energy_consumption: Optional[float] = Body(None, description="Energy consumption in kWh"),
    temperature: Optional[float] = Body(None, description="Temperature in Celsius"),
    humidity: Optional[float] = Body(None, description="Humidity percentage"),
    timestamp: Optional[str] = Body(None, description="ISO format timestamp")
):
    """
    Add a single manual energy reading

    At minimum, device_id is required. Other fields are optional.
    Power and energy_consumption will be calculated if voltage and current are provided.
    """
    result = manual_input.add_manual_reading(
        device_id=device_id,
        voltage=voltage,
        current=current,
        power=power,
        energy_consumption=energy_consumption,
        temperature=temperature,
        humidity=humidity,
        timestamp=timestamp
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/manual-readings/bulk", response_model=Dict[str, Any])
async def add_bulk_manual_readings(
    readings: List[Dict[str, Any]] = Body(..., description="List of reading objects")
):
    """
    Add multiple manual readings at once

    Each reading should be a dictionary with at least 'device_id' field.
    """
    result = manual_input.add_bulk_readings(readings)
    return result


@router.post("/household-plan", response_model=Dict[str, Any])
async def create_household_plan(
    appliances: List[Dict[str, Any]] = Body(..., description="Appliance entries with quantity and hours_per_day"),
    date: Optional[str] = Body(None, description="Optional date in ISO format or YYYY-MM-DD"),
    rate_per_kwh: float = Body(6.26, description="Electricity rate in INR per kWh"),
):
    """
    Calculate household energy usage from appliance-based manual entries.
    """
    result = manual_input.process_household_plan(appliances=appliances, date=date, rate_per_kwh=rate_per_kwh)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/simulate/{device_id}", response_model=Dict[str, Any])
async def simulate_device_reading(
    device_id: str,
    base_voltage: Optional[float] = 220.0,
    base_current: Optional[float] = 1.0,
    base_temperature: Optional[float] = 25.0,
    base_humidity: Optional[float] = 60.0
):
    """
    Generate and add a realistic simulated reading for a device

    Uses the provided base values with some random variation.
    """
    base_reading = {
        "voltage": base_voltage,
        "current": base_current,
        "temperature": base_temperature,
        "humidity": base_humidity
    }

    reading = manual_input.generate_realistic_reading(device_id, base_reading)
    result = manual_input.add_manual_reading(**reading)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/simulate-continuous", response_model=Dict[str, Any])
async def simulate_continuous_readings(
    device_ids: List[str] = Body(..., description="List of device IDs to simulate"),
    hours: int = Body(24, description="Number of hours to simulate"),
    interval_minutes: int = Body(60, description="Minutes between readings")
):
    """
    Simulate continuous data for multiple devices over a time period

    This will generate and add realistic readings for each device at regular intervals.
    """
    result = manual_input.simulate_continuous_data(device_ids, hours, interval_minutes)
    return result


@router.get("/manual-input-template", response_model=Dict[str, Any])
async def get_manual_input_template():
    """
    Get a template and examples for manual data input
    """
    return manual_input.get_manual_input_template()


@router.get("/export-data")
async def export_manual_data(
    device_id: Optional[str] = None,
    hours: int = 24,
    format: str = "json"
):
    """
    Export manual data for backup or analysis

    Parameters:
    - device_id: Filter by specific device (optional)
    - hours: Number of hours of data to export (default: 24)
    - format: Export format - "json" or "csv" (default: "json")
    """
    try:
        data = manual_input.export_data(device_id, hours, format)

        if format == "json":
            from fastapi.responses import JSONResponse
            import json
            return JSONResponse(content=json.loads(data))
        else:
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(content=data, media_type="text/csv")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
