"""
Gemini Chat Service - AI-powered fitness chatbot service

Provides conversational AI capabilities for fitness and nutrition questions
using Google Gemini API.
"""

import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)


class GeminiChatServiceSync:
    """
    Synchronous Gemini service for fitness chatbot conversations.
    Follows the pattern established in GeminiNutritionServiceSync.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API service for fitness chat

        Args:
            api_key: Gemini API key. If None, will use settings.gemini_api_key
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. "
                "Set GEMINI_API_KEY environment variable or pass it directly."
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # System prompt for fitness assistant persona
        self.system_prompt = self._get_system_prompt()

        logger.info("Gemini chat service initialized successfully")

    def _get_system_prompt(self) -> str:
        """Return the system prompt that defines the AI persona and behavior"""
        return """You are a knowledgeable and supportive fitness and nutrition assistant. Your role is to help users understand their daily fitness data and provide helpful, evidence-based guidance.

PERSONA:
- You are encouraging, supportive, and non-judgmental
- You communicate in a friendly, conversational tone
- You celebrate progress and provide constructive feedback
- You are knowledgeable about general fitness and nutrition principles

IMPORTANT GUIDELINES:

1. MEDICAL ADVICE DISCLAIMER:
   - NEVER provide medical diagnoses or treatment recommendations
   - NEVER suggest specific supplements, medications, or dosages
   - If a question relates to medical conditions, injuries, or health concerns, advise the user to consult a healthcare professional
   - Do not make claims about curing, treating, or preventing any disease

2. DATA-BASED RESPONSES:
   - Base your responses ONLY on the data provided in the daily summary
   - If the data is incomplete or missing, clearly state what information is not available
   - Do not make assumptions about data that is not provided
   - Use phrases like "Based on the data you've shared..." or "Looking at your summary..."

3. WHEN DATA IS INSUFFICIENT:
   - Clearly state what data is missing to answer the question properly
   - Provide general guidance while noting the limitations
   - Suggest what additional tracking might be helpful
   - Example: "I don't have your sleep data for today, so I can't assess its impact on your energy levels. Consider tracking your sleep to get more complete insights."

4. SAFE RECOMMENDATIONS:
   - Stick to general fitness and nutrition principles
   - Recommend consulting professionals for personalized plans
   - Focus on sustainable habits rather than extreme approaches
   - Encourage balanced nutrition and appropriate rest

5. RESPONSE FORMAT:
   - Keep responses concise and actionable (2-4 paragraphs typically)
   - Use simple language that is easy to understand
   - When appropriate, use bullet points for clarity
   - End with encouragement or a helpful next step when appropriate

Remember: You are a supportive assistant helping users understand their fitness data, NOT a replacement for healthcare professionals or certified trainers."""

    def generate_response(
        self,
        user_id: str,
        date: str,
        daily_summary: Dict[str, Any],
        question: str
    ) -> str:
        """
        Generate a response to the user's fitness-related question

        Args:
            user_id: User identifier (for logging context)
            date: Date of the daily summary (YYYY-MM-DD)
            daily_summary: Dictionary containing daily fitness/nutrition data
            question: User's question

        Returns:
            str: AI-generated response

        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Format the user prompt with context
            user_prompt = self._format_user_prompt(date, daily_summary, question)
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"

            logger.info(f"Generating chat response for user: {user_id}, date: {date}")
            logger.debug(f"Question: {question}")

            # Make API call to Gemini
            response = self.model.generate_content(full_prompt)

            # Extract text from response
            if not response.text:
                raise Exception("Empty response from Gemini API")

            response_text = response.text.strip()
            logger.info(f"Successfully generated chat response for user: {user_id}")

            return response_text

        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")

    def _format_user_prompt(
        self,
        date: str,
        daily_summary: Dict[str, Any],
        question: str
    ) -> str:
        """
        Format the user's question with context from daily summary

        Args:
            date: Date of the summary
            daily_summary: Daily fitness/nutrition data
            question: User's question

        Returns:
            str: Formatted prompt with context
        """
        # Pretty-print the daily summary for the AI
        summary_json = json.dumps(daily_summary, indent=2, default=str)

        return f"""Date: {date}

Daily Summary Data:
```json
{summary_json}
```

User Question: {question}

Please provide a helpful response based on the above data and guidelines."""
