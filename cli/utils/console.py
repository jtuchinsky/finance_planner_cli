"""
Rich console utilities for formatted output.

Provides a shared Rich console instance and helper functions.
"""
from typing import Optional
from rich.console import Console
from rich.panel import Panel

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


def print_tenant_context(tenant_name: str, tenant_id: int, role: Optional[str] = None) -> None:
    """
    Print current tenant context as header panel.

    Args:
        tenant_name: Name of the tenant
        tenant_id: ID of the tenant
        role: Optional user role in the tenant
    """
    info_text = f"[bold cyan]Tenant:[/bold cyan] {tenant_name} [dim](ID: {tenant_id})[/dim]"

    if role:
        # Role colors based on hierarchy
        role_styles = {
            "owner": "red bold",
            "admin": "yellow bold",
            "member": "green",
            "viewer": "blue"
        }
        role_style = role_styles.get(role.lower(), "white")
        info_text += f"\n[bold]Role:[/bold] [{role_style}]{role.upper()}[/{role_style}]"

    panel = Panel(
        info_text,
        border_style="cyan",
        padding=(0, 1)
    )
    console.print(panel)
