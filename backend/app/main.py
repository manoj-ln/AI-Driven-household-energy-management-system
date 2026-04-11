import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import energy, predictions, users
from app.routes.analytics import router as analytics_router
from app.routes.control import router as control_router
from app.routes.optimization import router as optimization_router
from app.routes.simulation import router as simulation_router
from app.routes.manual_input import router as manual_input_router
from app.routes.chatbot import router as chatbot_router

app = FastAPI(
    title="Household Energy Management API",
    description="Software-only energy monitoring, prediction, and anomaly detection API.",
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

app.include_router(energy.router, prefix="/energy", tags=["energy"])
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(control_router, prefix="/control", tags=["control"])
app.include_router(optimization_router, prefix="/optimization", tags=["optimization"])
app.include_router(simulation_router, prefix="/simulation", tags=["simulation"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(manual_input_router, prefix="/manual", tags=["manual-input"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Household Energy Management API"}
