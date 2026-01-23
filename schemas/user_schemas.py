from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# Base user schema
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    age: Optional[int] = Field(None, ge=0, le=120, description="User's age")

# User creation schema (for API input)
class UserCreate(UserBase):
    pass

# Complete user schema (for API output)
class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# User update schema
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=120)

# API Response schemas
class UserResponse(BaseModel):
    user: User
    message: str

class UsersListResponse(BaseModel):
    users: List[User]
    total_count: int