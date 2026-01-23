import logging
from typing import List, Optional
from repositories.user_day_meal_repository import UserDayMealRepositoryInterface
from schemas.meal_schemas import Meal
from schemas.user_day_meal_schemas import (
    DayMealsResponse,
    SaveDayMealsRequest,
    SaveDayMealsResponse,
    UserMealCreate
)
from gemini_nutrition import GeminiNutritionServiceSync
from config import settings

logger = logging.getLogger(__name__)


class UserMealManager:
    """
    Business logic layer for user-scoped meal operations.
    Handles authenticated user's meals and day meal tracking.
    """

    def __init__(self, repository: UserDayMealRepositoryInterface):
        self.repository = repository
        self.nutrition_service = self._initialize_nutrition_service()

    def _initialize_nutrition_service(self) -> Optional[GeminiNutritionServiceSync]:
        """Initialize Gemini nutrition service"""
        try:
            if not settings.gemini_api_key:
                logger.warning("Gemini API key not provided - nutrition analysis unavailable")
                return None

            service = GeminiNutritionServiceSync(api_key=settings.gemini_api_key)
            logger.info("Gemini nutrition service initialized for UserMealManager")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            return None

    def is_nutrition_service_available(self) -> bool:
        """Check if nutrition analysis service is available"""
        return self.nutrition_service is not None

    async def get_user_meals(self, user_id: str) -> List[Meal]:
        """
        Get all meals for a specific user.

        Args:
            user_id: The authenticated user's ID

        Returns:
            List[Meal]: List of user's meals
        """
        try:
            meals = await self.repository.get_user_meals(user_id)
            logger.info(f"Retrieved {len(meals)} meals for user {user_id}")
            return meals
        except Exception as e:
            logger.error(f"Error retrieving meals for user {user_id}: {str(e)}")
            raise

    async def add_user_meal(self, user_id: str, meal_data: UserMealCreate) -> Meal:
        """
        Create a new meal with nutrition analysis for a user.

        Args:
            user_id: The authenticated user's ID
            meal_data: The meal creation data (just name)

        Returns:
            Meal: The created meal with nutrition information

        Raises:
            ValueError: If nutrition service is unavailable
        """
        try:
            meal_name = meal_data.name.strip()
            logger.info(f"Creating meal with nutrition analysis for user {user_id}: {meal_name}")

            if not self.nutrition_service:
                raise ValueError("Nutrition analysis service is not available")

            # Analyze nutrition using Gemini
            nutrition_data = self._analyze_meal_nutrition(meal_name)

            # Prepare meal data
            meal_db_data = {
                "name": meal_name,
                **nutrition_data
            }

            # Create meal in repository
            new_meal = await self.repository.create_user_meal(user_id, meal_db_data)

            logger.info(f"Created meal {new_meal.id} for user {user_id}")
            return new_meal

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating meal for user {user_id}: {str(e)}")
            raise

    async def get_user_day_meals(self, user_id: str, date: str) -> DayMealsResponse:
        """
        Get meals for a user on a specific date organized by meal type.

        Args:
            user_id: The authenticated user's ID
            date: Date in YYYY-MM-DD format

        Returns:
            DayMealsResponse: Meals organized by breakfast, lunch, dinner
        """
        try:
            day_meals = await self.repository.get_day_meals(user_id, date)
            logger.info(f"Retrieved day meals for user {user_id} on {date}")
            return day_meals
        except Exception as e:
            logger.error(f"Error retrieving day meals for user {user_id}: {str(e)}")
            raise

    async def save_user_day_meals(
        self, user_id: str, request: SaveDayMealsRequest
    ) -> SaveDayMealsResponse:
        """
        Save/replace meal associations for a user on a specific date and meal type.
        Links existing meals to the date/mealType - does not create new meals.

        Args:
            user_id: The authenticated user's ID
            request: Save request with date, mealType, and mealIds

        Returns:
            SaveDayMealsResponse: Confirmation of saved associations
        """
        try:
            count = await self.repository.save_day_meals(
                user_id=user_id,
                date=request.date,
                meal_type=request.mealType,
                meal_ids=request.mealIds
            )

            logger.info(
                f"Saved {count} meal associations for user {user_id} on {request.date} ({request.mealType})"
            )

            return SaveDayMealsResponse(
                message=f"Successfully saved {count} meal associations",
                date=request.date,
                mealType=request.mealType,
                totalMeals=count
            )

        except Exception as e:
            logger.error(f"Error saving day meals for user {user_id}: {str(e)}")
            raise

    def _analyze_meal_nutrition(self, meal_name: str) -> dict:
        """
        Analyze meal nutrition using Gemini service.

        Args:
            meal_name: Name of the meal to analyze

        Returns:
            dict: Nutrition data
        """
        try:
            logger.info(f"Analyzing nutrition for: {meal_name}")
            nutrition_data = self.nutrition_service.analyze_meal_nutrition(meal_name)
            logger.info(f"Nutrition analysis completed for: {meal_name}")
            return nutrition_data
        except Exception as e:
            logger.error(f"Nutrition analysis failed for {meal_name}: {str(e)}")
            raise Exception(f"Failed to analyze meal nutrition: {str(e)}")
