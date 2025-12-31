"""
Pydantic models for API request/response data.

These models match the schemas from MCP_Auth and finance_planner APIs.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# MCP_Auth Models
# ============================================================================


class UserResponse(BaseModel):
    """User data from MCP_Auth."""

    id: int
    email: EmailStr
    is_active: bool = True
    is_totp_enabled: bool = False
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response from MCP_Auth login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class TokenStorage(BaseModel):
    """Token storage data for local file."""

    access_token: str
    refresh_token: str
    expires_at: datetime  # When access token expires
    user_id: Optional[str] = None


class TokenFile(BaseModel):
    """Root structure of tokens.json file."""

    current_user: Optional[str] = None
    tokens: dict[str, TokenStorage] = Field(default_factory=dict)


# ============================================================================
# Finance Planner Models
# ============================================================================


class AccountBase(BaseModel):
    """Base account fields."""

    name: str
    account_type: str  # checking, savings, credit, investment, cash
    balance: float = 0.0


class AccountCreate(AccountBase):
    """Account creation request."""

    pass


class AccountUpdate(BaseModel):
    """Account update request (all fields optional)."""

    name: Optional[str] = None
    account_type: Optional[str] = None
    balance: Optional[float] = None


class Account(AccountBase):
    """Account response from API."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Base transaction fields (future use)."""

    amount: float
    description: Optional[str] = None
    category: Optional[str] = None
    transaction_date: datetime


class Transaction(TransactionBase):
    """Transaction response from API (future use)."""

    id: int
    account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CLI-specific Models
# ============================================================================


class SecretKeyValidation(BaseModel):
    """Result of SECRET_KEY validation between projects."""

    is_valid: bool
    mcp_auth_key: Optional[str] = None
    finance_key: Optional[str] = None
    secret_key: Optional[str] = None  # Set when valid and matching
