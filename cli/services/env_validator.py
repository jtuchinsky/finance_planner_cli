"""
Environment validation service.

Validates .env files and SECRET_KEY consistency across projects.
"""
from pathlib import Path
from typing import Optional
from dotenv import dotenv_values

from cli.config.paths import get_project_paths
from cli.config.settings import get_settings
from cli.models.schemas import SecretKeyValidation
from cli.utils.errors import EnvironmentError


class EnvValidator:
    """Validates environment configuration across projects."""

    def __init__(self):
        """Initialize environment validator."""
        settings = get_settings()
        self.paths = get_project_paths(
            projects_root=settings.projects_root,
            mcp_auth_path=settings.mcp_auth_path,
            finance_planner_path=settings.finance_planner_path,
        )

    def check_env_files(self) -> dict[str, bool]:
        """
        Check if .env files exist in both projects.

        Returns:
            Dict with project names as keys and existence status as values
        """
        mcp_auth_env = self.paths.mcp_auth / ".env"
        finance_env = self.paths.finance_planner / ".env"

        return {
            "mcp_auth": mcp_auth_env.exists(),
            "finance_planner": finance_env.exists(),
            "mcp_auth_path": str(mcp_auth_env),
            "finance_path": str(finance_env),
        }

    def validate_secret_keys(self) -> SecretKeyValidation:
        """
        Validate SECRET_KEY is identical in both .env files.

        Returns:
            SecretKeyValidation with validation result

        Raises:
            EnvironmentError: If .env files are missing
        """
        mcp_auth_env = self.paths.mcp_auth / ".env"
        finance_env = self.paths.finance_planner / ".env"

        # Check files exist
        if not mcp_auth_env.exists():
            raise EnvironmentError(f"MCP_Auth .env file not found at {mcp_auth_env}")

        if not finance_env.exists():
            raise EnvironmentError(
                f"Finance Planner .env file not found at {finance_env}"
            )

        # Parse .env files
        mcp_auth_vars = dotenv_values(mcp_auth_env)
        finance_vars = dotenv_values(finance_env)

        mcp_auth_key = mcp_auth_vars.get("SECRET_KEY")
        finance_key = finance_vars.get("SECRET_KEY")

        # Check if SECRET_KEY exists
        if not mcp_auth_key:
            raise EnvironmentError("SECRET_KEY not found in MCP_Auth .env file")

        if not finance_key:
            raise EnvironmentError(
                "SECRET_KEY not found in Finance Planner .env file"
            )

        # Validate they match
        if mcp_auth_key == finance_key:
            return SecretKeyValidation(
                is_valid=True,
                secret_key=mcp_auth_key,
                mcp_auth_key=None,  # Don't expose full keys when valid
                finance_key=None,
            )
        else:
            return SecretKeyValidation(
                is_valid=False,
                mcp_auth_key=mcp_auth_key,
                finance_key=finance_key,
            )

    def get_env_var(self, project: str, var_name: str) -> Optional[str]:
        """
        Get environment variable from a project's .env file.

        Args:
            project: "mcp_auth" or "finance_planner"
            var_name: Variable name to retrieve

        Returns:
            Variable value or None if not found
        """
        if project == "mcp_auth":
            env_path = self.paths.mcp_auth / ".env"
        elif project == "finance_planner":
            env_path = self.paths.finance_planner / ".env"
        else:
            raise ValueError(f"Unknown project: {project}")

        if not env_path.exists():
            return None

        env_vars = dotenv_values(env_path)
        return env_vars.get(var_name)
