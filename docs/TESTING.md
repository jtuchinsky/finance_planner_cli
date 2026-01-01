# Testing Documentation

This document describes the testing strategy and how to run tests for the Finance Planner CLI.

## Table of Contents

- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)

---

## Test Organization

The test suite is organized into two main categories:

### Unit Tests (`tests/unit/`)

Fast, isolated tests that don't require external services. They use mocks to test individual components.

**Components tested:**
- `test_token_manager.py` - Token storage, retrieval, and management
- `test_auth_client.py` - MCP_Auth HTTP client methods
- `test_finance_client.py` - Finance Planner HTTP client methods

**Characteristics:**
- ✅ Fast execution (< 1 second)
- ✅ No external dependencies
- ✅ Use mocks for HTTP requests
- ✅ Test edge cases and error handling

### Integration Tests (`tests/integration/`)

End-to-end tests that verify complete workflows with actual services running.

**Test suites:**
- `test_auth_workflow.py` - Complete authentication flows
- `test_accounts_workflow.py` - Account CRUD operations

**Characteristics:**
- ⏱️ Slower execution (requires HTTP calls)
- 🔌 Require services running (MCP_Auth, finance_planner)
- 🔄 Test real API interactions
- ✅ Verify complete user workflows

---

## Running Tests

### Prerequisites

Install test dependencies:
```bash
cd ~/PycharmProjects/finance_planner_cli
uv sync --extra dev
```

Or manually:
```bash
uv add --dev pytest pytest-mock
```

### Run All Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv
```

### Run Specific Test Categories

**Unit Tests Only (Fast):**
```bash
pytest tests/unit/ -v
```

**Integration Tests Only:**
```bash
# Start services first!
# Terminal 1: cd ~/PycharmProjects/MCP_Auth && uv run uvicorn main:app --reload --port 8001
# Terminal 2: cd ~/PycharmProjects/finance_planner && uv run uvicorn app.main:app --reload --port 8000

# Then run integration tests
pytest tests/integration/ -v
```

**Run Specific Test File:**
```bash
pytest tests/unit/test_token_manager.py -v
```

**Run Specific Test:**
```bash
pytest tests/unit/test_token_manager.py::TestTokenManager::test_save_and_get_token -v
```

### Using Test Markers

Tests are marked with categories:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all except integration
pytest -m "not integration"
```

---

## Running Tests Before Commits

**Recommended workflow:**

```bash
# 1. Run fast unit tests first
pytest tests/unit/ -v

# 2. If unit tests pass, run integration tests
pytest tests/integration/ -v

# 3. Check all tests pass
pytest -v
```

---

## Test Output Examples

### Successful Test Run

```bash
$ pytest tests/unit/ -v

tests/unit/test_token_manager.py::TestTokenManager::test_save_and_get_token PASSED
tests/unit/test_token_manager.py::TestTokenManager::test_get_current_user PASSED
tests/unit/test_auth_client.py::TestAuthClient::test_register_success PASSED
tests/unit/test_finance_client.py::TestFinanceClient::test_create_account_success PASSED

======================== 15 passed in 0.45s =========================
```

### Failed Test

```bash
tests/unit/test_token_manager.py::TestTokenManager::test_logout FAILED

______ TestTokenManager.test_logout ______

    def test_logout(self, temp_token_file, mock_token_response):
        manager = TokenManager(storage_path=temp_token_file)
        email = "test@example.com"

        manager.save_token(email, mock_token_response)
        manager.logout(email)

>       token = manager.get_current_token(auto_refresh=False)
E       AssertionError: Token should be None after logout

======================== 1 failed, 14 passed in 0.52s =========================
```

---

## Writing Tests

### Unit Test Example

```python
"""tests/unit/test_my_feature.py"""
import pytest
from unittest.mock import Mock, patch

from cli.services.my_service import MyService


class TestMyService:
    """Test MyService functionality."""

    @patch('cli.services.my_service.httpx.Client')
    def test_my_method(self, mock_client_class, mock_httpx_response):
        """Test my method with mocked HTTP."""
        # Setup
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client_class.return_value = mock_client

        response = mock_httpx_response(200, {"result": "success"})
        mock_client.get.return_value = response

        # Test
        service = MyService()
        result = service.my_method()

        # Assert
        assert result == "success"
```

### Integration Test Example

```python
"""tests/integration/test_my_workflow.py"""
import pytest

pytestmark = pytest.mark.integration


class TestMyWorkflow:
    """Integration tests for my workflow."""

    def test_complete_flow(self, authenticated_token):
        """Test complete user flow."""
        try:
            # Perform actions with real services
            result = perform_action(authenticated_token)
            assert result.success
        except ServiceNotRunningError:
            pytest.skip("Service not running")
```

### Using Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
def test_with_temp_file(temp_token_file):
    """Use temporary file fixture."""
    # temp_token_file is automatically created and cleaned up
    assert temp_token_file.exists()

def test_with_mock_response(mock_token_response):
    """Use mock token response."""
    assert mock_token_response.access_token
```

---

## Test Coverage

### Generate Coverage Report

Install pytest-cov:
```bash
uv add --dev pytest-cov
```

Run with coverage:
```bash
pytest --cov=cli --cov-report=html --cov-report=term-missing
```

View HTML report:
```bash
open htmlcov/index.html
```

### Coverage Goals

- **Unit tests:** Aim for >80% coverage of core logic
- **Integration tests:** Cover all major user workflows
- **Critical paths:** 100% coverage for auth and token management

---

## Test Best Practices

### 1. Test Naming

```python
# Good - descriptive test names
def test_create_account_with_initial_balance():
def test_login_fails_with_invalid_password():

# Bad - vague names
def test_account():
def test_error():
```

### 2. Test Independence

```python
# Good - each test is independent
def test_feature_a():
    setup_for_test_a()
    # test code

def test_feature_b():
    setup_for_test_b()
    # test code

# Bad - tests depend on each other
def test_step_1():
    global state
    state = do_something()

def test_step_2():
    # Uses state from test_step_1
```

### 3. Use Fixtures for Setup

```python
# Good - use fixtures
@pytest.fixture
def test_user():
    return User(name="Test User")

def test_with_user(test_user):
    assert test_user.name == "Test User"

# Bad - duplicate setup
def test_1():
    user = User(name="Test User")
    # test code

def test_2():
    user = User(name="Test User")
    # test code
```

### 4. Mock External Dependencies

```python
# Good - mock HTTP calls in unit tests
@patch('cli.services.auth_client.httpx.Client')
def test_login(mock_client_class):
    # Mock setup
    result = auth_client.login(email, password)

# Bad - make real HTTP calls in unit tests
def test_login():
    # This will fail if service is down!
    result = auth_client.login(email, password)
```

---

## Troubleshooting Tests

### Integration Tests Fail with Connection Error

**Problem:** `ServiceNotRunningError: MCP_Auth is not running`

**Solution:** Start the required services:
```bash
# Terminal 1
cd ~/PycharmProjects/MCP_Auth
uv run uvicorn main:app --reload --port 8001

# Terminal 2
cd ~/PycharmProjects/finance_planner
uv run uvicorn app.main:app --reload --port 8000
```

### Tests Pass Locally But Fail in CI

**Common causes:**
- Different Python versions
- Missing environment variables
- Database not initialized
- Service ports in use

**Solution:** Check CI logs and ensure test environment matches local setup.

### Slow Test Execution

**Solution:**
```bash
# Run only fast unit tests during development
pytest tests/unit/ -v

# Run full suite before commits
pytest -v
```

---

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: uv sync --extra dev

    - name: Run unit tests
      run: uv run pytest tests/unit/ -v

    # Integration tests would require services running
    # - name: Run integration tests
    #   run: uv run pytest tests/integration/ -v
```

---

## Test Fixtures Reference

### Available Fixtures

| Fixture | Description | Scope |
|---------|-------------|-------|
| `temp_token_file` | Temporary token storage file | function |
| `mock_token_response` | Mock TokenResponse object | function |
| `mock_user_response` | Mock UserResponse object | function |
| `mock_account` | Mock Account object | function |
| `mock_accounts_list` | List of mock accounts | function |
| `mock_httpx_response` | Factory for mock HTTP responses | function |
| `unique_email` | Unique email for testing | function |
| `authenticated_token` | JWT token for integration tests | function |

### Using Fixtures

```python
def test_my_feature(temp_token_file, mock_token_response):
    """Test using multiple fixtures."""
    manager = TokenManager(storage_path=temp_token_file)
    manager.save_token("test@example.com", mock_token_response)
    # Test code
```

---

## Summary

### Quick Commands

```bash
# Run all unit tests (fast)
pytest tests/unit/ -v

# Run all integration tests (requires services)
pytest tests/integration/ -v

# Run specific test
pytest tests/unit/test_token_manager.py::TestTokenManager::test_logout -v

# Run with coverage
pytest --cov=cli --cov-report=term-missing

# Run only marked tests
pytest -m unit
pytest -m integration
```

### Test Files

- `tests/conftest.py` - Shared fixtures
- `tests/unit/test_token_manager.py` - Token management tests
- `tests/unit/test_auth_client.py` - Auth HTTP client tests
- `tests/unit/test_finance_client.py` - Finance HTTP client tests
- `tests/integration/test_auth_workflow.py` - Auth workflow tests
- `tests/integration/test_accounts_workflow.py` - Account workflow tests

---

**Happy Testing!** 🧪✅
