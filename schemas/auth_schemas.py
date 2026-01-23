from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")


class SignupRequest(BaseModel):
    """Schema for signup request"""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password (min 6 characters)")
    age: Optional[int] = Field(None, ge=0, le=120, description="User's age")


class AuthUser(BaseModel):
    """Schema for authenticated user data in responses"""
    id: str
    email: str
    name: str
    age: Optional[int] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response (login/signup)"""
    user: AuthUser
    token: str
    message: str = "Authentication successful"
