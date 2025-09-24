from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_db
from schemas.meal_schemas import HealthResponse
from config import settings

router = APIRouter(tags=["Health"])

@router.get(
    "/health", 
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Check the health status of the API and its services"
)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and services status"""
    
    # Check database connection
    try:
        # Try a simple database query
        db.execute("SELECT 1")
        database_status = "connected"
    except Exception:
        database_status = "disconnected"
    
    # Check Gemini service
    gemini_status = "available" if settings.gemini_api_key else "unavailable"
    
    return HealthResponse(
        status="healthy" if database_status == "connected" else "degraded",
        message=f"{settings.app_name} is running",
        gemini_service=gemini_status,
        database=database_status,
        timestamp=datetime.utcnow()
    )