from pydantic import BaseSettings

class Settings(BaseSettings):
    project_name: str = "AI-Driven Household Energy Management"
    api_prefix: str = "/api"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
