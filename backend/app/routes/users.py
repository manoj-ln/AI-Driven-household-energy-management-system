from fastapi import APIRouter

router = APIRouter()

@router.get("/me")
async def get_current_user():
    return {"user": "demo", "role": "owner"}
