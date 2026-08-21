from fastapi import APIRouter, Depends
from typing import Any, Dict
from app.core.security import get_current_user
from app.schemas.prediction_schema import PredictionSchema
from app.services.prediction_service import PredictionService
from app.services.anomaly_service import AnomalyService

router = APIRouter()


@router.get("/next-hour", response_model=Dict[str, Any])
async def get_next_hour_prediction(user: dict = Depends(get_current_user)):
    prediction = PredictionService.predict_next_hour()
    validated = PredictionSchema(
        energy_kwh=prediction["energy_kwh"],
        confidence=prediction["confidence"],
        model=prediction["model"],
        confidence_label=prediction.get("confidence_label", "Moderate"),
        trend=prediction.get("trend", "Stable"),
        estimated_cost_inr=prediction.get("estimated_cost_inr", 0.0),
        timestamp=prediction.get("timestamp", ""),
        next_hour=prediction.get("trend", "unknown"),
    )
    anomalies = AnomalyService.detect()
    anomaly_summary = AnomalyService.summary()
    return {
        "prediction": validated.model_dump(),
        "anomalies": anomalies,
        "anomaly_summary": anomaly_summary,
    }


@router.get("/models", response_model=Dict[str, Any])
async def get_available_models(user: dict = Depends(get_current_user)):
    return PredictionService.get_available_models()


@router.post("/models/{model_name}", response_model=Dict[str, Any])
async def set_model(model_name: str, user: dict = Depends(get_current_user)):
    return PredictionService.set_model(model_name)


@router.get("/forecast/{hours}", response_model=list)
async def get_forecast(hours: int = 7, user: dict = Depends(get_current_user)):
    return PredictionService.predict_multi_step(hours)


@router.get("/anomalies/{method}", response_model=list)
async def get_anomalies(method: str = "zscore", user: dict = Depends(get_current_user)):
    return AnomalyService.detect(method)


@router.get("/explain-next", response_model=Dict[str, Any])
async def get_prediction_explainability(user: dict = Depends(get_current_user)):
    return PredictionService.explain_next_hour_prediction()
