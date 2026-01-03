"""
Unit tests for FinanceClient transaction methods.
"""
import pytest
from unittest.mock import patch, MagicMock
import httpx

from cli.services.finance_client import FinanceClient
from cli.utils.errors import ServiceNotRunningError, AuthenticationError


# Mark all tests as unit tests
pytestmark = pytest.mark.unit


class TestTransactionClient:
    """Test FinanceClient transaction HTTP methods."""

    @patch('cli.services.finance_client.httpx.Client')
    def test_create_transaction_success(self, mock_client_class, mock_httpx_response, mock_transaction):
        """Test successful transaction creation."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(201, mock_transaction.model_dump(mode='json'))
        mock_client.post.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        transaction = client.create_transaction(
            token="access_token",
            account_id=1,
            amount=-50.00,
            date="2026-01-03",
            category="Food & Dining",
            merchant="Starbucks"
        )

        assert transaction.id == 1
        assert transaction.amount == -50.00
        assert transaction.merchant == "Starbucks"

    @patch('cli.services.finance_client.httpx.Client')
    def test_create_transaction_with_all_fields(self, mock_client_class, mock_httpx_response, mock_transaction):
        """Test transaction creation with all optional fields."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(201, mock_transaction.model_dump(mode='json'))
        mock_client.post.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        client.create_transaction(
            token="access_token",
            account_id=1,
            amount=-50.00,
            date="2026-01-03",
            category="Food & Dining",
            merchant="Starbucks",
            description="Morning coffee",
            location="123 Main St",
            tags=["coffee", "daily"]
        )

        # Verify all fields were sent
        call_args = mock_client.post.call_args
        sent_data = call_args.kwargs['json']
        assert sent_data['tags'] == ["coffee", "daily"]
        assert sent_data['location'] == "123 Main St"

    @patch('cli.services.finance_client.httpx.Client')
    def test_create_transaction_account_not_found(self, mock_client_class, mock_httpx_response):
        """Test transaction creation with non-existent account."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(404)
        mock_client.post.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(Exception, match="Account 1 not found"):
            client.create_transaction(
                token="access_token",
                account_id=1,
                amount=-50.00,
                date="2026-01-03"
            )

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_transactions_paginated_response(self, mock_client_class, mock_httpx_response, mock_transactions_list):
        """Test listing transactions with paginated response."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        paginated_data = {
            'transactions': [t.model_dump(mode='json') for t in mock_transactions_list],
            'total': len(mock_transactions_list)
        }
        response = mock_httpx_response(200, paginated_data)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        result = client.list_transactions(token="access_token")

        assert len(result.transactions) == 2
        assert result.total == 2

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_transactions_with_filters(self, mock_client_class, mock_httpx_response, mock_transactions_list):
        """Test listing transactions with query filters."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        paginated_data = {
            'transactions': [t.model_dump(mode='json') for t in mock_transactions_list],
            'total': 2
        }
        response = mock_httpx_response(200, paginated_data)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        client.list_transactions(
            token="access_token",
            account_id=1,
            start_date="2026-01-01",
            end_date="2026-01-31",
            category="Food & Dining",
            limit=50
        )

        # Verify query params were sent
        call_args = mock_client.get.call_args
        sent_params = call_args.kwargs['params']
        assert sent_params['account_id'] == 1
        assert sent_params['start_date'] == "2026-01-01"
        assert sent_params['category'] == "Food & Dining"

    @patch('cli.services.finance_client.httpx.Client')
    def test_list_transactions_empty(self, mock_client_class, mock_httpx_response):
        """Test listing transactions with no results."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        paginated_data = {'transactions': [], 'total': 0}
        response = mock_httpx_response(200, paginated_data)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        result = client.list_transactions(token="access_token")

        assert len(result.transactions) == 0
        assert result.total == 0

    @patch('cli.services.finance_client.httpx.Client')
    def test_get_transaction_success(self, mock_client_class, mock_httpx_response, mock_transaction):
        """Test getting specific transaction."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, mock_transaction.model_dump(mode='json'))
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        transaction = client.get_transaction(token="access_token", transaction_id=1)

        assert transaction.id == 1
        assert transaction.merchant == "Starbucks"

    @patch('cli.services.finance_client.httpx.Client')
    def test_get_transaction_not_found(self, mock_client_class, mock_httpx_response):
        """Test getting non-existent transaction."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(404)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(Exception, match="Transaction 999 not found"):
            client.get_transaction(token="access_token", transaction_id=999)

    @patch('cli.services.finance_client.httpx.Client')
    def test_update_transaction_partial(self, mock_client_class, mock_httpx_response, mock_transaction):
        """Test updating transaction with partial fields."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        updated_transaction = mock_transaction.model_copy()
        updated_transaction.amount = -75.00
        response = mock_httpx_response(200, updated_transaction.model_dump(mode='json'))
        mock_client.patch.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        transaction = client.update_transaction(
            token="access_token",
            transaction_id=1,
            amount=-75.00
        )

        assert transaction.amount == -75.00

        # Verify only amount was sent
        call_args = mock_client.patch.call_args
        sent_data = call_args.kwargs['json']
        assert 'amount' in sent_data
        assert 'category' not in sent_data

    @patch('cli.services.finance_client.httpx.Client')
    def test_update_transaction_validation_error(self, mock_client_class, mock_httpx_response):
        """Test updating transaction with validation error."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        error_detail = [
            {"loc": ["body", "date"], "msg": "Invalid date format"}
        ]
        response = mock_httpx_response(422, {"detail": error_detail})
        mock_client.patch.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(Exception, match="Validation errors"):
            client.update_transaction(
                token="access_token",
                transaction_id=1,
                date="invalid-date"
            )

    @patch('cli.services.finance_client.httpx.Client')
    def test_delete_transaction_success(self, mock_client_class, mock_httpx_response):
        """Test deleting transaction."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(204)
        mock_client.delete.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        client.delete_transaction(token="access_token", transaction_id=1)

        # Should not raise exception

    @patch('cli.services.finance_client.httpx.Client')
    def test_delete_transaction_not_found(self, mock_client_class, mock_httpx_response):
        """Test deleting non-existent transaction."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(404)
        mock_client.delete.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(Exception, match="Transaction 999 not found"):
            client.delete_transaction(token="access_token", transaction_id=999)

    @patch('cli.services.finance_client.httpx.Client')
    def test_unauthorized_error(self, mock_client_class, mock_httpx_response):
        """Test handling 401 unauthorized for all methods."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(401)
        mock_client.get.return_value = response

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(AuthenticationError, match="Invalid or expired token"):
            client.list_transactions(token="invalid_token")

    @patch('cli.services.finance_client.httpx.Client')
    def test_service_not_running(self, mock_client_class):
        """Test handling when service is not running."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        mock_client.get.side_effect = httpx.ConnectError("Connection refused")

        client = FinanceClient(base_url="http://test:8000")

        with pytest.raises(ServiceNotRunningError):
            client.list_transactions(token="access_token")

    @patch('cli.services.finance_client.httpx.Client')
    def test_batch_create_transactions_success(self, mock_client_class, mock_httpx_response, mock_transactions_list):
        """Test batch transaction creation."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        batch_response = {
            "transactions": [t.model_dump(mode='json') for t in mock_transactions_list],
            "account_balance": 950.00,
            "total_amount": 950.00,
            "count": 2
        }
        response = mock_httpx_response(201, batch_response)
        mock_client.post.return_value = response

        client = FinanceClient(base_url="http://test:8000")
        transactions_data = [
            {"amount": -50.00, "date": "2026-01-03", "category": "Food & Dining"},
            {"amount": 1000.00, "date": "2026-01-02", "category": "Income"}
        ]
        result = client.batch_create_transactions(
            token="access_token",
            account_id=1,
            transactions=transactions_data
        )

        assert result.count == 2
        assert result.account_balance == 950.00
        assert len(result.transactions) == 2
