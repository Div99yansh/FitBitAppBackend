from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database import MealDB
from schemas.meal_schemas import Meal, MealCreate
from datetime import datetime
import uuid

# Abstract repository interface (for easy MongoDB migration)
class MealRepositoryInterface(ABC):
    @abstractmethod
    async def create_meal(self, meal_data: Dict[str, Any]) -> Meal:
        pass
    
    @abstractmethod
    async def get_all_meals(self) -> List[Meal]:
        pass
    
    @abstractmethod
    async def get_meal_by_id(self, meal_id: str) -> Optional[Meal]:
        pass
    
    @abstractmethod
    async def update_meal(self, meal_id: str, meal_data: Dict[str, Any]) -> Optional[Meal]:
        pass
    
    @abstractmethod
    async def delete_meal(self, meal_id: str) -> bool:
        pass

# SQLAlchemy implementation
class SQLAlchemyMealRepository(MealRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db
    
    async def create_meal(self, meal_data: Dict[str, Any]) -> Meal:
        # Generate ID if not provided
        if 'id' not in meal_data:
            meal_data['id'] = str(uuid.uuid4())
        
        db_meal = MealDB(**meal_data)
        self.db.add(db_meal)
        self.db.commit()
        self.db.refresh(db_meal)
        
        return Meal.from_orm(db_meal)
    
    async def get_all_meals(self) -> List[Meal]:
        db_meals = self.db.query(MealDB).order_by(MealDB.created_at.desc()).all()
        return [Meal.from_orm(meal) for meal in db_meals]
    
    async def get_meal_by_id(self, meal_id: str) -> Optional[Meal]:
        db_meal = self.db.query(MealDB).filter(MealDB.id == meal_id).first()
        if db_meal:
            return Meal.from_orm(db_meal)
        return None
    
    async def update_meal(self, meal_id: str, meal_data: Dict[str, Any]) -> Optional[Meal]:
        db_meal = self.db.query(MealDB).filter(MealDB.id == meal_id).first()
        if not db_meal:
            return None
        
        # Update fields
        for field, value in meal_data.items():
            if hasattr(db_meal, field):
                setattr(db_meal, field, value)
        
        db_meal.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_meal)
        
        return Meal.from_orm(db_meal)
    
    async def delete_meal(self, meal_id: str) -> bool:
        db_meal = self.db.query(MealDB).filter(MealDB.id == meal_id).first()
        if db_meal:
            self.db.delete(db_meal)
            self.db.commit()
            return True
        return False

# MongoDB implementation placeholder (for future migration)
class MongoMealRepository(MealRepositoryInterface):
    """
    Placeholder for MongoDB implementation
    This will make it easy to switch to MongoDB later
    """
    def __init__(self, mongo_client):
        self.client = mongo_client
        # Implementation will be added when switching to MongoDB
        pass
    
    async def create_meal(self, meal_data: Dict[str, Any]) -> Meal:
        # TODO: Implement MongoDB create
        raise NotImplementedError("MongoDB implementation pending")
    
    async def get_all_meals(self) -> List[Meal]:
        # TODO: Implement MongoDB get all
        raise NotImplementedError("MongoDB implementation pending")
    
    async def get_meal_by_id(self, meal_id: str) -> Optional[Meal]:
        # TODO: Implement MongoDB get by ID
        raise NotImplementedError("MongoDB implementation pending")
    
    async def update_meal(self, meal_id: str, meal_data: Dict[str, Any]) -> Optional[Meal]:
        # TODO: Implement MongoDB update
        raise NotImplementedError("MongoDB implementation pending")
    
    async def delete_meal(self, meal_id: str) -> bool:
        # TODO: Implement MongoDB delete
        raise NotImplementedError("MongoDB implementation pending")