"""
Unit tests for TokenManager.
"""
import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path

from cli.services.token_manager import TokenManager
from cli.utils.errors import TokenNotFoundError


# Mark all tests as unit tests
pytestmark = pytest.mark.unit


class TestTokenManager:
    """Test TokenManager functionality."""

    def test_save_and_get_token(self, temp_token_file, mock_token_response):
        """Test saving and retrieving a token."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        # Save token
        manager.save_token(email, mock_token_response)

        # Retrieve token
        token = manager.get_current_token(auto_refresh=False)
        assert token == mock_token_response.access_token

    def test_get_current_user(self, temp_token_file, mock_token_response):
        """Test getting current user email."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response)
        current_user = manager.get_current_user()

        assert current_user == email

    def test_logout(self, temp_token_file, mock_token_response):
        """Test logout removes token."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response)
        manager.logout(email)

        token = manager.get_current_token(auto_refresh=False)
        assert token is None

    def test_multiple_users(self, temp_token_file, mock_token_response):
        """Test managing multiple users."""
        manager = TokenManager(storage_path=temp_token_file)

        # Add first user
        manager.save_token("user1@example.com", mock_token_response)

        # Add second user
        manager.save_token("user2@example.com", mock_token_response)

        # List users
        users = manager.list_users()
        assert len(users) == 2
        assert "user1@example.com" in users
        assert "user2@example.com" in users

        # Current user should be the last one added
        assert manager.get_current_user() == "user2@example.com"

    def test_switch_user(self, temp_token_file, mock_token_response):
        """Test switching between users."""
        manager = TokenManager(storage_path=temp_token_file)

        manager.save_token("user1@example.com", mock_token_response)
        manager.save_token("user2@example.com", mock_token_response)

        # Switch to user1
        manager.switch_user("user1@example.com")
        assert manager.get_current_user() == "user1@example.com"

    def test_switch_to_nonexistent_user(self, temp_token_file):
        """Test switching to a user without a token raises error."""
        manager = TokenManager(storage_path=temp_token_file)

        with pytest.raises(TokenNotFoundError):
            manager.switch_user("nonexistent@example.com")

    def test_token_file_permissions(self, temp_token_file, mock_token_response):
        """Test token file has secure permissions (0600)."""
        manager = TokenManager(storage_path=temp_token_file)
        manager.save_token("test@example.com", mock_token_response)

        # Check file permissions
        stat = temp_token_file.stat()
        permissions = stat.st_mode & 0o777
        assert permissions == 0o600, f"Expected 0o600, got {oct(permissions)}"

    def test_no_token_returns_none(self, temp_token_file):
        """Test getting token when none exists returns None."""
        manager = TokenManager(storage_path=temp_token_file)
        token = manager.get_current_token(auto_refresh=False)
        assert token is None

    def test_get_refresh_token(self, temp_token_file, mock_token_response):
        """Test retrieving refresh token."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response)
        refresh_token = manager.get_refresh_token()

        assert refresh_token == mock_token_response.refresh_token

    def test_corrupted_file_recovery(self, temp_token_file):
        """Test recovery from corrupted token file."""
        # Write invalid JSON to file
        temp_token_file.write_text("invalid json{")

        manager = TokenManager(storage_path=temp_token_file)
        token = manager.get_current_token(auto_refresh=False)

        # Should handle gracefully and return None
        assert token is None
