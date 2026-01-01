# Finance Planner CLI

A developer CLI tool for working with the [finance_planner](https://github.com/jtuchinsky/finance_planner) and [MCP_Auth](https://github.com/jtuchinsky/MCP_Auth) microservices.

## Features

- **Authentication Management**: Register, login, and manage JWT tokens automatically
- **Token Auto-Refresh**: Transparently refresh expired tokens
- **Account Operations**: Full CRUD operations for financial accounts
- **Environment Validation**: Check .env files and SECRET_KEY consistency
- **Multi-User Support**: Store and switch between multiple authenticated users
- **Beautiful Output**: Rich terminal formatting with tables and colors

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- MCP_Auth service running on port 8001
- finance_planner service running on port 8000

### Installation

```bash
# Clone the repository
cd /Users/jacobtuchinsky/PycharmProjects/finance_planner_cli

# Install dependencies
uv sync

# Verify installation (using uv run)
uv run finance-cli --help

# Or activate the virtual environment
source .venv/bin/activate
finance-cli --help
```

**Note:** With `uv`, you can either:
- Use `uv run finance-cli <command>` to run without activating
- Or activate the virtual environment: `source .venv/bin/activate` then use `finance-cli` directly

### First-Time Setup

1. **Check environment configuration**:
   ```bash
   finance-cli env check
   finance-cli env validate-secrets
   ```

2. **Register a user**:
   ```bash
   finance-cli auth register
   ```

3. **Login**:
   ```bash
   finance-cli auth login
   ```

4. **Create an account**:
   ```bash
   finance-cli accounts create
   ```

5. **List your accounts**:
   ```bash
   finance-cli accounts list
   ```

## Usage

### Environment Commands

All commands below assume you've either:
- Activated the virtual environment: `source .venv/bin/activate`
- Or prefix each command with `uv run`, e.g., `uv run finance-cli env check`

```bash
# Check if .env files exist in both projects
finance-cli env check

# Validate SECRET_KEY is identical across projects
finance-cli env validate-secrets

# Show detected project paths
finance-cli env show-paths
```

### Authentication Commands

```bash
# Register a new user
finance-cli auth register --email user@example.com

# Login and save token
finance-cli auth login --email user@example.com

# Show current user info
finance-cli auth whoami

# List all authenticated users
finance-cli auth list

# Switch between users
finance-cli auth switch user@example.com

# Logout
finance-cli auth logout
```

### Account Commands

```bash
# Create a new account (interactive)
finance-cli accounts create

# Create with flags
finance-cli accounts create \
  --name "Checking Account" \
  --type checking \
  --balance 1000.00

# List all accounts (table format)
finance-cli accounts list

# List as JSON
finance-cli accounts list --format json

# Get account details
finance-cli accounts get 1

# Update account
finance-cli accounts update 1 --balance 1500.00
finance-cli accounts update 1 --name "New Name" --type savings

# Delete account
finance-cli accounts delete 1
```

## Configuration

The CLI can be configured via environment variables (prefix `CLI_`) or a `.env.cli` file.

### Environment Variables

```bash
# Project paths (auto-detected by default)
export CLI_PROJECTS_ROOT=~/PycharmProjects
export CLI_MCP_AUTH_PATH=/path/to/MCP_Auth
export CLI_FINANCE_PLANNER_PATH=/path/to/finance_planner

# Service URLs
export CLI_MCP_AUTH_URL=http://127.0.0.1:8001
export CLI_FINANCE_PLANNER_URL=http://127.0.0.1:8000

# Development convenience (optional)
export CLI_DEFAULT_EMAIL=dev@example.com
export CLI_DEFAULT_PASSWORD=secret123

# Output preferences
export CLI_OUTPUT_FORMAT=table  # table, json, pretty
export CLI_COLOR_ENABLED=true

# Timeouts (seconds)
export CLI_HTTP_TIMEOUT=30
```

### Token Storage

Tokens are stored securely in `~/.config/finance-cli/tokens.json` with file permissions `0600` (owner read/write only).

Storage format:
```json
{
  "current_user": "user@example.com",
  "tokens": {
    "user@example.com": {
      "access_token": "eyJ...",
      "refresh_token": "...",
      "expires_at": "2025-12-31T14:30:00Z"
    }
  }
}
```

## Development

### Project Structure

```
cli/
├── main.py              # Main Typer app
├── commands/            # CLI command implementations
├── services/            # HTTP clients and business logic
├── config/              # Configuration management
├── models/              # Pydantic schemas
└── utils/               # Utilities (errors, console)
```

### Adding New Commands

1. Create a new file in `cli/commands/`:
   ```python
   import typer
   app = typer.Typer(help="Command group description")

   @app.command()
   def my_command():
       """Command description."""
       pass
   ```

2. Register in `cli/main.py`:
   ```python
   from cli.commands import my_commands
   app.add_typer(my_commands.app, name="mycommands")
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli
```

## Troubleshooting

### Service Not Running

If you see "Service not running" errors:

1. **Start MCP_Auth**:
   ```bash
   cd ~/PycharmProjects/MCP_Auth
   uvicorn main:app --reload --port 8001
   ```

2. **Start Finance Planner**:
   ```bash
   cd ~/PycharmProjects/finance_planner
   uvicorn app.main:app --reload --port 8000
   ```

### Token Expired

Tokens are automatically refreshed when expired. If you see authentication errors:

```bash
finance-cli auth login
```

### SECRET_KEY Mismatch

If `env validate-secrets` fails:

1. Generate a new SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Update both `.env` files with the same key:
   - `~/PycharmProjects/MCP_Auth/.env`
   - `~/PycharmProjects/finance_planner/.env`

### Project Not Found

If projects aren't auto-detected:

```bash
export CLI_MCP_AUTH_PATH=/path/to/MCP_Auth
export CLI_FINANCE_PLANNER_PATH=/path/to/finance_planner
```

## License

This project is part of the Finance Planner ecosystem.

## Related Projects

- [finance_planner](https://github.com/jtuchinsky/finance_planner) - Finance API service
- [MCP_Auth](https://github.com/jtuchinsky/MCP_Auth) - Authentication service
