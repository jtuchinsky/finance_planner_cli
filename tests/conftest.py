"""
Pytest configuration and shared fixtures.
"""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock

from cli.models.schemas import (
    TokenResponse,
    UserResponse,
    Account,
    Transaction,
    TransactionListResponse,
    Tenant,
    TenantMember,
    TenantSummary,
)


@pytest.fixture
def temp_token_file():
    """Create a temporary token storage file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def mock_token_response():
    """Mock token response from MCP_Auth."""
    return TokenResponse(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzY3Mjg4MzQwfQ.test",
        refresh_token="refresh_token_here",
        token_type="bearer",
        expires_in=900  # 15 minutes
    )


@pytest.fixture
def mock_user_response():
    """Mock user response from MCP_Auth."""
    return UserResponse(
        id=1,
        email="test@example.com",
        is_active=True,
        is_totp_enabled=False,
        created_at=datetime.now()
    )


@pytest.fixture
def mock_account():
    """Mock account response."""
    return Account(
        id=1,
        user_id=1,
        name="Test Account",
        account_type="checking",
        balance=1000.00,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_accounts_list(mock_account):
    """Mock list of accounts."""
    account2 = Account(
        id=2,
        user_id=1,
        name="Savings Account",
        account_type="savings",
        balance=5000.00,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return [mock_account, account2]


@pytest.fixture
def mock_transaction():
    """Mock transaction response."""
    return Transaction(
        id=1,
        user_id=1,
        account_id=1,
        amount=-50.00,
        date="2026-01-03",
        category="Food & Dining",
        merchant="Starbucks",
        description="Morning coffee",
        location="123 Main St",
        tags=["coffee", "daily"],
        der_category="food_and_dining",
        der_merchant="starbucks",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_transactions_list(mock_transaction):
    """Mock list of transactions."""
    transaction2 = Transaction(
        id=2,
        user_id=1,
        account_id=1,
        amount=1000.00,
        date="2026-01-02",
        category="Income",
        merchant="Employer",
        description="Paycheck",
        tags=["income", "salary"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return [mock_transaction, transaction2]


@pytest.fixture
def mock_transaction_list_response(mock_transactions_list):
    """Mock paginated transaction list response."""
    return TransactionListResponse(
        transactions=mock_transactions_list,
        total=2
    )


@pytest.fixture
def mock_httpx_response():
    """Factory for creating mock httpx responses."""
    def _create_response(status_code=200, json_data=None, text=""):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data if json_data else {}
        mock_response.text = text
        return mock_response

    return _create_response


@pytest.fixture
def mock_token_with_tenant():
    """Mock JWT token with tenant_id in claims."""
    # This is a JWT with payload: {"sub": "1", "email": "test@example.com", "tenant_id": "1", "exp": future}
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidGVuYW50X2lkIjoiMSIsImV4cCI6MTc2NzI4ODM0MH0.test"


@pytest.fixture
def mock_token_response_with_tenant(mock_token_with_tenant):
    """Mock token response with tenant_id in JWT."""
    return TokenResponse(
        access_token=mock_token_with_tenant,
        refresh_token="refresh_token_here",
        token_type="bearer",
        expires_in=900  # 15 minutes
    )


@pytest.fixture
def mock_tenant():
    """Mock tenant response."""
    return Tenant(
        id=1,
        name="Test Tenant",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_tenant_member():
    """Mock tenant member response."""
    return TenantMember(
        id=1,
        user_id=1,
        auth_user_id="auth_user_123",
        role="owner",
        created_at=datetime.now()
    )


@pytest.fixture
def mock_tenant_summary():
    """Mock tenant summary for list response."""
    return TenantSummary(
        id=1,
        name="Test Tenant",
        role="owner",
        created_at=datetime.now()
    )


@pytest.fixture
def mock_tenant_summaries_list(mock_tenant_summary):
    """Mock list of tenant summaries."""
    tenant2 = TenantSummary(
        id=2,
        name="Second Tenant",
        role="member",
        created_at=datetime.now()
    )
    return [mock_tenant_summary, tenant2]
