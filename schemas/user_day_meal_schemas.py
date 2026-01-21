from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from schemas.meal_schemas import Meal


class MealInput(BaseModel):
    """Schema for meal input when saving day meals"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the meal")
    calories: Optional[float] = Field(None, ge=0, le=5000, description="Calories in kcal")
    protein: Optional[float] = Field(None, ge=0, le=200, description="Protein in grams")
    fats: Optional[float] = Field(None, ge=0, le=200, description="Fats in grams")
    carbohydrates: Optional[float] = Field(None, ge=0, le=500, description="Carbohydrates in grams")
    fiber: Optional[float] = Field(None, ge=0, le=100, description="Fiber in grams")
    sugar: Optional[float] = Field(None, ge=0, le=200, description="Sugar in grams")
    sodium: Optional[float] = Field(None, ge=0, le=5000, description="Sodium in milligrams")


class DayMealsResponse(BaseModel):
    """Schema for day meals response organized by meal type"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    breakfast: List[Meal] = Field(default_factory=list)
    lunch: List[Meal] = Field(default_factory=list)
    dinner: List[Meal] = Field(default_factory=list)


class SaveDayMealsRequest(BaseModel):
    """Schema for saving day meals request"""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    mealType: str = Field(..., pattern=r"^(breakfast|lunch|dinner)$", description="Meal type: breakfast, lunch, or dinner")
    meals: List[MealInput] = Field(..., description="List of meals to save")


class SaveDayMealsResponse(BaseModel):
    """Schema for save day meals response"""
    message: str
    date: str
    mealType: str
    totalMeals: int


class UserMealCreate(BaseModel):
    """Schema for creating a user meal with nutrition analysis"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the meal")


class UserMealsListResponse(BaseModel):
    """Schema for user meals list response"""
    meals: List[Meal]
    total_count: int


class UserMealResponse(BaseModel):
    """Schema for single user meal response"""
    meal: Meal
    message: str
