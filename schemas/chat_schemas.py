"""
Chat Schemas - Pydantic models for fitness chatbot API

Defines request and response models for the AI-powered chat endpoint.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    """Schema for chat request input"""
    userId: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User identifier"
    )
    date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date in YYYY-MM-DD format"
    )
    dailySummary: Dict[str, Any] = Field(
        ...,
        description="Daily fitness/nutrition summary JSON from dashboard"
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question about their fitness data"
    )


class ChatResponse(BaseModel):
    """Schema for chat response output"""
    answer: str = Field(
        ...,
        description="AI-generated response based on the provided daily summary"
    )


class ChatHealthResponse(BaseModel):
    """Schema for chat service health check"""
    status: str = Field(..., description="Overall health status")
    chat_service: str = Field(..., description="Chat service availability")
    timestamp: datetime = Field(..., description="Health check timestamp")
