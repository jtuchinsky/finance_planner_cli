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
    tenant_id: Optional[int] = None  # Tenant context for this token


class TokenFile(BaseModel):
    """Root structure of tokens.json file."""

    current_user: Optional[str] = None
    current_tenant_id: Optional[int] = None  # Active tenant for current user
    tokens: dict[str, TokenStorage] = Field(default_factory=dict)
    tenant_preferences: dict[str, int] = Field(default_factory=dict)  # email -> tenant_id mapping


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
    """
    Account update request (all fields optional).

    Note: Balance cannot be updated directly as it's calculated from transactions.
    """

    name: Optional[str] = None
    account_type: Optional[str] = None


class Account(AccountBase):
    """Account response from API."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Base transaction fields."""

    account_id: int
    amount: float  # Positive for income, negative for expenses
    date: str  # ISO format: YYYY-MM-DD
    category: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[list[str]] = None  # JSON array of tags


class TransactionCreate(TransactionBase):
    """Transaction creation request."""

    der_category: Optional[str] = None  # Derived category
    der_merchant: Optional[str] = None  # Derived merchant


class TransactionUpdate(BaseModel):
    """
    Transaction update request (all fields optional).

    Only provided fields will be updated.
    """

    account_id: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[list[str]] = None
    der_category: Optional[str] = None  # Derived category
    der_merchant: Optional[str] = None  # Derived merchant


class Transaction(TransactionBase):
    """Transaction response from API."""

    id: int
    user_id: Optional[int] = None  # Not always returned by API
    der_category: Optional[str] = None  # Derived category
    der_merchant: Optional[str] = None  # Derived merchant
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Paginated transaction list response."""

    transactions: list[Transaction]
    total: int


class BatchTransactionRequest(BaseModel):
    """Batch transaction creation request."""

    account_id: int
    transactions: list[TransactionCreate]


class BatchTransactionResponse(BaseModel):
    """Batch transaction creation response."""

    transactions: list[Transaction]
    account_balance: float
    total_amount: float
    count: int


# ============================================================================
# CLI-specific Models
# ============================================================================


class SecretKeyValidation(BaseModel):
    """Result of SECRET_KEY validation between projects."""

    is_valid: bool
    mcp_auth_key: Optional[str] = None
    finance_key: Optional[str] = None
    secret_key: Optional[str] = None  # Set when valid and matching


# ============================================================================
# Tenant/RBAC Models
# ============================================================================


class Tenant(BaseModel):
    """Tenant response from API."""

    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantUpdate(BaseModel):
    """Tenant update request."""

    name: str


class TenantMember(BaseModel):
    """Tenant member response from API."""

    id: int
    user_id: int
    auth_user_id: str
    role: str  # owner, admin, member, viewer
    created_at: datetime

    class Config:
        from_attributes = True


class TenantInvite(BaseModel):
    """Tenant member invite request."""

    auth_user_id: str
    role: str


class TenantRoleUpdate(BaseModel):
    """Tenant member role update request."""

    role: str


class TenantSummary(BaseModel):
    """Summary of tenant user belongs to (from list endpoint)."""

    id: int
    name: str
    role: str  # User's role in this tenant: owner, admin, member, viewer
    created_at: datetime

    class Config:
        from_attributes = True
