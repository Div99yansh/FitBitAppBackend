"""
Chat Manager - Business logic layer for chat operations

Handles chat request processing and AI service orchestration.
Stateless - no repository needed as chat history is not persisted.
"""

import logging
from typing import Optional
from services.gemini_chat_service import GeminiChatServiceSync
from schemas.chat_schemas import ChatRequest, ChatResponse
from config import settings

logger = logging.getLogger(__name__)


class ChatManager:
    """
    Business logic layer for chat operations.
    Stateless - no repository needed as chat history is not persisted.
    """

    def __init__(self):
        """Initialize the chat manager with Gemini chat service"""
        self.chat_service = self._initialize_service()

    def _initialize_service(self) -> Optional[GeminiChatServiceSync]:
        """Initialize Gemini chat service"""
        try:
            if not settings.gemini_api_key:
                logger.warning(
                    "Gemini API key not provided - chat service will be unavailable"
                )
                return None

            service = GeminiChatServiceSync(api_key=settings.gemini_api_key)
            logger.info("Gemini chat service initialized successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize Gemini chat service: {str(e)}")
            return None

    def is_service_available(self) -> bool:
        """Check if chat service is available"""
        return self.chat_service is not None

    async def process_question(self, request: ChatRequest) -> ChatResponse:
        """
        Process a user's fitness question and generate a response

        Args:
            request: ChatRequest containing userId, date, dailySummary, and question

        Returns:
            ChatResponse with the AI-generated answer

        Raises:
            ValueError: If chat service is unavailable
            Exception: If response generation fails
        """
        try:
            logger.info(
                f"Processing chat question for user: {request.userId}, date: {request.date}"
            )

            if not self.chat_service:
                raise ValueError("Chat service is not available")

            # Generate response using Gemini
            answer = self.chat_service.generate_response(
                user_id=request.userId,
                date=request.date,
                daily_summary=request.dailySummary,
                question=request.question
            )

            logger.info(f"Successfully processed question for user: {request.userId}")

            return ChatResponse(answer=answer)

        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error(f"Error processing chat question: {str(e)}")
            raise
