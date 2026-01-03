"""
Main CLI entry point.

Registers all command groups and provides the main Typer app.
"""
import typer
from typing import Optional

from cli.commands import auth, accounts, env, transactions
from cli.utils.console import console

# Create main Typer app
app = typer.Typer(
    name="finance-cli",
    help="Developer CLI for Finance Planner and MCP_Auth services",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(accounts.app, name="accounts", help="Account management commands")
app.add_typer(transactions.app, name="transactions", help="Transaction management commands")
app.add_typer(env.app, name="env", help="Environment configuration management")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print("finance-cli version 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    Finance Planner CLI - Developer tools for MCP_Auth and finance_planner.

    This CLI simplifies development workflows by automating authentication,
    token management, and API operations.

    Examples:
        finance-cli auth login
        finance-cli accounts list
        finance-cli env check
    """
    pass


if __name__ == "__main__":
    app()
