import logging
from typing import List
from repositories.user_day_workout_repository import UserDayWorkoutRepositoryInterface
from schemas.workout_schemas import Workout
from schemas.user_day_workout_schemas import (
    DayWorkoutsResponse,
    SaveDayWorkoutsRequest,
    SaveDayWorkoutsResponse,
    UserWorkoutCreate
)

logger = logging.getLogger(__name__)


class UserWorkoutManager:
    """
    Business logic layer for user-scoped workout operations.
    Handles authenticated user's workouts and day workout tracking.
    Note: Unlike meals, workouts do not require AI/Gemini integration.
    """

    def __init__(self, repository: UserDayWorkoutRepositoryInterface):
        self.repository = repository

    async def get_user_workouts(self, user_id: str) -> List[Workout]:
        """
        Get all workouts for a specific user.

        Args:
            user_id: The authenticated user's ID

        Returns:
            List[Workout]: List of user's workouts
        """
        try:
            workouts = await self.repository.get_user_workouts(user_id)
            logger.info(f"Retrieved {len(workouts)} workouts for user {user_id}")
            return workouts
        except Exception as e:
            logger.error(f"Error retrieving workouts for user {user_id}: {str(e)}")
            raise

    async def add_user_workout(self, user_id: str, workout_data: UserWorkoutCreate) -> Workout:
        """
        Create a new workout for a user.

        Args:
            user_id: The authenticated user's ID
            workout_data: The workout creation data (name, reps, duration)

        Returns:
            Workout: The created workout
        """
        try:
            workout_name = workout_data.name.strip()
            logger.info(f"Creating workout for user {user_id}: {workout_name}")

            # Prepare workout data
            workout_db_data = {
                "name": workout_name,
                "reps": workout_data.reps,
                "duration": workout_data.duration
            }

            # Create workout in repository
            new_workout = await self.repository.create_user_workout(user_id, workout_db_data)

            logger.info(f"Created workout {new_workout.id} for user {user_id}")
            return new_workout

        except Exception as e:
            logger.error(f"Error creating workout for user {user_id}: {str(e)}")
            raise

    async def get_user_day_workouts(self, user_id: str, date: str) -> DayWorkoutsResponse:
        """
        Get workouts for a user on a specific date organized by workout type.

        Args:
            user_id: The authenticated user's ID
            date: Date in YYYY-MM-DD format

        Returns:
            DayWorkoutsResponse: Workouts organized by upperBody, lowerBody, core, fullBody
        """
        try:
            day_workouts = await self.repository.get_day_workouts(user_id, date)
            logger.info(f"Retrieved day workouts for user {user_id} on {date}")
            return day_workouts
        except Exception as e:
            logger.error(f"Error retrieving day workouts for user {user_id}: {str(e)}")
            raise

    async def save_user_day_workouts(
        self, user_id: str, request: SaveDayWorkoutsRequest
    ) -> SaveDayWorkoutsResponse:
        """
        Save/replace workout associations for a user on a specific date and workout type.
        Links existing workouts to the date/workoutType - does not create new workouts.

        Args:
            user_id: The authenticated user's ID
            request: Save request with date, workoutType, and workoutIds

        Returns:
            SaveDayWorkoutsResponse: Confirmation of saved associations
        """
        try:
            count = await self.repository.save_day_workouts(
                user_id=user_id,
                date=request.date,
                workout_type=request.workoutType,
                workout_ids=request.workoutIds
            )

            logger.info(
                f"Saved {count} workout associations for user {user_id} on {request.date} ({request.workoutType})"
            )

            return SaveDayWorkoutsResponse(
                message=f"Successfully saved {count} workout associations",
                date=request.date,
                workoutType=request.workoutType,
                totalWorkouts=count
            )

        except Exception as e:
            logger.error(f"Error saving day workouts for user {user_id}: {str(e)}")
            raise
