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
