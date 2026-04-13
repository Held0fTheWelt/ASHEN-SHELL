# Browser E2E (Playwright)

Python [`run_tests.py`](../run_tests.py) does **not** execute these tests. Use this folder for **critical UI flows** (login, play shell, admin publish) against a running stack (local Compose or staging URL).

## Setup

```bash
cd tests/e2e
npm install
npx playwright install --with-deps
```

## Run

Point `BASE_URL` at the frontend (default matches root `docker-compose.yml` host port):

```bash
cd tests/e2e
BASE_URL=http://127.0.0.1:5002 npx playwright test
```

## CI

Add a dedicated workflow when stable; keep **off** the default pytest gate to avoid flakiness and Node install cost on every PR.
