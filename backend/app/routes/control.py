from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from app.services.control_service import ControlService

router = APIRouter()


class DeviceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    device_type: str = Field(default="appliance", min_length=2, max_length=50)
    location: str = Field(default="Home", min_length=1, max_length=80)
    quantity: int = Field(default=1, ge=1, le=25)


class DeviceUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    device_type: str = Field(default="appliance", min_length=2, max_length=50)
    location: str = Field(default="Home", min_length=1, max_length=80)

@router.get("/devices", response_model=list)
async def get_control_devices():
    return ControlService.get_devices()


@router.post("/devices", response_model=dict)
async def create_control_device(payload: DeviceCreateRequest):
    try:
        return ControlService.add_device(
            name=payload.name,
            device_type=payload.device_type,
            location=payload.location,
            quantity=payload.quantity,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/devices/{device_id}", response_model=dict)
async def update_control_device(device_id: str, payload: DeviceUpdateRequest):
    try:
        return ControlService.update_device(
            device_id=device_id,
            name=payload.name,
            device_type=payload.device_type,
            location=payload.location,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/devices/{device_id}", response_model=dict)
async def delete_control_device(device_id: str):
    try:
        return ControlService.delete_device(device_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/devices/{device_name}/toggle", response_model=dict)
async def toggle_control_device(device_name: str):
    try:
        return ControlService.toggle_device(device_name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
