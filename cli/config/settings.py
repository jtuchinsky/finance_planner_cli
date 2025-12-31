"""
CLI configuration management using Pydantic Settings.

Loads configuration from environment variables and .env.cli file.
"""
from pathlib import Path
from typing import Optional
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CLISettings(BaseSettings):
    """CLI configuration loaded from .env.cli or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.cli",
        env_file_encoding="utf-8",
        env_prefix="CLI_",
        case_sensitive=False,
        extra="ignore",
    )

    # Project paths (auto-detected or configured)
    projects_root: Path = Field(
        default=Path.home() / "PycharmProjects",
        description="Parent directory containing all projects"
    )
    mcp_auth_path: Optional[Path] = Field(
        default=None,
        description="Path to MCP_Auth project (auto-detected if None)"
    )
    finance_planner_path: Optional[Path] = Field(
        default=None,
        description="Path to finance_planner project (auto-detected if None)"
    )

    # Service endpoints
    mcp_auth_url: str = Field(
        default="http://127.0.0.1:8001",
        description="MCP_Auth service URL"
    )
    finance_planner_url: str = Field(
        default="http://127.0.0.1:8000",
        description="Finance Planner service URL"
    )

    # Token storage
    token_storage_path: Path = Field(
        default=Path.home() / ".config" / "finance-cli" / "tokens.json",
        description="Path to token storage file"
    )

    # Default credentials (for development convenience only)
    default_email: Optional[str] = Field(
        default=None,
        description="Default email for login (dev only)"
    )
    default_password: Optional[str] = Field(
        default=None,
        description="Default password for login (dev only)"
    )

    # Output preferences
    output_format: str = Field(
        default="pretty",
        description="Default output format: pretty, json, table"
    )
    color_enabled: bool = Field(
        default=True,
        description="Enable colored output"
    )

    # Timeouts (seconds)
    http_timeout: int = Field(
        default=30,
        ge=1,
        description="HTTP request timeout in seconds"
    )
    service_startup_timeout: int = Field(
        default=10,
        ge=1,
        description="Service startup timeout in seconds"
    )


@lru_cache()
def get_settings() -> CLISettings:
    """
    Get cached CLI settings instance.

    Settings are loaded once and cached for performance.
    """
    return CLISettings()
