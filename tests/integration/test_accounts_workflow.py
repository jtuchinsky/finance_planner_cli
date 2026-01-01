"""
Integration tests for account management workflows.

These tests require both MCP_Auth and finance_planner services running.
Run with: pytest tests/integration/ -v
"""
import pytest
import secrets
from cli.services.auth_client import AuthClient
from cli.services.finance_client import FinanceClient
from cli.utils.errors import ServiceNotRunningError


# Mark all tests as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def unique_email():
    """Generate unique email for testing."""
    random_suffix = secrets.token_hex(4)
    return f"test_{random_suffix}@example.com"


@pytest.fixture
def authenticated_token(unique_email):
    """Create user and return authentication token."""
    auth_client = AuthClient(base_url="http://127.0.0.1:8001")
    password = "TestPassword123!"

    try:
        # Register and login
        auth_client.register(unique_email, password)
        token_response = auth_client.login(unique_email, password)
        return token_response.access_token
    except ServiceNotRunningError:
        pytest.skip("MCP_Auth service not running")


@pytest.fixture
def finance_client():
    """Create FinanceClient instance."""
    return FinanceClient(base_url="http://127.0.0.1:8000")


class TestAccountWorkflow:
    """Integration tests for account management."""

    def test_create_account_with_balance(self, finance_client, authenticated_token):
        """Test creating an account with initial balance."""
        try:
            account = finance_client.create_account(
                token=authenticated_token,
                name="Test Checking",
                account_type="checking",
                balance=1000.00
            )

            assert account.name == "Test Checking"
            assert account.account_type == "checking"
            assert account.balance == 1000.00
            assert account.id > 0
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_list_accounts(self, finance_client, authenticated_token):
        """Test listing accounts."""
        try:
            # Create an account first
            finance_client.create_account(
                token=authenticated_token,
                name="Account 1",
                account_type="savings",
                balance=5000.00
            )

            # List accounts
            accounts = finance_client.list_accounts(token=authenticated_token)

            assert len(accounts) >= 1
            assert any(acc.name == "Account 1" for acc in accounts)
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_get_specific_account(self, finance_client, authenticated_token):
        """Test getting specific account by ID."""
        try:
            # Create account
            created_account = finance_client.create_account(
                token=authenticated_token,
                name="Specific Account",
                account_type="investment",
                balance=10000.00
            )

            # Get the account
            account = finance_client.get_account(
                token=authenticated_token,
                account_id=created_account.id
            )

            assert account.id == created_account.id
            assert account.name == "Specific Account"
            assert account.balance == 10000.00
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_update_account_name(self, finance_client, authenticated_token):
        """Test updating account name."""
        try:
            # Create account
            account = finance_client.create_account(
                token=authenticated_token,
                name="Old Name",
                account_type="checking",
                balance=500.00
            )

            # Update name
            updated_account = finance_client.update_account(
                token=authenticated_token,
                account_id=account.id,
                name="New Name"
            )

            assert updated_account.name == "New Name"
            assert updated_account.id == account.id
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_update_account_type(self, finance_client, authenticated_token):
        """Test updating account type."""
        try:
            # Create account
            account = finance_client.create_account(
                token=authenticated_token,
                name="My Account",
                account_type="checking",
                balance=1000.00
            )

            # Update type
            updated_account = finance_client.update_account(
                token=authenticated_token,
                account_id=account.id,
                account_type="savings"
            )

            assert updated_account.account_type == "savings"
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_delete_account(self, finance_client, authenticated_token):
        """Test deleting an account."""
        try:
            # Create account
            account = finance_client.create_account(
                token=authenticated_token,
                name="To Delete",
                account_type="other",
                balance=100.00
            )

            account_id = account.id

            # Delete account
            finance_client.delete_account(
                token=authenticated_token,
                account_id=account_id
            )

            # Try to get deleted account - should raise exception
            with pytest.raises(Exception):  # Will be 404 error
                finance_client.get_account(
                    token=authenticated_token,
                    account_id=account_id
                )
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_multiple_account_types(self, finance_client, authenticated_token):
        """Test creating accounts of different types."""
        account_types = ["checking", "savings", "credit_card", "investment", "loan", "other"]

        try:
            for acc_type in account_types:
                account = finance_client.create_account(
                    token=authenticated_token,
                    name=f"{acc_type.title()} Account",
                    account_type=acc_type,
                    balance=1000.00
                )

                assert account.account_type == acc_type
                assert account.balance == 1000.00
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")

    def test_account_balance_readonly_after_creation(self, finance_client, authenticated_token):
        """Test that balance is preserved and read-only after creation."""
        try:
            # Create account with initial balance
            account = finance_client.create_account(
                token=authenticated_token,
                name="Balance Test",
                account_type="savings",
                balance=5000.00
            )

            initial_balance = account.balance

            # Update name (balance should remain unchanged)
            updated_account = finance_client.update_account(
                token=authenticated_token,
                account_id=account.id,
                name="Updated Name"
            )

            # Balance should be unchanged
            assert updated_account.balance == initial_balance
        except ServiceNotRunningError:
            pytest.skip("Finance Planner service not running")
