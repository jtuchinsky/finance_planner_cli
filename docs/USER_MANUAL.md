# Finance Planner CLI - User Manual

> **Version:** 0.1.0
> **Last Updated:** January 2026

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Authentication](#authentication)
5. [Account Management](#account-management)
6. [Transaction Management](#transaction-management)
7. [Environment Configuration](#environment-configuration)
8. [Common Workflows](#common-workflows)
9. [Output Formats](#output-formats)
10. [Troubleshooting](#troubleshooting)
11. [Tips & Best Practices](#tips--best-practices)

---

## Introduction

Finance Planner CLI is a command-line interface for managing personal finances. It provides comprehensive tools for:

- **User Authentication** - Secure login with JWT tokens and optional TOTP
- **Account Management** - Create and manage checking, savings, credit, investment, and cash accounts
- **Transaction Tracking** - Full CRUD operations with filtering, categorization, and batch imports
- **Multi-tenant Support** - Isolated data per user with automatic token management

### Prerequisites

- Python 3.11 or higher
- Access to running instances of:
  - MCP_Auth service (default: `http://127.0.0.1:8001`)
  - Finance Planner API (default: `http://127.0.0.1:8000`)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jtuchinsky/finance_planner_cli.git
cd finance_planner_cli
```

### 2. Install with uv (Recommended)

```bash
uv sync
```

### 3. Verify Installation

```bash
finance-cli --version
# Output: finance-cli version 0.1.0
```

### 4. Check Environment Configuration

```bash
finance-cli env check
```

This validates that both backend services are accessible and SECRET_KEY values match.

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Register a new account
finance-cli auth register

# 2. Login
finance-cli auth login

# 3. Create your first account
finance-cli accounts create

# 4. Add a transaction
finance-cli transactions create

# 5. View your transactions
finance-cli transactions list
```

---

## Authentication

### Register

Create a new user account:

```bash
finance-cli auth register
```

**Interactive Prompts:**
- Email address
- Password (minimum 8 characters)
- Password confirmation

**Example:**
```
Email: user@example.com
Password: ********
Confirm Password: ********
✓ Registration successful
✓ Logged in as user@example.com
```

### Login

Authenticate with existing credentials:

```bash
finance-cli auth login
```

**Interactive Prompts:**
- Email address
- Password
- TOTP code (if enabled)

**Example:**
```
Email: user@example.com
Password: ********
✓ Login successful
  User ID: 1
  Email: user@example.com
  TOTP Enabled: No
```

**With Flags:**
```bash
finance-cli auth login --email user@example.com --password mypassword
```

### Logout

Clear stored authentication tokens:

```bash
finance-cli auth logout
```

This removes your access and refresh tokens from local storage.

### Check Login Status

View current authentication status:

```bash
finance-cli auth whoami
```

**Example Output:**
```
Current User

  User ID: 1
  Email: user@example.com
  Active: Yes
  TOTP Enabled: No
  Registered: 2026-01-03 10:30:00
```

### Refresh Token

Manually refresh your access token:

```bash
finance-cli auth refresh
```

**Note:** Token refresh happens automatically when needed. Manual refresh is rarely required.

---

## Account Management

### Create Account

Create a new financial account:

```bash
finance-cli accounts create
```

**Interactive Prompts:**
- Account name
- Account type (checking, savings, credit, investment, cash)
- Initial balance (optional)

**Example:**
```
Account name: Chase Checking
Account type: checking
Initial balance (press Enter to skip): 1000
✓ Account created: Chase Checking
  ID: 1
  Type: checking
  Balance: $1,000.00
```

**With Flags:**
```bash
finance-cli accounts create \
  --name "Chase Checking" \
  --type checking \
  --balance 1000
```

**Account Types:**
- `checking` - Checking account
- `savings` - Savings account
- `credit` - Credit card
- `investment` - Investment/brokerage account
- `cash` - Cash on hand

**Important:** Balance can only be set during creation. After creation, balance is automatically calculated from transactions.

### List Accounts

View all your accounts:

```bash
finance-cli accounts list
```

**Example Output:**
```
┏━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ID ┃ Name           ┃ Type      ┃ Balance     ┃
┡━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1  │ Chase Checking │ checking  │ $1,000.00   │
│ 2  │ Savings        │ savings   │ $5,000.00   │
│ 3  │ Amex Gold      │ credit    │ -$250.00    │
└────┴────────────────┴───────────┴─────────────┘
```

### Get Account Details

View specific account information:

```bash
finance-cli accounts get <account_id>
```

**Example:**
```bash
finance-cli accounts get 1
```

**Output:**
```
Account Details

  ID: 1
  Name: Chase Checking
  Type: checking
  Balance: $1,000.00

  Created: 2026-01-03 10:30:00
  Updated: 2026-01-03 10:30:00
```

### Update Account

Modify account name or type:

```bash
finance-cli accounts update <account_id> [OPTIONS]
```

**Options:**
- `--name, -n` - New account name
- `--type, -t` - New account type

**Examples:**
```bash
# Update name
finance-cli accounts update 1 --name "Chase Freedom Checking"

# Update type
finance-cli accounts update 1 --type savings

# Update both
finance-cli accounts update 1 --name "My Savings" --type savings
```

**Note:** At least one field must be provided. Balance cannot be updated directly.

### Delete Account

Remove an account:

```bash
finance-cli accounts delete <account_id>
```

**With Confirmation:**
```bash
finance-cli accounts delete 1
# Prompts: Are you sure you want to delete account 1 "Chase Checking"? [y/N]:
```

**Skip Confirmation:**
```bash
finance-cli accounts delete 1 --yes
```

**Important:** Deleting an account also deletes all associated transactions. This action cannot be undone.

---

## Transaction Management

### Create Transaction

Add a single transaction:

```bash
finance-cli transactions create
```

**Interactive Prompts:**
- Account ID (required)
- Amount (required, negative for expenses, positive for income)
- Date (required, supports "today", "yesterday", or YYYY-MM-DD)
- Category (optional)
- Merchant (optional)
- Description (optional)
- Location (optional)
- Tags (optional, comma-separated)

**Example:**
```
Account ID: 1
Amount (negative for expenses, positive for income): -50.00
Date (YYYY-MM-DD, 'today', or 'yesterday'): today
Category (optional, press Enter to skip): Food & Dining
Merchant (optional, press Enter to skip): Starbucks
Description (optional, press Enter to skip): Morning coffee
Location (optional, press Enter to skip): Downtown Seattle
Tags (comma-separated, optional, press Enter to skip): coffee,daily

✓ Transaction created: $-50.00 at Starbucks
  ID: 1
  Account: 1
  Date: 2026-01-03
  Category: Food & Dining
  Merchant: Starbucks
  Description: Morning coffee
  Location: Downtown Seattle
  Tags: coffee, daily
```

**With Flags:**
```bash
finance-cli transactions create \
  -a 1 \
  -m -50.00 \
  -d today \
  -c "Food & Dining" \
  -M "Starbucks" \
  -D "Morning coffee" \
  -l "Downtown Seattle" \
  -t "coffee,daily"
```

**Amount Convention:**
- Negative values: Expenses (money going out)
- Positive values: Income (money coming in)
- Zero is not allowed

**Date Helpers:**
- `today` - Current date
- `yesterday` - Previous day
- `YYYY-MM-DD` - Specific date (e.g., 2026-01-03)

### List Transactions

View and filter transactions:

```bash
finance-cli transactions list [OPTIONS]
```

**Options:**
- `--account, -a` - Filter by account ID
- `--from` - Start date (YYYY-MM-DD)
- `--to` - End date (YYYY-MM-DD)
- `--category, -c` - Filter by category
- `--merchant, -M` - Filter by merchant
- `--tags, -t` - Filter by tags (comma-separated, matches ANY)
- `--limit, -l` - Maximum results (default: 100)
- `--offset, -o` - Pagination offset (default: 0)
- `--format, -f` - Output format: `table`, `json`, `summary` (default: table)

**Examples:**

**All transactions (table format):**
```bash
finance-cli transactions list
```

**Filter by date range:**
```bash
finance-cli transactions list --from 2026-01-01 --to 2026-01-31
```

**Filter by category:**
```bash
finance-cli transactions list --category "Food & Dining"
```

**Filter by merchant:**
```bash
finance-cli transactions list --merchant "Starbucks"
```

**Filter by tags:**
```bash
finance-cli transactions list --tags "coffee,daily"
```

**Combine filters:**
```bash
finance-cli transactions list \
  --account 1 \
  --from 2026-01-01 \
  --to 2026-01-31 \
  --category "Food & Dining"
```

**Pagination:**
```bash
# First page (results 1-50)
finance-cli transactions list --limit 50

# Second page (results 51-100)
finance-cli transactions list --limit 50 --offset 50
```

### Output Formats

#### Table Format (Default)

Rich formatted table with color-coded amounts:

```bash
finance-cli transactions list --format table
```

```
┏━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Date       ┃ Merchant  ┃ Derived    ┃  Amount ┃ Category   ┃ Derived    ┃
┃    ┃            ┃           ┃ Merchant   ┃         ┃            ┃ Category   ┃
┡━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 3  │ 2026-01-03 │ Employer  │ -          │ +$1,000 │ Income     │ -          │
│ 2  │ 2026-01-03 │ Starbucks │ -          │ -$50.00 │ Food &     │ -          │
│    │            │           │            │         │ Dining     │            │
└────┴────────────┴───────────┴────────────┴─────────┴────────────┴────────────┘
```

#### JSON Format

Machine-readable JSON array:

```bash
finance-cli transactions list --format json
```

```json
[
  {
    "id": 3,
    "account_id": 1,
    "amount": 1000.0,
    "date": "2026-01-03",
    "category": "Income",
    "merchant": "Employer",
    "description": "Paycheck",
    "tags": ["income", "salary"],
    "der_category": null,
    "der_merchant": null,
    "created_at": "2026-01-03T19:13:07",
    "updated_at": "2026-01-03T19:13:07"
  }
]
```

#### Summary Format

Financial statistics and insights:

```bash
finance-cli transactions list --format summary
```

```
Transaction Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date Range: 2026-01-01 to 2026-01-31
Total Transactions: 125

Financial Overview:
  Total Income:    +$5,250.00
  Total Expenses:  $-3,847.50
  Net Change:      +$1,402.50

Top Categories:
  1. Income                 +$5,250.00 (3 transactions)
  2. Food & Dining            $-850.00 (42 transactions)
  3. Transportation           $-650.00 (18 transactions)
  4. Shopping                 $-420.00 (15 transactions)
  5. Utilities                $-350.00 (6 transactions)
```

### Get Transaction Details

View detailed information about a specific transaction:

```bash
finance-cli transactions get <transaction_id>
```

**Example:**
```bash
finance-cli transactions get 1
```

**Output:**
```
Transaction Details

  ID: 1
  Account ID: 1
  Amount: -$50.00
  Date: 2026-01-03
  Category: Food & Dining
  Merchant: Starbucks
  Description: Morning coffee
  Location: Downtown Seattle
  Tags: coffee, daily

  Created: 2026-01-03 10:30:00
  Updated: 2026-01-03 10:30:00
```

### Update Transaction

Modify transaction fields:

```bash
finance-cli transactions update <transaction_id> [OPTIONS]
```

**Options:**
- `--account, -a` - New account ID
- `--amount, -m` - New amount
- `--date, -d` - New date (YYYY-MM-DD, "today", "yesterday")
- `--category, -c` - New category
- `--merchant, -M` - New merchant
- `--description, -D` - New description
- `--location, -l` - New location
- `--tags, -t` - New tags (comma-separated)

**Examples:**

**Update amount:**
```bash
finance-cli transactions update 1 --amount -75.00
```

**Update category and merchant:**
```bash
finance-cli transactions update 1 \
  --category "Coffee & Snacks" \
  --merchant "Starbucks Premium"
```

**Update tags:**
```bash
finance-cli transactions update 1 --tags "coffee,breakfast,daily"
```

**Output:**
```
✓ Transaction 1 updated
  Amount: $-75.00
  Category: Coffee & Snacks
  Merchant: Starbucks Premium
```

**Important:**
- At least one field must be provided
- Only specified fields are updated (partial updates)
- **Known limitation:** Date field updates may fail with API validation error

### Delete Transaction

Remove a transaction:

```bash
finance-cli transactions delete <transaction_id>
```

**With Confirmation:**
```bash
finance-cli transactions delete 1
# Prompts: Are you sure you want to delete transaction 1? [y/N]:
```

**Skip Confirmation:**
```bash
finance-cli transactions delete 1 --yes
```

**Output:**
```
✓ Transaction 1 deleted
```

### Batch Import

Import multiple transactions from CSV or JSON files:

```bash
finance-cli transactions batch <account_id> <file_path> [OPTIONS]
```

**Options:**
- `--format, -f` - File format: `csv` or `json` (default: csv)

**Constraints:**
- Minimum: 1 transaction
- Maximum: 100 transactions per batch
- All transactions use the same account ID
- Atomic operation: all succeed or all fail

#### CSV Format

**File Structure:**
```csv
amount,date,category,merchant,description,tags
-50.00,2026-01-03,Food & Dining,Starbucks,Morning coffee,"coffee,daily"
-30.00,2026-01-03,Transportation,Shell,Gas,"gas,commute"
1000.00,2026-01-03,Income,Employer,Paycheck,"income,salary"
```

**Required Columns:** `amount`, `date`
**Optional Columns:** `category`, `merchant`, `description`, `location`, `tags`

**Import:**
```bash
finance-cli transactions batch 1 transactions.csv
```

**Output:**
```
Found 3 transaction(s) to import...
✓ Created 3 transactions for account 1
  Total amount: $+920.00
  New account balance: $1,920.00

Transactions:
  1. $-50.00 - Starbucks (Food & Dining)
  2. $-30.00 - Shell (Transportation)
  3. $+1,000.00 - Employer (Income)
```

#### JSON Format

**File Structure:**
```json
[
  {
    "amount": -50.00,
    "date": "2026-01-03",
    "category": "Food & Dining",
    "merchant": "Starbucks",
    "description": "Morning coffee",
    "tags": ["coffee", "daily"]
  },
  {
    "amount": -30.00,
    "date": "2026-01-03",
    "category": "Transportation",
    "merchant": "Shell",
    "description": "Gas",
    "tags": ["gas", "commute"]
  }
]
```

**Required Fields:** `amount`, `date`
**Optional Fields:** `category`, `merchant`, `description`, `location`, `tags`

**Import:**
```bash
finance-cli transactions batch 1 transactions.json --format json
```

---

## Environment Configuration

### Check Environment

Validate backend service connectivity and configuration:

```bash
finance-cli env check
```

**Example Output:**
```
Environment Configuration Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MCP_Auth Service
  URL: http://127.0.0.1:8001
  Status: ✓ Running
  Response: {"status":"healthy"}

Finance Planner Service
  URL: http://127.0.0.1:8000
  Status: ✓ Running
  Response: {"status":"healthy"}

SECRET_KEY Validation
  Status: ✓ Valid
  MCP_Auth: abc123...
  Finance Planner: abc123...

✓ All checks passed
```

**Checks Performed:**
1. MCP_Auth service is running and responding
2. Finance Planner service is running and responding
3. SECRET_KEY values match between services
4. Both services are accessible

### Show Configuration

Display current environment settings:

```bash
finance-cli env show
```

**Example Output:**
```
Environment Variables
  MCP_AUTH_URL: http://127.0.0.1:8001
  FINANCE_API_URL: http://127.0.0.1:8000
  TOKEN_FILE: /Users/username/.finance-cli/tokens.json
```

---

## Common Workflows

### Monthly Budget Review

```bash
# 1. View summary for the month
finance-cli transactions list \
  --from 2026-01-01 \
  --to 2026-01-31 \
  --format summary

# 2. Check specific categories
finance-cli transactions list \
  --from 2026-01-01 \
  --to 2026-01-31 \
  --category "Food & Dining"

# 3. Export to JSON for analysis
finance-cli transactions list \
  --from 2026-01-01 \
  --to 2026-01-31 \
  --format json > january_2026.json
```

### Import Bank Statements

```bash
# 1. Prepare CSV file from bank export
# (Convert bank statement to required format)

# 2. Import transactions
finance-cli transactions batch 1 bank_statement_jan.csv

# 3. Verify import
finance-cli transactions list \
  --from 2026-01-01 \
  --to 2026-01-31
```

### Reconcile Credit Card

```bash
# 1. Create credit card account
finance-cli accounts create \
  --name "Amex Gold" \
  --type credit \
  --balance -250.00

# 2. Add transactions
finance-cli transactions create \
  -a 3 \
  -m -85.00 \
  -d today \
  -c "Shopping" \
  -M "Amazon"

# 3. View current balance
finance-cli accounts get 3
```

### Track Cash Spending

```bash
# 1. Create cash account
finance-cli accounts create \
  --name "Wallet" \
  --type cash \
  --balance 100.00

# 2. Log small purchases
finance-cli transactions create \
  -a 4 \
  -m -5.50 \
  -d today \
  -c "Food & Dining" \
  -M "Coffee Shop"
```

### Generate Tax Report

```bash
# 1. Get all income for the year
finance-cli transactions list \
  --from 2026-01-01 \
  --to 2026-12-31 \
  --category "Income" \
  --format json > income_2026.json

# 2. Get deductible expenses
finance-cli transactions list \
  --from 2026-01-01 \
  --to 2026-12-31 \
  --category "Business" \
  --format json > business_expenses_2026.json
```

---

## Output Formats

### Table Format

**Use Case:** Interactive terminal viewing
**Features:**
- Color-coded amounts (green for income, red for expenses)
- Rich formatting with borders and alignment
- Shows pagination info (e.g., "2 of 10 total")

**Command:**
```bash
finance-cli transactions list --format table
```

### JSON Format

**Use Case:** Programmatic processing, data export
**Features:**
- Machine-readable format
- Complete field data
- Can be piped to other tools (jq, Python scripts, etc.)

**Command:**
```bash
finance-cli transactions list --format json
```

**Processing with jq:**
```bash
# Get total expenses
finance-cli transactions list --format json | \
  jq '[.[] | select(.amount < 0) | .amount] | add'

# Count transactions by category
finance-cli transactions list --format json | \
  jq 'group_by(.category) | map({category: .[0].category, count: length})'
```

### Summary Format

**Use Case:** Financial insights, reporting
**Features:**
- Date range statistics
- Income/expense breakdown
- Net change calculation
- Top 5 categories by spending

**Command:**
```bash
finance-cli transactions list --format summary
```

---

## Troubleshooting

### Authentication Issues

**Problem:** "Not logged in" error

**Solution:**
```bash
# Check login status
finance-cli auth whoami

# Login if needed
finance-cli auth login

# If token is expired, refresh
finance-cli auth refresh
```

---

**Problem:** "Authentication failed - token may be expired"

**Solution:**
```bash
# Login again to get a fresh token
finance-cli auth login
```

---

### Service Connection Issues

**Problem:** "Service not running" error

**Solution:**
```bash
# Check environment configuration
finance-cli env check

# Start MCP_Auth service
cd ~/PycharmProjects/MCP_Auth
uv run uvicorn app.main:app --reload --port 8001

# Start Finance Planner service
cd ~/PycharmProjects/finance_planner
uv run uvicorn app.main:app --reload --port 8000
```

---

**Problem:** "SECRET_KEY mismatch" warning

**Solution:**
Ensure both services use the same SECRET_KEY in their `.env` files:

```bash
# MCP_Auth .env
SECRET_KEY=your_secret_key_here

# finance_planner .env
SECRET_KEY=your_secret_key_here
```

Restart both services after updating.

---

### Validation Errors

**Problem:** "Invalid date format" error

**Solution:**
Use one of these formats:
- `today`
- `yesterday`
- `YYYY-MM-DD` (e.g., `2026-01-03`)

---

**Problem:** "Amount cannot be zero" error

**Solution:**
Transactions must have a non-zero amount. Use negative values for expenses and positive values for income.

---

**Problem:** CSV import fails with "Invalid amount value"

**Solution:**
Check CSV file:
- Ensure amount column contains valid numbers
- Don't include currency symbols ($, €, etc.)
- Use negative sign for expenses
- Example: `-50.00` not `$-50.00`

---

### Data Issues

**Problem:** Account balance doesn't match expected value

**Solution:**
Balance is automatically calculated from transactions. You cannot update balance directly after account creation. If the balance is incorrect:

1. Check all transactions for the account
2. Look for duplicate or missing transactions
3. Verify transaction amounts are correct (sign and value)

---

**Problem:** Transaction not found after creation

**Solution:**
```bash
# Check if transaction was created
finance-cli transactions list --limit 10

# Search by merchant or category
finance-cli transactions list --merchant "Starbucks"
```

---

## Tips & Best Practices

### Security

1. **Protect your credentials:**
   - Never share your password or tokens
   - Use a strong password (minimum 8 characters)
   - Consider enabling TOTP for additional security

2. **Logout when done:**
   ```bash
   finance-cli auth logout
   ```

3. **Token storage:**
   - Tokens are stored in `~/.finance-cli/tokens.json`
   - File permissions are automatically set to 0600 (owner read/write only)
   - Never commit tokens.json to version control

### Data Entry

1. **Use consistent categories:**
   - Standardize category names (e.g., "Food & Dining" not "food", "dining", "restaurants")
   - Use sentence case for readability
   - Create a personal list of categories and stick to it

2. **Tag strategically:**
   - Use tags for filtering across categories
   - Examples: "tax-deductible", "business", "reimbursable", "gift"
   - Keep tags short and lowercase

3. **Add descriptions:**
   - Descriptions help future you remember the transaction
   - Include relevant details (e.g., "Client dinner - Project X")

4. **Use batch import for bank statements:**
   - Export from your bank in CSV format
   - Convert to required format
   - Import in one atomic operation

### Workflow Optimization

1. **Use command aliases:**
   ```bash
   # Add to your .bashrc or .zshrc
   alias ft='finance-cli transactions'
   alias fa='finance-cli accounts'

   # Now you can use:
   ft list
   fa list
   ```

2. **Create template files:**
   ```bash
   # Keep a template CSV for quick imports
   cp transaction_template.csv this_week.csv
   # Edit this_week.csv with your transactions
   finance-cli transactions batch 1 this_week.csv
   ```

3. **Regular backups:**
   ```bash
   # Export all data monthly
   finance-cli transactions list --format json > backup_$(date +%Y%m).json
   ```

4. **Use summary format for reviews:**
   ```bash
   # Weekly spending review
   finance-cli transactions list \
     --from $(date -d '7 days ago' +%Y-%m-%d) \
     --to $(date +%Y-%m-%d) \
     --format summary
   ```

### Account Organization

1. **One account per real-world account:**
   - Don't combine multiple bank accounts into one
   - Keep checking, savings, credit cards separate

2. **Use descriptive names:**
   - "Chase Freedom Checking" instead of "Checking 1"
   - Include bank name for clarity

3. **Set initial balance carefully:**
   - Only set during account creation
   - Match your bank's current balance
   - All future balance changes happen via transactions

### Transaction Management

1. **Regular imports:**
   - Import transactions weekly to avoid large backlogs
   - Review imported transactions for accuracy

2. **Fix errors promptly:**
   - Use update command to correct mistakes
   - Delete and recreate if major changes needed

3. **Archive old data:**
   ```bash
   # Export last year's transactions
   finance-cli transactions list \
     --from 2025-01-01 \
     --to 2025-12-31 \
     --format json > archive_2025.json
   ```

### Performance

1. **Use filters to limit results:**
   ```bash
   # Instead of listing all transactions
   finance-cli transactions list

   # Filter to current month
   finance-cli transactions list --from 2026-01-01 --to 2026-01-31
   ```

2. **Use pagination for large result sets:**
   ```bash
   # Get results in batches
   finance-cli transactions list --limit 50 --offset 0
   finance-cli transactions list --limit 50 --offset 50
   ```

3. **Use summary format for overviews:**
   - Summary format is faster than loading full table
   - Good for checking totals without seeing individual transactions

---

## Getting Help

### Built-in Help

Every command has built-in help:

```bash
# Main help
finance-cli --help

# Command group help
finance-cli transactions --help

# Specific command help
finance-cli transactions create --help
```

### Version Information

```bash
finance-cli --version
```

### Support

- **GitHub Issues:** https://github.com/jtuchinsky/finance_planner_cli/issues
- **Documentation:** See `docs/` directory
- **Tutorial:** See `docs/TUTORIAL.md`

---

## Appendix

### Transaction Amount Convention

| Type | Sign | Example | Meaning |
|------|------|---------|---------|
| Expense | Negative | -50.00 | Money spent |
| Income | Positive | 1000.00 | Money received |
| Transfer Out | Negative | -200.00 | Money moved out |
| Transfer In | Positive | 200.00 | Money moved in |

### Account Types

| Type | Description | Example Use Case |
|------|-------------|------------------|
| `checking` | Checking account | Day-to-day spending |
| `savings` | Savings account | Emergency fund, savings goals |
| `credit` | Credit card | Credit card purchases |
| `investment` | Investment/brokerage | Stocks, bonds, mutual funds |
| `cash` | Cash on hand | Wallet cash, petty cash |

### Date Format Examples

| Input | Result | Notes |
|-------|--------|-------|
| `today` | 2026-01-03 | Current date |
| `yesterday` | 2026-01-02 | Previous day |
| `2026-01-03` | 2026-01-03 | Explicit ISO format |
| `2026-12-25` | 2026-12-25 | Any valid date |

### Reserved Tag Names

Avoid using these tag names as they may be used for future features:
- `system`
- `auto`
- `import`
- `archived`
- `deleted`

### File Paths

- **Tokens:** `~/.finance-cli/tokens.json`
- **Configuration:** Environment variables (MCP_AUTH_URL, FINANCE_API_URL)
- **Import files:** Any readable path on your filesystem

---

**Last Updated:** January 3, 2026
**CLI Version:** 0.1.0
**Generated with:** Claude Code
