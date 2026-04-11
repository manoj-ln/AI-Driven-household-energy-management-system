from fastapi import APIRouter
from app.services.dataset_service import DatasetService

router = APIRouter()

@router.get("/summary", response_model=dict)
async def get_analytics_summary():
    return DatasetService.get_summary()

@router.get("/recent", response_model=list)
async def get_recent_usage():
    return DatasetService.get_recent_data(12)

@router.get("/device-breakdown", response_model=list)
async def get_device_breakdown():
    return DatasetService.get_device_breakdown()

@router.get("/historical/{days}", response_model=list)
async def get_historical_data(days: int = 7):
    return DatasetService.get_historical_data(days)

@router.get("/device-series/{hours}", response_model=list)
async def get_device_time_series(hours: int = 24):
    return DatasetService.get_device_time_series(hours * 60)

@router.get("/device-series", response_model=list)
async def get_device_time_series_window(minutes: int = 1440):
    return DatasetService.get_device_time_series(minutes)

@router.get("/anomalies", response_model=list)
async def get_anomaly_detection():
    return DatasetService.get_anomaly_detection()

@router.get("/efficiency-score", response_model=dict)
async def get_energy_efficiency_score():
    return DatasetService.get_energy_efficiency_score()

@router.get("/pattern-insights", response_model=dict)
async def get_pattern_insights():
    return DatasetService.get_pattern_insights()
