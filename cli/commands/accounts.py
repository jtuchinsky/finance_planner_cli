"""
Account management commands.

Commands for creating, listing, updating, and deleting financial accounts.
"""
import typer
import json
from typing import Optional
from rich.table import Table

from cli.services.finance_client import FinanceClient
from cli.services.token_manager import TokenManager
from cli.utils.console import console, print_success, print_error, print_warning, print_tenant_context
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    TokenRefreshError,
)

app = typer.Typer(help="Account management commands")


@app.command()
def create(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Account name"),
    account_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Account type: checking, savings, credit_card, investment, loan, other",
    ),
    balance: Optional[float] = typer.Option(None, "--balance", "-b", help="Initial balance"),
):
    """Create a new financial account."""
    # Prompt for missing values
    if not name:
        name = typer.prompt("Account name")

    if not account_type:
        console.print("\nAccount types:")
        console.print("  1. checking")
        console.print("  2. savings")
        console.print("  3. credit_card")
        console.print("  4. investment")
        console.print("  5. loan")
        console.print("  6. other")

        valid_types = ["checking", "savings", "credit_card", "investment", "loan", "other"]
        while True:
            account_type = typer.prompt("Account type")
            if account_type in valid_types:
                break
            print_error(f"Invalid account type. Choose from: {', '.join(valid_types)}")

    if balance is None:
        balance = typer.prompt("Initial balance", type=float, default=0.0)

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        account = client.create_account(
            token=token,
            name=name,
            account_type=account_type,
            balance=balance,
        )

        print_success(f"Account created: {account.name}")
        console.print(f"  ID: {account.id}")
        console.print(f"  Type: {account.account_type}")
        console.print(f"  Balance: ${account.balance:,.2f}")

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
    except TokenRefreshError as e:
        print_error(f"Failed to refresh token: {str(e)}")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command("list")
def list_accounts(
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, pretty",
    ),
    show_context: bool = typer.Option(
        True,
        "--context/--no-context",
        help="Show tenant context",
    ),
):
    """List all accounts for the current user."""
    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()

        # Show tenant context if enabled
        if show_context:
            try:
                tenant = client.get_current_tenant(token)
                print_tenant_context(tenant.name, tenant.id)
            except Exception:
                # Silently skip if tenant fetch fails
                pass

        accounts = client.list_accounts(token)

        if not accounts:
            console.print("No accounts found", style="yellow")
            console.print("\nCreate an account with: finance-cli accounts create")
            raise typer.Exit(0)

        # Output based on format
        if output_format == "json":
            print(json.dumps([acc.model_dump(mode="json") for acc in accounts], indent=2, default=str))
        elif output_format == "table":
            table = Table(title="Your Accounts")
            table.add_column("ID", justify="right", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Type", style="green")
            table.add_column("Balance", justify="right", style="yellow")

            for acc in accounts:
                table.add_row(
                    str(acc.id),
                    acc.name,
                    acc.account_type,
                    f"${acc.balance:,.2f}",
                )

            console.print(table)
        else:  # pretty
            for acc in accounts:
                console.print(
                    f"[cyan]{acc.id}[/cyan] - {acc.name} ({acc.account_type}): [yellow]${acc.balance:,.2f}[/yellow]"
                )

    except ServiceNotRunningError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def get(
    account_id: int = typer.Argument(..., help="Account ID"),
):
    """Get details of a specific account."""
    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        account = client.get_account(token, account_id)

        console.print(f"\n[bold]Account Details[/bold]")
        console.print(f"  ID: {account.id}")
        console.print(f"  Name: {account.name}")
        console.print(f"  Type: {account.account_type}")
        console.print(f"  Balance: ${account.balance:,.2f}")
        console.print(f"  User ID: {account.user_id}")
        console.print(f"  Created: {account.created_at}")
        console.print(f"  Updated: {account.updated_at}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def update(
    account_id: int = typer.Argument(..., help="Account ID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New account name"),
    account_type: Optional[str] = typer.Option(None, "--type", "-t", help="New account type"),
):
    """
    Update an account's name or type.

    Note: Balance cannot be updated directly. It is managed through transactions.
    """
    if not any([name, account_type]):
        print_error("At least one field must be provided to update")
        console.print("\nUsage: finance-cli accounts update <id> --name <name> --type <type>")
        console.print("\nNote: Balance is read-only and calculated from transactions")
        raise typer.Exit(1)

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nLogin with: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        account = client.update_account(
            token=token,
            account_id=account_id,
            name=name,
            account_type=account_type,
        )

        print_success(f"Account {account_id} updated")
        console.print(f"  Name: {account.name}")
        console.print(f"  Type: {account.account_type}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def delete(
    account_id: int = typer.Argument(..., help="Account ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete an account."""
    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete account {account_id}?")
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
        client.delete_account(token, account_id)

        print_success(f"Account {account_id} deleted")

    except ServiceNotRunningError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except AuthenticationError:
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)
