"""
Custom exception classes for the CLI.

Provides specific error types for better error handling and user messaging.
"""


class CLIError(Exception):
    """Base exception for all CLI errors."""

    pass


class ServiceNotRunningError(CLIError):
    """Service is not running or unreachable."""

    def __init__(self, service_name: str, url: str):
        self.service_name = service_name
        self.url = url
        super().__init__(f"{service_name} is not running at {url}")


class TokenExpiredError(CLIError):
    """Access token has expired and needs refresh."""

    pass


class TokenRefreshError(CLIError):
    """Failed to refresh access token."""

    pass


class AuthenticationError(CLIError):
    """Authentication failed (invalid credentials)."""

    pass


class ValidationError(CLIError):
    """Input validation failed."""

    pass


class EnvironmentError(CLIError):
    """Environment configuration issue (e.g., missing .env, mismatched SECRET_KEY)."""

    pass


class ProjectNotFoundError(CLIError):
    """Required project directory not found."""

    pass


class TokenNotFoundError(CLIError):
    """No valid token found for current user."""

    pass


class PermissionDeniedError(CLIError):
    """Permission denied (403 Forbidden - insufficient role/privileges)."""

    pass


class NotFoundException(CLIError):
    """Resource not found (404 Not Found)."""

    pass


class TenantNotFoundError(CLIError):
    """Tenant doesn't exist or user doesn't have access."""

    pass


class TenantSwitchError(CLIError):
    """Tenant switch failed."""

    pass
