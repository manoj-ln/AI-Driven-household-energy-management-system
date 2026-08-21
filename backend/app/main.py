import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.routes import energy, predictions, users
from app.routes.analytics import router as analytics_router
from app.routes.control import router as control_router
from app.routes.optimization import router as optimization_router
from app.routes.simulation import router as simulation_router
from app.routes.manual_input import router as manual_input_router
from app.routes.chatbot import router as chatbot_router
from app.routes.mqtt import router as mqtt_router
from app.routes.bill import router as bill_router
from app.services.mqtt_service import mqtt_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.db_service import DatabaseService

    DatabaseService.ensure_knowledge_base()
    mqtt_service.start()
    yield
    mqtt_service.stop()


app = FastAPI(
    title=settings.project_name,
    description="Modular service-oriented backend for software-only energy monitoring, prediction, optimization, and explainability.",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

allowed_origins = [
    origin.strip()
    for origin in settings.cors_allowed_origins.split(",")
    if origin.strip()
]
if "null" not in allowed_origins:
    allowed_origins.append("null")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=(
        r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?"
    ),
    allow_credentials=True,
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
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"
    response.headers["X-DNS-Prefetch-Control"] = "off"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


app.include_router(energy.router, prefix="/energy", tags=["energy"])
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(control_router, prefix="/control", tags=["control"])
app.include_router(optimization_router, prefix="/optimization", tags=["optimization"])
app.include_router(simulation_router, prefix="/simulation", tags=["simulation"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(manual_input_router, prefix="/manual", tags=["manual-input"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
app.include_router(mqtt_router, prefix="/mqtt", tags=["mqtt"])
app.include_router(bill_router, prefix="/bill", tags=["bill"])


@app.get("/health")
async def health_check():
    try:
        from app.database.connection import get_connection
        with get_connection() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "ok",
        "service": "AI-Driven Household Energy Management System API",
        "database": db_status,
    }
