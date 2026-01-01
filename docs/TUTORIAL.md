# Finance Planner Quick Start Tutorial

Get the complete Finance Planner system running in 5-10 minutes.

## What You'll Build

By the end of this tutorial, you'll have:
- ✅ MCP_Auth authentication service running (port 8001)
- ✅ Finance Planner API service running (port 8000)
- ✅ Finance CLI installed and configured
- ✅ A registered user with JWT tokens
- ✅ Created and managed financial accounts via API

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
# Copy example env file
cp .env.example .env

# Generate a SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" > .env.secret

# Add database URL to .env
cat >> .env <<EOF
DATABASE_URL=sqlite:///./auth.db
EOF

# Append the secret key
cat .env.secret >> .env
rm .env.secret
```

### Initialize Database

```bash
# Run migrations
alembic upgrade head
```

**Your `.env` file should contain:**
- `SECRET_KEY=<generated-key>`
- `DATABASE_URL=sqlite:///./auth.db`

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
# Copy the SECRET_KEY from MCP_Auth
SECRET_KEY=$(grep SECRET_KEY ~/PycharmProjects/MCP_Auth/.env)

# Create .env file
cat > .env <<EOF
${SECRET_KEY}
DATABASE_URL=sqlite:///./finance.db
EOF
```

### Initialize Database

```bash
# Run migrations
alembic upgrade head
```

**Your `.env` file should contain:**
- `SECRET_KEY=<same-as-mcp-auth>`
- `DATABASE_URL=sqlite:///./finance.db`

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
uvicorn main:app --reload --port 8001
```

**Wait for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### Terminal 2: Start Finance Planner

```bash
cd ~/PycharmProjects/finance_planner
uvicorn app.main:app --reload --port 8000
```

**Wait for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
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
  3. credit
  4. investment
  5. cash
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

```bash
finance-cli accounts update 1 --balance 1500.00
```

**Output:**
```
✓ Account 1 updated
  Name: Checking Account
  Type: checking
  Balance: $1,500.00
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

## Step 9: Test Direct API Access (Optional)

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

## Step 10: Explore API Documentation (Optional)

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
5. How to access the APIs directly

---

## Next Steps

### Add More Accounts

```bash
finance-cli accounts create --name "Investment Account" --type investment --balance 10000
finance-cli accounts create --name "Cash" --type cash --balance 500
```

### Explore More CLI Features

```bash
# Switch between multiple users
finance-cli auth register  # Create another user
finance-cli auth switch user2@example.com
finance-cli auth list      # See all logged-in users

# Export accounts as JSON
finance-cli accounts list --format json > accounts.json
```

### Test Token Refresh

Wait 15 minutes for your token to expire, then run:
```bash
finance-cli accounts list
# Token will auto-refresh transparently
```

### Add Transactions (Future Feature)

The Finance Planner will support transaction tracking. Stay tuned!

---

## Troubleshooting

### Service Not Running

**Error:** `✗ MCP_Auth is not running at http://127.0.0.1:8001`

**Fix:** Make sure Terminal 1 is running MCP_Auth:
```bash
cd ~/PycharmProjects/MCP_Auth
uvicorn main:app --reload --port 8001
```

### SECRET_KEY Mismatch

**Error:** `✗ SECRET_KEY mismatch detected!`

**Fix:** Copy SECRET_KEY from MCP_Auth to Finance Planner:
```bash
grep SECRET_KEY ~/PycharmProjects/MCP_Auth/.env
# Copy the value and update finance_planner/.env
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
rm auth.db  # or finance.db
alembic upgrade head
```

---

## Quick Reference Commands

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
finance-cli accounts create
finance-cli accounts list
finance-cli accounts get <id>
finance-cli accounts update <id> --balance <amount>
finance-cli accounts delete <id>

# Services (start in separate terminals)
cd ~/PycharmProjects/MCP_Auth && uvicorn main:app --reload --port 8001
cd ~/PycharmProjects/finance_planner && uvicorn app.main:app --reload --port 8000
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
