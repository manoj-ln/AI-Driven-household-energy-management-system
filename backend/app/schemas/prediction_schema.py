from pydantic import BaseModel


class PredictionSchema(BaseModel):
    energy_kwh: float
    confidence: float
    model: str
    confidence_label: str = "Moderate"
    trend: str = "Stable"
    estimated_cost_inr: float = 0.0
    timestamp: str
    unit: str = "kWh"
    next_hour: str
