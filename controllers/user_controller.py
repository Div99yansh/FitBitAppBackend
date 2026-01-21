from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging
from sqlalchemy.orm import Session

# Import dependencies
from database import get_db
from repositories.user_repository import SQLAlchemyUserRepository
from schemas.user_schemas import User, UserCreate, UserResponse, UsersListResponse
from managers.user_manager import UserManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# Dependency to get user manager
def get_user_manager(db: Session = Depends(get_db)) -> UserManager:
    """Dependency to get user manager with repository"""
    repository = SQLAlchemyUserRepository(db)
    return UserManager(repository)

@router.get(
    "/getUsers", 
    response_model=UsersListResponse,
    summary="Get all users from database",
    description="Retrieve all users stored in the database"
)
async def get_users(manager: UserManager = Depends(get_user_manager)):
    """Get all users from the database"""
    try:
        users = await manager.get_all_users()
        logger.info(f"Retrieved {len(users)} users via API")
        
        return UsersListResponse(
            users=users,
            total_count=len(users)
        )
    except Exception as e:
        logger.error(f"API error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users from database"
        )

@router.post(
    "/addUser", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Add new user",
    description="Create a new user and store in the database"
)
async def add_user(
    user_data: UserCreate,
    manager: UserManager = Depends(get_user_manager)
):
    """Add a new user to the database"""
    try:
        new_user = await manager.create_user(user_data)
        
        return UserResponse(
            user=new_user,
            message="User created successfully"
        )
        
    except Exception as e:
        logger.error(f"API error adding user: {str(e)}")
        # Check for duplicate email error
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while adding the user"
            )

@router.get(
    "/getUser/{user_id}",
    response_model=User,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID from the database"
)
async def get_user_by_id(
    user_id: str,
    manager: UserManager = Depends(get_user_manager)
):
    """Get a specific user by ID from database"""
    try:
        user = await manager.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.put(
    "/updateUser/{user_id}",
    response_model=UserResponse,
    summary="Update user by ID",
    description="Update an existing user's information"
)
async def update_user(
    user_id: str,
    user_data: UserCreate,
    manager: UserManager = Depends(get_user_manager)
):
    """Update an existing user"""
    try:
        # Convert UserCreate to dict
        update_data = user_data.dict(exclude_unset=True)
        
        updated_user = await manager.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserResponse(
            user=updated_user,
            message="User updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete(
    "/deleteUser/{user_id}",
    summary="Delete user by ID",
    description="Delete a user from the database"
)
async def delete_user(
    user_id: str,
    manager: UserManager = Depends(get_user_manager)
):
    """Delete a user from database"""
    try:
        deleted = await manager.delete_user(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return {"message": "User deleted successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )