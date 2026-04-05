# Better Tomorrow (World of Shadows)

World of Shadows is organized as separate services with clear ownership boundaries:

- `frontend/` - canonical player/public web frontend
- `administration-tool/` - separate admin/management frontend (intentionally not merged)
- `backend/` - API/business/auth/policy service
- `world-engine/` - authoritative runtime/play service

## Repository structure

```text
backend/               # Flask API and business logic
frontend/              # Player/public Flask frontend
administration-tool/   # Admin/management frontend
world-engine/          # FastAPI runtime service
docs/                  # Architecture, operations, development docs
tests/                 # Multi-suite test runner
```

## Service responsibilities

### `frontend/`
- Owns player/public pages: login, register, dashboard, news, wiki, community, game menu, play shell
- Integrates with backend API and play-service endpoints
- Does not own admin/management pages

### `administration-tool/`
- Owns management/editorial workflows (`/manage/*`)
- Uses backend API for auth and data operations
- Remains a standalone service by design

### `backend/`
- Owns API endpoints, authN/authZ, policy enforcement, persistence, and service integration
- Exposes game/bootstrap/ticket APIs for frontend and play-service orchestration
- Serves a small **technical HTML area** at `/backend/*` (architecture, API, ops — not player/admin UI); **`/` redirects to `/backend`**
- Legacy `backend/app/web/*` paths (except `/` and `/health`) remain compatibility redirects to `FRONTEND_URL`, not canonical player UI hosting

### `world-engine/`
- Owns authoritative game runtime state, session execution, and WebSocket live behavior

## Local development quick start

### 1) Backend

```bash
cd backend
pip install -r requirements.txt
flask init-db
flask db upgrade
python run.py
```

Backend default URL: `http://127.0.0.1:5000`

### 2) Player/Public frontend

```bash
cd frontend
pip install -r requirements.txt
python run.py
```

Frontend default URL: `http://127.0.0.1:5002`

### 3) Administration tool (separate)

```bash
cd administration-tool
pip install -r requirements.txt
python app.py
```

Administration default URL: `http://127.0.0.1:5001`

### 4) Play service

```bash
cd world-engine
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

Play-service default URL: `http://127.0.0.1:8001`

## Required environment variables (high-level)

- `SECRET_KEY`, `JWT_SECRET_KEY` for backend
- `FRONTEND_SECRET_KEY` for `frontend/`
- `BACKEND_API_URL` for `frontend/` and `administration-tool/`
- `CORS_ORIGINS` on backend including `frontend` and `administration-tool` origins
- `FRONTEND_URL` on backend for legacy path redirects (`/login`, `/play`, …); optional `ADMINISTRATION_TOOL_URL` for links on `/backend`
- `PLAY_SERVICE_PUBLIC_URL`, `PLAY_SERVICE_INTERNAL_URL`, `PLAY_SERVICE_SHARED_SECRET` for backend/play integration

## Docker compose

Use the root compose file:

```bash
docker compose up --build
```

It starts:
- backend (`:8000`)
- frontend (`:5002`)
- administration-tool (`:5001`)
- play-service (`:8001`)

`frontend` and `administration-tool` use `BACKEND_API_URL=http://backend:8000` so server-side API calls resolve the backend container (not `localhost` inside each app container). Bare-metal local dev uses backend on **5000** and sets `BACKEND_API_URL=http://127.0.0.1:5000` instead.

## Testing

### Quick Start: Canonical Smoke Suite

Validate core repository health in seconds:

```bash
# macOS / Linux
./run-smoke-tests.sh

# Windows
run-smoke-tests.bat

# Or use pytest directly
python -m pytest tests/smoke/ -v --tb=short
```

Expected: ~140 tests pass in <15 seconds.

### Comprehensive Testing

**Backend (complete test suite with coverage):**

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v
```

**Per-service (legacy runner):**

```bash
cd tests
python run_tests.py --suite backend      # Backend API, auth, models
python run_tests.py --suite administration  # Admin frontend
python run_tests.py --suite engine       # World engine (install engine requirements first)
```

### Test Documentation

- **[Testing Setup Guide](docs/testing-setup.md)** — Test profiles, fixtures, canonical commands, troubleshooting
- **[Test Environment Hygiene](docs/test-environment-hygiene.md)** — How dependencies stay explicit, clean-environment reproducibility

### Test Profiles

The repository supports three explicit test execution profiles:

1. **testing_isolated** (default unit tests) — In-memory DB, no routing bootstrap
2. **testing_bootstrap_on** — Production-like routing with in-memory DB
3. **testing_isolated_production_like** (smoke tests) — Production config, real DB file

See [Testing Setup Guide](docs/testing-setup.md) for details.

### World Engine Tests

Install dependencies first so imports of `ai_stack` and `langchain_core` succeed:

```bash
pip install -r world-engine/requirements-dev.txt
python run_tests.py --suite engine
```

GitHub Actions installs this automatically in `.github/workflows/engine-tests.yml`. For **GitHub Codespaces** or **VS Code Dev Containers**, use `.devcontainer/devcontainer.json`.

## Documentation

- `docs/architecture/README.md`
- `docs/architecture/ServerArchitecture.md`
- `docs/development/LocalDevelopment.md`
- `docs/operations/RUNBOOK.md`
- `.devcontainer/devcontainer.json` — GitHub Codespaces / Dev Containers (installs `world-engine/requirements-dev.txt`, sets `PYTHONPATH` for `ai_stack`)
