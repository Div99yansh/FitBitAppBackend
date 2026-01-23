"""
Chat Controller - API endpoints for fitness chatbot

Provides endpoints for AI-powered fitness and nutrition Q&A.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import logging

from schemas.chat_schemas import ChatRequest, ChatResponse, ChatHealthResponse
from managers.chat_manager import ChatManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])

# Singleton chat manager instance (stateless, no DB needed)
_chat_manager: ChatManager = None


def get_chat_manager() -> ChatManager:
    """Dependency to get chat manager (singleton pattern)"""
    global _chat_manager
    if _chat_manager is None:
        _chat_manager = ChatManager()
    return _chat_manager


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Ask fitness assistant a question",
    description="Submit a question along with daily summary data to receive AI-powered fitness and nutrition guidance"
)
async def ask_question(
    request: ChatRequest,
    manager: ChatManager = Depends(get_chat_manager)
):
    """
    Process a user's fitness/nutrition question and return AI-generated response.

    The endpoint is stateless - each request must include the full context
    (daily summary) needed to answer the question.

    - **userId**: User identifier
    - **date**: Date of the daily summary (YYYY-MM-DD)
    - **dailySummary**: JSON object containing fitness/nutrition metrics
    - **question**: User's question about their fitness data
    """
    try:
        # Check if chat service is available
        if not manager.is_service_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chat service is not available. Please check API configuration."
            )

        # Process the question
        response = await manager.process_question(request)
        return response

    except ValueError as ve:
        logger.error(f"Validation error in chat: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(ve)
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        if "Failed to generate response" in str(e):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to generate AI response. Please try again."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your question"
        )


@router.get(
    "/health",
    response_model=ChatHealthResponse,
    summary="Chat service health check",
    description="Check the availability of the chat service"
)
async def chat_health_check(
    manager: ChatManager = Depends(get_chat_manager)
):
    """Check the health status of the chat service"""
    service_available = manager.is_service_available()
    return ChatHealthResponse(
        status="healthy" if service_available else "unavailable",
        chat_service="available" if service_available else "unavailable",
        timestamp=datetime.utcnow()
    )
