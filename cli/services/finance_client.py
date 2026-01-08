"""
Finance Planner HTTP client.

Handles communication with the finance_planner API service.
"""
import httpx
from typing import Optional

from cli.config.settings import get_settings
from cli.models.schemas import (
    Account,
    AccountCreate,
    AccountUpdate,
    Transaction,
    TransactionListResponse,
    BatchTransactionResponse,
    Tenant,
    TenantMember,
    TenantSummary,
)
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    ValidationError as CLIValidationError,
    PermissionDeniedError,
    NotFoundException,
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
    ) -> Account:
        """
        Update an account.

        Note: Balance cannot be updated directly. It is calculated from transactions.

        Args:
            token: JWT access token
            account_id: Account ID to update
            name: New account name (optional)
            account_type: New account type (optional)

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

    # ========================================================================
    # Transaction Methods
    # ========================================================================

    def create_transaction(
        self,
        token: str,
        account_id: int,
        amount: float,
        date: str,
        category: Optional[str] = None,
        merchant: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[list[str]] = None,
        der_category: Optional[str] = None,
        der_merchant: Optional[str] = None,
    ) -> Transaction:
        """
        Create a new transaction.

        Args:
            token: JWT access token
            account_id: Account ID this transaction belongs to
            amount: Transaction amount (negative for expenses, positive for income)
            date: Transaction date in ISO format (YYYY-MM-DD)
            category: Optional category
            merchant: Optional merchant name
            description: Optional description
            location: Optional location
            tags: Optional list of tags
            der_category: Optional derived category
            der_merchant: Optional derived merchant

        Returns:
            Created transaction data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            CLIValidationError: If input is invalid
        """
        url = f"{self.base_url}/api/transactions"
        headers = {"Authorization": f"Bearer {token}"}

        data = {
            "account_id": account_id,
            "amount": amount,
            "date": date,
        }

        # Add optional fields only if provided
        if category is not None:
            data["category"] = category
        if merchant is not None:
            data["merchant"] = merchant
        if description is not None:
            data["description"] = description
        if location is not None:
            data["location"] = location
        if tags is not None:
            data["tags"] = tags
        if der_category is not None:
            data["der_category"] = der_category
        if der_merchant is not None:
            data["der_merchant"] = der_merchant

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data, headers=headers)

                if response.status_code == 201:
                    return Transaction(**response.json())
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
                        f"Create transaction failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def list_transactions(
        self,
        token: str,
        account_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        merchant: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> TransactionListResponse:
        """
        List transactions with optional filters.

        Args:
            token: JWT access token
            account_id: Filter by account ID
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            category: Filter by category
            merchant: Filter by merchant
            tags: Filter by tags (comma-separated list matches ANY tag)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            TransactionListResponse with transactions and total count

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
        """
        url = f"{self.base_url}/api/transactions"
        headers = {"Authorization": f"Bearer {token}"}

        # Build query parameters
        params = {}
        if account_id is not None:
            params["account_id"] = account_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if category is not None:
            params["category"] = category
        if merchant is not None:
            params["merchant"] = merchant
        if tags is not None:
            # Convert list to comma-separated string for query param
            params["tags"] = ",".join(tags)
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    response_data = response.json()

                    # Handle paginated response format: {'transactions': [...], 'total': N}
                    if isinstance(response_data, dict) and "transactions" in response_data:
                        return TransactionListResponse(**response_data)
                    elif isinstance(response_data, list):
                        # Fallback: simple list format
                        return TransactionListResponse(
                            transactions=response_data, total=len(response_data)
                        )
                    else:
                        # Unexpected format
                        return TransactionListResponse(transactions=[], total=0)
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                else:
                    raise Exception(
                        f"List transactions failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def get_transaction(self, token: str, transaction_id: int) -> Transaction:
        """
        Get a specific transaction by ID.

        Args:
            token: JWT access token
            transaction_id: Transaction ID

        Returns:
            Transaction data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            Exception: If transaction not found or access denied
        """
        url = f"{self.base_url}/api/transactions/{transaction_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    return Transaction(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise Exception(f"Transaction {transaction_id} not found")
                else:
                    raise Exception(
                        f"Get transaction failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def update_transaction(
        self,
        token: str,
        transaction_id: int,
        account_id: Optional[int] = None,
        amount: Optional[float] = None,
        date: Optional[str] = None,
        category: Optional[str] = None,
        merchant: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[list[str]] = None,
        der_category: Optional[str] = None,
        der_merchant: Optional[str] = None,
    ) -> Transaction:
        """
        Update a transaction.

        Args:
            token: JWT access token
            transaction_id: Transaction ID to update
            account_id: New account ID (optional)
            amount: New amount (optional)
            date: New date (optional)
            category: New category (optional)
            merchant: New merchant (optional)
            description: New description (optional)
            location: New location (optional)
            tags: New tags list (optional)
            der_category: New derived category (optional)
            der_merchant: New derived merchant (optional)

        Returns:
            Updated transaction data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            Exception: If transaction not found or access denied
        """
        url = f"{self.base_url}/api/transactions/{transaction_id}"
        headers = {"Authorization": f"Bearer {token}"}

        # Build update data (only include provided fields)
        data = {}
        if account_id is not None:
            data["account_id"] = account_id
        if amount is not None:
            data["amount"] = amount
        if date is not None:
            data["date"] = date
        if category is not None:
            data["category"] = category
        if merchant is not None:
            data["merchant"] = merchant
        if description is not None:
            data["description"] = description
        if location is not None:
            data["location"] = location
        if tags is not None:
            data["tags"] = tags
        if der_category is not None:
            data["der_category"] = der_category
        if der_merchant is not None:
            data["der_merchant"] = der_merchant

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.patch(url, json=data, headers=headers)

                if response.status_code == 200:
                    return Transaction(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise Exception(f"Transaction {transaction_id} not found")
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise Exception(
                        f"Update transaction failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def delete_transaction(self, token: str, transaction_id: int) -> None:
        """
        Delete a transaction.

        Args:
            token: JWT access token
            transaction_id: Transaction ID to delete

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            Exception: If transaction not found or access denied
        """
        url = f"{self.base_url}/api/transactions/{transaction_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.delete(url, headers=headers)

                if response.status_code == 204:
                    return  # Success
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise Exception(f"Transaction {transaction_id} not found")
                else:
                    raise Exception(
                        f"Delete transaction failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def batch_create_transactions(
        self, token: str, account_id: int, transactions: list[dict]
    ) -> BatchTransactionResponse:
        """
        Create multiple transactions in one atomic operation.

        Args:
            token: JWT access token
            account_id: Account ID for all transactions
            transactions: List of transaction dicts (amount, date, category, etc.)

        Returns:
            BatchTransactionResponse with created transactions and account balance

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            CLIValidationError: If input is invalid
        """
        url = f"{self.base_url}/api/transactions/batch"
        headers = {"Authorization": f"Bearer {token}"}

        data = {"account_id": account_id, "transactions": transactions}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data, headers=headers)

                if response.status_code == 201:
                    return BatchTransactionResponse(**response.json())
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
                        f"Batch create transactions failed: {response.status_code} - {response.text}"
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

    # ========================================================================
    # Tenant Methods
    # ========================================================================

    def get_current_tenant(self, token: str) -> Tenant:
        """
        Get current tenant information.

        Args:
            token: JWT access token

        Returns:
            Tenant data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            NotFoundException: If tenant not found
        """
        url = f"{self.base_url}/api/tenants/me"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    return Tenant(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise NotFoundException("Tenant not found")
                else:
                    raise Exception(
                        f"Get tenant failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def update_tenant(self, token: str, name: str) -> Tenant:
        """
        Update current tenant name.

        Args:
            token: JWT access token
            name: New tenant name

        Returns:
            Updated tenant data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            PermissionDeniedError: If user is not OWNER
            CLIValidationError: If input is invalid
        """
        url = f"{self.base_url}/api/tenants/me"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"name": name}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.patch(url, json=data, headers=headers)

                if response.status_code == 200:
                    return Tenant(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 403:
                    raise PermissionDeniedError("Only OWNER can update tenant name")
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise Exception(
                        f"Update tenant failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def list_tenant_members(self, token: str) -> list[TenantMember]:
        """
        List all members of current tenant.

        Args:
            token: JWT access token

        Returns:
            List of tenant member objects

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
        """
        url = f"{self.base_url}/api/tenants/me/members"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    members_data = response.json()
                    return [TenantMember(**member) for member in members_data]
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                else:
                    raise Exception(
                        f"List members failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def invite_member(self, token: str, auth_user_id: str, role: str) -> TenantMember:
        """
        Invite a new member to the tenant.

        Args:
            token: JWT access token
            auth_user_id: Auth user ID to invite
            role: Role to assign (owner, admin, member, viewer)

        Returns:
            Created tenant member data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            PermissionDeniedError: If user lacks permission
            CLIValidationError: If input is invalid
        """
        url = f"{self.base_url}/api/tenants/me/members"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"auth_user_id": auth_user_id, "role": role}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data, headers=headers)

                if response.status_code == 201:
                    return TenantMember(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 403:
                    error_detail = response.json().get("detail", "Permission denied")
                    raise PermissionDeniedError(error_detail)
                elif response.status_code == 409:
                    raise Exception("User is already a member of this tenant")
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise Exception(
                        f"Invite member failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def update_member_role(self, token: str, user_id: int, role: str) -> TenantMember:
        """
        Update a member's role in the tenant.

        Args:
            token: JWT access token
            user_id: User ID to update
            role: New role (admin, member, viewer)

        Returns:
            Updated tenant member data

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            PermissionDeniedError: If user is not OWNER
            NotFoundException: If member not found
            CLIValidationError: If input is invalid
        """
        url = f"{self.base_url}/api/tenants/me/members/{user_id}/role"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"role": role}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.patch(url, json=data, headers=headers)

                if response.status_code == 200:
                    return TenantMember(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 403:
                    error_detail = response.json().get("detail", "Only OWNER can change roles")
                    raise PermissionDeniedError(error_detail)
                elif response.status_code == 404:
                    raise NotFoundException(f"Member with user_id {user_id} not found")
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise Exception(
                        f"Update member role failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def remove_member(self, token: str, user_id: int) -> dict:
        """
        Remove a member from the tenant.

        Args:
            token: JWT access token
            user_id: User ID to remove

        Returns:
            Response dict with message and removed_user_id

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            PermissionDeniedError: If user lacks permission
            NotFoundException: If member not found
        """
        url = f"{self.base_url}/api/tenants/me/members/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.delete(url, headers=headers)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 403:
                    error_detail = response.json().get("detail", "Permission denied")
                    raise PermissionDeniedError(error_detail)
                elif response.status_code == 404:
                    raise NotFoundException(f"Member with user_id {user_id} not found")
                else:
                    raise Exception(
                        f"Remove member failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e

    def list_user_tenants(self, token: str) -> list[TenantSummary]:
        """
        List all tenants the authenticated user belongs to.

        NOTE: This endpoint requires backend support (GET /api/tenants).
        If the backend doesn't have this endpoint yet, this will fail.

        Args:
            token: JWT access token

        Returns:
            List of tenant summaries with user's role in each tenant

        Raises:
            ServiceNotRunningError: If finance_planner is not running
            AuthenticationError: If token is invalid
            NotFoundException: If endpoint doesn't exist (404)
        """
        url = f"{self.base_url}/api/tenants"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    tenants_data = response.json()
                    return [TenantSummary(**tenant) for tenant in tenants_data]
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                elif response.status_code == 404:
                    raise NotFoundException(
                        "Tenant list endpoint not found. Backend may not support multi-tenant listing yet."
                    )
                else:
                    raise Exception(
                        f"List tenants failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("Finance Planner", self.base_url) from e
