"""
Workout Controller - FastAPI endpoints for workout management

Provides user-scoped workout tracking endpoints:
- getUserWorkouts: Get all workouts for authenticated user
- addUserWorkout: Add new workout with name, reps, duration
- getUserDayWorkouts: Get workouts for a date grouped by type
- saveUserDayWorkouts: Save workouts to date/workoutType
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
import logging
from sqlalchemy.orm import Session

# Import dependencies
from database import get_db, UserDB
from repositories.user_day_workout_repository import SQLAlchemyUserDayWorkoutRepository
from schemas.user_day_workout_schemas import (
    DayWorkoutsResponse,
    SaveDayWorkoutsRequest,
    SaveDayWorkoutsResponse,
    UserWorkoutCreate,
    UserWorkoutsListResponse,
    UserWorkoutResponse
)
from managers.user_workout_manager import UserWorkoutManager
from auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/fitbit", tags=["Workouts"])


# Dependency to get user workout manager
def get_user_workout_manager(db: Session = Depends(get_db)) -> UserWorkoutManager:
    """Dependency to get user workout manager with repository"""
    repository = SQLAlchemyUserDayWorkoutRepository(db)
    return UserWorkoutManager(repository)


# ============================================================================
# User-Scoped Workout Endpoints (Protected - Require Authentication)
# ============================================================================

@router.get(
    "/getUserWorkouts",
    response_model=UserWorkoutsListResponse,
    summary="Get authenticated user's workouts",
    description="Retrieve all workouts for the authenticated user"
)
async def get_user_workouts(
    current_user: UserDB = Depends(get_current_user),
    manager: UserWorkoutManager = Depends(get_user_workout_manager)
):
    """Get all workouts for the authenticated user"""
    try:
        workouts = await manager.get_user_workouts(current_user.id)
        return UserWorkoutsListResponse(
            workouts=workouts,
            total_count=len(workouts)
        )
    except Exception as e:
        logger.error(f"API error retrieving user workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user workouts"
        )


@router.post(
    "/addUserWorkout",
    response_model=UserWorkoutResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add workout for authenticated user",
    description="Add a new workout for the authenticated user with name, reps, and duration"
)
async def add_user_workout(
    workout_data: UserWorkoutCreate,
    current_user: UserDB = Depends(get_current_user),
    manager: UserWorkoutManager = Depends(get_user_workout_manager)
):
    """Add a new workout for the authenticated user"""
    try:
        new_workout = await manager.add_user_workout(current_user.id, workout_data)

        return UserWorkoutResponse(
            workout=new_workout,
            message="Workout saved successfully"
        )

    except Exception as e:
        logger.error(f"API error adding user workout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the workout"
        )


@router.get(
    "/getUserDayWorkouts",
    response_model=DayWorkoutsResponse,
    summary="Get user's workouts for a specific date",
    description="Retrieve all workouts for the authenticated user on a specific date, organized by workout type"
)
async def get_user_day_workouts(
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format"),
    current_user: UserDB = Depends(get_current_user),
    manager: UserWorkoutManager = Depends(get_user_workout_manager)
):
    """Get workouts for the authenticated user on a specific date"""
    try:
        day_workouts = await manager.get_user_day_workouts(current_user.id, date)
        return day_workouts
    except Exception as e:
        logger.error(f"API error retrieving user day workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve day workouts"
        )


@router.post(
    "/saveUserDayWorkouts",
    response_model=SaveDayWorkoutsResponse,
    summary="Save workouts for a specific date and workout type",
    description="Save/replace workouts for the authenticated user on a specific date and workout type"
)
async def save_user_day_workouts(
    request: SaveDayWorkoutsRequest,
    current_user: UserDB = Depends(get_current_user),
    manager: UserWorkoutManager = Depends(get_user_workout_manager)
):
    """Save day workouts for the authenticated user"""
    try:
        result = await manager.save_user_day_workouts(current_user.id, request)
        return result
    except ValueError as ve:
        logger.warning(f"Invalid workout IDs in save request: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"API error saving user day workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save day workouts"
        )
