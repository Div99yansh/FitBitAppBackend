import logging
from typing import List, Optional, Dict, Any
from repositories.user_repository import UserRepositoryInterface
from schemas.user_schemas import User, UserCreate

logger = logging.getLogger(__name__)

class UserManager:
    """
    Business logic layer for user operations
    """
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
    
    async def get_all_users(self) -> List[User]:
        """
        Retrieve all users from repository
        
        Returns:
            List[User]: List of all users
        """
        try:
            users = await self.user_repository.get_all_users()
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a specific user by ID
        
        Args:
            user_id: The user identifier
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if user:
                logger.info(f"Retrieved user: {user.name} (ID: {user_id})")
            else:
                logger.warning(f"User not found with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user
        
        Args:
            user_data: The user creation data
            
        Returns:
            User: The created user
        """
        try:
            # Convert Pydantic model to dict
            user_dict = user_data.dict()
            
            # Create user in repository
            new_user = await self.user_repository.create_user(user_dict)
            
            logger.info(f"Successfully created user: {new_user.name} with ID: {new_user.id}")
            return new_user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update an existing user
        
        Args:
            user_id: The user identifier
            user_data: Updated user data
            
        Returns:
            Optional[User]: The updated user if found, None otherwise
        """
        try:
            updated_user = await self.user_repository.update_user(user_id, user_data)
            if updated_user:
                logger.info(f"Successfully updated user: {user_id}")
            else:
                logger.warning(f"User not found for update: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user
        
        Args:
            user_id: The user identifier
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        try:
            deleted = await self.user_repository.delete_user(user_id)
            if deleted:
                logger.info(f"Successfully deleted user: {user_id}")
            else:
                logger.warning(f"User not found for deletion: {user_id}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise