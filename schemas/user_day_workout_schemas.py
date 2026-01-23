from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.workout_schemas import Workout


class DayWorkoutsResponse(BaseModel):
    """Schema for day workouts response organized by workout type"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    upperBody: List[Workout] = Field(default_factory=list)
    lowerBody: List[Workout] = Field(default_factory=list)
    core: List[Workout] = Field(default_factory=list)
    fullBody: List[Workout] = Field(default_factory=list)


class SaveDayWorkoutsRequest(BaseModel):
    """Schema for saving day workouts request - links existing workouts to a date/workoutType"""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    workoutType: str = Field(..., pattern=r"^(upperBody|lowerBody|core|fullBody)$", description="Workout type")
    workoutIds: List[str] = Field(..., description="List of workout IDs to associate with this date/workoutType")


class SaveDayWorkoutsResponse(BaseModel):
    """Schema for save day workouts response"""
    message: str
    date: str
    workoutType: str
    totalWorkouts: int


class UserWorkoutCreate(BaseModel):
    """Schema for creating a user workout"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the workout")
    reps: Optional[int] = Field(None, ge=0, le=1000, description="Number of repetitions")
    duration: Optional[float] = Field(None, ge=0, le=480, description="Duration in minutes")


class UserWorkoutsListResponse(BaseModel):
    """Schema for user workouts list response"""
    workouts: List[Workout]
    total_count: int


class UserWorkoutResponse(BaseModel):
    """Schema for single user workout response"""
    workout: Workout
    message: str
