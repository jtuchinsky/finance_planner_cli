"""
Project path resolution and validation.

Automatically detects MCP_Auth and finance_planner project locations.
"""
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ProjectPaths:
    """Holds paths to related projects."""

    mcp_auth: Path
    finance_planner: Path
    projects_root: Path


def get_project_paths(
    projects_root: Optional[Path] = None,
    mcp_auth_path: Optional[Path] = None,
    finance_planner_path: Optional[Path] = None,
) -> ProjectPaths:
    """
    Detect or validate project paths.

    Args:
        projects_root: Parent directory containing projects (default: ~/PycharmProjects)
        mcp_auth_path: Explicit path to MCP_Auth (overrides auto-detection)
        finance_planner_path: Explicit path to finance_planner (overrides auto-detection)

    Returns:
        ProjectPaths with resolved paths

    Raises:
        FileNotFoundError: If projects cannot be found
    """
    if projects_root is None:
        projects_root = Path.home() / "PycharmProjects"

    # Use explicit paths if provided, otherwise auto-detect
    if mcp_auth_path is None:
        mcp_auth_path = projects_root / "MCP_Auth"

    if finance_planner_path is None:
        finance_planner_path = projects_root / "finance_planner"

    # Validate paths exist
    if not mcp_auth_path.exists():
        raise FileNotFoundError(
            f"MCP_Auth project not found at {mcp_auth_path}. "
            f"Set CLI_MCP_AUTH_PATH environment variable to override."
        )

    if not finance_planner_path.exists():
        raise FileNotFoundError(
            f"finance_planner project not found at {finance_planner_path}. "
            f"Set CLI_FINANCE_PLANNER_PATH environment variable to override."
        )

    # Additional validation - check for expected files
    _validate_mcp_auth_structure(mcp_auth_path)
    _validate_finance_planner_structure(finance_planner_path)

    return ProjectPaths(
        mcp_auth=mcp_auth_path,
        finance_planner=finance_planner_path,
        projects_root=projects_root,
    )


def _validate_mcp_auth_structure(path: Path) -> None:
    """Validate MCP_Auth project has expected structure."""
    expected_files = ["main.py"]

    for file_name in expected_files:
        if not (path / file_name).exists():
            raise ValueError(
                f"MCP_Auth directory exists but missing {file_name}. "
                f"Is {path} the correct MCP_Auth project?"
            )


def _validate_finance_planner_structure(path: Path) -> None:
    """Validate finance_planner project has expected structure."""
    expected_paths = ["app"]

    for dir_name in expected_paths:
        if not (path / dir_name).exists():
            raise ValueError(
                f"finance_planner directory exists but missing {dir_name}/. "
                f"Is {path} the correct finance_planner project?"
            )
