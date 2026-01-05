"""Authentication Models - Pydantic models for auth requests/responses."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password must be between 8 and 72 characters")
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "phone": "+1234567890"
            }
        }


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str
    remember_me: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "remember_me": True
            }
        }


class UserResponse(BaseModel):
    """User information response."""
    id: int
    user_id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_active: Optional[datetime] = None
    modules_enabled: List[str] = []
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update request."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    preferences: Optional[dict] = None


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)


class PasswordReset(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=72)


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str
    scopes: List[str] = []
    exp: Optional[datetime] = None


class RefreshToken(BaseModel):
    """Refresh token request."""
    refresh_token: str
