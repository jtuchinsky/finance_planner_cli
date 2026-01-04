"""
Transaction management commands.

Commands for creating, listing, viewing, updating, and deleting transactions.
"""
import typer
import json
import csv
from pathlib import Path
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
    der_category: Optional[str] = typer.Option(None, "--der-category", help="Derived category"),
    der_merchant: Optional[str] = typer.Option(None, "--der-merchant", help="Derived merchant"),
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

    if der_category is None:
        der_category_input = typer.prompt("Derived category (optional, press Enter to skip)", default="", show_default=False)
        der_category = der_category_input if der_category_input else None

    if der_merchant is None:
        der_merchant_input = typer.prompt("Derived merchant (optional, press Enter to skip)", default="", show_default=False)
        der_merchant = der_merchant_input if der_merchant_input else None

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
            der_category=der_category,
            der_merchant=der_merchant,
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
        if transaction.der_category:
            console.print(f"  Derived Category: {transaction.der_category}")
        if transaction.merchant:
            console.print(f"  Merchant: {transaction.merchant}")
        if transaction.der_merchant:
            console.print(f"  Derived Merchant: {transaction.der_merchant}")
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


@app.command("get")
def get_transaction(transaction_id: int):
    """Get detailed information about a specific transaction."""
    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nPlease login first: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        txn = client.get_transaction(token=token, transaction_id=transaction_id)

        # Display transaction details
        console.print("\n[bold]Transaction Details[/bold]\n")

        console.print(f"  ID: {txn.id}")
        console.print(f"  Account ID: {txn.account_id}")

        # Format amount with color
        if txn.amount >= 0:
            amount_display = f"[green]+${txn.amount:,.2f}[/green]"
        else:
            amount_display = f"[red]-${abs(txn.amount):,.2f}[/red]"
        console.print(f"  Amount: {amount_display}")

        console.print(f"  Date: {txn.date}")

        if txn.category:
            console.print(f"  Category: {txn.category}")
        if txn.der_category:
            console.print(f"  Derived Category: {txn.der_category}")

        if txn.merchant:
            console.print(f"  Merchant: {txn.merchant}")
        if txn.der_merchant:
            console.print(f"  Derived Merchant: {txn.der_merchant}")

        if txn.description:
            console.print(f"  Description: {txn.description}")
        if txn.location:
            console.print(f"  Location: {txn.location}")
        if txn.tags:
            console.print(f"  Tags: {', '.join(txn.tags)}")

        console.print(f"\n  Created: {txn.created_at}")
        console.print(f"  Updated: {txn.updated_at}")
        console.print()

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


@app.command("update")
def update_transaction(
    transaction_id: int,
    account_id: Optional[int] = typer.Option(None, "--account", "-a", help="New account ID"),
    amount: Optional[float] = typer.Option(None, "--amount", "-m", help="New amount"),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="New date (YYYY-MM-DD, or 'today', 'yesterday')"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="New category"),
    merchant: Optional[str] = typer.Option(None, "--merchant", "-M", help="New merchant"),
    description: Optional[str] = typer.Option(None, "--description", "-D", help="New description"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="New location"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="New tags (comma-separated)"),
    der_category: Optional[str] = typer.Option(None, "--der-category", help="New derived category"),
    der_merchant: Optional[str] = typer.Option(None, "--der-merchant", help="New derived merchant"),
):
    """Update a transaction's fields."""
    # Check that at least one field is provided
    if all(
        field is None
        for field in [account_id, amount, date, category, merchant, description, location, tags, der_category, der_merchant]
    ):
        print_error("At least one field must be provided to update")
        console.print("\nUse --help to see available fields")
        raise typer.Exit(1)

    # Parse date if provided
    parsed_date = None
    if date is not None:
        try:
            parsed_date = parse_date(date)
        except ValueError as e:
            print_error(str(e))
            raise typer.Exit(1)

    # Parse tags from comma-separated string to list
    tags_list = None
    if tags is not None:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nPlease login first: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        txn = client.update_transaction(
            token=token,
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
            date=parsed_date,
            category=category,
            merchant=merchant,
            description=description,
            location=location,
            tags=tags_list,
            der_category=der_category,
            der_merchant=der_merchant,
        )

        print_success(f"Transaction {transaction_id} updated")

        # Show updated fields
        if account_id is not None:
            console.print(f"  Account: {txn.account_id}")
        if amount is not None:
            amount_display = f"${amount:+,.2f}" if amount >= 0 else f"$-{abs(amount):,.2f}"
            console.print(f"  Amount: {amount_display}")
        if parsed_date is not None:
            console.print(f"  Date: {txn.date}")
        if category is not None:
            console.print(f"  Category: {txn.category}")
        if der_category is not None:
            console.print(f"  Derived Category: {txn.der_category}")
        if merchant is not None:
            console.print(f"  Merchant: {txn.merchant}")
        if der_merchant is not None:
            console.print(f"  Derived Merchant: {txn.der_merchant}")
        if description is not None:
            console.print(f"  Description: {txn.description}")
        if location is not None:
            console.print(f"  Location: {txn.location}")
        if tags_list is not None:
            console.print(f"  Tags: {', '.join(txn.tags) if txn.tags else 'None'}")

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


@app.command("delete")
def delete_transaction(
    transaction_id: int,
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a transaction."""
    # Confirmation prompt unless --yes flag is used
    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete transaction {transaction_id}?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nPlease login first: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        client.delete_transaction(token=token, transaction_id=transaction_id)

        print_success(f"Transaction {transaction_id} deleted")

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


@app.command("batch")
def batch_create(
    account_id: int,
    file_path: str,
    format: str = typer.Option("csv", "--format", "-f", help="File format: csv or json"),
):
    """Create multiple transactions from a CSV or JSON file (atomic operation)."""
    # Validate format
    valid_formats = ["csv", "json"]
    if format not in valid_formats:
        print_error(f"Invalid format: '{format}'. Must be one of: {', '.join(valid_formats)}")
        raise typer.Exit(1)

    # Check if file exists
    file = Path(file_path)
    if not file.exists():
        print_error(f"File not found: {file_path}")
        raise typer.Exit(1)

    # Parse file based on format
    try:
        if format == "csv":
            transactions = _parse_csv_file(file)
        else:  # json
            transactions = _parse_json_file(file)
    except Exception as e:
        print_error(f"Failed to parse {format.upper()} file: {e}")
        raise typer.Exit(1)

    # Validate batch size
    if len(transactions) == 0:
        print_error("No transactions found in file")
        raise typer.Exit(1)
    if len(transactions) > 100:
        print_error(f"Too many transactions ({len(transactions)}). Maximum is 100 per batch.")
        raise typer.Exit(1)

    console.print(f"Found {len(transactions)} transaction(s) to import...")

    try:
        token_manager = TokenManager()
        token = token_manager.get_current_token()

        if not token:
            print_error("Not logged in")
            console.print("\nPlease login first: finance-cli auth login")
            raise typer.Exit(1)

        client = FinanceClient()
        result = client.batch_create_transactions(
            token=token,
            account_id=account_id,
            transactions=transactions,
        )

        print_success(f"Created {result.count} transactions for account {account_id}")
        console.print(f"  Total amount: ${result.total_amount:+,.2f}")
        console.print(f"  New account balance: ${result.account_balance:,.2f}\n")

        console.print("[bold]Transactions:[/bold]")
        for i, txn in enumerate(result.transactions, 1):
            amount_display = f"${txn.amount:+,.2f}" if txn.amount >= 0 else f"$-{abs(txn.amount):,.2f}"
            merchant_display = f" - {txn.merchant}" if txn.merchant else ""
            category_display = f" ({txn.category})" if txn.category else ""
            console.print(f"  {i}. {amount_display}{merchant_display}{category_display}")

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


def _parse_csv_file(file_path: Path) -> list[dict]:
    """
    Parse CSV file with transaction data.

    Expected columns: amount, date, category, merchant, description, location, tags

    Returns:
        List of transaction dictionaries
    """
    transactions = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Validate required columns
        if 'amount' not in reader.fieldnames or 'date' not in reader.fieldnames:
            raise ValueError("CSV must have 'amount' and 'date' columns")

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                txn = {
                    'amount': float(row['amount']),
                    'date': row['date'].strip(),
                }

                # Add optional fields
                if 'category' in row and row['category']:
                    txn['category'] = row['category'].strip()
                if 'merchant' in row and row['merchant']:
                    txn['merchant'] = row['merchant'].strip()
                if 'description' in row and row['description']:
                    txn['description'] = row['description'].strip()
                if 'location' in row and row['location']:
                    txn['location'] = row['location'].strip()
                if 'tags' in row and row['tags']:
                    # Parse comma-separated tags
                    tags_str = row['tags'].strip()
                    if tags_str:
                        txn['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

                transactions.append(txn)

            except ValueError as e:
                raise ValueError(f"Row {row_num}: Invalid amount value '{row.get('amount', '')}'") from e
            except KeyError as e:
                raise ValueError(f"Row {row_num}: Missing required field {e}") from e

    return transactions


def _parse_json_file(file_path: Path) -> list[dict]:
    """
    Parse JSON file with transaction data.

    Expected format: Array of transaction objects with fields:
    - amount (required, number)
    - date (required, string ISO format)
    - category, merchant, description, location (optional, strings)
    - tags (optional, array of strings)

    Returns:
        List of transaction dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of transactions")

    transactions = []

    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Transaction {i}: Must be an object")

        if 'amount' not in item or 'date' not in item:
            raise ValueError(f"Transaction {i}: Missing required fields 'amount' and/or 'date'")

        try:
            txn = {
                'amount': float(item['amount']),
                'date': str(item['date']),
            }

            # Add optional fields if present
            if 'category' in item and item['category']:
                txn['category'] = str(item['category'])
            if 'merchant' in item and item['merchant']:
                txn['merchant'] = str(item['merchant'])
            if 'description' in item and item['description']:
                txn['description'] = str(item['description'])
            if 'location' in item and item['location']:
                txn['location'] = str(item['location'])
            if 'tags' in item and item['tags']:
                if isinstance(item['tags'], list):
                    txn['tags'] = [str(tag) for tag in item['tags']]
                else:
                    raise ValueError(f"Transaction {i}: 'tags' must be an array")

            transactions.append(txn)

        except (ValueError, TypeError) as e:
            raise ValueError(f"Transaction {i}: {e}") from e

    return transactions
