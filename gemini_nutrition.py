import json
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from pydantic import BaseModel

#loading dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    
class GeminiNutritionService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API service for nutrition analysis
        
        Args:
            api_key: Gemini API key. If None, will try to get from environment variable
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        logger.info(f"API key is : {self.api_key}")
        if not self.api_key:
            raise ValueError(f"Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it directly. {self.api_key}")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for nutrition analysis
        self.system_prompt = """
        You are a nutrition analysis expert. Given a meal description, provide accurate nutritional information.

        Instructions:
        1. Analyze the meal and estimate nutritional values per serving
        2. Return ONLY a valid JSON object with the following structure:
        {
            "calories": <number or null>,
            "protein": <number or null>,
            "fats": <number or null>, 
            "carbohydrates": <number or null>,
            "fiber": <number or null>,
            "sugar": <number or null>,
            "sodium": <number or null>
        }
        
        3. All values should be in standard units:
           - calories: kcal
           - protein: grams
           - fats: grams
           - carbohydrates: grams
           - fiber: grams
           - sugar: grams
           - sodium: milligrams
        
        4. If you cannot determine a specific nutrient, use null
        5. Be as accurate as possible based on standard food databases
        6. Do not include any explanations, just return the JSON object
        7. Make sure the JSON is properly formatted and valid
        """
    
    async def analyze_meal_nutrition(self, meal_name: str) -> Dict[str, Any]:
        """
        Analyze nutritional information for a given meal
        
        Args:
            meal_name: Name/description of the meal
            
        Returns:
            Dictionary containing nutritional information
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Create the prompt
            user_prompt = f"Meal: {meal_name}"
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Analyzing nutrition for meal: {meal_name}")
            
            # Make API call to Gemini
            response = self.model.generate_content(full_prompt)
            
            # Extract text from response
            if not response.text:
                raise Exception("Empty response from Gemini API")
                
            response_text = response.text.strip()
            logger.info(f"Raw Gemini response: {response_text}")
            
            # Clean response text (remove any markdown formatting)
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON response
            try:
                nutrition_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response_text}")
                raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
            
            # Validate response structure
            validated_data = self._validate_nutrition_data(nutrition_data)
            
            logger.info(f"Successfully analyzed nutrition for {meal_name}")
            return validated_data
            
        except Exception as e:
            logger.error(f"Error analyzing meal nutrition: {str(e)}")
            raise
    
    def _validate_nutrition_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean nutrition data
        
        Args:
            data: Raw nutrition data from Gemini
            
        Returns:
            Validated nutrition data
        """
        try:
            # Create NutritionInfo object for validation
            nutrition_info = NutritionInfo(**data)
            return nutrition_info.model_dump()
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            # Return a default structure with available data
            validated_data = {
                "calories": data.get("calories"),
                "protein": data.get("protein"), 
                "fats": data.get("fats"),
                "carbohydrates": data.get("carbohydrates"),
                "fiber": data.get("fiber"),
                "sugar": data.get("sugar"),
                "sodium": data.get("sodium")
            }
            return validated_data

# Synchronous version for easier integration
class GeminiNutritionServiceSync:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API service for nutrition analysis (synchronous)
        
        Args:
            api_key: Gemini API key. If None, will try to get from environment variable
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it directly.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for nutrition analysis
        self.system_prompt = """
        You are a nutrition analysis expert. Given a meal description, provide accurate nutritional information.

        Instructions:
        1. Analyze the meal and estimate nutritional values per serving
        2. Return ONLY a valid JSON object with the following structure:
        {
            "calories": <number or null>,
            "protein": <number or null>,
            "fats": <number or null>, 
            "carbohydrates": <number or null>,
            "fiber": <number or null>,
            "sugar": <number or null>,
            "sodium": <number or null>
        }
        
        3. All values should be in standard units:
           - calories: kcal
           - protein: grams
           - fats: grams
           - carbohydrates: grams
           - fiber: grams
           - sugar: grams
           - sodium: milligrams
        
        4. If you cannot determine a specific nutrient, use null
        5. Be as accurate as possible based on standard food databases
        6. Do not include any explanations, just return the JSON object
        7. Make sure the JSON is properly formatted and valid
        """
    
    def analyze_meal_nutrition(self, meal_name: str) -> Dict[str, Any]:
        """
        Analyze nutritional information for a given meal (synchronous)
        
        Args:
            meal_name: Name/description of the meal
            
        Returns:
            Dictionary containing nutritional information
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Create the prompt
            user_prompt = f"Meal: {meal_name}"
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            logger.info(f"Analyzing nutrition for meal: {meal_name}")
            
            # Make API call to Gemini
            response = self.model.generate_content(full_prompt)
            
            # Extract text from response
            if not response.text:
                raise Exception("Empty response from Gemini API")
                
            response_text = response.text.strip()
            logger.info(f"Raw Gemini response: {response_text}")
            
            # Clean response text (remove any markdown formatting)
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON response
            try:
                nutrition_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response_text}")
                raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
            
            # Validate response structure
            validated_data = self._validate_nutrition_data(nutrition_data)
            
            logger.info(f"Successfully analyzed nutrition for {meal_name}")
            return validated_data
            
        except Exception as e:
            logger.error(f"Error analyzing meal nutrition: {str(e)}")
            raise
    
    def _validate_nutrition_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean nutrition data
        
        Args:
            data: Raw nutrition data from Gemini
            
        Returns:
            Validated nutrition data
        """
        try:
            # Create NutritionInfo object for validation
            nutrition_info = NutritionInfo(**data)
            return nutrition_info.model_dump()
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            # Return a default structure with available data
            validated_data = {
                "calories": data.get("calories"),
                "protein": data.get("protein"), 
                "fats": data.get("fats"),
                "carbohydrates": data.get("carbohydrates"),
                "fiber": data.get("fiber"),
                "sugar": data.get("sugar"),
                "sodium": data.get("sodium")
            }
            return validated_data

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    try:
        # Initialize service (make sure to set GEMINI_API_KEY environment variable)
        nutrition_service = GeminiNutritionServiceSync()
        
        # Test meals
        test_meals = [
            "2 Chapati",
            "1 Bowl Dal", 
            "1 Plate Upma",
            "Oatmeal Bowl with milk and honey"
        ]
        
        for meal in test_meals:
            try:
                result = nutrition_service.analyze_meal_nutrition(meal)
                print(f"\nMeal: {meal}")
                print(f"Nutrition: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"Error analyzing {meal}: {str(e)}")
                
    except Exception as e:
        print(f"Service initialization failed: {str(e)}")
        print("Make sure to set GEMINI_API_KEY environment variable")