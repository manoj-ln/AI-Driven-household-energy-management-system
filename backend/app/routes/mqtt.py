from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def get_mqtt_status():
    return {
        "connected": False,
        "mode": "disabled",
        "message": "MQTT integration is disabled in this software-only version.",
    }
