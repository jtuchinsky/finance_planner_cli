# Finance Planner Quick Start Tutorial

Get the complete Finance Planner system running in 5-10 minutes.

## What You'll Build

By the end of this tutorial, you'll have:
- ✅ MCP_Auth authentication service running (port 8001)
- ✅ Finance Planner API service running (port 8000)
- ✅ Finance CLI installed and configured
- ✅ A registered user with JWT tokens
- ✅ Created and managed financial accounts
- ✅ Created and tracked transactions
- ✅ Understanding of multi-tenant access control

## Prerequisites

- **Python 3.12+** installed
- **uv** package manager ([install here](https://github.com/astral-sh/uv))
- **Git** for cloning repositories
- **Terminal** with 3 tabs/windows

**Time Required:** 5-10 minutes

---

## Step 1: Clone All Repositories (1 minute)

Open your terminal and clone all three projects:

```bash
cd ~/PycharmProjects

# Clone MCP_Auth
git clone https://github.com/jtuchinsky/MCP_Auth.git

# Clone Finance Planner
git clone https://github.com/jtuchinsky/finance_planner.git

# Clone Finance Planner CLI
git clone https://github.com/jtuchinsky/finance_planner_cli.git
```

**Verify:**
```bash
ls ~/PycharmProjects
# Should show: MCP_Auth  finance_planner  finance_planner_cli
```

---

## Step 2: Set Up MCP_Auth (2 minutes)

### Install Dependencies

```bash
cd ~/PycharmProjects/MCP_Auth
uv sync
```

### Configure Environment

```bash
# Generate and create .env file with SECRET_KEY and DATABASE_URL
python3 << 'PYTHON_SCRIPT'
import secrets
secret_key = secrets.token_urlsafe(32)
with open('.env', 'w') as f:
    f.write(f'SECRET_KEY={secret_key}\n')
    f.write('DATABASE_URL=sqlite:///./auth.db\n')
print(f'✓ Created .env with SECRET_KEY: {secret_key[:10]}...')
PYTHON_SCRIPT
```

### Initialize Database

```bash
# Run migrations (using uv to ensure correct Python environment)
uv run alembic upgrade head
```

**Your `.env` file should now contain:**
- `SECRET_KEY=<generated-key>`
- `DATABASE_URL=sqlite:///./auth.db`

**Verify:**
```bash
cat .env
# Should show SECRET_KEY and DATABASE_URL
```

---

## Step 3: Set Up Finance Planner (2 minutes)

### Install Dependencies

```bash
cd ~/PycharmProjects/finance_planner
uv sync
```

### Configure Environment

**IMPORTANT:** Use the **same SECRET_KEY** from MCP_Auth!

```bash
# Copy SECRET_KEY from MCP_Auth and create .env file
SECRET_KEY=$(grep "^SECRET_KEY=" ~/PycharmProjects/MCP_Auth/.env | cut -d'=' -f2)

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:///./finance.db
EOF
```

**Verify:**
```bash
cat .env
# Should show SECRET_KEY (same as MCP_Auth) and DATABASE_URL
```

### Initialize Database

```bash
# Run migrations (using uv to ensure correct Python environment)
uv run alembic upgrade head
```

**Your `.env` file should contain (and nothing else):**
- `SECRET_KEY=<same-as-mcp-auth>`
- `DATABASE_URL=sqlite:///./finance.db`

**⚠️ Important:** Do NOT add `MCP_AUTH_URL` or any other variables to this .env file!

---

## Step 4: Set Up Finance CLI (1 minute)

```bash
cd ~/PycharmProjects/finance_planner_cli
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

### Verify Installation

```bash
finance-cli --version
# Should output: finance-cli version 0.1.0

finance-cli env show-paths
# Should show both projects detected
```

**Note:** For the rest of this tutorial, we assume the virtual environment is activated.
If you prefer not to activate, prefix all `finance-cli` commands with `uv run`, e.g., `uv run finance-cli env check`.

---

## Step 5: Start Both Services (1 minute)

Open **three terminal tabs/windows**:

### Terminal 1: Start MCP_Auth

```bash
cd ~/PycharmProjects/MCP_Auth
uv run uvicorn main:app --reload --port 8001
```

**Wait for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Terminal 2: Start Finance Planner

```bash
cd ~/PycharmProjects/finance_planner
uv run uvicorn app.main:app --reload --port 8000
```

**Wait for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Terminal 3: Use the CLI

This terminal is for running `finance-cli` commands.

---

## Step 6: Verify Environment (30 seconds)

In **Terminal 3**, run:

```bash
cd ~/PycharmProjects/finance_planner_cli

# Check .env files exist
finance-cli env check

# Verify SECRET_KEY matches
finance-cli env validate-secrets
```

**Expected output:**
```
✓ MCP_Auth .env found: /Users/.../MCP_Auth/.env
✓ Finance Planner .env found: /Users/.../finance_planner/.env

✓ SECRET_KEY matches in both projects
```

---

## Step 7: Register and Login (1 minute)

Still in **Terminal 3**:

### Register a New User

```bash
finance-cli auth register
```

**Prompts:**
```
Email: demo@example.com
Password: ********
Confirm password: ********
```

**Output:**
```
✓ User registered: demo@example.com
  User ID: 1
  Created: 2025-12-31T14:00:00
```

### Login

```bash
finance-cli auth login
```

**Prompts:**
```
Email: demo@example.com
Password: ********
```

**Output:**
```
✓ Logged in as demo@example.com
  Token expires in 15 minutes
```

### Verify Login

```bash
finance-cli auth whoami
```

**Output:**
```
Current user: demo@example.com
  User ID: 1
  Active: True
  TOTP Enabled: False
```

---

## Step 8: Test the API with Account Operations (2 minutes)

### Create Your First Account

```bash
finance-cli accounts create
```

**Prompts:**
```
Account name: Checking Account
Account types:
  1. checking
  2. savings
  3. credit_card
  4. investment
  5. loan
  6. other
Account type: checking
Initial balance: 1000.00
```

**Output:**
```
✓ Account created: Checking Account
  ID: 1
  Type: checking
  Balance: $1,000.00
```

**💡 Important Note:** Balance can only be set when creating an account. Once created, balance is read-only and managed through transactions.

### Create a Savings Account

```bash
finance-cli accounts create \
  --name "Savings Account" \
  --type savings \
  --balance 5000.00
```

**Output:**
```
✓ Account created: Savings Account
  ID: 2
  Type: savings
  Balance: $5,000.00
```

### List All Accounts

```bash
finance-cli accounts list
```

**Output:**
```
                    Your Accounts
┏━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Name             ┃ Type     ┃ Balance   ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│  1 │ Checking Account │ checking │ $1,000.00 │
│  2 │ Savings Account  │ savings  │ $5,000.00 │
└────┴──────────────────┴──────────┴───────────┘
```

### Get Account Details

```bash
finance-cli accounts get 1
```

**Output:**
```
Account Details
  ID: 1
  Name: Checking Account
  Type: checking
  Balance: $1,000.00
  User ID: 1
  Created: 2025-12-31T14:05:00
  Updated: 2025-12-31T14:05:00
```

### Update an Account

You can update an account's **name** or **type** (balance cannot be updated):

```bash
finance-cli accounts update 1 --name "Main Checking"
```

**Output:**
```
✓ Account 1 updated
  Name: Main Checking
  Type: checking
```

**Note:** Balance is read-only after creation and is now managed through transactions.

You can also change the account type:
```bash
finance-cli accounts update 1 --type savings
```

### Delete an Account

```bash
finance-cli accounts delete 2
```

**Prompts:**
```
Are you sure you want to delete account 2? [y/N]: y
```

**Output:**
```
✓ Account 2 deleted
```

---

## Step 9: Work with Transactions (2 minutes)

Now that you have an account, let's add some transactions to track your finances.

### Create a Transaction

```bash
finance-cli transactions create --account 1 --amount -45.99 --date today
```

**Prompts:**
```
Category (optional, press Enter to skip): Groceries
Merchant (optional, press Enter to skip): Whole Foods
Description (optional, press Enter to skip): Weekly shopping
```

**Output:**
```
✓ Transaction created: $-45.99 at Whole Foods
  ID: 1
  Account: 1
  Date: 2025-01-07
  Category: Groceries
  Merchant: Whole Foods
```

**💡 Transaction Amounts:**
- Negative amounts (-45.99) = Expenses
- Positive amounts (+100.00) = Income

### Create More Transactions

```bash
# Coffee purchase
finance-cli transactions create \
  --account 1 \
  --amount -5.50 \
  --date yesterday \
  --category "Coffee" \
  --merchant "Starbucks"

# Income deposit
finance-cli transactions create \
  --account 1 \
  --amount 2500.00 \
  --date 2025-01-01 \
  --category "Income" \
  --merchant "Employer" \
  --description "Salary payment"
```

### List Transactions

```bash
finance-cli transactions list --account 1
```

**Output:**
```
                 Transactions (3 of 3 total)
┏━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Date       ┃ Merchant   ┃ Der. Merchant ┃ Amount     ┃ Category  ┃
┡━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ 2025-01-07 │ Whole F... │ -             │ -$45.99    │ Groceries │
│ 2  │ 2025-01-06 │ Starbucks  │ -             │ -$5.50     │ Coffee    │
│ 3  │ 2025-01-01 │ Employer   │ -             │ +$2,500.00 │ Income    │
└────┴────────────┴────────────┴───────────────┴────────────┴───────────┘
```

### View Transaction Summary

```bash
finance-cli transactions list --account 1 --format summary
```

**Output:**
```
Transaction Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date Range: 2025-01-01 to 2025-01-07
Total Transactions: 3

Financial Overview:
  Total Income:    +$2,500.00
  Total Expenses:  $-51.49
  Net Change:      +$2,448.51

Top Categories:
  1. Income              +$2,500.00 (1 transaction)
  2. Groceries           $-45.99 (1 transaction)
  3. Coffee              $-5.50 (1 transaction)
```

### Batch Import Transactions

Create a CSV file with multiple transactions:

```bash
cat > transactions.csv <<EOF
amount,date,category,merchant,description
-32.50,2025-01-05,Gas,Shell,Fuel
-15.99,2025-01-04,Lunch,Chipotle,Work lunch
-120.00,2025-01-03,Utilities,Electric Co,Monthly bill
EOF
```

Import the transactions:

```bash
finance-cli transactions batch 1 transactions.csv --format csv
```

**Output:**
```
Found 3 transaction(s) to import...
✓ Created 3 transactions for account 1
  Total amount: $-168.49
  New account balance: $3,280.02

Transactions:
  1. $-32.50 - Shell (Gas)
  2. $-15.99 - Chipotle (Lunch)
  3. $-120.00 - Electric Co (Utilities)
```

---

## Step 10: Explore Multi-Tenant Features (2 minutes)

The Finance Planner includes built-in multi-tenancy with role-based access control and seamless tenant switching.

### View Your Current Tenant

```bash
finance-cli tenants show
```

**Output:**
```
┌─ Current Tenant ──────────────────────────┐
│ Name: demo@example.com's Tenant           │
│ ID: 1                                     │
│ Created: 2025-01-07T10:00:00             │
│ Updated: 2025-01-07T10:00:00             │
└───────────────────────────────────────────┘
```

### List All Your Tenants

See all tenants you belong to and your role in each:

```bash
finance-cli tenants list
```

**Output:**
```
                Your Tenants
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Name                 ┃ Role   ┃ Status   ┃ Joined    ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ Personal Budget      │ OWNER  │ ★ ACTIVE │ 2025-01-07│
│ 2  │ Family Budget        │ ADMIN  │          │ 2025-01-08│
│ 3  │ Work Team Budget     │ MEMBER │          │ 2025-01-09│
└────┴──────────────────────┴────────┴──────────┴───────────┘

Total tenants: 3
Current tenant ID: 1
```

**Note:** The active tenant is marked with a ★ symbol.

### Switch Between Tenants

When you belong to multiple tenants, you can switch between them:

```bash
# Switch to Family Budget (tenant ID 2)
finance-cli tenants switch 2
```

**Output:**
```
✓ Switched to tenant: Family Budget (ID: 2)

Please login again to complete the switch:
  finance-cli auth login

After login, all commands will operate on the new tenant
```

**Important:** After switching tenants, you must login again to get a new JWT token with the correct tenant context:

```bash
finance-cli auth login
```

Now all your commands (accounts, transactions, etc.) will operate on the Family Budget tenant.

**To verify the switch:**
```bash
finance-cli tenants show  # Shows "Family Budget" as current tenant
```

### List Tenant Members

```bash
finance-cli tenants members list
```

**Output:**
```
           Tenant Members
┏━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ User ID ┃ Auth User ID ┃ Role  ┃ Joined    ┃
┡━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│ 1  │ 1       │ user_123...  │ OWNER │ 2025-01-07│
└────┴─────────┴──────────────┴───────┴───────────┘

Total members: 1
```

**Role Hierarchy:**
- **OWNER** - Full control, manage all members and roles
- **ADMIN** - Invite/remove members (except owner), manage tenant settings
- **MEMBER** - Create/update accounts and transactions
- **VIEWER** - Read-only access

### Invite a Team Member (requires another registered user)

```bash
# First, register another user in Terminal 3
finance-cli auth register

# Then invite them to your tenant
finance-cli tenants members invite \
  --auth-user-id <their-auth-user-id> \
  --role member
```

### Tenant Context in Commands

When listing accounts or transactions, the CLI automatically shows which tenant you're operating on:

```bash
finance-cli accounts list
```

**Output:**
```
┌───────────────────────────────────┐
│ Tenant: Family Budget (ID: 2)    │
└───────────────────────────────────┘

             Your Accounts
┏━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID ┃ Name         ┃ Type     ┃ Balance  ┃
...
```

This helps you confirm which tenant context you're working in. You can suppress this display with the `--no-context` flag:

```bash
finance-cli accounts list --no-context    # Hide tenant context
finance-cli transactions list --no-context
```

### Check Your Tenant Details

Use the `whoami` command to see both user and tenant information:

```bash
finance-cli auth whoami
```

**Output:**
```
Current user: demo@example.com
  User ID: 1
  Active: True
  TOTP Enabled: False
  Created: 2025-01-07 10:00:00

Tenant:
  Name: Family Budget
  ID: 2
  Role: ADMIN
```

### Multi-Tenant Workflow Example

```bash
# 1. List your tenants
finance-cli tenants list

# 2. Switch to work tenant
finance-cli tenants switch 3

# 3. Login to activate the switch (shows tenant ID after login)
finance-cli auth login
# Output includes: "Tenant ID: 3"

# 4. Verify the switch
finance-cli auth whoami  # Shows tenant name, ID, and role

# 5. Now all commands operate on the work tenant
finance-cli accounts list          # Shows "Tenant: Work Team Budget (ID: 3)" panel
finance-cli transactions list      # Shows work transactions with tenant context

# 6. Switch back to personal tenant
finance-cli tenants switch 1
finance-cli auth login

# 7. Verify you're back on personal tenant
finance-cli tenants show
```

---

## Step 11: Test Direct API Access (Optional)

You can also test the APIs directly with curl:

### Check API Health

```bash
curl http://127.0.0.1:8000/health
```

**Output:**
```json
{
  "status": "healthy",
  "service": "Finance Planner API"
}
```

### Get JWT Token

```bash
# Login via MCP_Auth
curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "your-password"
  }'
```

**Save the access_token from response, then:**

### List Accounts via API

```bash
TOKEN="<your-access-token>"

curl http://127.0.0.1:8000/api/accounts \
  -H "Authorization: Bearer $TOKEN"
```

### Create Account via API

```bash
curl -X POST http://127.0.0.1:8000/api/accounts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Credit Card",
    "account_type": "credit",
    "balance": 0.00
  }'
```

---

## Step 12: Explore API Documentation (Optional)

Both services provide interactive API documentation:

### MCP_Auth API Docs
- **Swagger UI:** http://127.0.0.1:8001/docs
- **ReDoc:** http://127.0.0.1:8001/redoc

### Finance Planner API Docs
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Open these in your browser to explore all available endpoints.

---

## 🎉 Congratulations!

You now have a fully functional Finance Planner system:

✅ **MCP_Auth** - Handling authentication and JWT tokens
✅ **Finance Planner** - Managing financial accounts
✅ **Finance CLI** - Convenient developer tools

### What You've Learned

1. How to set up and configure both microservices
2. How to ensure SECRET_KEY consistency across services
3. How to use the Finance CLI for development
4. How to create, list, update, and delete accounts
5. How to create and track transactions with filtering and summaries
6. How to batch import transactions from CSV/JSON files
7. How to work with multi-tenant features and role-based access control
8. How to access the APIs directly

---

## Next Steps

### Add More Accounts

```bash
finance-cli accounts create --name "Investment Account" --type investment --balance 10000
finance-cli accounts create --name "Credit Card" --type credit_card --balance 0
finance-cli accounts create --name "Personal Loan" --type loan --balance 5000
```

**Valid account types:** `checking`, `savings`, `credit_card`, `investment`, `loan`, `other`

### Track More Transactions

```bash
# Add expenses
finance-cli transactions create --account 1 --amount -89.99 --date 2025-01-10 --category "Shopping" --merchant "Amazon"

# Add income
finance-cli transactions create --account 1 --amount 500.00 --date 2025-01-15 --category "Income" --description "Freelance payment"

# Filter transactions by date range
finance-cli transactions list --account 1 --from 2025-01-01 --to 2025-01-15

# View spending by category
finance-cli transactions list --account 1 --format summary
```

### Explore More CLI Features

```bash
# Switch between multiple users
finance-cli auth register  # Create another user
finance-cli auth switch user2@example.com
finance-cli auth list      # See all logged-in users

# Export data as JSON
finance-cli accounts list --format json > accounts.json
finance-cli transactions list --account 1 --format json > transactions.json
```

### Test Token Refresh

Wait 15 minutes for your token to expire, then run:
```bash
finance-cli accounts list
# Token will auto-refresh transparently
```

---

## Troubleshooting

### Alembic Migration Error: "Extra inputs are not permitted"

**Error:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
MCP_AUTH_URL
  Extra inputs are not permitted [type=extra_forbidden]
```

**Cause:** Your finance_planner `.env` file contains extra variables not expected by the Settings model.

**Fix:**
```bash
cd ~/PycharmProjects/finance_planner

# Recreate .env with only required variables
SECRET_KEY=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2)

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:///./finance.db
EOF

# Verify
cat .env

# Run migration again
uv run alembic upgrade head
```

**Remember:** The finance_planner `.env` should ONLY contain `SECRET_KEY` and `DATABASE_URL`.

### Service Not Running

**Error:** `✗ MCP_Auth is not running at http://127.0.0.1:8001`

**Fix:** Make sure Terminal 1 is running MCP_Auth:
```bash
cd ~/PycharmProjects/MCP_Auth
uv run uvicorn main:app --reload --port 8001
```

### SECRET_KEY Mismatch

**Error:** `✗ SECRET_KEY mismatch detected!`

**Fix:** Copy SECRET_KEY from MCP_Auth to Finance Planner:
```bash
cd ~/PycharmProjects/finance_planner
SECRET_KEY=$(grep "^SECRET_KEY=" ~/PycharmProjects/MCP_Auth/.env | cut -d'=' -f2)

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:///./finance.db
EOF

# Verify it worked
finance-cli env validate-secrets
```

### Invalid Account Type Error

**Error:** `Validation errors: account_type: Input should be 'checking', 'savings', 'credit_card', 'investment', 'loan' or 'other'`

**Cause:** Using an invalid account type like `credit` or `cash`.

**Fix:** Use one of the valid account types:
```bash
# Valid types
finance-cli accounts create --name "Credit Card" --type credit_card --balance 0
finance-cli accounts create --name "Savings" --type savings --balance 5000

# Valid types: checking, savings, credit_card, investment, loan, other
```

### Balance Update Not Supported

**Error:** `No such option: --balance`

**Cause:** Trying to update account balance, which is read-only after creation.

**Explanation:**
Balance can only be set when creating an account. After creation, balance is read-only and is managed through transactions.

**What you can do:**
```bash
# ✓ Set balance on creation
finance-cli accounts create --name "Savings" --type savings --balance 5000

# ✓ Update name or type
finance-cli accounts update 1 --name "Emergency Fund"
finance-cli accounts update 1 --type checking

# ✗ Cannot update balance after creation (use transactions instead)
# finance-cli accounts update 1 --balance 10000  # This won't work

# ✓ Manage balance through transactions
finance-cli transactions create --account 1 --amount -50 --date today  # Decrease balance
finance-cli transactions create --account 1 --amount 100 --date today  # Increase balance
```

### Token Expired

**Error:** `✗ Authentication failed - token may be expired`

**Fix:** Just login again:
```bash
finance-cli auth login
```

### Port Already in Use

**Error:** `OSError: [Errno 48] Address already in use`

**Fix:** Kill the process using the port:
```bash
lsof -ti:8001 | xargs kill -9  # For MCP_Auth
lsof -ti:8000 | xargs kill -9  # For Finance Planner
```

### Database Migration Errors

**Fix:** Reset the database:
```bash
cd ~/PycharmProjects/MCP_Auth  # or finance_planner
rm auth.db  # or finance.db
uv run alembic upgrade head
```

---

## Quick Reference Commands

**Note:** All `finance-cli` commands assume you've activated the virtual environment (`source .venv/bin/activate`) or prefix with `uv run`.

```bash
# Environment
finance-cli env check
finance-cli env validate-secrets
finance-cli env show-paths

# Authentication
finance-cli auth register
finance-cli auth login
finance-cli auth whoami
finance-cli auth logout

# Accounts
finance-cli accounts create                          # Interactive prompts
finance-cli accounts create --name "Account" --type checking --balance 1000
finance-cli accounts list                            # Table format
finance-cli accounts list --format json              # JSON output
finance-cli accounts get <id>
finance-cli accounts update <id> --name "New Name"   # Update name
finance-cli accounts update <id> --type savings      # Update type
finance-cli accounts delete <id>

# Transactions
finance-cli transactions create --account <id> --amount <amount> --date today
finance-cli transactions list --account <id>
finance-cli transactions list --account <id> --format summary
finance-cli transactions get <id>
finance-cli transactions update <id> --amount <new_amount>
finance-cli transactions delete <id>
finance-cli transactions batch <account_id> file.csv --format csv

# Tenants
finance-cli tenants show
finance-cli tenants update --name "New Name"
finance-cli tenants members list
finance-cli tenants members invite --auth-user-id <id> --role member
finance-cli tenants members set-role <user_id> --role admin
finance-cli tenants members remove <user_id>

# Services (start in separate terminals with uv run)
cd ~/PycharmProjects/MCP_Auth && uv run uvicorn main:app --reload --port 8001
cd ~/PycharmProjects/finance_planner && uv run uvicorn app.main:app --reload --port 8000
```

---

## Resources

- **MCP_Auth Repository:** https://github.com/jtuchinsky/MCP_Auth
- **Finance Planner Repository:** https://github.com/jtuchinsky/finance_planner
- **Finance CLI Repository:** https://github.com/jtuchinsky/finance_planner_cli
- **Finance CLI README:** [../README.md](../README.md)
- **Two-Terminal Workflow:** [TWO_TERMINAL.md](https://github.com/jtuchinsky/finance_planner/blob/main/docs/TWO_TERMINAL.md)

---

**Time Spent:** 5-10 minutes ⏱️
**Next:** Start building your finance tracking application! 🚀
