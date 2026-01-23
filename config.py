import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

#loading dotenv
load_dotenv()

class Settings(BaseSettings):
    # App settings
    app_name: str = "Fitbit Meals API"
    app_version: str = "2.0.0"
    description: str = "A modern FastAPI backend for managing meals with nutritional information"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "true").lower() == "true"

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./meals.db")

    # CORS settings
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True
    
    # Gemini API settings
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # JWT settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Logging settings
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()