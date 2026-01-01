"""
Unit tests for AuthClient.
"""
import pytest
from unittest.mock import patch, MagicMock
import httpx

from cli.services.auth_client import AuthClient
from cli.utils.errors import ServiceNotRunningError, AuthenticationError


# Mark all tests as unit tests
pytestmark = pytest.mark.unit


class TestAuthClient:
    """Test AuthClient HTTP methods."""

    @patch('cli.services.auth_client.httpx.Client')
    def test_register_success(self, mock_client_class, mock_httpx_response, mock_user_response):
        """Test successful user registration."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(201, mock_user_response.model_dump(mode='json'))
        mock_client.post.return_value = response

        # Test
        client = AuthClient(base_url="http://test:8001")
        user = client.register("test@example.com", "password123")

        assert user.email == "test@example.com"
        assert user.id == 1

    @patch('cli.services.auth_client.httpx.Client')
    def test_register_duplicate_email(self, mock_client_class, mock_httpx_response):
        """Test registration with duplicate email."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(400, {"detail": "Email already registered"})
        mock_client.post.return_value = response

        client = AuthClient(base_url="http://test:8001")

        with pytest.raises(AuthenticationError, match="Email already registered"):
            client.register("test@example.com", "password123")

    @patch('cli.services.auth_client.httpx.Client')
    def test_login_success(self, mock_client_class, mock_httpx_response, mock_token_response):
        """Test successful login."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, mock_token_response.model_dump())
        mock_client.post.return_value = response

        client = AuthClient(base_url="http://test:8001")
        token_resp = client.login("test@example.com", "password123")

        assert token_resp.access_token == mock_token_response.access_token
        assert token_resp.token_type == "bearer"

    @patch('cli.services.auth_client.httpx.Client')
    def test_login_invalid_credentials(self, mock_client_class, mock_httpx_response):
        """Test login with invalid credentials."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(401, {"detail": "Invalid credentials"})
        mock_client.post.return_value = response

        client = AuthClient(base_url="http://test:8001")

        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            client.login("test@example.com", "wrongpassword")

    @patch('cli.services.auth_client.httpx.Client')
    def test_refresh_token(self, mock_client_class, mock_httpx_response, mock_token_response):
        """Test token refresh."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, mock_token_response.model_dump())
        mock_client.post.return_value = response

        client = AuthClient(base_url="http://test:8001")
        token_resp = client.refresh("refresh_token_here")

        assert token_resp.access_token == mock_token_response.access_token

    @patch('cli.services.auth_client.httpx.Client')
    def test_get_profile(self, mock_client_class, mock_httpx_response, mock_user_response):
        """Test getting user profile."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, mock_user_response.model_dump(mode='json'))
        mock_client.get.return_value = response

        client = AuthClient(base_url="http://test:8001")
        user = client.get_profile("access_token")

        assert user.email == "test@example.com"
        assert user.id == 1

    @patch('cli.services.auth_client.httpx.Client')
    def test_service_not_running(self, mock_client_class):
        """Test handling when service is not running."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        mock_client.post.side_effect = httpx.ConnectError("Connection refused")

        client = AuthClient(base_url="http://test:8001")

        with pytest.raises(ServiceNotRunningError):
            client.login("test@example.com", "password123")
