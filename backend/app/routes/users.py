from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
import re

from app.core.security import get_current_user
from app.schemas.user_schema import UserSchema
from app.services.auth_service import AuthService

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    age: str = Field(min_length=1, max_length=3)
    identifier: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=8, max_length=64)

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        identifier = value.strip().lower()
        email_ok = re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", identifier)
        phone_ok = re.fullmatch(r"\d{10}", identifier)
        if not (email_ok or phone_ok):
            raise ValueError("Identifier must be a valid email or 10-digit phone number")
        return identifier

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must include at least one number")
        return value


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=8, max_length=64)


class ProfileUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    age: str = Field(min_length=1, max_length=3)


@router.post("/register")
async def register(payload: RegisterRequest):
    result = AuthService.register(
        name=payload.name,
        age=payload.age,
        identifier=payload.identifier,
        password=payload.password,
    )
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))
    return result


@router.post("/login")
async def login(payload: LoginRequest):
    result = AuthService.login(identifier=payload.identifier, password=payload.password)
    if result.get("status") != "success":
        raise HTTPException(status_code=401, detail=result.get("message", "Login failed"))
    return result


@router.get("/me", response_model=dict)
async def read_current_user(user: dict = Depends(get_current_user)):
    return {"user": UserSchema(**user).model_dump()}


@router.put("/me", response_model=dict)
async def update_current_user(payload: ProfileUpdateRequest, user: dict = Depends(get_current_user)):
    result = AuthService.update_profile(
        identifier=user["identifier"],
        name=payload.name,
        age=payload.age,
    )
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "Profile update failed"))
    profile = result["profile"]
    return {"profile": UserSchema(**profile).model_dump(), "status": result["status"]}
