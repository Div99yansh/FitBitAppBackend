import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from dotenv import load_dotenv
from typing import List

#loading dotenv
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # App settings
    app_name: str = "Fitbit Meals API"
    app_version: str = "2.0.0"
    description: str = "A modern FastAPI backend for managing meals with nutritional information"
    debug: bool = True

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Database settings
    database_url: str = "sqlite:///./meals.db"

    # CORS settings (stored as comma-separated string from env)
    allowed_origins_str: str = "http://localhost:5173"
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True

    @computed_field
    @property
    def allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins_str.split(",")]

    # Gemini API settings
    gemini_api_key: str = ""

    # JWT settings
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Logging settings
    log_level: str = "INFO"

# Global settings instance
settings = Settings()