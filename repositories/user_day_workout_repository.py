from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import WorkoutDB, UserDayWorkoutDB
from schemas.workout_schemas import Workout
from schemas.user_day_workout_schemas import DayWorkoutsResponse
import uuid


class UserDayWorkoutRepositoryInterface(ABC):
    """Abstract interface for user day workout repository"""

    @abstractmethod
    async def get_user_workouts(self, user_id: str) -> List[Workout]:
        """Get all workouts for a user"""
        pass

    @abstractmethod
    async def create_user_workout(self, user_id: str, workout_data: Dict[str, Any]) -> Workout:
        """Create a workout associated with a user"""
        pass

    @abstractmethod
    async def get_day_workouts(self, user_id: str, date: str) -> DayWorkoutsResponse:
        """Get workouts for a user on a specific date organized by type"""
        pass

    @abstractmethod
    async def save_day_workouts(
        self, user_id: str, date: str, workout_type: str, workout_ids: List[str]
    ) -> int:
        """Save/replace day workout associations for a user, returns count of associations created"""
        pass


class SQLAlchemyUserDayWorkoutRepository(UserDayWorkoutRepositoryInterface):
    """SQLAlchemy implementation of user day workout repository"""

    def __init__(self, db: Session):
        self.db = db

    async def get_user_workouts(self, user_id: str) -> List[Workout]:
        """Get all workouts associated with a user"""
        db_workouts = (
            self.db.query(WorkoutDB)
            .filter(WorkoutDB.user_id == user_id)
            .order_by(WorkoutDB.created_at.desc())
            .all()
        )
        return [Workout.model_validate(workout) for workout in db_workouts]

    async def create_user_workout(self, user_id: str, workout_data: Dict[str, Any]) -> Workout:
        """Create a new workout associated with a user"""
        if 'id' not in workout_data:
            workout_data['id'] = str(uuid.uuid4())

        workout_data['user_id'] = user_id

        db_workout = WorkoutDB(**workout_data)
        self.db.add(db_workout)
        self.db.commit()
        self.db.refresh(db_workout)

        return Workout.model_validate(db_workout)

    async def get_day_workouts(self, user_id: str, date: str) -> DayWorkoutsResponse:
        """Get workouts for a user on a specific date organized by workout type"""
        # Query all day workout entries for the user and date
        day_workout_entries = (
            self.db.query(UserDayWorkoutDB)
            .filter(UserDayWorkoutDB.user_id == user_id, UserDayWorkoutDB.date == date)
            .all()
        )

        # Organize workouts by type
        upper_body_workouts = []
        lower_body_workouts = []
        core_workouts = []
        full_body_workouts = []

        for entry in day_workout_entries:
            workout = self.db.query(WorkoutDB).filter(WorkoutDB.id == entry.workout_id).first()
            if workout:
                workout_schema = Workout.model_validate(workout)
                if entry.workout_type == "upperBody":
                    upper_body_workouts.append(workout_schema)
                elif entry.workout_type == "lowerBody":
                    lower_body_workouts.append(workout_schema)
                elif entry.workout_type == "core":
                    core_workouts.append(workout_schema)
                elif entry.workout_type == "fullBody":
                    full_body_workouts.append(workout_schema)

        return DayWorkoutsResponse(
            date=date,
            upperBody=upper_body_workouts,
            lowerBody=lower_body_workouts,
            core=core_workouts,
            fullBody=full_body_workouts
        )

    async def save_day_workouts(
        self, user_id: str, date: str, workout_type: str, workout_ids: List[str]
    ) -> int:
        """
        Save/replace day workout associations for a user.
        Removes existing entries for the user/date/workout_type combo and creates new associations.
        Only links to existing workouts - does not create new workout records.

        Raises:
            ValueError: If any workout ID is not found or doesn't belong to the user
        """
        if not workout_ids:
            raise ValueError("No workout IDs provided")

        # Validate all workout IDs first before making any changes
        not_found_ids = []
        valid_workouts = []

        for workout_id in workout_ids:
            workout = self.db.query(WorkoutDB).filter(
                WorkoutDB.id == workout_id,
                WorkoutDB.user_id == user_id
            ).first()

            if workout:
                valid_workouts.append(workout)
            else:
                not_found_ids.append(workout_id)

        # If any workout IDs are invalid, raise an error
        if not_found_ids:
            raise ValueError(f"Workout IDs not found or don't belong to user: {', '.join(not_found_ids)}")

        # Remove existing entries for this user/date/workout_type
        existing_entries = (
            self.db.query(UserDayWorkoutDB)
            .filter(
                UserDayWorkoutDB.user_id == user_id,
                UserDayWorkoutDB.date == date,
                UserDayWorkoutDB.workout_type == workout_type
            )
            .all()
        )

        for entry in existing_entries:
            self.db.delete(entry)

        # Create day workout entries linking to existing workouts
        for workout in valid_workouts:
            day_workout_entry = UserDayWorkoutDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                workout_id=workout.id,
                date=date,
                workout_type=workout_type
            )
            self.db.add(day_workout_entry)

        self.db.commit()
        return len(valid_workouts)
