"""
Token management service.

Handles JWT token storage, retrieval, validation, and auto-refresh.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

from cli.models.schemas import TokenResponse, TokenStorage, TokenFile
from cli.utils.errors import TokenExpiredError, TokenNotFoundError, TokenRefreshError


class TokenManager:
    """
    Manages JWT tokens for authentication.

    - Stores tokens securely in JSON file (mode 0600)
    - Validates token expiration
    - Auto-refreshes expired tokens
    - Supports multiple users
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize token manager.

        Args:
            storage_path: Path to token storage file (default: ~/.config/finance-cli/tokens.json)
        """
        if storage_path is None:
            from cli.config.settings import get_settings
            storage_path = get_settings().token_storage_path

        self.storage_path = storage_path

        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize file if it doesn't exist
        if not self.storage_path.exists():
            self._write_token_file(TokenFile())

    def save_token(self, email: str, token_response: TokenResponse) -> None:
        """
        Save token for a user and set as current user.

        Args:
            email: User's email address
            token_response: Token data from login/refresh
        """
        # Calculate expiration time
        expires_at = datetime.now() + timedelta(seconds=token_response.expires_in)

        # Extract tenant_id from JWT token
        tenant_id = self.get_tenant_id_from_token(token_response.access_token)

        # Create storage entry
        token_storage = TokenStorage(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            expires_at=expires_at,
            tenant_id=tenant_id,
        )

        # Load existing tokens
        token_file = self._read_token_file()

        # Update tokens
        token_file.tokens[email] = token_storage
        token_file.current_user = email

        # Update tenant preferences and current_tenant_id
        if tenant_id:
            token_file.tenant_preferences[email] = tenant_id
            token_file.current_tenant_id = tenant_id

        # Write back to file
        self._write_token_file(token_file)

    def get_current_token(self, auto_refresh: bool = True) -> Optional[str]:
        """
        Get access token for current user.

        Args:
            auto_refresh: Automatically refresh if token is expired

        Returns:
            Access token string, or None if not logged in

        Raises:
            TokenExpiredError: If token is expired and auto_refresh=False
            TokenRefreshError: If auto-refresh fails
        """
        token_file = self._read_token_file()

        if not token_file.current_user:
            return None

        token_storage = token_file.tokens.get(token_file.current_user)
        if not token_storage:
            return None

        # Check if token is expired
        if self._is_expired(token_storage.expires_at):
            if auto_refresh:
                return self._refresh_current_token()
            else:
                raise TokenExpiredError("Access token has expired")

        return token_storage.access_token

    def get_refresh_token(self) -> Optional[str]:
        """
        Get refresh token for current user.

        Returns:
            Refresh token string, or None if not logged in
        """
        token_file = self._read_token_file()

        if not token_file.current_user:
            return None

        token_storage = token_file.tokens.get(token_file.current_user)
        if not token_storage:
            return None

        return token_storage.refresh_token

    def get_current_user(self) -> Optional[str]:
        """
        Get email of currently logged in user.

        Returns:
            User's email, or None if not logged in
        """
        token_file = self._read_token_file()
        return token_file.current_user

    def get_current_tenant_id(self) -> Optional[int]:
        """
        Get current tenant ID for logged-in user.

        Returns:
            Tenant ID from user's tenant preference, or None if not set
        """
        token_file = self._read_token_file()
        if not token_file.current_user:
            return None
        return token_file.tenant_preferences.get(token_file.current_user)

    def logout(self, email: Optional[str] = None) -> None:
        """
        Logout user (remove tokens).

        Args:
            email: User email to logout (default: current user)
        """
        token_file = self._read_token_file()

        # Determine which user to logout
        target_email = email or token_file.current_user

        if target_email and target_email in token_file.tokens:
            del token_file.tokens[target_email]

        # Clear current user if it's the one being logged out
        if token_file.current_user == target_email:
            token_file.current_user = None

        self._write_token_file(token_file)

    def switch_user(self, email: str) -> None:
        """
        Switch to a different authenticated user.

        Args:
            email: Email of user to switch to

        Raises:
            TokenNotFoundError: If user has no stored token
        """
        token_file = self._read_token_file()

        if email not in token_file.tokens:
            raise TokenNotFoundError(f"No token found for {email}")

        token_file.current_user = email
        self._write_token_file(token_file)

    def switch_tenant(self, tenant_id: int) -> None:
        """
        Switch to a different tenant context for current user.

        This clears the current token and updates the tenant preference,
        requiring the user to log in again to get a token for the new tenant.

        Args:
            tenant_id: Tenant ID to switch to

        Raises:
            TokenNotFoundError: If no current user
        """
        token_file = self._read_token_file()

        if not token_file.current_user:
            raise TokenNotFoundError("No current user")

        # Update tenant preference
        token_file.tenant_preferences[token_file.current_user] = tenant_id
        token_file.current_tenant_id = tenant_id

        # Clear token to force re-authentication with new tenant context
        if token_file.current_user in token_file.tokens:
            del token_file.tokens[token_file.current_user]

        self._write_token_file(token_file)

    def list_users(self) -> list[str]:
        """
        List all authenticated users.

        Returns:
            List of user emails with stored tokens
        """
        token_file = self._read_token_file()
        return list(token_file.tokens.keys())

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a JWT token is expired.

        Args:
            token: JWT token string

        Returns:
            True if token is expired
        """
        try:
            # Decode without verification (just to check expiration)
            payload = jwt.get_unverified_claims(token)
            exp = payload.get("exp")

            if exp is None:
                return False

            # Check expiration
            exp_datetime = datetime.fromtimestamp(exp)
            return self._is_expired(exp_datetime)

        except (JWTError, ValueError, KeyError):
            # If we can't decode, consider it expired
            return True

    def get_tenant_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract tenant_id from JWT token claims.

        Args:
            token: JWT token string

        Returns:
            Tenant ID from token, or None if not found
        """
        try:
            payload = jwt.get_unverified_claims(token)
            tenant_id = payload.get("tenant_id")

            if tenant_id is not None:
                return int(tenant_id)
            return None

        except (JWTError, ValueError, KeyError):
            return None

    def _refresh_current_token(self) -> str:
        """
        Refresh access token for current user.

        Returns:
            New access token

        Raises:
            TokenNotFoundError: If no current user or refresh token
            TokenRefreshError: If refresh fails
        """
        from cli.services.auth_client import AuthClient

        refresh_token = self.get_refresh_token()
        current_user = self.get_current_user()

        if not refresh_token or not current_user:
            raise TokenNotFoundError("No refresh token available")

        try:
            # Call auth service to refresh
            auth_client = AuthClient()
            token_response = auth_client.refresh(refresh_token)

            # Save new tokens
            self.save_token(current_user, token_response)

            return token_response.access_token

        except Exception as e:
            raise TokenRefreshError(f"Failed to refresh token: {str(e)}") from e

    def _read_token_file(self) -> TokenFile:
        """Read token file from disk."""
        if not self.storage_path.exists():
            return TokenFile()

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                token_file = TokenFile(**data)

                # Migrate old format if needed
                token_file = self._migrate_token_file(token_file)

                return token_file
        except (json.JSONDecodeError, ValueError):
            # Corrupted file, start fresh
            return TokenFile()

    def _migrate_token_file(self, token_file: TokenFile) -> TokenFile:
        """
        Migrate old token file format to new format with tenant support.

        Extracts tenant_id from existing JWT tokens and populates tenant_preferences.
        This ensures backwards compatibility with old token files.

        Args:
            token_file: Token file to migrate

        Returns:
            Migrated token file
        """
        migrated = False

        # Ensure tenant_preferences dict exists
        if not hasattr(token_file, 'tenant_preferences') or token_file.tenant_preferences is None:
            token_file.tenant_preferences = {}
            migrated = True

        # Ensure current_tenant_id field exists
        if not hasattr(token_file, 'current_tenant_id'):
            token_file.current_tenant_id = None
            migrated = True

        # Extract tenant_id from existing tokens
        for email, token_storage in token_file.tokens.items():
            # Ensure tenant_id field exists in token_storage
            if not hasattr(token_storage, 'tenant_id') or token_storage.tenant_id is None:
                # Extract from JWT
                tenant_id = self.get_tenant_id_from_token(token_storage.access_token)
                token_storage.tenant_id = tenant_id
                migrated = True

                # Update tenant preference if we found one
                if tenant_id and email not in token_file.tenant_preferences:
                    token_file.tenant_preferences[email] = tenant_id
                    migrated = True

        # Set current_tenant_id if we have a current user
        if token_file.current_user and token_file.current_tenant_id is None:
            tenant_id = token_file.tenant_preferences.get(token_file.current_user)
            if tenant_id:
                token_file.current_tenant_id = tenant_id
                migrated = True

        # Write migrated file back to disk
        if migrated:
            self._write_token_file(token_file)

        return token_file

    def _write_token_file(self, token_file: TokenFile) -> None:
        """Write token file to disk with secure permissions."""
        # Write to temporary file first
        temp_path = self.storage_path.with_suffix(".tmp")

        with open(temp_path, "w") as f:
            json.dump(token_file.model_dump(), f, indent=2, default=str)

        # Set restrictive permissions (owner read/write only)
        os.chmod(temp_path, 0o600)

        # Atomic rename
        temp_path.replace(self.storage_path)

    @staticmethod
    def _is_expired(expires_at: datetime) -> bool:
        """Check if a datetime is in the past."""
        return datetime.now() >= expires_at
