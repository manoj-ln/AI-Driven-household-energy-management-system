from fastapi import Body, Depends, APIRouter

from app.core.security import get_current_user
from app.services.bill_calculator import BillCalculator

router = APIRouter()


@router.post("/calculate")
async def calculate_bill(
    payload: dict = Body(...),
    _: dict = Depends(get_current_user),
):
    """Calculate a BESCOM-style electricity bill from user-provided inputs."""
    return BillCalculator.calculate_from_dict(payload)


@router.get("/tariffs")
async def get_tariff_references(
    _: dict = Depends(get_current_user),
):
    """Return the full tariff reference table for available states and connection types."""
    return BillCalculator.get_tariff_references()
