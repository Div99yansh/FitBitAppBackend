from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

# Import our modules
from database import get_db, create_tables
from meal_repository import (
    SQLAlchemyMealRepository, 
    Meal, 
    MealCreate,
    MealRepositoryInterface
)
from gemini_nutrition import GeminiNutritionServiceSync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Response models
class MealResponse(BaseModel):
    meal: Meal
    message: str

class MealsListResponse(BaseModel):
    meals: List[Meal]
    total_count: int

# Initialize Gemini nutrition service
try:
    nutrition_service = GeminiNutritionServiceSync()
    logger.info("Gemini nutrition service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini service: {str(e)}")
    nutrition_service = None

# FastAPI app
app = FastAPI(
    title="Fitbit Meals API with Database",
    description="A modern FastAPI backend for managing meals with nutritional information using SQLAlchemy",
    version="2.0.0"
)

# CORS middleware for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables...")
    create_tables()
    
    # Add some sample data if database is empty
    db = next(get_db())
    repo = SQLAlchemyMealRepository(db)
    
    try:
        existing_meals = await repo.get_all_meals()
        if not existing_meals:
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
            
            logger.info("Sample meals added successfully")
    except Exception as e:
        logger.error(f"Error setting up sample data: {str(e)}")

# Dependency to get repository
def get_meal_repository(db: Session = Depends(get_db)) -> MealRepositoryInterface:
    return SQLAlchemyMealRepository(db)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Fitbit Meals API with Database is running",
        "gemini_service": "available" if nutrition_service else "unavailable"
    }

# Get all meals endpoint
@app.get(
    "/fitbit/getMeals", 
    response_model=MealsListResponse,
    tags=["Meals"],
    summary="Get all meals from database"
)
async def get_meals(repo: MealRepositoryInterface = Depends(get_meal_repository)):
    """Get all meals from the database"""
    try:
        meals = await repo.get_all_meals()
        logger.info(f"Retrieved {len(meals)} meals from database")
        
        return MealsListResponse(
            meals=meals,
            total_count=len(meals)
        )
    except Exception as e:
        logger.error(f"Error retrieving meals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve meals from database"
        )

# Add meal with nutrition analysis
@app.post(
    "/fitbit/addMeal", 
    response_model=MealResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["Meals"],
    summary="Add new meal with AI nutrition analysis"
)
async def add_meal(
    meal_data: MealCreate,
    repo: MealRepositoryInterface = Depends(get_meal_repository)
):
    """
    Add a new meal with automatic nutrition analysis using Gemini AI
    and store it in the database
    """
    try:
        # Check if Gemini service is available
        if not nutrition_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nutrition analysis service is not available. Please check API configuration."
            )
        
        meal_name = meal_data.name.strip()
        logger.info(f"Processing meal: {meal_name}")
        
        # Analyze nutrition using Gemini
        try:
            nutrition_data = nutrition_service.analyze_meal_nutrition(meal_name)
            logger.info(f"Nutrition analysis completed for: {meal_name}")
        except Exception as e:
            logger.error(f"Nutrition analysis failed for {meal_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to analyze meal nutrition: {str(e)}"
            )
        
        # Prepare meal data for database
        meal_db_data = {
            "name": meal_name,
            "calories": nutrition_data.get("calories"),
            "protein": nutrition_data.get("protein"),
            "fats": nutrition_data.get("fats"),
            "carbohydrates": nutrition_data.get("carbohydrates"),
            "fiber": nutrition_data.get("fiber"),
            "sugar": nutrition_data.get("sugar"),
            "sodium": nutrition_data.get("sodium")
        }
        
        # Save to database
        new_meal = await repo.create_meal(meal_db_data)
        
        logger.info(f"Successfully added meal to database: {meal_name} with ID: {new_meal.id}")
        
        return MealResponse(
            meal=new_meal,
            message="Meal analyzed and saved to database successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding meal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the meal"
        )

# Get meal by ID
@app.get(
    "/fitbit/getMeal/{meal_id}",
    response_model=Meal,
    tags=["Meals"],
    summary="Get meal by ID"
)
async def get_meal_by_id(
    meal_id: str,
    repo: MealRepositoryInterface = Depends(get_meal_repository)
):
    """Get a specific meal by ID from database"""
    try:
        meal = await repo.get_meal_by_id(meal_id)
        if not meal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meal with ID {meal_id} not found"
            )
        return meal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving meal {meal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve meal"
        )

# Delete meal
@app.delete(
    "/fitbit/deleteMeal/{meal_id}",
    tags=["Meals"],
    summary="Delete meal by ID"
)
async def delete_meal(
    meal_id: str,
    repo: MealRepositoryInterface = Depends(get_meal_repository)
):
    """Delete a meal from database"""
    try:
        deleted = await repo.delete_meal(meal_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meal with ID {meal_id} not found"
            )
        
        logger.info(f"Meal {meal_id} deleted successfully")
        return {"message": "Meal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meal {meal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete meal"
        )

# Get meal statistics
@app.get("/fitbit/stats", tags=["Statistics"])
async def get_meal_stats(repo: MealRepositoryInterface = Depends(get_meal_repository)):
    """Get statistics about all meals in database"""
    try:
        meals = await repo.get_all_meals()
        
        total_meals = len(meals)
        if total_meals == 0:
            return {
                "total_meals": 0,
                "message": "No meals in database"
            }
        
        # Calculate statistics
        meals_with_calories = len([m for m in meals if m.calories is not None])
        meals_with_protein = len([m for m in meals if m.protein is not None])
        
        total_calories = sum(m.calories or 0 for m in meals)
        total_protein = sum(m.protein or 0 for m in meals)
        total_fats = sum(m.fats or 0 for m in meals)
        total_carbs = sum(m.carbohydrates or 0 for m in meals)
        
        return {
            "total_meals": total_meals,
            "meals_with_calories": meals_with_calories,
            "meals_with_protein": meals_with_protein,
            "totals": {
                "calories": round(total_calories, 2),
                "protein": round(total_protein, 2),
                "fats": round(total_fats, 2),
                "carbohydrates": round(total_carbs, 2)
            },
            "averages": {
                "calories_per_meal": round(total_calories / total_meals, 2) if total_meals > 0 else 0,
                "protein_per_meal": round(total_protein / total_meals, 2) if total_meals > 0 else 0,
                "fats_per_meal": round(total_fats / total_meals, 2) if total_meals > 0 else 0,
                "carbs_per_meal": round(total_carbs / total_meals, 2) if total_meals > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Error calculating stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate meal statistics"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)