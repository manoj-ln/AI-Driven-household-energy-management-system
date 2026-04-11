from fastapi import APIRouter
from app.services.optimization_service import OptimizationService

router = APIRouter()

@router.get("/report", response_model=dict)
async def get_optimization_report():
    return OptimizationService.get_report()
