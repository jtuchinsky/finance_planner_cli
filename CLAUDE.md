# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finance Planner CLI is a developer tool for working with the finance_planner and MCP_Auth microservices. It automates authentication workflows, token management, and provides convenient commands for managing accounts, transactions, and multi-tenant access control.

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

# Run CLI (choose one method):

# Method 1: Use uv run (no activation needed)
uv run finance-cli --help

# Method 2: Activate virtual environment first
source .venv/bin/activate
finance-cli --help

# Method 3: Use python -m
uv run python -m cli.main --help
```

## Project Structure

```
cli/
├── main.py                     # Main Typer app and command registration
├── commands/                   # CLI command implementations
│   ├── auth.py                 # Authentication commands (register, login, logout, whoami)
│   ├── accounts.py             # Account CRUD commands
│   ├── transactions.py         # Transaction CRUD + batch import
│   ├── tenants.py              # Tenant & member management with RBAC
│   └── env.py                  # Environment validation commands
├── services/                   # Business logic and API clients
│   ├── auth_client.py          # MCP_Auth HTTP client
│   ├── finance_client.py       # Finance Planner HTTP client (accounts, transactions, tenants)
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
- **FinanceClient**: Handles all Finance Planner API calls (accounts, transactions, tenants)
- Both clients handle error cases (service not running, auth failures, validation errors)

### Multi-Tenancy & RBAC
- Each user belongs to a tenant with a specific role: OWNER, ADMIN, MEMBER, or VIEWER
- Role hierarchy determines permissions:
  - **OWNER**: Full control, manage all members and roles
  - **ADMIN**: Invite/remove members (except owner), manage tenant settings
  - **MEMBER**: Create/update accounts and transactions
  - **VIEWER**: Read-only access
- JWT token includes tenant_id and role claims for authorization

### Transaction Features
- **Derived Fields**: Transactions support both user-entered and derived (cleaned/normalized) versions of category and merchant fields
- **Date Parsing**: Smart date input supporting "today", "yesterday", or ISO format (YYYY-MM-DD)
- **Batch Import**: Atomic batch creation from CSV/JSON files (up to 100 transactions)
- **Filtering**: List transactions by account, date range, category, merchant, or tags
- **Multiple Output Formats**: Table (default), JSON, or summary statistics

### Configuration
- Settings loaded from environment variables with `CLI_` prefix
- Optional `.env.cli` file for local overrides
- Auto-detects project paths in `~/PycharmProjects/`
- Can override with `CLI_MCP_AUTH_PATH` and `CLI_FINANCE_PLANNER_PATH`

## Common Commands

**Note:** All commands below assume you've activated the venv with `source .venv/bin/activate`.
Alternatively, prefix each command with `uv run`.

```bash
# Environment validation
finance-cli env check                    # Check .env files exist
finance-cli env validate-secrets         # Verify SECRET_KEY matches
finance-cli env show-paths               # Show detected project paths

# Authentication
finance-cli auth register                # Register new user
finance-cli auth login                   # Login and save token
finance-cli auth whoami                  # Show current user
finance-cli auth list                    # List all authenticated users
finance-cli auth switch <email>          # Switch between users
finance-cli auth logout                  # Clear tokens

# Account management
finance-cli accounts create              # Create account (interactive)
finance-cli accounts list                # List all accounts
finance-cli accounts get <id>            # Get account details
finance-cli accounts update <id> --balance 1000
finance-cli accounts delete <id>

# Transaction management
finance-cli transactions create --account 1 --amount -50 --date today
finance-cli transactions list --account 1 --from 2025-01-01
finance-cli transactions list --format summary    # Show statistics
finance-cli transactions get <id>
finance-cli transactions update <id> --amount -75 --category "Groceries"
finance-cli transactions delete <id>
finance-cli transactions batch <account_id> <file.csv> --format csv

# Tenant & member management
finance-cli tenants show                 # Show current tenant info
finance-cli tenants list                 # List all tenants you belong to
finance-cli tenants switch <id>          # Switch to different tenant (requires re-login)
finance-cli tenants update --name "New Tenant Name"
finance-cli tenants members list         # List all members
finance-cli tenants members invite --auth-user-id <id> --role member
finance-cli tenants members set-role <user_id> --role admin
finance-cli tenants members remove <user_id>
```

## Multi-Tenant Switching Workflow

When users belong to multiple tenants, they can switch between them:

```bash
# 1. List all tenants you belong to
finance-cli tenants list

# 2. Switch to desired tenant
finance-cli tenants switch <tenant_id>

# 3. Login to activate the tenant switch
finance-cli auth login

# 4. Verify the switch
finance-cli tenants show

# Now all commands operate on the new tenant
finance-cli accounts list
finance-cli transactions list
```

**Important Notes:**
- After switching tenants, you must login again to get a new JWT token with the correct tenant_id claim
- The tenant_id is extracted from the JWT token and stored in TokenStorage
- TokenManager automatically tracks tenant preferences per user
- Old token files (without tenant fields) auto-migrate when read
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

### Nested Command Groups

For nested command structures (like `tenants members list`), create sub-apps and register them:

```python
app = typer.Typer(help="Parent command group")
sub_app = typer.Typer(help="Nested command group")

# Register nested group
app.add_typer(sub_app, name="subcommand")

# Example: cli/commands/tenants.py
# - tenants show/update
# - tenants members list/invite/remove/set-role
```

## Testing

Run the CLI locally:
```bash
python -m cli.main <command>
```

Or use the installed command:
```bash
finance-cli <command>
```

Run tests with pytest:
```bash
pytest
pytest --cov=cli  # With coverage
```

## Batch Import File Formats

### CSV Format

Required columns: `amount`, `date`
Optional columns: `category`, `merchant`, `description`, `location`, `tags`

```csv
amount,date,category,merchant,description,tags
-45.99,2025-01-05,Groceries,Whole Foods,Weekly shopping,"food,grocery"
-12.50,2025-01-06,Coffee,Starbucks,Morning coffee,
100.00,2025-01-07,Income,Freelance,Project payment,"income,work"
```

### JSON Format

```json
[
  {
    "amount": -45.99,
    "date": "2025-01-05",
    "category": "Groceries",
    "merchant": "Whole Foods",
    "description": "Weekly shopping",
    "tags": ["food", "grocery"]
  },
  {
    "amount": 100.00,
    "date": "2025-01-07",
    "category": "Income",
    "tags": ["income", "work"]
  }
]
```

## Important Notes

- Token storage uses file permissions 0600 for security
- Tokens auto-refresh when expired (15-minute access token, refresh token available)
- Multiple users supported - CLI stores tokens for each email
- All commands require services to be running (MCP_Auth on 8001, finance_planner on 8000)
- Path auto-detection assumes all projects are in `~/PycharmProjects/`
- Batch imports are atomic - either all transactions succeed or none are created
- Transaction amounts: negative for expenses, positive for income