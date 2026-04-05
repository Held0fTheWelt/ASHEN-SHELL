# Testing Setup and Reproducible Validation Guide

This document explains how to install test dependencies, run tests, understand test profiles, and validate the repository in clean environments.

## Quick Start

### Install Test Dependencies

For testing the backend in a clean environment:

```bash
cd backend
pip install -r requirements.txt -r requirements-test.txt
```

Or, for development (includes testing plus optional dev tools):

```bash
cd backend
pip install -r requirements-dev.txt
```

### Run Canonical Smoke Suite

To run a quick validation of core repository health:

```bash
# From repository root
python -m pytest tests/smoke/ -v --tb=short
```

Expected result: ~140 tests pass in <15 seconds.

### Run Backend Unit Tests

To run all backend tests with coverage:

```bash
cd backend
python -m pytest tests/ -v
```

## Test Profiles: What They Mean

The repository supports three explicit test execution profiles:

### 1. **testing_isolated** (Default Backend Tests)

**What it is:** Tests run against `TestingConfig` with an **in-memory SQLite database**, **no routing bootstrap**, and **CSRF disabled by default**.

**When to use:**
- Running unit tests for rapid development feedback
- Testing business logic in isolation
- CI/CD pipelines where database state must not leak between tests

**Configuration:**
- `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"`
- `ROUTING_REGISTRY_BOOTSTRAP = False` (prevents process-global router contamination)
- `WTF_CSRF_ENABLED = False` (enabled separately for CSRF-specific tests)
- Fixed secrets (safe for CI)

**How to select:**
```bash
cd backend
pytest tests/ -v
```

**Fixtures available:**
- `app` — Flask app with in-memory DB, ready for testing
- `client` — Test client for the app
- `test_user` — Pre-created regular user (username: testuser, password: Testpass1)
- `auth_headers` — JWT headers for test_user
- `moderator_user`, `moderator_headers` — Moderator role
- `admin_user`, `admin_headers` — Admin role
- `super_admin_user`, `super_admin_headers` — Admin with level 100
- `runner` — Flask CLI runner for command testing

**Example test:**
```python
def test_example(app, test_user, auth_headers):
    with app.app_context():
        # Your test code
        pass
```

---

### 2. **testing_bootstrap_on** (Production-like Routing Tests)

**What it is:** Tests run with `ROUTING_REGISTRY_BOOTSTRAP = True`, simulating production-like routing initialization. Uses the same in-memory database and test fixtures, but enables routing registry bootstrap.

**When to use:**
- Validating Area 2 convergence and final closure gates
- Testing HTTP proofs that depend on routing initialization
- Verifying production-like configuration behavior

**Configuration:**
- `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"`
- `ROUTING_REGISTRY_BOOTSTRAP = True` (enables routing initialization)
- `WTF_CSRF_ENABLED = False`
- Fixed secrets

**How to select:**
```python
# In your test, inject the bootstrap-on fixtures instead of regular ones:

def test_with_bootstrap(app_bootstrap_on, client_bootstrap_on, auth_headers_bootstrap_on):
    # Tests run with routing bootstrap enabled
    response = client_bootstrap_on.get("/api/v1/areas/convergence")
    assert response.status_code == 200
```

**Bootstrap-specific fixtures:**
- `app_bootstrap_on` — App with `ROUTING_REGISTRY_BOOTSTRAP = True`
- `client_bootstrap_on` — Client for bootstrap-on app
- `test_user_bootstrap` — Test user in bootstrap-on app's DB
- `auth_headers_bootstrap_on` — JWT for bootstrap-on test user

**Note:** Bootstrap-on tests have their own isolated database lifecycle, separate from regular `app` tests. Do not mix fixtures.

---

### 3. **testing_isolated_production_like** (Smoke Tests)

**What it is:** Production-like configuration (database file, bootstrap enabled, full initialization) for validation tests that simulate real deployment startup behavior.

**When to use:**
- Smoke testing: rapid checks that core services initialize
- Validating production configuration defaults
- Testing real database file operations (not in-memory)

**Configuration:**
- Uses production `Config` class (not `TestingConfig`)
- `ROUTING_REGISTRY_BOOTSTRAP = True` (default)
- Real database file (not in-memory)
- Fixtures from backend test suite imported

**How to select:**
```bash
# From repository root
python -m pytest tests/smoke/ -v
```

**Fixtures available:** All backend fixtures (test_user, auth_headers, etc.) are available via pytest plugin loading.

---

## Canonical Smoke Suite

A lightweight validation to catch major breakage quickly:

```bash
python -m pytest tests/smoke/ -v --tb=short
```

This runs ~140 tests covering:
- **Backend startup:** App creation, config, database connection
- **Engine startup:** World Engine dependencies and initialization
- **Content modules:** W0 and W1 contract validation, YAML structure
- **Core routing:** Area 2 convergence and closure gates

**Expected result:** All pass in ~10–15 seconds.

**What it validates:**
- Core Flask app starts without errors
- Database is connectable and has required tables
- Runtime routing bootstrap works
- Content module YAML is valid and internally consistent
- Core API endpoints respond

---

## Running Broader Test Subsets

### All Backend Tests (with coverage)

```bash
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html
```

This covers:
- Unit tests (fast, no external deps)
- Integration tests (DB, auth, API)
- Security tests (OWASP, input validation, authZ)
- Contract tests (API stability)
- E2E tests (full workflows)

### Fast Mode: Only Unit Tests

```bash
cd backend
python -m pytest tests/ -m unit -v
```

Skips integration and slow tests.

### Security-Specific Tests

```bash
cd backend
python -m pytest tests/ -m security -v
```

### Content Module Tests

```bash
python -m pytest tests/smoke/test_w0_contracts.py tests/smoke/test_w1_module.py -v
```

---

## Pytest Configuration Files

The repository uses pytest configuration in two places for consistency:

### `backend/pytest.ini`

Classic pytest INI format. Defines:
- `pythonpath`: Includes `.` and `..` for flexible import paths
- `testpaths`: `tests/` directory
- `markers`: Unit, integration, security, contract, e2e, persistence, slow
- `asyncio_mode`: strict (required for async test determinism)
- `addopts`: Verbose output, coverage, short tracebacks

### `backend/pyproject.toml`

Duplicate configuration in TOML format (for tools that prefer TOML). Includes pytest, coverage, and path settings.

Both files must stay in sync. If you modify one, update the other.

---

## Test Dependency Declarations

### `backend/requirements.txt`

Production dependencies only. Used by:
- Production deployments
- Test environments (as a base)
- Any environment that needs the app to run

### `backend/requirements-test.txt`

**Test dependencies explicitly declared** (imports requirements.txt as a base).

Used for clean-environment testing:
```bash
pip install -r requirements.txt -r requirements-test.txt
```

Includes:
- `pytest>=7.0,<9` — test runner
- `pytest-asyncio>=0.21,<1` — async test support (import-time requirement)
- `pytest-cov>=4.0,<6` — coverage measurement
- `pytest-timeout>=2.1` — timeout enforcement

**Does NOT include** dev-only tools like formatters, linters, type checkers.

### `backend/requirements-dev.txt`

Development dependencies (super-set of test requirements).

Used by developers:
```bash
pip install -r requirements-dev.txt
```

Includes:
- All of requirements.txt
- All test requirements (via requirements-test.txt)
- Optional dev tools (commented, can be uncommented)

---

## Environment-Sensitive Behavior

The following aspects may vary between environments and are **intentionally left configurable**:

### Database URI
- **Default:** SQLite file at `backend/instance/wos.db`
- **Override:** Set `DATABASE_URI` environment variable
- **Testing:** In-memory SQLite (set automatically by TestingConfig)

### Secrets (Development Only)
- **Production:** Requires `SECRET_KEY` and `JWT_SECRET_KEY` environment variables
- **Development:** Set `DEV_SECRETS_OK=1` to enable fallback secrets (NEVER in production)
- **Testing:** Fixed secrets in TestingConfig (safe for CI)

### CORS Origins
- **Default:** None (same-origin only)
- **Override:** Set `CORS_ORIGINS=http://localhost:3000,https://example.com`

### Email Configuration
- **Default:** Disabled (`MAIL_ENABLED=0`)
- **Override:** Set `MAIL_ENABLED=1`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`

### Routing Bootstrap
- **Production:** Enabled by default (`ROUTING_REGISTRY_BOOTSTRAP=True` in Config)
- **Unit tests:** Disabled (`ROUTING_REGISTRY_BOOTSTRAP=False` in TestingConfig) to avoid cross-test contamination
- **Smoke tests:** Enabled (production-like behavior)
- **Bootstrap tests:** Use `app_bootstrap_on` fixture to override

---

## Clean-Environment Validation (for CI/CD)

To validate that the repository can be tested in a fresh environment:

1. **Install dependencies:**
   ```bash
   pip install --no-cache-dir -r backend/requirements.txt -r backend/requirements-test.txt
   ```

2. **Run canonical smoke suite:**
   ```bash
   python -m pytest tests/smoke/ -v --tb=short
   ```

3. **Run broader test suite:**
   ```bash
   cd backend
   python -m pytest tests/ -v --tb=short
   ```

If both pass, the environment is valid. If tests fail, check:
- All required packages are in requirements files
- PYTHONPATH is correctly set (pytest.ini handles this)
- Database is readable/writable (if using file-based SQLite)
- No local environment assumptions are leaked

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app.database'"
- This is a fixed import error in the repository. Use `from app.extensions import db` instead.
- Smoke tests have been updated to use the correct import.

### "fixture 'auth_headers' not found"
- Ensure pytest loads plugins correctly. Smoke tests import backend fixtures via `pytest_plugins`.
- If running a custom test outside smoke/backend, add this to your conftest:
  ```python
  pytest_plugins = ['backend.tests.conftest']
  ```

### "ROUTING_REGISTRY_BOOTSTRAP is not set" or "RuntimeError: working outside of application context"
- Use the correct fixture for your profile:
  - `app` for isolated tests
  - `app_bootstrap_on` for bootstrap tests
  - Ensure you're inside the app context when accessing app globals

### Tests run slowly
- Run only unit tests: `pytest tests/ -m unit`
- Skip slow tests: `pytest tests/ -m "not slow"`
- Use pytest-xvs for early exit on failure: `pytest tests/ -xvs`

### Database errors or "table does not exist"
- The test fixtures automatically create all tables. If you see this:
  1. Ensure the `app` fixture is used (it calls `db.create_all()`)
  2. Check that migrations are properly applied (if using a real DB)
  3. Verify `SQLALCHEMY_DATABASE_URI` is set correctly in TestingConfig

---

## Glossary

**testing_isolated:** Default profile; uses in-memory DB, no routing bootstrap, CSRF disabled. For unit tests.

**testing_bootstrap_on:** Production-like routing with in-memory DB and test fixtures. For area-specific tests.

**testing_isolated_production_like:** Full production config (real DB file, bootstrap, etc.). For smoke tests.

**ROUTING_REGISTRY_BOOTSTRAP:** When true, initializes the global routing registry at startup. Must be false in isolated unit tests to prevent cross-test contamination.

**Smoke test:** Lightweight, quick test of core functionality (not heavy integration testing). Validates startup, basic health, and key paths.

**Fixture:** Pytest fixture; a reusable test setup (e.g., `app`, `test_user`, `auth_headers`). Defined in conftest.py.

**Profile:** A named test configuration (e.g., testing_isolated, testing_bootstrap_on). Determines what config class is used and what fixtures are available.

