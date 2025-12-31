"""
Environment management commands.

Commands for validating environment configuration across projects.
"""
import typer
from rich.table import Table

from cli.services.env_validator import EnvValidator
from cli.config.paths import get_project_paths
from cli.config.settings import get_settings
from cli.utils.console import console, print_success, print_error, print_warning
from cli.utils.errors import EnvironmentError, ProjectNotFoundError

app = typer.Typer(help="Environment configuration management")


@app.command()
def check():
    """Check if .env files exist in both projects."""
    try:
        validator = EnvValidator()
        result = validator.check_env_files()

        console.print("\n[bold]Environment Files Check[/bold]\n")

        # MCP_Auth
        if result["mcp_auth"]:
            print_success(f"MCP_Auth .env found: {result['mcp_auth_path']}")
        else:
            print_error(f"MCP_Auth .env missing: {result['mcp_auth_path']}")
            console.print("  Create from example:", style="yellow")
            console.print(f"    cd {validator.paths.mcp_auth}")
            console.print("    cp .env.example .env")

        # Finance Planner
        if result["finance_planner"]:
            print_success(f"Finance Planner .env found: {result['finance_path']}")
        else:
            print_error(f"Finance Planner .env missing: {result['finance_path']}")
            console.print("  Create from example:", style="yellow")
            console.print(f"    cd {validator.paths.finance_planner}")
            console.print("    cp .env.example .env")

        # Exit with error if any missing
        if not all([result["mcp_auth"], result["finance_planner"]]):
            raise typer.Exit(1)

    except ProjectNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def validate_secrets():
    """Verify SECRET_KEY is identical in both .env files."""
    try:
        validator = EnvValidator()
        result = validator.validate_secret_keys()

        if result.is_valid:
            print_success("SECRET_KEY matches in both projects")
            console.print(f"  Key preview: {result.secret_key[:10]}...{result.secret_key[-10:]}")
        else:
            print_error("SECRET_KEY mismatch detected!")
            console.print("\nKeys do not match:")
            console.print(f"  MCP_Auth:       {result.mcp_auth_key[:30]}...")
            console.print(f"  Finance Planner: {result.finance_key[:30]}...")

            console.print("\n[yellow]To fix this:[/yellow]")
            console.print("1. Choose one SECRET_KEY to use (or generate a new one)")
            console.print("2. Update both .env files with the same SECRET_KEY")
            console.print("\nGenerate a new key:")
            console.print('  python -c "import secrets; print(secrets.token_urlsafe(32))"')

            raise typer.Exit(1)

    except EnvironmentError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except ProjectNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def show_paths():
    """Display detected project paths."""
    try:
        settings = get_settings()
        paths = get_project_paths(
            projects_root=settings.projects_root,
            mcp_auth_path=settings.mcp_auth_path,
            finance_planner_path=settings.finance_planner_path,
        )

        table = Table(title="Detected Project Paths")
        table.add_column("Project", style="cyan")
        table.add_column("Path", style="yellow")
        table.add_column("Status", style="green")

        # MCP_Auth
        mcp_status = "✓ Found" if paths.mcp_auth.exists() else "✗ Not found"
        table.add_row("MCP_Auth", str(paths.mcp_auth), mcp_status)

        # Finance Planner
        finance_status = "✓ Found" if paths.finance_planner.exists() else "✗ Not found"
        table.add_row("Finance Planner", str(paths.finance_planner), finance_status)

        # Projects root
        table.add_row("Projects Root", str(paths.projects_root), "")

        console.print(table)

        console.print("\n[bold]Service URLs[/bold]")
        console.print(f"  MCP_Auth:       {settings.mcp_auth_url}")
        console.print(f"  Finance Planner: {settings.finance_planner_url}")

        console.print("\n[dim]Override paths with environment variables:[/dim]")
        console.print("  CLI_MCP_AUTH_PATH=/path/to/MCP_Auth")
        console.print("  CLI_FINANCE_PLANNER_PATH=/path/to/finance_planner")

    except ProjectNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        raise typer.Exit(1)
