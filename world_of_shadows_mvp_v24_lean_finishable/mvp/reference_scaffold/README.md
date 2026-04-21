# World of Shadows MVP v21 — Runnable Reference Scaffold

This scaffold is now a **real runnable MVP slice** embedded directly into the v21 package.

It includes:
- a world-engine-centered runtime service
- publish-bound session creation from the bundled published artifact
- clean player routes and explicitly gated internal operator routes
- incident-visible SQLite persistence
- a compact MCP-safe session surface for health, session reads, diagnostics, state, logs, and turn execution

## Run locally

```bash
python -m pip install -e .
cp .env.example .env
uvicorn wos_mvp.app:app --reload
```

Or:

```bash
python -m wos_mvp.main
```

## API highlights

- `GET /api/v1/health`
- `POST /api/v1/sessions`
- `GET /api/v1/sessions/{session_id}`
- `POST /api/v1/sessions/{session_id}/turns`
- `GET /api/v1/sessions/{session_id}/state` *(internal key required)*
- `GET /api/v1/sessions/{session_id}/logs` *(internal key required)*
- `GET /api/v1/sessions/{session_id}/diagnostics` *(internal key required)*

## Internal auth

Internal/operator-only routes require `X-Internal-API-Key` matching `WOS_INTERNAL_API_KEY`.

## Tests

```bash
pytest
```
