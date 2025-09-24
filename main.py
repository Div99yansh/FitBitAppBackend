"""
Fitbit Meals API - Main Application Entry Point

This is the startup file for the FastAPI application.
It handles application initialization, middleware setup, and route registration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from config import settings

# Import controllers
from controllers.meal_controller import router as meal_router
from controllers.health_controller import router as health_router

# Import services
from services.startup_service import StartupService

# Configure logging
StartupService.setup_logging()
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Returns:
        FastAPI: Configured application instance
    """
    
    # Create FastAPI instance
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    
    # Register routers
    app.include_router(health_router)
    app.include_router(meal_router)
    
    # Application event handlers
    @app.on_event("startup")
    async def startup_event():
        """Handle application startup"""
        await StartupService.startup_event()
        logger.info(f"🚀 {settings.app_name} v{settings.app_version} started successfully")
        logger.info(f"📖 API Documentation: http://{settings.host}:{settings.port}/docs")
        logger.info(f"🌐 Frontend CORS enabled for: {', '.join(settings.allowed_origins)}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle application shutdown"""
        logger.info("Shutting down application...")
        # Add any cleanup logic here if needed
    
    return app

# Create the application instance
app = create_app()

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "meals_endpoint": "/fitbit/getMeals"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} server...")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )