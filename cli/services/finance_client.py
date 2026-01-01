"""
Finance Planner HTTP client.

Handles communication with the finance_planner API service.
"""
import httpx
from typing import Optional

from cli.config.settings import get_settings
from cli.models.schemas import Account, AccountCreate, AccountUpdate
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    ValidationError as CLIValidationError,
)


class FinanceClient:
    """HTTP client for finance_planner service."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize finance client.

        Args:
            base_url: Finance Planner service URL (default: from settings)
        """
        if base_url is None:
            settings = get_settings()
            base_url = settings.finance_planner_url

        self.base_url = base_url.rstrip("/")
        self.timeout = get_settings().http_timeout

    def create_account(
        self, token: str, name: str, account_type: str, balance: float = 0.0
    ) -> Account:
        """
        Create a new financial account.

        Args:
            token: JWT access token
            name: Account name
            account_type: Account type (checking, savings, credit, investment, cash)
            balance: Initial balance (default: 0.0)

        Returns:
            Created account data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            CLIValidationError: If input is invalid
        """
        url = f"{self.base_url}/api/accounts"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"name": name, "account_type": account_type, "initial_balance": balance}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data, headers=headers)

                if response.status_code == 201:
                    return Account(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise Exception(
                        f"Create account failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def list_accounts(self, token: str) -> list[Account]:
        """
        List all accounts for the current user.

        Args:
            token: JWT access token

        Returns:
            List of account objects

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
        """
        url = f"{self.base_url}/api/accounts"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    response_data = response.json()

                    # Handle paginated response format: {'accounts': [...], 'total': N}
                    if isinstance(response_data, dict) and 'accounts' in response_data:
                        accounts_data = response_data['accounts']
                    elif isinstance(response_data, list):
                        accounts_data = response_data
                    else:
                        # Unexpected format
                        accounts_data = []

                    return [Account(**acc) for acc in accounts_data]
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                else:
                    raise Exception(
                        f"List accounts failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def get_account(self, token: str, account_id: int) -> Account:
        """
        Get a specific account by ID.

        Args:
            token: JWT access token
            account_id: Account ID

        Returns:
            Account data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            Exception: If account not found or access denied
        """
        url = f"{self.base_url}/api/accounts/{account_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    return Account(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise Exception(f"Account {account_id} not found")
                else:
                    raise Exception(
                        f"Get account failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def update_account(
        self,
        token: str,
        account_id: int,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        balance: Optional[float] = None,
    ) -> Account:
        """
        Update an account.

        Args:
            token: JWT access token
            account_id: Account ID to update
            name: New account name (optional)
            account_type: New account type (optional)
            balance: New balance (optional)

        Returns:
            Updated account data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            Exception: If account not found or access denied
        """
        url = f"{self.base_url}/api/accounts/{account_id}"
        headers = {"Authorization": f"Bearer {token}"}

        # Build update data (only include provided fields)
        data = {}
        if name is not None:
            data["name"] = name
        if account_type is not None:
            data["account_type"] = account_type
        if balance is not None:
            data["balance"] = balance

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.patch(url, json=data, headers=headers)

                if response.status_code == 200:
                    return Account(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise Exception(f"Account {account_id} not found")
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise Exception(
                        f"Update account failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def delete_account(self, token: str, account_id: int) -> None:
        """
        Delete an account.

        Args:
            token: JWT access token
            account_id: Account ID to delete

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            Exception: If account not found or access denied
        """
        url = f"{self.base_url}/api/accounts/{account_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.delete(url, headers=headers)

                if response.status_code == 204:
                    return  # Success
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise Exception(f"Account {account_id} not found")
                else:
                    raise Exception(
                        f"Delete account failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    @staticmethod
    def _format_validation_errors(errors: list) -> str:
        """Format FastAPI validation errors into readable message."""
        if not errors:
            return "Validation failed"

        messages = []
        for error in errors:
            field = " -> ".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            messages.append(f"{field}: {msg}")

        return "Validation errors:\n  " + "\n  ".join(messages)
