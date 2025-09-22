from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
import logging
from gemini_nutrition import GeminiNutritionServiceSync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class Meal(BaseModel):
    id: str
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None

class MealCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the meal")

class MealResponse(BaseModel):
    meal: Meal
    message: str

# Sample meals data
meals_storage: List[Meal] = [
    Meal(id="1", name="2 Chapati", calories=240, protein=8, fats=4, carbohydrates=48, fiber=4, sugar=2, sodium=320),
    Meal(id="2", name="1 Bowl Dal", calories=180, protein=12, fats=2, carbohydrates=28, fiber=6, sugar=3, sodium=450),
    Meal(id="3", name="1 Plate Upma", calories=220, protein=6, fats=8, carbohydrates=35, fiber=3, sugar=4, sodium=380),
    Meal(id="4", name="Oatmeal Bowl", calories=150, protein=5, fats=3, carbohydrates=27, fiber=4, sugar=8, sodium=200),
]

# Initialize Gemini nutrition service
try:
    nutrition_service = GeminiNutritionServiceSync()
    logger.info("Gemini nutrition service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini service: {str(e)}")
    nutrition_service = None

# FastAPI app
app = FastAPI(title="Fitbit Meals API")

# CORS middleware for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5123"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Get meals endpoint
@app.get("/fitbit/getMeals", response_model=List[Meal])
async def get_meals():
    """Get all meals"""
    logger.info(f"Fetching all meals. Current count: {len(meals_storage)}")
    return meals_storage

# Add meal with nutrition analysis
@app.post("/fitbit/addMeal", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def add_meal(meal_data: MealCreate):
    """
    Add a new meal with automatic nutrition analysis using Gemini AI
    
    Args:
        meal_data: Meal information containing the name
        
    Returns:
        MealResponse: The created meal with complete nutritional information
    """
    try:
        # Check if Gemini service is available
        if not nutrition_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nutrition analysis service is not available. Please check API configuration."
            )
        
        meal_name = meal_data.name.strip()
        logger.info(f"Processing meal: {meal_name}")
        
        # Analyze nutrition using Gemini
        try:
            nutrition_data = nutrition_service.analyze_meal_nutrition(meal_name)
            logger.info(f"Nutrition analysis completed for: {meal_name}")
        except Exception as e:
            logger.error(f"Nutrition analysis failed for {meal_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to analyze meal nutrition: {str(e)}"
            )
        
        # Generate unique ID for the meal
        new_id = str(uuid.uuid4())
        
        # Create new meal with nutrition data
        new_meal = Meal(
            id=new_id,
            name=meal_name,
            calories=nutrition_data.get("calories"),
            protein=nutrition_data.get("protein"),
            fats=nutrition_data.get("fats"),
            carbohydrates=nutrition_data.get("carbohydrates"),
            fiber=nutrition_data.get("fiber"),
            sugar=nutrition_data.get("sugar"),
            sodium=nutrition_data.get("sodium")
        )
        
        # Add to storage
        meals_storage.append(new_meal)
        
        logger.info(f"Successfully added meal: {meal_name} with ID: {new_id}")
        
        return MealResponse(
            meal=new_meal,
            message="Meal analyzed and added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding meal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the meal"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)