"""
Centralized application settings.

Every environment-configurable value (CORS origins, secrets, tariff rates,
MQTT config, model paths, etc.) should be read from here rather than each
module calling `os.getenv` independently.

Uses `pydantic_settings.BaseSettings` for pydantic v2 compatibility.
The `.env` file is loaded automatically.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # -- General -----------------------------------------------------------
    project_name: str = "AI-Driven Household Energy Management"
    api_prefix: str = "/api"
    debug: bool = True

    # -- CORS ----------------------------------------------------------------
    cors_allowed_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:8000,http://127.0.0.1:8000,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8080,http://127.0.0.1:8080"
    )

    # -- Auth ------------------------------------------------------------
    auth_secret_key: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # -- Database --------------------------------------------------------
    database_path: str = ""

    # -- Tariff Rates ----------------------------------------------------
    # BESCOM FY2026-27 (LT-1 Domestic) rates
    bescom_base_rate: float = 5.80
    bescom_surcharge_rate: float = 0.35
    bescom_fixed_charge_per_kw: float = 150.00
    # Electricity tax (ad valorem) on energy + fixed charges
    bescom_electricity_tax_rate: float = 0.09
    # Default reference tariff for non-bill-calculator uses
    bescom_energy_rate: float = 6.15  # base + surcharge (5.80 + 0.35)

    # -- Weather API -----------------------------------------------------
    weather_api_base_url: str = "https://api.open-meteo.com/v1"

    # -- Logging ---------------------------------------------------------
    log_level: str = "INFO"
    log_format: str = "json"

    # -- ML Model Settings ----------------------------------------------
    model_dir: str = "models/trained"
    model_performance_file: str = "model_performances.pkl"

    # -- MQTT ------------------------------------------------------------
    mqtt_enabled: bool = False
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_topic_prefix: str = "energy"

    @field_validator("debug", "mqtt_enabled", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


settings = Settings()
