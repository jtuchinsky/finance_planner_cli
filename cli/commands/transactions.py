"""
Transaction management commands.

Commands for creating, listing, viewing, updating, and deleting transactions.
"""
import typer
import json
from typing import Optional
from datetime import datetime, timedelta

from rich.table import Table

from cli.services.finance_client import FinanceClient
from cli.services.token_manager import TokenManager
from cli.utils.console import console, print_success, print_error, print_warning
from cli.utils.errors import (
    ServiceNotRunningError,
    AuthenticationError,
    TokenRefreshError,
)

app = typer.Typer(help="Transaction management commands")


def parse_date(date_input: str) -> str:
    """
    Convert date input to ISO format (YYYY-MM-DD).

    Supports:
    - "today" -> current date
    - "yesterday" -> yesterday's date
    - ISO format (YYYY-MM-DD) -> validated and returned

    Args:
        date_input: Date string to parse

    Returns:
        ISO formatted date string

    Raises:
        ValueError: If date format is invalid
    """
    date_lower = date_input.lower().strip()

    if date_lower == "today":
        return datetime.now().strftime("%Y-%m-%d")
    elif date_lower == "yesterday":
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        # Validate ISO format
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            return date_input
        except ValueError:
            raise ValueError(
                f"Invalid date format: '{date_input}'. Use YYYY-MM-DD, 'today', or 'yesterday'"
            )


@app.command()
def create(
    account_id: Optional[int] = typer.Option(None, "--account", "-a", help="Account ID"),
    amount: Optional[float] = typer.Option(None, "--amount", "-m", help="Amount (negative for expenses)"),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD, or 'today', 'yesterday')"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category"),
    merchant: Optional[str] = typer.Option(None, "--merchant", "-M", help="Merchant"),
    description: Optional[str] = typer.Option(None, "--description", "-D", help="Description"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Location"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Tags (comma-separated)"),
):
    """Create a new transaction."""
    # Prompt for required fields
    if account_id is None:
        account_id = typer.prompt("Account ID", type=int)

    if amount is None:
        amount = typer.prompt("Amount (negative for expenses, positive for income)", type=float)

    # Validate amount is non-zero
    if amount == 0:
        print_error("Amount cannot be zero")
        raise typer.Exit(1)

    if date is None:
        date = typer.prompt("Date (YYYY-MM-DD, 'today', or 'yesterday')", default="today")

    # Parse and validate date
    try:
        date = parse_date(date)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)

    # Optional prompts (can skip with Enter)
    if category is None:
        category_input = typer.prompt("Category (optional, press Enter to skip)", default="", show_default=False)
        category = category_input if category_input else None

    if merchant is None:
        merchant_input = typer.prompt("Merchant (optional, press Enter to skip)", default="", show_default=False)
        merchant = merchant_input if merchant_input else None

    if description is None:
        description_input = typer.prompt("Description (optional, press Enter to skip)", default="", show_default=False)
        description = description_input if description_input else None

    if location is None:
        location_input = typer.prompt("Location (optional, press Enter to skip)", default="", show_default=False)
        location = location_input if location_input else None

    if tags is None:
        tags_input = typer.prompt("Tags (comma-separated, optional, press Enter to skip)", default="", show_default=False)
        tags = tags_input if tags_input else None

    # Parse tags from comma-separated string to list
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nPlease login first: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        transaction = client.create_transaction(
            token=token,
            account_id=account_id,
            amount=amount,
            date=date,
            category=category,
            merchant=merchant,
            description=description,
            location=location,
            tags=tags_list,
        )

        # Format amount with sign for display
        amount_display = f"${amount:+,.2f}" if amount >= 0 else f"$-{abs(amount):,.2f}"
        merchant_display = f" at {transaction.merchant}" if transaction.merchant else ""
        print_success(f"Transaction created: {amount_display}{merchant_display}")

        console.print(f"  ID: {transaction.id}")
        console.print(f"  Account: {transaction.account_id}")
        console.print(f"  Date: {transaction.date}")

        if transaction.category:
            console.print(f"  Category: {transaction.category}")
        if transaction.merchant:
            console.print(f"  Merchant: {transaction.merchant}")
        if transaction.description:
            console.print(f"  Description: {transaction.description}")
        if transaction.location:
            console.print(f"  Location: {transaction.location}")
        if transaction.tags:
            console.print(f"  Tags: {', '.join(transaction.tags)}")

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uv run uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except (AuthenticationError, TokenRefreshError):
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        raise typer.Exit(1)


@app.command("list")
def list_transactions(
    account_id: Optional[int] = typer.Option(None, "--account", "-a", help="Filter by account ID"),
    start_date: Optional[str] = typer.Option(None, "--from", help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--to", help="End date (YYYY-MM-DD)"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    merchant: Optional[str] = typer.Option(None, "--merchant", "-M", help="Filter by merchant"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of results"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of results to skip"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, summary"),
):
    """List transactions with optional filters."""
    # Validate format
    valid_formats = ["table", "json", "summary"]
    if format not in valid_formats:
        print_error(f"Invalid format: '{format}'. Must be one of: {', '.join(valid_formats)}")
        raise typer.Exit(1)

    # Parse tags from comma-separated string to list
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nPlease login first: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        result = client.list_transactions(
            token=token,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            merchant=merchant,
            tags=tags_list,
            limit=limit,
            offset=offset,
        )

        # Handle empty results
        if not result.transactions:
            print_warning("No transactions found")
            return

        # Output based on format
        if format == "json":
            # JSON output - machine readable
            transactions_data = [t.model_dump(mode='json') for t in result.transactions]
            console.print(json.dumps(transactions_data, indent=2, default=str))

        elif format == "summary":
            # Summary output - statistics view
            _print_summary(result.transactions, start_date, end_date)

        else:  # table (default)
            # Table output - Rich formatted
            _print_table(result.transactions, result.total)

    except ServiceNotRunningError as e:
        print_error(str(e))
        console.print("\nTo start Finance Planner:")
        console.print("  cd ~/PycharmProjects/finance_planner")
        console.print("  uv run uvicorn app.main:app --reload --port 8000")
        raise typer.Exit(1)
    except (AuthenticationError, TokenRefreshError):
        print_error("Authentication failed - token may be expired")
        console.print("\nPlease login again: finance-cli auth login")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        raise typer.Exit(1)


def _print_table(transactions, total):
    """Print transactions in table format."""
    table = Table(title=f"Transactions ({len(transactions)} of {total} total)")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Date", style="magenta")
    table.add_column("Merchant", style="white")
    table.add_column("Derived Merchant", style="dim white")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Category", style="yellow")
    table.add_column("Derived Category", style="dim yellow")

    for txn in transactions:
        # Format amount with color based on sign
        if txn.amount >= 0:
            amount_display = f"[green]+${txn.amount:,.2f}[/green]"
        else:
            amount_display = f"[red]-${abs(txn.amount):,.2f}[/red]"

        table.add_row(
            str(txn.id),
            txn.date,
            txn.merchant or "-",
            txn.der_merchant or "-",
            amount_display,
            txn.category or "-",
            txn.der_category or "-",
        )

    console.print(table)


def _print_summary(transactions, start_date=None, end_date=None):
    """Print transaction summary with statistics."""
    from collections import defaultdict

    console.print("\n[bold]Transaction Summary[/bold]")
    console.print("━" * 40)

    # Calculate date range
    if transactions:
        dates = [txn.date for txn in transactions]
        actual_start = min(dates)
        actual_end = max(dates)
        console.print(f"Date Range: {actual_start} to {actual_end}")

    console.print(f"Total Transactions: {len(transactions)}\n")

    # Calculate financial overview
    total_income = sum(txn.amount for txn in transactions if txn.amount > 0)
    total_expenses = sum(txn.amount for txn in transactions if txn.amount < 0)
    net_change = total_income + total_expenses

    console.print("[bold]Financial Overview:[/bold]")
    console.print(f"  Total Income:    [green]+${total_income:,.2f}[/green]")
    console.print(f"  Total Expenses:  [red]${total_expenses:,.2f}[/red]")

    if net_change >= 0:
        console.print(f"  Net Change:      [green]+${net_change:,.2f}[/green]\n")
    else:
        console.print(f"  Net Change:      [red]${net_change:,.2f}[/red]\n")

    # Calculate top categories
    category_stats = defaultdict(lambda: {"amount": 0, "count": 0})

    for txn in transactions:
        cat = txn.category or "Uncategorized"
        category_stats[cat]["amount"] += txn.amount
        category_stats[cat]["count"] += 1

    # Sort by absolute amount (largest first)
    sorted_categories = sorted(
        category_stats.items(),
        key=lambda x: abs(x[1]["amount"]),
        reverse=True
    )

    if sorted_categories:
        console.print("[bold]Top Categories:[/bold]")
        for i, (category, stats) in enumerate(sorted_categories[:5], 1):
            amount = stats["amount"]
            count = stats["count"]
            amount_display = f"+${amount:,.2f}" if amount >= 0 else f"${amount:,.2f}"

            console.print(f"  {i}. {category:<20} {amount_display:>12} ({count} transaction{'s' if count != 1 else ''})")

    console.print()
