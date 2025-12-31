"""
Authentication commands.

Commands for user registration, login, logout, and profile management.
"""
import typer
from typing import Optional

from cli.services.auth_client import AuthClient
from cli.services.token_manager import TokenManager
from cli.config.settings import get_settings
from cli.utils.console import console, print_success, print_error, print_warning
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    TokenNotFoundError,
    TokenExpiredError,
)

app = typer.Typer(help="Authentication commands")


@app.command()
def register(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="User email"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="User password", hide_input=True),
):
    """Register a new user with MCP_Auth."""
    # Prompt for missing values
    if not email:
        email = typer.prompt("Email")
    if not password:
        password = typer.prompt("Password", hide_input=True)
        password_confirm = typer.prompt("Confirm password", hide_input=True)

        if password != password_confirm:
            print_error("Passwords do not match")
            raise typer.Exit(1)

    try:
        client = AuthClient()
        user = client.register(email, password)

        print_success(f"User registered: {user.email}")
        console.print(f"  User ID: {user.id}")
        console.print(f"  Created: {user.created_at}")
        console.print("\nYou can now login with: finance-cli auth login")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print(f"\nTo start MCP_Auth:")
        console.print(f"  cd ~/PycharmProjects/MCP_Auth")
        console.print(f"  uvicorn main:app --reload --port 8001")
        raise typer.Exit(1)
    except AuthenticationError as e:
        print_error(f"Registration failed: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def login(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="User email"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="User password", hide_input=True),
    save: bool = typer.Option(True, help="Save token for future use"),
):
    """Login and obtain JWT token."""
    settings = get_settings()

    # Use defaults from config if available
    if not email:
        email = settings.default_email
    if not email:
        email = typer.prompt("Email")

    if not password:
        password = settings.default_password
    if not password:
        password = typer.prompt("Password", hide_input=True)

    try:
        client = AuthClient()
        token_response = client.login(email, password)

        if save:
            token_manager = TokenManager()
            token_manager.save_token(email, token_response)

            print_success(f"Logged in as {email}")
            console.print(f"  Token expires in {token_response.expires_in // 60} minutes")
            console.print("\nYou can now use finance-cli commands")
        else:
            # Just print the token
            console.print(token_response.access_token)

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start MCP_Auth:")
        console.print("  cd ~/PycharmProjects/MCP_Auth")
        console.print("  uvicorn main:app --reload --port 8001")
        raise typer.Exit(1)
    except AuthenticationError as e:
        print_error(f"Login failed: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def logout(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email to logout (default: current user)"),
):
    """Logout and clear stored tokens."""
    try:
        token_manager = TokenManager()
        current_user = token_manager.get_current_user()

        if not current_user and not email:
            print_warning("Not logged in")
            raise typer.Exit(0)

        # Determine which user to logout
        target_email = email or current_user

        # Try to call server logout endpoint
        try:
            token = token_manager.get_current_token(auto_refresh=False)
            if token:
                client = AuthClient()
                client.logout(token)
        except (TokenExpiredError, TokenNotFoundError, Exception):
            # Continue even if server logout fails
            pass

        # Remove local tokens
        token_manager.logout(target_email)
        print_success(f"Logged out {target_email}")

    except Exception as e:
        print_error(f"Logout failed: {str(e)}")
        raise typer.Exit(1)


@app.command()
def whoami():
    """Display currently authenticated user information."""
    try:
        token_manager = TokenManager()
        current_user = token_manager.get_current_user()

        if not current_user:
            console.print("Not logged in", style="yellow")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(0)

        token = token_manager.get_current_token()

        try:
            client = AuthClient()
            user = client.get_profile(token)

            console.print(f"Current user: [green]{user.email}[/green]")
            console.print(f"  User ID: {user.id}")
            console.print(f"  Active: {user.is_active}")
            console.print(f"  TOTP Enabled: {user.is_totp_enabled}")
            console.print(f"  Created: {user.created_at}")

        except AuthenticationError:
            print_warning("Token expired or invalid")
            console.print(f"  Last logged in as: {current_user}")
            console.print("\nPlease login again: finance-cli auth login")
            raise typer.Exit(1)

    except ServiceNotRunningError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def switch(
    email: str = typer.Argument(..., help="Email of user to switch to"),
):
    """Switch to a different authenticated user."""
    try:
        token_manager = TokenManager()
        token_manager.switch_user(email)

        print_success(f"Switched to {email}")

    except TokenNotFoundError:
        print_error(f"No saved token for {email}")
        console.print("\nAvailable users:")
        token_manager = TokenManager()
        users = token_manager.list_users()
        if users:
            for user in users:
                console.print(f"  - {user}")
        else:
            console.print("  (none)")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command("list")
def list_users():
    """List all authenticated users."""
    token_manager = TokenManager()
    users = token_manager.list_users()
    current = token_manager.get_current_user()

    if not users:
        console.print("No authenticated users", style="yellow")
        console.print("\nLogin with: finance-cli auth login")
        raise typer.Exit(0)

    console.print("Authenticated users:")
    for user in users:
        if user == current:
            console.print(f"  [green]● {user}[/green] (current)")
        else:
            console.print(f"    {user}")
