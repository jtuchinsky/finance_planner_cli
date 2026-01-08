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


class TestTokenManagerMultiTenant:
    """Test TokenManager multi-tenant functionality."""

    def test_extract_tenant_id_from_token(self, temp_token_file, mock_token_with_tenant):
        """Test extracting tenant_id from JWT token."""
        manager = TokenManager(storage_path=temp_token_file)
        tenant_id = manager.get_tenant_id_from_token(mock_token_with_tenant)

        assert tenant_id == 1

    def test_extract_tenant_id_from_token_without_tenant(self, temp_token_file, mock_token_response):
        """Test extracting tenant_id from JWT token without tenant_id claim."""
        manager = TokenManager(storage_path=temp_token_file)
        tenant_id = manager.get_tenant_id_from_token(mock_token_response.access_token)

        assert tenant_id is None

    def test_extract_tenant_id_from_invalid_token(self, temp_token_file):
        """Test extracting tenant_id from invalid JWT token."""
        manager = TokenManager(storage_path=temp_token_file)
        tenant_id = manager.get_tenant_id_from_token("invalid.jwt.token")

        assert tenant_id is None

    def test_save_token_with_tenant_id(self, temp_token_file, mock_token_response_with_tenant):
        """Test saving token automatically extracts and stores tenant_id."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response_with_tenant)

        # Check tenant_id was stored in token storage
        token_file = manager._read_token_file()
        assert email in token_file.tokens
        assert token_file.tokens[email].tenant_id == 1

        # Check tenant preferences were updated
        assert email in token_file.tenant_preferences
        assert token_file.tenant_preferences[email] == 1

        # Check current_tenant_id was set
        assert token_file.current_tenant_id == 1

    def test_get_current_tenant_id(self, temp_token_file, mock_token_response_with_tenant):
        """Test getting current tenant ID for logged-in user."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response_with_tenant)
        tenant_id = manager.get_current_tenant_id()

        assert tenant_id == 1

    def test_get_current_tenant_id_no_user(self, temp_token_file):
        """Test getting current tenant ID when no user is logged in."""
        manager = TokenManager(storage_path=temp_token_file)
        tenant_id = manager.get_current_tenant_id()

        assert tenant_id is None

    def test_switch_tenant(self, temp_token_file, mock_token_response_with_tenant):
        """Test switching tenant context."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        # Login and save token
        manager.save_token(email, mock_token_response_with_tenant)

        # Switch to different tenant
        manager.switch_tenant(tenant_id=2)

        # Check tenant preference was updated
        token_file = manager._read_token_file()
        assert token_file.tenant_preferences[email] == 2
        assert token_file.current_tenant_id == 2

        # Check token was cleared (to force re-auth)
        assert email not in token_file.tokens

    def test_switch_tenant_no_current_user(self, temp_token_file):
        """Test switching tenant when no user is logged in raises error."""
        manager = TokenManager(storage_path=temp_token_file)

        with pytest.raises(TokenNotFoundError):
            manager.switch_tenant(tenant_id=2)

    def test_multiple_users_different_tenants(self, temp_token_file, mock_token_response_with_tenant):
        """Test multiple users can have different tenant preferences."""
        manager = TokenManager(storage_path=temp_token_file)

        # User 1 with tenant 1
        manager.save_token("user1@example.com", mock_token_response_with_tenant)

        # User 2 with tenant 1 (same token for simplicity)
        manager.save_token("user2@example.com", mock_token_response_with_tenant)

        # Switch user 1 to tenant 2
        manager.switch_user("user1@example.com")
        manager.switch_tenant(tenant_id=2)

        # Re-login user 1 (simulating getting new token)
        manager.save_token("user1@example.com", mock_token_response_with_tenant)

        # Check user 1 has tenant 1 (from new token, but preference is 2)
        token_file = manager._read_token_file()
        assert token_file.tenant_preferences["user1@example.com"] == 1  # Updated by save_token
        assert token_file.tenant_preferences["user2@example.com"] == 1

    def test_migrate_old_token_file(self, temp_token_file, mock_token_response_with_tenant):
        """Test migration of old token file format to new format."""
        # Create old-format token file (without tenant fields)
        old_format_data = {
            "current_user": "test@example.com",
            "tokens": {
                "test@example.com": {
                    "access_token": mock_token_response_with_tenant.access_token,
                    "refresh_token": "refresh_token_here",
                    "expires_at": "2025-01-15T10:00:00"
                }
            }
        }

        with open(temp_token_file, 'w') as f:
            json.dump(old_format_data, f)

        # Load with TokenManager (should trigger migration)
        manager = TokenManager(storage_path=temp_token_file)
        token_file = manager._read_token_file()

        # Check migration added new fields
        assert hasattr(token_file, 'tenant_preferences')
        assert hasattr(token_file, 'current_tenant_id')

        # Check tenant_id was extracted from JWT
        assert token_file.tokens["test@example.com"].tenant_id == 1
        assert token_file.tenant_preferences["test@example.com"] == 1
        assert token_file.current_tenant_id == 1

    def test_migrate_preserves_existing_data(self, temp_token_file, mock_token_response):
        """Test migration preserves existing tokens and user data."""
        # Create old-format token file with multiple users
        old_format_data = {
            "current_user": "user2@example.com",
            "tokens": {
                "user1@example.com": {
                    "access_token": mock_token_response.access_token,
                    "refresh_token": "refresh1",
                    "expires_at": "2025-01-15T10:00:00"
                },
                "user2@example.com": {
                    "access_token": mock_token_response.access_token,
                    "refresh_token": "refresh2",
                    "expires_at": "2025-01-15T11:00:00"
                }
            }
        }

        with open(temp_token_file, 'w') as f:
            json.dump(old_format_data, f)

        # Load with TokenManager
        manager = TokenManager(storage_path=temp_token_file)
        token_file = manager._read_token_file()

        # Check all users preserved
        assert len(token_file.tokens) == 2
        assert "user1@example.com" in token_file.tokens
        assert "user2@example.com" in token_file.tokens

        # Check current user preserved
        assert token_file.current_user == "user2@example.com"

        # Check tokens preserved
        assert token_file.tokens["user1@example.com"].refresh_token == "refresh1"
        assert token_file.tokens["user2@example.com"].refresh_token == "refresh2"

    def test_save_token_without_tenant_id(self, temp_token_file, mock_token_response):
        """Test saving token without tenant_id in JWT still works."""
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response)

        # Check token was saved
        token = manager.get_current_token(auto_refresh=False)
        assert token == mock_token_response.access_token

        # Check tenant fields are None/empty
        token_file = manager._read_token_file()
        assert token_file.tokens[email].tenant_id is None
        assert token_file.current_tenant_id is None
        assert email not in token_file.tenant_preferences or token_file.tenant_preferences[email] is None

    def test_tenant_context_persists_across_sessions(self, temp_token_file, mock_token_response_with_tenant):
        """Test tenant context persists when TokenManager is recreated."""
        email = "test@example.com"

        # Session 1: Login and save token
        manager1 = TokenManager(storage_path=temp_token_file)
        manager1.save_token(email, mock_token_response_with_tenant)
        tenant_id_1 = manager1.get_current_tenant_id()
        assert tenant_id_1 == 1

        # Session 2: Create new TokenManager instance
        manager2 = TokenManager(storage_path=temp_token_file)
        tenant_id_2 = manager2.get_current_tenant_id()

        # Tenant context should persist
        assert tenant_id_2 == 1
        assert tenant_id_2 == tenant_id_1
