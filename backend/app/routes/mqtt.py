from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.mqtt_service import mqtt_service

router = APIRouter()


class PublishRequest(BaseModel):
    topic: str
    payload: Dict[str, Any] = {}
    qos: int = 1


class CommandRequest(BaseModel):
    device_id: str
    command: str
    params: Dict[str, Any] = {}


class SubscribeRequest(BaseModel):
    topic: str
    qos: int = 1


class BroadcastRequest(BaseModel):
    command: str
    params: Dict[str, Any] = {}
    device_type: str = None


@router.get("/status")
async def get_mqtt_status():
    return mqtt_service.get_status()


@router.post("/publish")
async def publish_message(
    request: PublishRequest,
    user: dict = Depends(get_current_user),
):
    success = mqtt_service.publish(request.topic, request.payload, qos=request.qos)
    if not success:
        raise HTTPException(status_code=503, detail="MQTT broker is not connected or disabled")
    return {"status": "success", "topic": request.topic, "qos": request.qos}


@router.post("/command")
async def send_device_command(
    request: CommandRequest,
    user: dict = Depends(get_current_user),
):
    success = mqtt_service.send_command(request.device_id, request.command, params=request.params)
    if not success:
        raise HTTPException(status_code=503, detail="MQTT broker is not connected or disabled")
    return {"status": "success", "device_id": request.device_id, "command": request.command}


@router.post("/broadcast")
async def broadcast_command(
    request: BroadcastRequest,
    user: dict = Depends(get_current_user),
):
    success = mqtt_service.broadcast_command(request.command, params=request.params, device_type=request.device_type)
    if not success:
        raise HTTPException(status_code=503, detail="MQTT broker is not connected or disabled")
    return {"status": "success", "command": request.command, "device_type": request.device_type}


@router.post("/subscribe")
async def subscribe_topic(
    request: SubscribeRequest,
    user: dict = Depends(get_current_user),
):
    success = mqtt_service.subscribe(request.topic, qos=request.qos)
    if not success:
        raise HTTPException(status_code=503, detail="MQTT broker is not connected or disabled")
    return {"status": "success", "topic": request.topic, "qos": request.qos}
