from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class WorkoutBase(BaseModel):
    """Base workout schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the workout")
    reps: Optional[int] = Field(None, ge=0, le=1000, description="Number of repetitions")
    duration: Optional[float] = Field(None, ge=0, le=480, description="Duration in minutes")


class WorkoutCreate(WorkoutBase):
    """Schema for creating a new workout"""
    pass


class Workout(WorkoutBase):
    """Complete workout schema with all fields for API output"""
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutResponse(BaseModel):
    """Schema for single workout API response"""
    workout: Workout
    message: str


class WorkoutsListResponse(BaseModel):
    """Schema for workout list API response"""
    workouts: List[Workout]
    total_count: int


class WorkoutUpdate(BaseModel):
    """Schema for updating an existing workout"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    reps: Optional[int] = Field(None, ge=0, le=1000)
    duration: Optional[float] = Field(None, ge=0, le=480)
