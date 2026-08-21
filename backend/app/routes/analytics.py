from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import get_current_user
from app.services.dataset_service import DatasetService

router = APIRouter()


class DatasetModeRequest(BaseModel):
    mode: str


class DatasetSelectRequest(BaseModel):
    dataset_name: str

@router.get("/summary", response_model=dict)
async def get_analytics_summary(user: dict = Depends(get_current_user)):
    return DatasetService.get_summary()

@router.get("/recent", response_model=list)
async def get_recent_usage(user: dict = Depends(get_current_user)):
    return DatasetService.get_recent_data(12)

@router.get("/device-breakdown", response_model=list)
async def get_device_breakdown(user: dict = Depends(get_current_user)):
    return DatasetService.get_device_breakdown()

@router.get("/historical/{days}", response_model=list)
async def get_historical_data(days: int = 7, user: dict = Depends(get_current_user)):
    return DatasetService.get_historical_data(days)

@router.get("/device-series/{hours}", response_model=list)
async def get_device_time_series(hours: int = 24, user: dict = Depends(get_current_user)):
    return DatasetService.get_device_time_series(hours * 60)

@router.get("/device-series", response_model=list)
async def get_device_time_series_window(minutes: int = 1440, user: dict = Depends(get_current_user)):
    return DatasetService.get_device_time_series(minutes)

@router.get("/anomalies", response_model=list)
async def get_anomaly_detection(user: dict = Depends(get_current_user)):
    return DatasetService.get_anomaly_detection()

@router.get("/efficiency-score", response_model=dict)
async def get_energy_efficiency_score(user: dict = Depends(get_current_user)):
    return DatasetService.get_energy_efficiency_score()

@router.get("/pattern-insights", response_model=dict)
async def get_pattern_insights(user: dict = Depends(get_current_user)):
    return DatasetService.get_pattern_insights()


@router.get("/dataset-mode", response_model=dict)
async def get_dataset_mode(user: dict = Depends(get_current_user)):
    return DatasetService.get_dataset_mode()


@router.post("/dataset-mode", response_model=dict)
async def set_dataset_mode(payload: DatasetModeRequest, user: dict = Depends(get_current_user)):
    result = DatasetService.set_dataset_mode(payload.mode)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Invalid dataset mode"))
    return result


@router.get("/catalog", response_model=dict)
async def get_device_catalog(user: dict = Depends(get_current_user)):
    return DatasetService.get_catalog()


@router.get("/datasets", response_model=dict)
async def get_available_datasets(user: dict = Depends(get_current_user)):
    datasets = DatasetService.list_datasets()
    return {
        "datasets": datasets,
        "preview_datasets": DatasetService.list_preview_datasets(),
        "selected_dataset": DatasetService.get_dataset_mode().get("selected_dataset"),
    }


@router.post("/datasets/select", response_model=dict)
async def select_dataset(payload: DatasetSelectRequest, user: dict = Depends(get_current_user)):
    result = DatasetService.select_dataset(payload.dataset_name)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Invalid dataset selection"))
    return result
