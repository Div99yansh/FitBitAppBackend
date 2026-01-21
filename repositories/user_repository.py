from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database import UserDB
from schemas.user_schemas import User, UserCreate
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

# Abstract repository interface
class UserRepositoryInterface(ABC):
    @abstractmethod
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        pass
    
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass

# SQLAlchemy implementation
class SQLAlchemyUserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        # Generate ID if not provided
        if 'id' not in user_data:
            user_data['id'] = str(uuid.uuid4())
        
        db_user = UserDB(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return User.from_orm(db_user)
    
    async def get_all_users(self) -> List[User]:
        db_users = self.db.query(UserDB).order_by(UserDB.created_at.desc()).all()
        return [User.from_orm(user) for user in db_users]
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            return User.from_orm(db_user)
        return None
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return None
        
        # Update fields
        for field, value in user_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        
        return User.from_orm(db_user)
    
    async def delete_user(self, user_id: str) -> bool:
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

# MongoDB implementation placeholder (for future migration)
class MongoUserRepository(UserRepositoryInterface):
    """
    Placeholder for MongoDB implementation
    """
    def __init__(self, mongo_client):
        self.client = mongo_client
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        raise NotImplementedError("MongoDB implementation pending")
    
    async def get_all_users(self) -> List[User]:
        raise NotImplementedError("MongoDB implementation pending")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError("MongoDB implementation pending")
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        raise NotImplementedError("MongoDB implementation pending")
    
    async def delete_user(self, user_id: str) -> bool:
        raise NotImplementedError("MongoDB implementation pending")