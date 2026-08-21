from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.optimization_service import OptimizationService

router = APIRouter()

@router.get("/report", response_model=dict)
async def get_optimization_report(user: dict = Depends(get_current_user)):
    return OptimizationService.get_report()
