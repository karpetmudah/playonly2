from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User data model for SaaS multi-tenant application"""

    user_id: str = Field(..., description='Unique user identifier')
    email: EmailStr = Field(..., description='User email address')
    password_hash: str = Field(..., description='Hashed password')
    full_name: str | None = Field(None, description="User's full name")
    is_active: bool = Field(True, description='Whether user account is active')
    is_verified: bool = Field(False, description='Whether email is verified')
    credits: float = Field(0.0, description='Available credits')
    total_credits_purchased: float = Field(
        0.0, description='Total credits ever purchased'
    )
    total_credits_used: float = Field(0.0, description='Total credits used')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = None
    workspace_path: str | None = Field(
        None, description="User's workspace directory path"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class UserRegistration(BaseModel):
    """User registration request model"""

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description='Password must be at least 8 characters'
    )
    full_name: str | None = None


class UserLogin(BaseModel):
    """User login request model"""

    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """User profile update model"""

    full_name: str | None = None
    email: EmailStr | None = None


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""

    user_id: str
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    credits: float
    total_credits_purchased: float
    total_credits_used: float
    created_at: datetime
    last_login: datetime | None


class TokenResponse(BaseModel):
    """JWT token response model"""

    access_token: str
    token_type: str = 'bearer'
    expires_in: int
    user: UserResponse


class CreditTransaction(BaseModel):
    """Credit transaction model"""

    transaction_id: str
    user_id: str
    amount: float
    transaction_type: str  # "purchase", "usage", "refund"
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict | None = (
        None  # For storing additional info like token count, task details
    )
