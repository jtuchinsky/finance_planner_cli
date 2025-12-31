# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finance Planner CLI is a developer tool for working with the finance_planner and MCP_Auth microservices. It automates authentication workflows, token management, and provides convenient commands for API testing.

## Related Projects

This CLI interacts with two sibling projects:
- **MCP_Auth** (`../MCP_Auth/`) - OAuth 2.1 authentication service on port 8001
- **finance_planner** (`../finance_planner/`) - Finance API service on port 8000

Both services must be running for the CLI to function properly.

## Development Setup

This project uses `uv` for package management.

```bash
# Install dependencies
uv sync

# Run CLI
python -m cli.main --help

# Or use the installed command
finance-cli --help
```

## Project Structure

```
cli/
├── main.py                     # Main Typer app and command registration
├── commands/                   # CLI command implementations
│   ├── auth.py                 # Authentication commands (register, login, logout, whoami)
│   ├── accounts.py             # Account CRUD commands
│   └── env.py                  # Environment validation commands
├── services/                   # Business logic and API clients
│   ├── auth_client.py          # MCP_Auth HTTP client
│   ├── finance_client.py       # Finance Planner HTTP client
│   ├── token_manager.py        # JWT token storage and refresh
│   └── env_validator.py        # .env file validation
├── config/                     # Configuration management
│   ├── settings.py             # Pydantic settings (URLs, paths, defaults)
│   └── paths.py                # Auto-detect project locations
├── models/
│   └── schemas.py              # Pydantic models for API data
└── utils/
    ├── errors.py               # Custom exception classes
    └── console.py              # Rich console utilities
```

## Architecture

### CLI Framework
- **Typer**: Command-line framework with automatic help generation
- **Rich**: Beautiful terminal output (tables, colors, formatting)
- **Pydantic**: Data validation and settings management

### Authentication Flow
1. User runs `finance-cli auth register` to create account in MCP_Auth
2. User runs `finance-cli auth login` to get JWT tokens
3. TokenManager stores tokens in `~/.config/finance-cli/tokens.json` (mode 0600)
4. All subsequent commands auto-inject the access token
5. TokenManager auto-refreshes expired tokens using refresh token

### HTTP Clients
- **AuthClient**: Handles all MCP_Auth API calls (register, login, refresh, profile)
- **FinanceClient**: Handles all Finance Planner API calls (accounts CRUD)
- Both clients handle error cases (service not running, auth failures, validation errors)

### Configuration
- Settings loaded from environment variables with `CLI_` prefix
- Optional `.env.cli` file for local overrides
- Auto-detects project paths in `~/PycharmProjects/`
- Can override with `CLI_MCP_AUTH_PATH` and `CLI_FINANCE_PLANNER_PATH`

## Common Commands

```bash
# Environment validation
finance-cli env check                    # Check .env files exist
finance-cli env validate-secrets         # Verify SECRET_KEY matches
finance-cli env show-paths               # Show detected project paths

# Authentication
finance-cli auth register                # Register new user
finance-cli auth login                   # Login and save token
finance-cli auth whoami                  # Show current user
finance-cli auth logout                  # Clear tokens

# Account management
finance-cli accounts create              # Create account (interactive)
finance-cli accounts list                # List all accounts
finance-cli accounts get <id>            # Get account details
finance-cli accounts update <id> --balance 1000
finance-cli accounts delete <id>
```

## Adding Dependencies

Use `uv` to add dependencies:
```bash
uv add package-name
```

Or manually edit `pyproject.toml`:
```toml
dependencies = [
    "new-package>=version"
]
```

Then run `uv sync`.

## Adding New Commands

1. Create new command file in `cli/commands/`
2. Create Typer app: `app = typer.Typer(help="Description")`
3. Add command functions with `@app.command()` decorator
4. Register in `cli/main.py`: `app.add_typer(new_commands.app, name="cmd-name")`

## Testing

Run the CLI locally:
```bash
python -m cli.main <command>
```

Or use the installed command:
```bash
finance-cli <command>
```

## Important Notes

- Token storage uses file permissions 0600 for security
- Tokens auto-refresh when expired (15-minute access token, refresh token available)
- Multiple users supported - CLI stores tokens for each email
- All commands require services to be running (MCP_Auth on 8001, finance_planner on 8000)
- Path auto-detection assumes all projects are in `~/PycharmProjects/`