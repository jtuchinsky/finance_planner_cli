# Finance Planner CLI - Commands Reference

> **Complete command reference for finance-cli**
>
> **Version:** 0.1.0
> **Last Updated:** January 2026

## Table of Contents

1. [Authentication Commands](#authentication-commands)
2. [Account Commands](#account-commands)
3. [Transaction Commands](#transaction-commands)
4. [Tenant Commands](#tenant-commands)
5. [Environment Commands](#environment-commands)
6. [Global Options](#global-options)

---

## Authentication Commands

Manage user authentication, login sessions, and tokens.

### `finance-cli auth register`

Register a new user account with MCP_Auth.

**Usage:**
```bash
finance-cli auth register [OPTIONS]
```

**Options:**
- `--email, -e TEXT` - User email address
- `--password, -p TEXT` - User password (hidden input)
- `--username, -u TEXT` - Username
- `--tenant-id, -t INTEGER` - Tenant ID to join (optional, defaults to 1)

**Interactive Mode:**
```bash
finance-cli auth register
# Prompts: Email, Username, Password, Confirm Password
```

**With Flags:**
```bash
finance-cli auth register \
  --email user@example.com \
  --username myuser \
  --password mypassword \
  --tenant-id 1
```

**Output:**
```
✓ User registered: user@example.com
  User ID: 1
  Username: myuser
  Created: 2026-01-09 10:30:00

You can now login with: finance-cli auth login
```

**Notes:**
- Password must be at least 8 characters
- Username is required in multi-tenant mode
- Tenant ID defaults to 1 if not specified

---

### `finance-cli auth login`

Login and obtain JWT authentication token.

**Usage:**
```bash
finance-cli auth login [OPTIONS]
```

**Options:**
- `--email, -e TEXT` - Tenant email (your email for your own tenant)
- `--password, -p TEXT` - Password (hidden input)
- `--no-save` - Don't save token (just print it)

**Interactive Mode:**
```bash
finance-cli auth login
# Prompts: Email, Password
```

**With Flags:**
```bash
finance-cli auth login --email user@example.com --password mypassword
```

**Output:**
```
✓ Logged in as user@example.com
  Token expires in 15 minutes
  Tenant ID: 1

To see all your tenants: finance-cli tenants list

You can now use finance-cli commands
```

**How It Works:**
- First login auto-creates tenant + owner user if tenant doesn't exist
- Subsequent logins authenticate against existing tenant
- JWT token contains tenant_id and role claims
- Token is stored in `~/.config/finance-cli/tokens.json` (mode 0600)

---

### `finance-cli auth logout`

Logout and clear stored authentication tokens.

**Usage:**
```bash
finance-cli auth logout [OPTIONS]
```

**Options:**
- `--email, -e TEXT` - Email to logout (default: current user)

**Examples:**
```bash
# Logout current user
finance-cli auth logout

# Logout specific user
finance-cli auth logout --email other@example.com
```

**Output:**
```
✓ Logged out user@example.com
```

---

### `finance-cli auth whoami`

Display currently authenticated user information and current tenant details.

**Usage:**
```bash
finance-cli auth whoami
```

**Output:**
```
Current user: user@example.com
  User ID: 1
  Active: True
  TOTP Enabled: False
  Created: 2026-01-09 10:30:00

Tenant:
  Name: Family Budget
  ID: 2
  Role: ADMIN
```

**Note:** Tenant information is shown if the backend supports multi-tenant mode and the Finance Planner service is available.

---

### `finance-cli auth list`

List all authenticated users with saved tokens.

**Usage:**
```bash
finance-cli auth list
```

**Output:**
```
Authenticated users:
  ● user@example.com (current)
    other@example.com
```

---

### `finance-cli auth switch`

Switch to a different authenticated user.

**Usage:**
```bash
finance-cli auth switch EMAIL
```

**Arguments:**
- `EMAIL` - Email of user to switch to

**Example:**
```bash
finance-cli auth switch other@example.com
✓ Switched to other@example.com
```

**Notes:**
- User must have a saved token
- Use `finance-cli auth list` to see available users

---

## Account Commands

Manage financial accounts (checking, savings, credit, investment, cash).

### `finance-cli accounts create`

Create a new financial account.

**Usage:**
```bash
finance-cli accounts create [OPTIONS]
```

**Options:**
- `--name, -n TEXT` - Account name
- `--type, -t TEXT` - Account type: checking, savings, credit, investment, cash
- `--balance, -b FLOAT` - Initial balance (optional)

**Interactive Mode:**
```bash
finance-cli accounts create
# Prompts: Name, Type, Initial Balance
```

**With Flags:**
```bash
finance-cli accounts create \
  --name "Chase Checking" \
  --type checking \
  --balance 1000.00
```

**Output:**
```
✓ Account created: Chase Checking
  ID: 1
  Type: checking
  Balance: $1,000.00
```

**Notes:**
- Balance can only be set during creation
- After creation, balance is calculated from transactions
- Requires authentication

---

### `finance-cli accounts list`

List all financial accounts.

**Usage:**
```bash
finance-cli accounts list [OPTIONS]
```

**Options:**
- `--format, -f` - Output format: `table` (default), `json`, or `pretty`
- `--context / --no-context` - Show/hide tenant context panel (default: show)

**Examples:**
```bash
# Table format with tenant context (default)
finance-cli accounts list

# JSON format
finance-cli accounts list --format json

# Hide tenant context
finance-cli accounts list --no-context
```

**Output:**
```
┌───────────────────────────────────┐
│ Tenant: Family Budget (ID: 2)    │
└───────────────────────────────────┘

┏━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ID ┃ Name           ┃ Type      ┃ Balance     ┃
┡━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1  │ Chase Checking │ checking  │ $1,000.00   │
│ 2  │ Savings        │ savings   │ $5,000.00   │
│ 3  │ Amex Gold      │ credit    │ -$250.00    │
└────┴────────────────┴───────────┴─────────────┘
```

**Note:** By default, shows tenant context panel. Use `--no-context` to suppress.

---

### `finance-cli accounts get`

Get details of a specific account.

**Usage:**
```bash
finance-cli accounts get ACCOUNT_ID
```

**Arguments:**
- `ACCOUNT_ID` - Account ID (integer)

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

  Created: 2026-01-09 10:30:00
  Updated: 2026-01-09 10:30:00
```

---

### `finance-cli accounts update`

Update account name or type.

**Usage:**
```bash
finance-cli accounts update ACCOUNT_ID [OPTIONS]
```

**Arguments:**
- `ACCOUNT_ID` - Account ID (integer)

**Options:**
- `--name, -n TEXT` - New account name
- `--type, -t TEXT` - New account type

**Examples:**
```bash
# Update name
finance-cli accounts update 1 --name "Chase Freedom Checking"

# Update type
finance-cli accounts update 1 --type savings

# Update both
finance-cli accounts update 1 --name "Savings Account" --type savings
```

**Output:**
```
✓ Account 1 updated
  Name: Chase Freedom Checking
  Type: checking
  Balance: $1,000.00
```

**Notes:**
- At least one field (name or type) must be provided
- Balance cannot be updated directly

---

### `finance-cli accounts delete`

Delete an account.

**Usage:**
```bash
finance-cli accounts delete ACCOUNT_ID [OPTIONS]
```

**Arguments:**
- `ACCOUNT_ID` - Account ID (integer)

**Options:**
- `--yes, -y` - Skip confirmation prompt

**Examples:**
```bash
# With confirmation
finance-cli accounts delete 1
# Prompts: Are you sure you want to delete account 1 "Chase Checking"? [y/N]:

# Skip confirmation
finance-cli accounts delete 1 --yes
```

**Output:**
```
✓ Account 1 deleted
```

**Warning:**
- Deleting an account also deletes all associated transactions
- This action cannot be undone

---

## Transaction Commands

Manage financial transactions with filtering and batch import.

### `finance-cli transactions create`

Create a new transaction.

**Usage:**
```bash
finance-cli transactions create [OPTIONS]
```

**Options:**
- `--account, -a INTEGER` - Account ID (required)
- `--amount, -m FLOAT` - Amount (required, negative for expenses, positive for income)
- `--date, -d TEXT` - Date (YYYY-MM-DD, 'today', 'yesterday')
- `--category, -c TEXT` - Category (optional)
- `--merchant, -M TEXT` - Merchant (optional)
- `--description, -D TEXT` - Description (optional)
- `--location, -l TEXT` - Location (optional)
- `--tags, -t TEXT` - Tags, comma-separated (optional)
- `--der-category TEXT` - Derived/normalized category (optional)
- `--der-merchant TEXT` - Derived/normalized merchant (optional)

**Interactive Mode:**
```bash
finance-cli transactions create
# Prompts for all fields
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
  -t "coffee,daily" \
  --der-category "food_dining" \
  --der-merchant "starbucks"
```

**Output:**
```
✓ Transaction created: $-50.00 at Starbucks
  ID: 1
  Account: 1
  Date: 2026-01-09
  Category: Food & Dining
  Derived Category: food_dining
  Merchant: Starbucks
  Derived Merchant: starbucks
  Description: Morning coffee
  Location: Downtown Seattle
  Tags: coffee, daily
```

**Amount Convention:**
- **Negative values:** Expenses (money going out)
- **Positive values:** Income (money coming in)
- Zero is not allowed

**Date Helpers:**
- `today` - Current date
- `yesterday` - Previous day
- `YYYY-MM-DD` - Specific date (e.g., 2026-01-09)

---

### `finance-cli transactions list`

List and filter transactions.

**Usage:**
```bash
finance-cli transactions list [OPTIONS]
```

**Options:**
- `--account, -a INTEGER` - Filter by account ID
- `--from TEXT` - Start date (YYYY-MM-DD)
- `--to TEXT` - End date (YYYY-MM-DD)
- `--category, -c TEXT` - Filter by category
- `--merchant, -M TEXT` - Filter by merchant
- `--tags, -t TEXT` - Filter by tags (comma-separated, matches ANY)
- `--limit, -l INTEGER` - Maximum results (default: 100)
- `--offset, -o INTEGER` - Pagination offset (default: 0)
- `--format, -f TEXT` - Output format: table, json, summary (default: table)
- `--context / --no-context` - Show/hide tenant context panel (default: show)

**Examples:**

**All transactions (default table format):**
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

**Filter by account:**
```bash
finance-cli transactions list --account 1
```

**Combine filters:**
```bash
finance-cli transactions list \
  --account 1 \
  --from 2026-01-01 \
  --to 2026-01-31 \
  --category "Food & Dining"
```

**JSON output:**
```bash
finance-cli transactions list --format json
```

**Summary format:**
```bash
finance-cli transactions list --format summary
```

**Pagination:**
```bash
# First page (results 1-50)
finance-cli transactions list --limit 50

# Second page (results 51-100)
finance-cli transactions list --limit 50 --offset 50
```

**Output (Table Format):**
```
┏━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Date       ┃ Merchant  ┃ Derived    ┃  Amount ┃ Category   ┃
┃    ┃            ┃           ┃ Merchant   ┃         ┃            ┃
┡━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 3  │ 2026-01-09 │ Employer  │ -          │ +$1,000 │ Income     │
│ 2  │ 2026-01-09 │ Starbucks │ starbucks  │ -$50.00 │ Food       │
└────┴────────────┴───────────┴────────────┴─────────┴────────────┘
```

**Output (Summary Format):**
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
```

---

### `finance-cli transactions get`

Get details of a specific transaction.

**Usage:**
```bash
finance-cli transactions get TRANSACTION_ID
```

**Arguments:**
- `TRANSACTION_ID` - Transaction ID (integer)

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
  Date: 2026-01-09
  Category: Food & Dining
  Derived Category: food_dining
  Merchant: Starbucks
  Derived Merchant: starbucks
  Description: Morning coffee
  Location: Downtown Seattle
  Tags: coffee, daily

  Created: 2026-01-09 10:30:00
  Updated: 2026-01-09 10:30:00
```

---

### `finance-cli transactions update`

Update transaction fields.

**Usage:**
```bash
finance-cli transactions update TRANSACTION_ID [OPTIONS]
```

**Arguments:**
- `TRANSACTION_ID` - Transaction ID (integer)

**Options:**
- `--account, -a INTEGER` - New account ID
- `--amount, -m FLOAT` - New amount
- `--date, -d TEXT` - New date (YYYY-MM-DD, "today", "yesterday")
- `--category, -c TEXT` - New category
- `--merchant, -M TEXT` - New merchant
- `--description, -D TEXT` - New description
- `--location, -l TEXT` - New location
- `--tags, -t TEXT` - New tags (comma-separated)
- `--der-category TEXT` - New derived category
- `--der-merchant TEXT` - New derived merchant

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

**Update derived fields:**
```bash
finance-cli transactions update 1 \
  --der-category "coffee_shops" \
  --der-merchant "starbucks_premium"
```

**Output:**
```
✓ Transaction 1 updated
  Amount: $-75.00
  Category: Coffee & Snacks
  Merchant: Starbucks Premium
```

**Notes:**
- At least one field must be provided
- Only specified fields are updated (partial updates)

---

### `finance-cli transactions delete`

Delete a transaction.

**Usage:**
```bash
finance-cli transactions delete TRANSACTION_ID [OPTIONS]
```

**Arguments:**
- `TRANSACTION_ID` - Transaction ID (integer)

**Options:**
- `--yes, -y` - Skip confirmation prompt

**Examples:**
```bash
# With confirmation
finance-cli transactions delete 1
# Prompts: Are you sure you want to delete transaction 1? [y/N]:

# Skip confirmation
finance-cli transactions delete 1 --yes
```

**Output:**
```
✓ Transaction 1 deleted
```

---

### `finance-cli transactions batch`

Import multiple transactions from CSV or JSON files.

**Usage:**
```bash
finance-cli transactions batch ACCOUNT_ID FILE_PATH [OPTIONS]
```

**Arguments:**
- `ACCOUNT_ID` - Account ID (integer)
- `FILE_PATH` - Path to CSV or JSON file

**Options:**
- `--format, -f TEXT` - File format: csv or json (default: csv)

**Constraints:**
- Minimum: 1 transaction
- Maximum: 100 transactions per batch
- All transactions use the same account ID
- Atomic operation: all succeed or all fail

**CSV Format:**

Required columns: `amount`, `date`
Optional columns: `category`, `merchant`, `description`, `location`, `tags`

```csv
amount,date,category,merchant,description,tags
-50.00,2026-01-09,Food & Dining,Starbucks,Morning coffee,"coffee,daily"
-30.00,2026-01-09,Transportation,Shell,Gas,"gas,commute"
1000.00,2026-01-09,Income,Employer,Paycheck,"income,salary"
```

**Import CSV:**
```bash
finance-cli transactions batch 1 transactions.csv
```

**JSON Format:**

Required fields: `amount`, `date`
Optional fields: `category`, `merchant`, `description`, `location`, `tags`

```json
[
  {
    "amount": -50.00,
    "date": "2026-01-09",
    "category": "Food & Dining",
    "merchant": "Starbucks",
    "description": "Morning coffee",
    "tags": ["coffee", "daily"]
  },
  {
    "amount": 1000.00,
    "date": "2026-01-09",
    "category": "Income",
    "tags": ["income", "salary"]
  }
]
```

**Import JSON:**
```bash
finance-cli transactions batch 1 transactions.json --format json
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

---

## Tenant Commands

Manage multi-tenant access control and team members.

### `finance-cli tenants show`

Display current tenant information.

**Usage:**
```bash
finance-cli tenants show
```

**Output:**
```
╭─────────────────────────────── Current Tenant ───────────────────────────────╮
│ Name: Company Budget                                                         │
│ ID: 1                                                                        │
│ Created: 2026-01-09 10:00:00                                                 │
│ Updated: 2026-01-09 10:00:00                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

### `finance-cli tenants list`

List all tenants you belong to.

**Usage:**
```bash
finance-cli tenants list
```

**Output:**
```
                Your Tenants
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Name                 ┃ Role   ┃ Status   ┃ Joined    ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ Personal Budget      │ OWNER  │ ★ ACTIVE │ 2026-01-07│
│ 2  │ Family Budget        │ ADMIN  │          │ 2026-01-08│
│ 3  │ Work Team Budget     │ MEMBER │          │ 2026-01-09│
└────┴──────────────────────┴────────┴──────────┴───────────┘

Total tenants: 3
Current tenant ID: 1

To switch tenants: finance-cli tenants switch <id>
```

**Note:** Requires backend support for `GET /api/tenants` endpoint.

---

### `finance-cli tenants switch`

Switch to a different tenant context.

**Usage:**
```bash
finance-cli tenants switch TENANT_ID
```

**Arguments:**
- `TENANT_ID` - Tenant ID to switch to (integer)

**Example:**
```bash
finance-cli tenants switch 2
```

**Output:**
```
✓ Switched to tenant: Family Budget (ID: 2)

Please login again to complete the switch:
  finance-cli auth login

After login, all commands will operate on the new tenant
```

**Important:**
- You must login again after switching
- Validates that you have access to the tenant
- All subsequent commands operate on the new tenant after re-login

**Complete Workflow:**
```bash
# 1. List available tenants
finance-cli tenants list

# 2. Switch to desired tenant
finance-cli tenants switch 2

# 3. Login to activate switch
finance-cli auth login

# 4. Verify switch
finance-cli tenants show

# 5. Now all commands use new tenant
finance-cli accounts list
```

**Note:** Requires backend support for multi-tenant listing and switching.

---

### `finance-cli tenants update`

Update current tenant name.

**Usage:**
```bash
finance-cli tenants update [OPTIONS]
```

**Options:**
- `--name, -n TEXT` - New tenant name (required)

**Example:**
```bash
finance-cli tenants update --name "Family Budget 2026"
```

**Output:**
```
✓ Tenant updated: Family Budget 2026
  ID: 1
  Name: Family Budget 2026
  Updated: 2026-01-09 11:00:00
```

**Note:** Requires OWNER or ADMIN role.

---

### `finance-cli tenants members list`

List all members in your tenant.

**Usage:**
```bash
finance-cli tenants members list
```

**Output:**
```
           Tenant Members
┏━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ User ID ┃ Auth User ID ┃ Role  ┃ Joined    ┃
┡━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ 1       │ user_abc123  │ OWNER │ 2026-01-07│
│ 2  │ 2       │ user_def456  │ ADMIN │ 2026-01-08│
│ 3  │ 3       │ user_ghi789  │ MEMBER│ 2026-01-09│
└────┴─────────┴──────────────┴───────┴───────────┘

Total members: 3
```

**Role Hierarchy:**
- **OWNER** - Full control, manage all members and roles
- **ADMIN** - Invite/remove members (except owner), manage settings
- **MEMBER** - Create/update accounts and transactions
- **VIEWER** - Read-only access

---

### `finance-cli tenants members invite`

Invite a new member to your tenant.

**Usage:**
```bash
finance-cli tenants members invite [OPTIONS]
```

**Options:**
- `--auth-user-id, -u TEXT` - Auth service user ID (required)
- `--role, -r TEXT` - Member role: owner, admin, member, viewer (required)

**Example:**
```bash
finance-cli tenants members invite \
  --auth-user-id user_xyz123 \
  --role member
```

**Output:**
```
✓ Member invited successfully
  User ID: 4
  Auth User ID: user_xyz123
  Role: MEMBER
  Joined: 2026-01-09
```

**Notes:**
- Requires OWNER or ADMIN role
- Only OWNER can invite other OWNER members
- ADMIN cannot invite or manage OWNER members

---

### `finance-cli tenants members set-role`

Change a member's role.

**Usage:**
```bash
finance-cli tenants members set-role USER_ID [OPTIONS]
```

**Arguments:**
- `USER_ID` - User ID (integer)

**Options:**
- `--role, -r TEXT` - New role: owner, admin, member, viewer (required)

**Example:**
```bash
finance-cli tenants members set-role 3 --role admin
```

**Output:**
```
✓ Member role updated
  User ID: 3
  New Role: ADMIN
```

**Restrictions:**
- Requires OWNER or ADMIN role
- Only OWNER can change roles to/from OWNER
- ADMIN cannot modify OWNER members
- Cannot change your own role

---

### `finance-cli tenants members remove`

Remove a member from your tenant.

**Usage:**
```bash
finance-cli tenants members remove USER_ID [OPTIONS]
```

**Arguments:**
- `USER_ID` - User ID (integer)

**Options:**
- `--yes, -y` - Skip confirmation prompt

**Examples:**
```bash
# With confirmation
finance-cli tenants members remove 3
# Prompts: Are you sure you want to remove member 3? [y/N]:

# Skip confirmation
finance-cli tenants members remove 3 --yes
```

**Output:**
```
✓ Member 3 removed from tenant
```

**Restrictions:**
- Requires OWNER or ADMIN role
- ADMIN cannot remove OWNER members
- Cannot remove yourself
- Removing a member does not delete their auth account

---

## Environment Commands

Validate backend service connectivity and configuration.

### `finance-cli env check`

Check backend services and validate configuration.

**Usage:**
```bash
finance-cli env check
```

**Output:**
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

---

### `finance-cli env show`

Display current environment settings.

**Usage:**
```bash
finance-cli env show
```

**Output:**
```
Environment Variables
  MCP_AUTH_URL: http://127.0.0.1:8001
  FINANCE_API_URL: http://127.0.0.1:8000
  TOKEN_FILE: /Users/username/.config/finance-cli/tokens.json
```

---

### `finance-cli env validate-secrets`

Verify SECRET_KEY matches between services.

**Usage:**
```bash
finance-cli env validate-secrets
```

**Output:**
```
✓ SECRET_KEY validation passed
  MCP_Auth: abc123...
  Finance Planner: abc123...
```

---

### `finance-cli env show-paths`

Show detected project paths.

**Usage:**
```bash
finance-cli env show-paths
```

**Output:**
```
Project Paths
  MCP_Auth: ~/PycharmProjects/MCP_Auth
  Finance Planner: ~/PycharmProjects/finance_planner
```

---

## Global Options

Options available for all commands.

### `--help`

Show help message for any command.

**Examples:**
```bash
finance-cli --help                      # Main help
finance-cli auth --help                 # Auth commands help
finance-cli transactions create --help  # Specific command help
```

### `--version`

Show CLI version.

**Usage:**
```bash
finance-cli --version
```

**Output:**
```
finance-cli version 0.1.0
```

---

## Quick Reference

### Common Workflows

**First-time setup:**
```bash
finance-cli auth login                    # Auto-creates tenant
finance-cli accounts create               # Create first account
finance-cli transactions create           # Add transaction
```

**Daily usage:**
```bash
finance-cli transactions create           # Log expense/income
finance-cli accounts list                 # Check balances
finance-cli transactions list --format summary  # View summary
```

**Monthly review:**
```bash
finance-cli transactions list --from 2026-01-01 --to 2026-01-31 --format summary
```

**Import bank statement:**
```bash
finance-cli transactions batch 1 statement.csv
```

### Keyboard Shortcuts

When prompted for input:
- `Ctrl+C` - Cancel operation
- `Enter` - Submit/skip optional field
- `Tab` - Autocomplete (where supported)

### Token Management

Tokens are stored in `~/.config/finance-cli/tokens.json` with permissions 0600.

**Token lifecycle:**
- Access tokens expire after 15 minutes
- Refresh tokens expire after 30 days
- Tokens auto-refresh when expired
- Logout revokes both tokens

---

## Getting Help

**Built-in help:**
```bash
finance-cli --help
finance-cli COMMAND --help
```

**Documentation:**
- Tutorial: `docs/TUTORIAL.md`
- User Manual: `docs/USER_MANUAL.md`
- This Reference: `docs/COMMANDS.md`

**GitHub:**
- Issues: https://github.com/jtuchinsky/finance_planner_cli/issues
- Discussions: https://github.com/jtuchinsky/finance_planner_cli/discussions

---

**Last Updated:** January 9, 2026
**CLI Version:** 0.1.0
**Generated with:** Claude Code