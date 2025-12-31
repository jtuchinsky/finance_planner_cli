"""
Rich console utilities for formatted output.

Provides a shared Rich console instance and helper functions.
"""
from rich.console import Console

# Shared console instance
console = Console()


def print_success(message: str) -> None:
    """Print success message in green with checkmark."""
    console.print(f"✓ {message}", style="green")


def print_error(message: str) -> None:
    """Print error message in red with X mark."""
    console.print(f"✗ {message}", style="red")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"⚠ {message}", style="yellow")


def print_info(message: str) -> None:
    """Print info message in blue."""
    console.print(f"ℹ {message}", style="blue")
