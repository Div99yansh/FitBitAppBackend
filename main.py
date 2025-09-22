from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Pydantic model for Meal
class Meal(BaseModel):
    id: str
    name: str
    calories: Optional[int] = None
    protein: Optional[float] = None

# Sample meals data
meals_storage: List[Meal] = [
    Meal(id="1", name="2 Chapati", calories=240, protein=8),
    Meal(id="2", name="1 Bowl Dal", calories=180, protein=12),
    Meal(id="3", name="1 Plate Upma", calories=220, protein=6),
    Meal(id="4", name="Oatmeal Bowl", calories=150, protein=5),
]

# FastAPI app
app = FastAPI(title="Fitbit Meals API")

# CORS middleware for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Get meals endpoint
@app.get("/fitbit/getMeals", response_model=List[Meal])
async def get_meals():
    """Get all meals"""
    return meals_storage

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)