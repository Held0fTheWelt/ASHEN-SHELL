# Compose smoke lane (optional)

**Purpose:** narrow **production-near** checks that require real services (TCP, multiple containers, WebSockets), which the default [`run_tests.py`](../../run_tests.py) Python orchestrator does **not** start.

## Prerequisites

- Docker and Docker Compose v2
- Repository root [`docker-compose.yml`](../../../docker-compose.yml) (or your deployment-specific override) reviewed for ports and env files

## Suggested flow

1. Copy or export the env files referenced by Compose (see repo `.env.example` / component docs).
2. From the repository root:

   ```bash
   docker compose up -d --build
   ```

3. Run **one** scripted happy path (to be expanded in-repo), for example:

   - Backend health: `GET /api/v1/health` (or documented health URL)
   - Frontend reachability if exposed
   - World-engine health if part of the stack

4. Tear down:

   ```bash
   docker compose down -v
   ```

## CI

Workflow [`.github/workflows/compose-smoke.yml`](../../../.github/workflows/compose-smoke.yml) runs **manually** (`workflow_dispatch`) so it does not slow every PR. Enable it when Compose definitions and secrets are stable enough for CI agents.

## Relationship to `run_tests.py`

Keep **pytest** suites as the default merge gate. Use this lane as an **optional** or **nightly** signal that “containers wire together,” not as a replacement for unit/contract tests.
