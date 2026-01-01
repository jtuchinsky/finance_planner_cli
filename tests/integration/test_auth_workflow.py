"""
Integration tests for authentication workflows.

These tests require MCP_Auth service to be running on port 8001.
Run with: pytest tests/integration/ -v
"""
import pytest
import secrets
from cli.services.auth_client import AuthClient
from cli.services.token_manager import TokenManager
from cli.utils.errors import ServiceNotRunningError, AuthenticationError


# Mark all tests as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def unique_email():
    """Generate unique email for testing."""
    random_suffix = secrets.token_hex(4)
    return f"test_{random_suffix}@example.com"


@pytest.fixture
def auth_client():
    """Create AuthClient instance."""
    return AuthClient(base_url="http://127.0.0.1:8001")


class TestAuthenticationWorkflow:
    """Integration tests for complete auth workflows."""

    def test_register_and_login_flow(self, auth_client, unique_email, temp_token_file):
        """Test complete registration and login workflow."""
        password = "TestPassword123!"

        # Step 1: Register user
        try:
            user = auth_client.register(unique_email, password)
            assert user.email == unique_email
            assert user.id > 0
        except ServiceNotRunningError:
            pytest.skip("MCP_Auth service not running")

        # Step 2: Login
        token_response = auth_client.login(unique_email, password)
        assert token_response.access_token
        assert token_response.refresh_token
        assert token_response.expires_in > 0

        # Step 3: Save token
        token_manager = TokenManager(storage_path=temp_token_file)
        token_manager.save_token(unique_email, token_response)

        # Step 4: Get profile with token
        profile = auth_client.get_profile(token_response.access_token)
        assert profile.email == unique_email

    def test_login_with_wrong_password(self, auth_client, unique_email):
        """Test login fails with wrong password."""
        try:
            # Register first
            auth_client.register(unique_email, "CorrectPassword123!")
        except ServiceNotRunningError:
            pytest.skip("MCP_Auth service not running")

        # Try to login with wrong password
        with pytest.raises(AuthenticationError):
            auth_client.login(unique_email, "WrongPassword123!")

    def test_token_refresh_flow(self, auth_client, unique_email, temp_token_file):
        """Test token refresh workflow."""
        password = "TestPassword123!"

        try:
            # Register and login
            auth_client.register(unique_email, password)
            token_response = auth_client.login(unique_email, password)
        except ServiceNotRunningError:
            pytest.skip("MCP_Auth service not running")

        # Refresh token
        new_token_response = auth_client.refresh(token_response.refresh_token)
        assert new_token_response.access_token
        assert new_token_response.refresh_token
        # Note: access_token might be the same if not expired yet
        # Just verify we got valid token data back
        assert new_token_response.expires_in > 0

    def test_logout_flow(self, auth_client, unique_email, temp_token_file):
        """Test complete logout workflow."""
        password = "TestPassword123!"

        try:
            # Register and login
            auth_client.register(unique_email, password)
            token_response = auth_client.login(unique_email, password)
        except ServiceNotRunningError:
            pytest.skip("MCP_Auth service not running")

        # Save token
        token_manager = TokenManager(storage_path=temp_token_file)
        token_manager.save_token(unique_email, token_response)

        # Logout from server (revoke refresh token)
        auth_client.logout(token_response.refresh_token)

        # Clear local token
        token_manager.logout(unique_email)

        # Verify token is gone
        assert token_manager.get_current_token(auto_refresh=False) is None

    def test_duplicate_registration(self, auth_client, unique_email):
        """Test that duplicate registration fails."""
        password = "TestPassword123!"

        try:
            # Register once
            auth_client.register(unique_email, password)

            # Try to register again
            with pytest.raises(AuthenticationError):
                auth_client.register(unique_email, password)
        except ServiceNotRunningError:
            pytest.skip("MCP_Auth service not running")
