from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.core.security import get_current_user
from app.services.control_service import ControlService

router = APIRouter()


class DeviceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    device_type: str = Field(default="appliance", min_length=2, max_length=50)
    location: str = Field(default="Home", min_length=1, max_length=80)
    quantity: int = Field(default=1, ge=1, le=25)
    rated_power_w: float = Field(default=100.0, gt=0, le=100000)
    standby_power_w: float = Field(default=0.0, ge=0, le=10000)
    priority: int = Field(default=3, ge=1, le=5)
    efficiency: float = Field(default=1.0, gt=0, le=1)
    operating_state: str = Field(default="on", pattern="^(on|off|standby)$")


class DeviceUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    device_type: str = Field(default="appliance", min_length=2, max_length=50)
    location: str = Field(default="Home", min_length=1, max_length=80)
    rated_power_w: float = Field(default=100.0, gt=0, le=100000)
    standby_power_w: float = Field(default=0.0, ge=0, le=10000)
    priority: int = Field(default=3, ge=1, le=5)
    efficiency: float = Field(default=1.0, gt=0, le=1)
    operating_state: str = Field(default="on", pattern="^(on|off|standby)$")

@router.get("/devices", response_model=list)
async def get_control_devices(user: dict = Depends(get_current_user)):
    return ControlService.get_devices()


@router.post("/devices", response_model=dict)
async def create_control_device(payload: DeviceCreateRequest, user: dict = Depends(get_current_user)):
    try:
        return ControlService.add_device(
            name=payload.name,
            device_type=payload.device_type,
            location=payload.location,
            quantity=payload.quantity,
            rated_power_w=payload.rated_power_w,
            standby_power_w=payload.standby_power_w,
            priority=payload.priority,
            efficiency=payload.efficiency,
            operating_state=payload.operating_state,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/devices/{device_id}", response_model=dict)
async def update_control_device(device_id: str, payload: DeviceUpdateRequest, user: dict = Depends(get_current_user)):
    try:
        return ControlService.update_device(
            device_id=device_id,
            name=payload.name,
            device_type=payload.device_type,
            location=payload.location,
            rated_power_w=payload.rated_power_w,
            standby_power_w=payload.standby_power_w,
            priority=payload.priority,
            efficiency=payload.efficiency,
            operating_state=payload.operating_state,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/devices/{device_id}", response_model=dict)
async def delete_control_device(device_id: str, user: dict = Depends(get_current_user)):
    try:
        return ControlService.delete_device(device_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/devices/{device_name}/toggle", response_model=dict)
async def toggle_control_device(device_name: str, user: dict = Depends(get_current_user)):
    try:
        return ControlService.toggle_device(device_name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/devices/{device_id}/state-events", response_model=list)
async def get_device_state_events(device_id: str, user: dict = Depends(get_current_user)):
    return ControlService.get_state_events(device_id)


@router.get("/load", response_model=dict)
async def get_current_load(user: dict = Depends(get_current_user)):
    return ControlService.current_load()
