from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
from config import settings

# Create engine
engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# User model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    password_hash = Column(String, nullable=True)  # nullable for existing users
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to meals
    meals = relationship("MealDB", back_populates="user")
    # Relationship to day meals
    day_meals = relationship("UserDayMealDB", back_populates="user")
    # Relationship to workouts
    workouts = relationship("WorkoutDB", back_populates="user")
    # Relationship to day workouts
    day_workouts = relationship("UserDayWorkoutDB", back_populates="user")

# Meal model (updated with user relationship)
class MealDB(Base):
    __tablename__ = "meals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    
    # Foreign key to user (nullable for backward compatibility)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationship
    user = relationship("UserDB", back_populates="meals")
    # Relationship to day meal entries
    day_meal_entries = relationship("UserDayMealDB", back_populates="meal")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# User Day Meal model (junction table for user-date-meal associations)
class UserDayMealDB(Base):
    __tablename__ = "user_day_meals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    meal_id = Column(String, ForeignKey("meals.id"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserDB", back_populates="day_meals")
    meal = relationship("MealDB", back_populates="day_meal_entries")


# Workout model
class WorkoutDB(Base):
    __tablename__ = "workouts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    reps = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in minutes

    # Foreign key to user (nullable for backward compatibility)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationship
    user = relationship("UserDB", back_populates="workouts")
    # Relationship to day workout entries
    day_workout_entries = relationship("UserDayWorkoutDB", back_populates="workout")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# User Day Workout model (junction table for user-date-workout associations)
class UserDayWorkoutDB(Base):
    __tablename__ = "user_day_workouts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    workout_id = Column(String, ForeignKey("workouts.id"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    workout_type = Column(String, nullable=False)  # upperBody, lowerBody, core, fullBody
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserDB", back_populates="day_workouts")
    workout = relationship("WorkoutDB", back_populates="day_workout_entries")


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()