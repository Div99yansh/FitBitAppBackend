import logging
from typing import List, Optional, Dict, Any
from meal_repository import MealRepositoryInterface
from schemas.meal_schemas import Meal, MealCreate
from gemini_nutrition import GeminiNutritionServiceSync
from config import settings

logger = logging.getLogger(__name__)

class MealManager:
    """
    Business logic layer for meal operations
    Handles all meal-related business logic and orchestrates
    between repository and external services
    """
    
    def __init__(self, meal_repository: MealRepositoryInterface):
        self.meal_repository = meal_repository
        self.nutrition_service = self._initialize_nutrition_service()
    
    def _initialize_nutrition_service(self) -> Optional[GeminiNutritionServiceSync]:
        """Initialize Gemini nutrition service"""
        try:
            if not settings.gemini_api_key:
                logger.warning("Gemini API key not provided - nutrition analysis will be unavailable")
                return None
            
            service = GeminiNutritionServiceSync(api_key=settings.gemini_api_key)
            logger.info("Gemini nutrition service initialized successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            return None
    
    async def get_all_meals(self) -> List[Meal]:
        """
        Retrieve all meals from repository
        
        Returns:
            List[Meal]: List of all meals
        """
        try:
            meals = await self.meal_repository.get_all_meals()
            logger.info(f"Retrieved {len(meals)} meals")
            return meals
        except Exception as e:
            logger.error(f"Error retrieving meals: {str(e)}")
            raise
    
    async def get_meal_by_id(self, meal_id: str) -> Optional[Meal]:
        """
        Retrieve a specific meal by ID
        
        Args:
            meal_id: The meal identifier
            
        Returns:
            Optional[Meal]: The meal if found, None otherwise
        """
        try:
            meal = await self.meal_repository.get_meal_by_id(meal_id)
            if meal:
                logger.info(f"Retrieved meal: {meal.name} (ID: {meal_id})")
            else:
                logger.warning(f"Meal not found with ID: {meal_id}")
            return meal
        except Exception as e:
            logger.error(f"Error retrieving meal {meal_id}: {str(e)}")
            raise
    
    async def create_meal_with_nutrition_analysis(self, meal_data: MealCreate) -> Meal:
        """
        Create a new meal with automatic nutrition analysis
        
        Args:
            meal_data: The meal creation data
            
        Returns:
            Meal: The created meal with nutrition information
            
        Raises:
            ValueError: If nutrition service is unavailable
            Exception: If nutrition analysis or meal creation fails
        """
        try:
            meal_name = meal_data.name.strip()
            logger.info(f"Creating meal with nutrition analysis: {meal_name}")
            
            # Check if nutrition service is available
            if not self.nutrition_service:
                raise ValueError("Nutrition analysis service is not available")
            
            # Analyze nutrition using Gemini
            nutrition_data = await self._analyze_meal_nutrition(meal_name)
            
            # Prepare meal data for storage
            meal_db_data = {
                "name": meal_name,
                **nutrition_data  # Unpack all nutrition data
            }
            
            # Create meal in repository
            new_meal = await self.meal_repository.create_meal(meal_db_data)
            
            logger.info(f"Successfully created meal: {meal_name} with ID: {new_meal.id}")
            return new_meal
            
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error(f"Error creating meal with nutrition analysis: {str(e)}")
            raise
    
    async def create_meal_manual(self, meal_data: Dict[str, Any]) -> Meal:
        """
        Create a meal with manually provided nutrition data
        
        Args:
            meal_data: Complete meal data including nutrition
            
        Returns:
            Meal: The created meal
        """
        try:
            meal_name = meal_data.get("name", "").strip()
            logger.info(f"Creating meal with manual data: {meal_name}")
            
            new_meal = await self.meal_repository.create_meal(meal_data)
            logger.info(f"Successfully created manual meal: {meal_name} with ID: {new_meal.id}")
            return new_meal
            
        except Exception as e:
            logger.error(f"Error creating manual meal: {str(e)}")
            raise
    
    async def update_meal(self, meal_id: str, meal_data: Dict[str, Any]) -> Optional[Meal]:
        """
        Update an existing meal
        
        Args:
            meal_id: The meal identifier
            meal_data: Updated meal data
            
        Returns:
            Optional[Meal]: The updated meal if found, None otherwise
        """
        try:
            updated_meal = await self.meal_repository.update_meal(meal_id, meal_data)
            if updated_meal:
                logger.info(f"Successfully updated meal: {meal_id}")
            else:
                logger.warning(f"Meal not found for update: {meal_id}")
            return updated_meal
        except Exception as e:
            logger.error(f"Error updating meal {meal_id}: {str(e)}")
            raise
    
    async def delete_meal(self, meal_id: str) -> bool:
        """
        Delete a meal
        
        Args:
            meal_id: The meal identifier
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        try:
            deleted = await self.meal_repository.delete_meal(meal_id)
            if deleted:
                logger.info(f"Successfully deleted meal: {meal_id}")
            else:
                logger.warning(f"Meal not found for deletion: {meal_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting meal {meal_id}: {str(e)}")
            raise
    
    async def get_meal_statistics(self) -> Dict[str, Any]:
        """
        Calculate and return meal statistics
        
        Returns:
            Dict[str, Any]: Comprehensive meal statistics
        """
        try:
            meals = await self.meal_repository.get_all_meals()
            
            total_meals = len(meals)
            if total_meals == 0:
                return {
                    "total_meals": 0,
                    "message": "No meals in database"
                }
            
            # Calculate statistics
            stats = self._calculate_meal_statistics(meals)
            logger.info("Calculated meal statistics successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating meal statistics: {str(e)}")
            raise
    
    async def _analyze_meal_nutrition(self, meal_name: str) -> Dict[str, Any]:
        """
        Analyze meal nutrition using Gemini service
        
        Args:
            meal_name: Name of the meal to analyze
            
        Returns:
            Dict[str, Any]: Nutrition data
        """
        try:
            logger.info(f"Analyzing nutrition for: {meal_name}")
            nutrition_data = self.nutrition_service.analyze_meal_nutrition(meal_name)
            logger.info(f"Nutrition analysis completed for: {meal_name}")
            return nutrition_data
        except Exception as e:
            logger.error(f"Nutrition analysis failed for {meal_name}: {str(e)}")
            raise Exception(f"Failed to analyze meal nutrition: {str(e)}")
    
    def _calculate_meal_statistics(self, meals: List[Meal]) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics from meals list
        
        Args:
            meals: List of meals to analyze
            
        Returns:
            Dict[str, Any]: Calculated statistics
        """
        total_meals = len(meals)
        
        # Count meals with different nutrients
        meals_with_calories = len([m for m in meals if m.calories is not None])
        meals_with_protein = len([m for m in meals if m.protein is not None])
        meals_with_fats = len([m for m in meals if m.fats is not None])
        meals_with_carbs = len([m for m in meals if m.carbohydrates is not None])
        
        # Calculate totals
        total_calories = sum(m.calories or 0 for m in meals)
        total_protein = sum(m.protein or 0 for m in meals)
        total_fats = sum(m.fats or 0 for m in meals)
        total_carbs = sum(m.carbohydrates or 0 for m in meals)
        total_fiber = sum(m.fiber or 0 for m in meals)
        total_sugar = sum(m.sugar or 0 for m in meals)
        total_sodium = sum(m.sodium or 0 for m in meals)
        
        return {
            "total_meals": total_meals,
            "data_completeness": {
                "meals_with_calories": meals_with_calories,
                "meals_with_protein": meals_with_protein,
                "meals_with_fats": meals_with_fats,
                "meals_with_carbohydrates": meals_with_carbs,
                "completion_percentage": {
                    "calories": round((meals_with_calories / total_meals) * 100, 1),
                    "protein": round((meals_with_protein / total_meals) * 100, 1),
                    "fats": round((meals_with_fats / total_meals) * 100, 1),
                    "carbohydrates": round((meals_with_carbs / total_meals) * 100, 1)
                }
            },
            "totals": {
                "calories": round(total_calories, 2),
                "protein": round(total_protein, 2),
                "fats": round(total_fats, 2),
                "carbohydrates": round(total_carbs, 2),
                "fiber": round(total_fiber, 2),
                "sugar": round(total_sugar, 2),
                "sodium": round(total_sodium, 2)
            },
            "averages_per_meal": {
                "calories": round(total_calories / total_meals, 2) if total_meals > 0 else 0,
                "protein": round(total_protein / total_meals, 2) if total_meals > 0 else 0,
                "fats": round(total_fats / total_meals, 2) if total_meals > 0 else 0,
                "carbohydrates": round(total_carbs / total_meals, 2) if total_meals > 0 else 0,
                "fiber": round(total_fiber / total_meals, 2) if total_meals > 0 else 0,
                "sugar": round(total_sugar / total_meals, 2) if total_meals > 0 else 0,
                "sodium": round(total_sodium / total_meals, 2) if total_meals > 0 else 0
            },
            "nutrition_insights": {
                "high_protein_meals": len([m for m in meals if (m.protein or 0) > 15]),
                "low_calorie_meals": len([m for m in meals if (m.calories or 0) < 200]),
                "high_fiber_meals": len([m for m in meals if (m.fiber or 0) > 5]),
                "high_sodium_meals": len([m for m in meals if (m.sodium or 0) > 400])
            }
        }
    
    def is_nutrition_service_available(self) -> bool:
        """Check if nutrition analysis service is available"""
        return self.nutrition_service is not None