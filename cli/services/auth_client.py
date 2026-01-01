"""
MCP_Auth HTTP client.

Handles communication with the MCP_Auth authentication service.
"""
import httpx
from typing import Optional

from cli.config.settings import get_settings
from cli.models.schemas import UserResponse, TokenResponse
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    ValidationError as CLIValidationError,
)


class AuthClient:
    """HTTP client for MCP_Auth service."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize auth client.

        Args:
            base_url: MCP_Auth service URL (default: from settings)
        """
        if base_url is None:
            settings = get_settings()
            base_url = settings.mcp_auth_url

        self.base_url = base_url.rstrip("/")
        self.timeout = get_settings().http_timeout

    def register(self, email: str, password: str) -> UserResponse:
        """
        Register a new user.

        Args:
            email: User's email address
            password: User's password

        Returns:
            User data

        Raises:
            ServiceNotRunningError: If MCP_Auth is not running
            CLIValidationError: If input is invalid
            AuthenticationError: If registration fails
        """
        url = f"{self.base_url}/auth/register"
        data = {"email": email, "password": password}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data)

                if response.status_code == 201:
                    return UserResponse(**response.json())
                elif response.status_code == 400:
                    error_detail = response.json().get("detail", "Registration failed")
                    raise AuthenticationError(error_detail)
                elif response.status_code == 422:
                    errors = response.json().get("detail", [])
                    error_msg = self._format_validation_errors(errors)
                    raise CLIValidationError(error_msg)
                else:
                    raise AuthenticationError(
                        f"Registration failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("MCP_Auth", self.base_url) from e

    def login(self, email: str, password: str) -> TokenResponse:
        """
        Login and get JWT tokens.

        Args:
            email: User's email
            password: User's password

        Returns:
            Token data (access_token, refresh_token, etc.)

        Raises:
            ServiceNotRunningError: If MCP_Auth is not running
            AuthenticationError: If credentials are invalid
        """
        url = f"{self.base_url}/auth/login"
        data = {"email": email, "password": password}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data)

                if response.status_code == 200:
                    return TokenResponse(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid email or password")
                elif response.status_code == 403:
                    error_detail = response.json().get("detail", "")
                    if "TOTP" in error_detail:
                        raise AuthenticationError(
                            "This account requires two-factor authentication (TOTP). "
                            "Use the /auth/totp/validate endpoint for TOTP login."
                        )
                    raise AuthenticationError(error_detail)
                else:
                    raise AuthenticationError(
                        f"Login failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("MCP_Auth", self.base_url) from e

    def refresh(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token data

        Raises:
            ServiceNotRunningError: If MCP_Auth is not running
            AuthenticationError: If refresh token is invalid
        """
        url = f"{self.base_url}/auth/refresh"
        data = {"refresh_token": refresh_token}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data)

                if response.status_code == 200:
                    return TokenResponse(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired refresh token")
                else:
                    raise AuthenticationError(
                        f"Token refresh failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("MCP_Auth", self.base_url) from e

    def logout(self, refresh_token: str) -> None:
        """
        Logout (revoke refresh token).

        Args:
            refresh_token: Refresh token to revoke

        Raises:
            ServiceNotRunningError: If MCP_Auth is not running
        """
        url = f"{self.base_url}/auth/logout"
        data = {"refresh_token": refresh_token}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(url, json=data)

                # Logout succeeds even with 401 (already logged out)
                if response.status_code not in [200, 204, 401]:
                    raise AuthenticationError(
                        f"Logout failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("MCP_Auth", self.base_url) from e

    def get_profile(self, access_token: str) -> UserResponse:
        """
        Get current user profile.

        Args:
            access_token: Valid access token

        Returns:
            User data

        Raises:
            ServiceNotRunningError: If MCP_Auth is not running
            AuthenticationError: If token is invalid
        """
        url = f"{self.base_url}/api/protected/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)

                if response.status_code == 200:
                    return UserResponse(**response.json())
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired token")
                else:
                    raise AuthenticationError(
                        f"Get profile failed: {response.status_code} - {response.text}"
                    )

        except httpx.ConnectError as e:
            raise ServiceNotRunningError("MCP_Auth", self.base_url) from e

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
