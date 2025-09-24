from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging
from sqlalchemy.orm import Session

# Import dependencies
from database import get_db
from meal_repository import SQLAlchemyMealRepository
from schemas.meal_schemas import Meal, MealCreate, MealResponse, MealsListResponse
from managers.meal_manager import MealManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/fitbit", tags=["Meals"])

# Dependency to get meal manager
def get_meal_manager(db: Session = Depends(get_db)) -> MealManager:
    """Dependency to get meal manager with repository"""
    repository = SQLAlchemyMealRepository(db)
    return MealManager(repository)

@router.get(
    "/getMeals", 
    response_model=MealsListResponse,
    summary="Get all meals from database",
    description="Retrieve all meals stored in the database with their nutritional information"
)
async def get_meals(manager: MealManager = Depends(get_meal_manager)):
    """Get all meals from the database"""
    try:
        meals = await manager.get_all_meals()
        logger.info(f"Retrieved {len(meals)} meals via API")
        
        return MealsListResponse(
            meals=meals,
            total_count=len(meals)
        )
    except Exception as e:
        logger.error(f"API error retrieving meals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve meals from database"
        )

@router.post(
    "/addMeal", 
    response_model=MealResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Add new meal with AI nutrition analysis",
    description="Add a new meal with automatic nutrition analysis using Gemini AI and store it in the database"
)
async def add_meal(
    meal_data: MealCreate,
    manager: MealManager = Depends(get_meal_manager)
):
    """Add a new meal with automatic nutrition analysis using Gemini AI"""
    try:
        # Check if nutrition service is available
        if not manager.is_nutrition_service_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nutrition analysis service is not available. Please check API configuration."
            )
        
        # Create meal with nutrition analysis
        new_meal = await manager.create_meal_with_nutrition_analysis(meal_data)
        
        return MealResponse(
            meal=new_meal,
            message="Meal analyzed and saved to database successfully"
        )
        
    except ValueError as ve:
        # Handle business logic validation errors
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"API error adding meal: {str(e)}")
        if "Failed to analyze meal nutrition" in str(e):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while adding the meal"
            )

@router.get(
    "/getMeal/{meal_id}",
    response_model=Meal,
    summary="Get meal by ID",
    description="Retrieve a specific meal by its ID from the database"
)
async def get_meal_by_id(
    meal_id: str,
    manager: MealManager = Depends(get_meal_manager)
):
    """Get a specific meal by ID from database"""
    try:
        meal = await manager.get_meal_by_id(meal_id)
        if not meal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meal with ID {meal_id} not found"
            )
        return meal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error retrieving meal {meal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve meal"
        )

@router.put(
    "/updateMeal/{meal_id}",
    response_model=MealResponse,
    summary="Update meal by ID",
    description="Update an existing meal's information"
)
async def update_meal(
    meal_id: str,
    meal_data: MealCreate,
    manager: MealManager = Depends(get_meal_manager)
):
    """Update an existing meal"""
    try:
        # Convert MealCreate to dict
        update_data = meal_data.dict(exclude_unset=True)
        
        updated_meal = await manager.update_meal(meal_id, update_data)
        if not updated_meal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meal with ID {meal_id} not found"
            )
        
        return MealResponse(
            meal=updated_meal,
            message="Meal updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error updating meal {meal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update meal"
        )

@router.delete(
    "/deleteMeal/{meal_id}",
    summary="Delete meal by ID",
    description="Delete a meal from the database"
)
async def delete_meal(
    meal_id: str,
    manager: MealManager = Depends(get_meal_manager)
):
    """Delete a meal from database"""
    try:
        deleted = await manager.delete_meal(meal_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meal with ID {meal_id} not found"
            )
        
        return {"message": "Meal deleted successfully", "meal_id": meal_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error deleting meal {meal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete meal"
        )

@router.get(
    "/stats",
    summary="Get meal statistics",
    description="Get comprehensive statistics about all meals in the database"
)
async def get_meal_stats(manager: MealManager = Depends(get_meal_manager)):
    """Get comprehensive statistics about all meals in database"""
    try:
        stats = await manager.get_meal_statistics()
        return stats
    except Exception as e:
        logger.error(f"API error calculating stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate meal statistics"
        )