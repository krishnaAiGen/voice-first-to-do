"""Authentication request/response schemas"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID


class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    
    email: EmailStr = Field(..., description="User email address (will be lowercased)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    display_name: Optional[str] = Field(None, description="Display name (optional)")


class LoginRequest(BaseModel):
    """Request schema for user login"""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """User information response"""
    
    id: str
    email: str
    display_name: Optional[str]
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response after login/register"""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    
    refresh_token: str

