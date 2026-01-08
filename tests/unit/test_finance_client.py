"""
Unit tests for FinanceClient.
"""
import pytest
from unittest.mock import patch, MagicMock
import httpx

from cli.services.finance_client import FinanceClient
from cli.utils.errors import ServiceNotRunningError, AuthenticationError


# Mark all tests as unit tests
pytestmark = pytest.mark.unit


class TestFinanceClient:
    """Test FinanceClient HTTP methods."""

    @patch('cli.services.finance_client.httpx.Client')
    def test_create_account_success(self, mock_client_class, mock_httpx_response, mock_account):
        """Test successful account creation."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(201, mock_account.model_dump(mode='json'))
        mock_client.post.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        account = client.create_account(
            token="access_token",
            name="Test Account",
            account_type="checking",
            balance=1000.00
        )

        assert account.name == "Test Account"
        assert account.balance == 1000.00

    @patch('cli.services.finance_client.httpx.Client')
    def test_create_account_with_initial_balance(self, mock_client_class, mock_httpx_response, mock_account):
        """Test that initial_balance is sent correctly."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(201, mock_account.model_dump(mode='json'))
        mock_client.post.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        client.create_account(
            token="access_token",
            name="Test Account",
            account_type="checking",
            balance=5000.00
        )

        # Verify initial_balance was sent
        call_args = mock_client.post.call_args
        sent_data = call_args.kwargs['json']
        assert sent_data['initial_balance'] == 5000.00

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_accounts_paginated_response(self, mock_client_class, mock_httpx_response, mock_accounts_list):
        """Test listing accounts with paginated response."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        # Paginated format: {'accounts': [...], 'total': N}
        paginated_data = {
            'accounts': [acc.model_dump(mode='json') for acc in mock_accounts_list],
            'total': len(mock_accounts_list)
        }
        response = mock_httpx_response(200, paginated_data)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        accounts = client.list_accounts(token="access_token")

        assert len(accounts) == 2
        assert accounts[0].name == "Test Account"
        assert accounts[1].name == "Savings Account"

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_accounts_list_response(self, mock_client_class, mock_httpx_response, mock_accounts_list):
        """Test listing accounts with simple list response."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        # Simple list format
        list_data = [acc.model_dump(mode='json') for acc in mock_accounts_list]
        response = mock_httpx_response(200, list_data)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        accounts = client.list_accounts(token="access_token")

        assert len(accounts) == 2

    @patch('cli.services.finance_client.httpx.Client')
    def test_get_account(self, mock_client_class, mock_httpx_response, mock_account):
        """Test getting specific account."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, mock_account.model_dump(mode='json'))
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        account = client.get_account(token="access_token", account_id=1)

        assert account.id == 1
        assert account.name == "Test Account"

    @patch('cli.services.finance_client.httpx.Client')
    def test_update_account(self, mock_client_class, mock_httpx_response, mock_account):
        """Test updating account."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        updated_account = mock_account.model_copy()
        updated_account.name = "Updated Account"
        response = mock_httpx_response(200, updated_account.model_dump(mode='json'))
        mock_client.patch.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        account = client.update_account(
            token="access_token",
            account_id=1,
            name="Updated Account"
        )

        assert account.name == "Updated Account"

    @patch('cli.services.finance_client.httpx.Client')
    def test_update_account_no_balance(self, mock_client_class, mock_httpx_response, mock_account):
        """Test that balance cannot be updated."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, mock_account.model_dump(mode='json'))
        mock_client.patch.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        client.update_account(
            token="access_token",
            account_id=1,
            name="Updated Account"
        )

        # Verify balance was NOT sent
        call_args = mock_client.patch.call_args
        sent_data = call_args.kwargs['json']
        assert 'balance' not in sent_data

    @patch('cli.services.finance_client.httpx.Client')
    def test_delete_account(self, mock_client_class, mock_httpx_response):
        """Test deleting account."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(204)
        mock_client.delete.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        client.delete_account(token="access_token", account_id=1)

        # Should not raise exception

    @patch('cli.services.finance_client.httpx.Client')
    def test_unauthorized_error(self, mock_client_class, mock_httpx_response):
        """Test handling 401 unauthorized."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(401)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(AuthenticationError, match="Invalid or expired token"):
            client.list_accounts(token="invalid_token")

    @patch('cli.services.finance_client.httpx.Client')
    def test_service_not_running(self, mock_client_class):
        """Test handling when service is not running."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(ServiceNotRunningError):
            client.list_accounts(token="access_token")


class TestFinanceClientTenants:
    """Test FinanceClient tenant methods."""

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_user_tenants_success(self, mock_client_class, mock_httpx_response, mock_tenant_summaries_list):
        """Test successful retrieval of user's tenants."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        tenants_data = [t.model_dump(mode='json') for t in mock_tenant_summaries_list]
        response = mock_httpx_response(200, tenants_data)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        tenants = client.list_user_tenants(token="access_token")

        assert len(tenants) == 2
        assert tenants[0].id == 1
        assert tenants[0].name == "Test Tenant"
        assert tenants[0].role == "owner"
        assert tenants[1].id == 2
        assert tenants[1].name == "Second Tenant"
        assert tenants[1].role == "member"

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_user_tenants_empty_list(self, mock_client_class, mock_httpx_response):
        """Test listing tenants when user belongs to no tenants."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, [])
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        tenants = client.list_user_tenants(token="access_token")

        assert len(tenants) == 0

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_user_tenants_auth_error(self, mock_client_class, mock_httpx_response):
        """Test listing tenants with invalid token."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(401)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(AuthenticationError, match="Invalid or expired token"):
            client.list_user_tenants(token="invalid_token")

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_user_tenants_endpoint_not_found(self, mock_client_class, mock_httpx_response):
        """Test listing tenants when backend doesn't support the endpoint."""
        from cli.utils.errors import NotFoundException

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(404)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(NotFoundException, match="Tenant list endpoint not found"):
            client.list_user_tenants(token="access_token")

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_user_tenants_service_not_running(self, mock_client_class):
        """Test listing tenants when service is not running."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(ServiceNotRunningError):
            client.list_user_tenants(token="access_token")
