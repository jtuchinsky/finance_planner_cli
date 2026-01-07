"""
Tenant management commands.

Commands for managing tenants and their members with role-based access control.
"""
import typer
from typing import Optional
from rich.table import Table
from rich.panel import Panel

from cli.services.finance_client import FinanceClient
from cli.services.token_manager import TokenManager
from cli.utils.console import console, print_success, print_error
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundException,
)

app = typer.Typer(help="Tenant management commands")
members_app = typer.Typer(help="Tenant member management commands")

# Register nested command group
app.add_typer(members_app, name="members")


def _get_role_style(role: str) -> str:
    """Get Rich style for role based on hierarchy."""
    role_lower = role.lower()
    if role_lower == "owner":
        return "red bold"
    elif role_lower == "admin":
        return "yellow bold"
    elif role_lower == "member":
        return "green"
    elif role_lower == "viewer":
        return "blue"
    else:
        return "white"


@app.command()
def show():
    """Display current tenant information."""
    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        tenant = client.get_current_tenant(token)

        # Create Rich Panel with tenant info
        info_text = f"""[bold]Name:[/bold] {tenant.name}
[bold]ID:[/bold] {tenant.id}
[bold]Created:[/bold] {tenant.created_at}
[bold]Updated:[/bold] {tenant.updated_at}"""

        panel = Panel(
            info_text,
            title="[bold cyan]Current Tenant[/bold cyan]",
            border_style="cyan"
        )
        console.print(panel)

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except NotFoundException as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def update(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New tenant name"),
):
    """Update current tenant name (OWNER only)."""
    # Prompt for name if not provided
    if not name:
        name = typer.prompt("New tenant name")

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        tenant = client.update_tenant(token, name)

        print_success(f"Tenant updated: {tenant.name}")
        console.print(f"  ID: {tenant.id}")
        console.print(f"  Updated: {tenant.updated_at}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except PermissionDeniedError as e:
        print_error(str(e))
        console.print("\n[yellow]Only OWNER can update tenant name[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@members_app.command("list")
def list_members():
    """List all members of current tenant."""
    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        members = client.list_tenant_members(token)

        if not members:
            console.print("No members found", style="yellow")
            raise typer.Exit(0)

        # Create Rich Table
        table = Table(title="Tenant Members")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("User ID", justify="right", style="cyan")
        table.add_column("Auth User ID", style="magenta")
        table.add_column("Role", style="bold")
        table.add_column("Joined", style="dim")

        for member in members:
            role_style = _get_role_style(member.role)
            table.add_row(
                str(member.id),
                str(member.user_id),
                member.auth_user_id,
                f"[{role_style}]{member.role.upper()}[/{role_style}]",
                str(member.created_at.date()),
            )

        console.print(table)
        console.print(f"\nTotal members: {len(members)}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@members_app.command()
def invite(
    auth_user_id: Optional[str] = typer.Option(None, "--auth-user-id", "-u", help="Auth user ID to invite"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="Role: owner, admin, member, viewer"),
):
    """Invite a new member to the tenant (ADMIN/OWNER only)."""
    # Prompt for auth_user_id if not provided
    if not auth_user_id:
        auth_user_id = typer.prompt("Auth user ID")

    # Prompt for role if not provided
    if not role:
        console.print("\nAvailable roles:")
        console.print("  [red bold]owner[/red bold]  - Full access, can manage all members and roles")
        console.print("  [yellow bold]admin[/yellow bold]  - Can invite/remove members (except owner)")
        console.print("  [green]member[/green] - Can create/update accounts and transactions")
        console.print("  [blue]viewer[/blue]  - Read-only access")

        valid_roles = ["owner", "admin", "member", "viewer"]
        while True:
            role = typer.prompt("Role", type=str).lower()
            if role in valid_roles:
                break
            print_error(f"Invalid role. Choose from: {', '.join(valid_roles)}")

    # Normalize role to lowercase
    role = role.lower()

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        member = client.invite_member(token, auth_user_id, role)

        role_style = _get_role_style(member.role)
        print_success(f"Member invited: {member.auth_user_id}")
        console.print(f"  User ID: {member.user_id}")
        console.print(f"  Role: [{role_style}]{member.role.upper()}[/{role_style}]")
        console.print(f"  Membership ID: {member.id}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except PermissionDeniedError as e:
        print_error(str(e))
        console.print("\n[yellow]Permission requirements:[/yellow]")
        console.print("  - ADMIN can invite as: admin, member, viewer")
        console.print("  - OWNER can invite as: any role")
        raise typer.Exit(1)
    except Exception as e:
        error_msg = str(e)
        print_error(f"Error: {error_msg}")
        if "already a member" in error_msg.lower():
            console.print("\n[yellow]This user is already a member of the tenant[/yellow]")
        raise typer.Exit(1)


@members_app.command("set-role")
def set_role(
    user_id: int = typer.Argument(..., help="User ID of member to update"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="New role: admin, member, viewer"),
):
    """Change a member's role (OWNER only)."""
    # Prompt for role if not provided
    if not role:
        console.print("\nAvailable roles:")
        console.print("  [yellow bold]admin[/yellow bold]  - Can invite/remove members (except owner)")
        console.print("  [green]member[/green] - Can create/update accounts and transactions")
        console.print("  [blue]viewer[/blue]  - Read-only access")
        console.print("\n[dim]Note: Cannot change OWNER role or your own role[/dim]")

        valid_roles = ["admin", "member", "viewer"]
        while True:
            role = typer.prompt("New role", type=str).lower()
            if role in valid_roles:
                break
            print_error(f"Invalid role. Choose from: {', '.join(valid_roles)}")

    # Normalize role to lowercase
    role = role.lower()

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        member = client.update_member_role(token, user_id, role)

        role_style = _get_role_style(member.role)
        print_success(f"Member role updated")
        console.print(f"  User ID: {member.user_id}")
        console.print(f"  Auth User ID: {member.auth_user_id}")
        console.print(f"  New Role: [{role_style}]{member.role.upper()}[/{role_style}]")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except PermissionDeniedError as e:
        print_error(str(e))
        console.print("\n[yellow]Restrictions:[/yellow]")
        console.print("  - Only OWNER can change roles")
        console.print("  - Cannot change OWNER's role")
        console.print("  - Cannot change your own role")
        raise typer.Exit(1)
    except NotFoundException as e:
        print_error(str(e))
        console.print(f"\n[yellow]Member with user_id {user_id} not found[/yellow]")
        console.print("List members with: finance-cli tenants members list")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@members_app.command()
def remove(
    user_id: int = typer.Argument(..., help="User ID of member to remove"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Remove a member from the tenant (ADMIN/OWNER only)."""
    if not yes:
        confirm = typer.confirm(
            f"Are you sure you want to remove member with user_id {user_id}?"
        )
        if not confirm:
            console.print("Cancelled")
            raise typer.Exit(0)

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        result = client.remove_member(token, user_id)

        print_success(f"Member removed")
        console.print(f"  Removed user_id: {result.get('removed_user_id', user_id)}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except PermissionDeniedError as e:
        print_error(str(e))
        console.print("\n[yellow]Restrictions:[/yellow]")
        console.print("  - ADMIN and OWNER can remove members")
        console.print("  - Cannot remove OWNER")
        console.print("  - Cannot remove yourself")
        raise typer.Exit(1)
    except NotFoundException as e:
        print_error(str(e))
        console.print(f"\n[yellow]Member with user_id {user_id} not found[/yellow]")
        console.print("List members with: finance-cli tenants members list")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)
