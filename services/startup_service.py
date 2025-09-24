import logging
from database import create_tables, get_db
from meal_repository import SQLAlchemyMealRepository

logger = logging.getLogger(__name__)

class StartupService:
    """Service to handle application startup logic"""
    
    @staticmethod
    async def initialize_database():
        """Initialize database and add sample data if needed"""
        try:
            logger.info("Creating database tables...")
            create_tables()
            
            # Add sample data if database is empty
            await StartupService._add_sample_data_if_needed()
            
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    @staticmethod
    async def _add_sample_data_if_needed():
        """Add sample meals if database is empty"""
        try:
            db = next(get_db())
            repo = SQLAlchemyMealRepository(db)
            
            # Check if meals already exist
            existing_meals = await repo.get_all_meals()
            if existing_meals:
                logger.info(f"Database already contains {len(existing_meals)} meals")
                return
            
            logger.info("Adding sample meals to database...")
            sample_meals = [
                {
                    "name": "2 Chapati",
                    "calories": 240.0,
                    "protein": 8.0,
                    "fats": 4.0,
                    "carbohydrates": 48.0,
                    "fiber": 4.0,
                    "sugar": 2.0,
                    "sodium": 320.0
                },
                {
                    "name": "1 Bowl Dal",
                    "calories": 180.0,
                    "protein": 12.0,
                    "fats": 2.0,
                    "carbohydrates": 28.0,
                    "fiber": 6.0,
                    "sugar": 3.0,
                    "sodium": 450.0
                },
                {
                    "name": "1 Plate Upma",
                    "calories": 220.0,
                    "protein": 6.0,
                    "fats": 8.0,
                    "carbohydrates": 35.0,
                    "fiber": 3.0,
                    "sugar": 4.0,
                    "sodium": 380.0
                },
                {
                    "name": "Oatmeal Bowl",
                    "calories": 150.0,
                    "protein": 5.0,
                    "fats": 3.0,
                    "carbohydrates": 27.0,
                    "fiber": 4.0,
                    "sugar": 8.0,
                    "sodium": 200.0
                }
            ]
            
            for meal_data in sample_meals:
                await repo.create_meal(meal_data)
            
            logger.info(f"Added {len(sample_meals)} sample meals successfully")
            
        except Exception as e:
            logger.error(f"Error adding sample data: {str(e)}")
            # Don't raise the exception as this is not critical
    
    @staticmethod
    def setup_logging():
        """Configure application logging"""
        from config import settings
        
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                # logging.FileHandler("app.log")  # Uncomment if you want file logging
            ]
        )
        
        logger.info(f"Logging configured with level: {settings.log_level}")
    
    @staticmethod
    async def startup_event():
        """Complete startup sequence"""
        logger.info("Starting application startup sequence...")
        
        # Setup logging first
        StartupService.setup_logging()
        
        # Initialize database
        await StartupService.initialize_database()
        
        logger.info("Application startup sequence completed successfully")