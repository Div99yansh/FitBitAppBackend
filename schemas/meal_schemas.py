from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Base meal schema
class MealBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the meal")
    calories: Optional[float] = Field(None, ge=0, le=5000, description="Calories in kcal")
    protein: Optional[float] = Field(None, ge=0, le=200, description="Protein in grams")
    fats: Optional[float] = Field(None, ge=0, le=200, description="Fats in grams")
    carbohydrates: Optional[float] = Field(None, ge=0, le=500, description="Carbohydrates in grams")
    fiber: Optional[float] = Field(None, ge=0, le=100, description="Fiber in grams")
    sugar: Optional[float] = Field(None, ge=0, le=200, description="Sugar in grams")
    sodium: Optional[float] = Field(None, ge=0, le=5000, description="Sodium in milligrams")

# Meal creation schema (for API input)
class MealCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the meal")

# Complete meal schema (for API output)
class Meal(MealBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# API Response schemas
class MealResponse(BaseModel):
    meal: Meal
    message: str

class MealsListResponse(BaseModel):
    meals: List[Meal]
    total_count: int

# Update meal schema
class MealUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    calories: Optional[float] = Field(None, ge=0, le=5000)
    protein: Optional[float] = Field(None, ge=0, le=200)
    fats: Optional[float] = Field(None, ge=0, le=200)
    carbohydrates: Optional[float] = Field(None, ge=0, le=500)
    fiber: Optional[float] = Field(None, ge=0, le=100)
    sugar: Optional[float] = Field(None, ge=0, le=200)
    sodium: Optional[float] = Field(None, ge=0, le=5000)

# Health check response
class HealthResponse(BaseModel):
    status: str
    message: str
    gemini_service: str
    database: str
    timestamp: datetime