from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database import MealDB, UserDayMealDB
from schemas.meal_schemas import Meal
from schemas.user_day_meal_schemas import DayMealsResponse, MealInput
from datetime import datetime
import uuid


class UserDayMealRepositoryInterface(ABC):
    """Abstract interface for user day meal repository"""

    @abstractmethod
    async def get_user_meals(self, user_id: str) -> List[Meal]:
        """Get all meals for a user"""
        pass

    @abstractmethod
    async def create_user_meal(self, user_id: str, meal_data: Dict[str, Any]) -> Meal:
        """Create a meal associated with a user"""
        pass

    @abstractmethod
    async def get_day_meals(self, user_id: str, date: str) -> DayMealsResponse:
        """Get meals for a user on a specific date organized by type"""
        pass

    @abstractmethod
    async def save_day_meals(
        self, user_id: str, date: str, meal_type: str, meals: List[MealInput]
    ) -> int:
        """Save/replace day meals for a user, returns count of meals saved"""
        pass


class SQLAlchemyUserDayMealRepository(UserDayMealRepositoryInterface):
    """SQLAlchemy implementation of user day meal repository"""

    def __init__(self, db: Session):
        self.db = db

    async def get_user_meals(self, user_id: str) -> List[Meal]:
        """Get all meals associated with a user"""
        db_meals = (
            self.db.query(MealDB)
            .filter(MealDB.user_id == user_id)
            .order_by(MealDB.created_at.desc())
            .all()
        )
        return [Meal.model_validate(meal) for meal in db_meals]

    async def create_user_meal(self, user_id: str, meal_data: Dict[str, Any]) -> Meal:
        """Create a new meal associated with a user"""
        if 'id' not in meal_data:
            meal_data['id'] = str(uuid.uuid4())

        meal_data['user_id'] = user_id

        db_meal = MealDB(**meal_data)
        self.db.add(db_meal)
        self.db.commit()
        self.db.refresh(db_meal)

        return Meal.model_validate(db_meal)

    async def get_day_meals(self, user_id: str, date: str) -> DayMealsResponse:
        """Get meals for a user on a specific date organized by meal type"""
        # Query all day meal entries for the user and date
        day_meal_entries = (
            self.db.query(UserDayMealDB)
            .filter(UserDayMealDB.user_id == user_id, UserDayMealDB.date == date)
            .all()
        )

        # Organize meals by type
        breakfast_meals = []
        lunch_meals = []
        dinner_meals = []

        for entry in day_meal_entries:
            meal = self.db.query(MealDB).filter(MealDB.id == entry.meal_id).first()
            if meal:
                meal_schema = Meal.model_validate(meal)
                if entry.meal_type == "breakfast":
                    breakfast_meals.append(meal_schema)
                elif entry.meal_type == "lunch":
                    lunch_meals.append(meal_schema)
                elif entry.meal_type == "dinner":
                    dinner_meals.append(meal_schema)

        return DayMealsResponse(
            date=date,
            breakfast=breakfast_meals,
            lunch=lunch_meals,
            dinner=dinner_meals
        )

    async def save_day_meals(
        self, user_id: str, date: str, meal_type: str, meals: List[MealInput]
    ) -> int:
        """
        Save/replace day meals for a user.
        Removes existing entries for the user/date/meal_type combo and adds new ones.
        """
        # Remove existing entries for this user/date/meal_type
        existing_entries = (
            self.db.query(UserDayMealDB)
            .filter(
                UserDayMealDB.user_id == user_id,
                UserDayMealDB.date == date,
                UserDayMealDB.meal_type == meal_type
            )
            .all()
        )

        for entry in existing_entries:
            self.db.delete(entry)

        # Create new meals and day meal entries
        count = 0
        for meal_input in meals:
            # Create the meal
            meal_id = str(uuid.uuid4())
            db_meal = MealDB(
                id=meal_id,
                name=meal_input.name,
                calories=meal_input.calories,
                protein=meal_input.protein,
                fats=meal_input.fats,
                carbohydrates=meal_input.carbohydrates,
                fiber=meal_input.fiber,
                sugar=meal_input.sugar,
                sodium=meal_input.sodium,
                user_id=user_id
            )
            self.db.add(db_meal)

            # Create the day meal entry
            day_meal_entry = UserDayMealDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                meal_id=meal_id,
                date=date,
                meal_type=meal_type
            )
            self.db.add(day_meal_entry)
            count += 1

        self.db.commit()
        return count
