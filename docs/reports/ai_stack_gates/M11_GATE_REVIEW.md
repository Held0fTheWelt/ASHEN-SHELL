# Milestone 11 Gate Review — Observability, Governance, Release Hardening

**Date:** 2026-04-04  
**Status:** PASS  
**Recommendation:** Proceed (with documented partial areas)

## Milestone scope (M11.1–M11.9)

- Canonical observability/governance architecture document.
- End-to-end trace propagation for the **backend → World-Engine → LangGraph** story path.
- Structured audit logging (backend + World-Engine) for bridge, workflows, and story turns.
- Governance evidence APIs and administration-tool page backed by real APIs.
- Reproducibility metadata on graph output (`repro_metadata`).
- Operational failure visibility (bridge errors, graph error lists, audit failure events).
- Release readiness checklist and automated tests proving operational behavior.

## Prerequisite verification (M0–M10)

- M10 gate artifact present and PASS (`docs/reports/ai_stack_gates/M10_GATE_REVIEW.md`).
- Prior AI stack architecture docs and unified-stack flows remain in repo; no competing authority model introduced.

## Files changed (high level)

- **Trace / bridge:** `backend/app/services/game_service.py`, `backend/app/api/v1/session_routes.py`, `world-engine/app/middleware/trace_middleware.py`, `world-engine/app/main.py`, `world-engine/tests/conftest.py`, `world-engine/app/api/http.py`, `world-engine/app/story_runtime/manager.py`
- **Repro / graph:** `wos_ai_stack/langgraph_runtime.py`, `wos_ai_stack/version.py`, `wos_ai_stack/__init__.py`, `wos_ai_stack/tests/test_langgraph_runtime.py`
- **Audit:** `backend/app/observability/audit_log.py`, `world-engine/app/observability/*`
- **Governance:** `backend/app/services/ai_stack_evidence_service.py`, `backend/app/api/v1/ai_stack_governance_routes.py`, `backend/app/api/v1/__init__.py`, `administration-tool/app.py`, `administration-tool/templates/manage/*`, `administration-tool/static/manage_ai_stack_governance.js`
- **Workflows:** `backend/app/api/v1/writers_room_routes.py`, `backend/app/services/writers_room_service.py`, `backend/app/api/v1/improvement_routes.py`
- **Tests:** `backend/tests/test_m11_ai_stack_observability.py`, `backend/tests/test_game_service.py`, `backend/tests/test_session_routes.py`, `backend/tests/test_writers_room_routes.py`, `world-engine/tests/test_trace_middleware.py`, `administration-tool/tests/test_routes.py`, `administration-tool/tests/test_manage_game_routes.py`
- **Docs:** `docs/architecture/observability_and_governance_in_world_of_shadows.md`, `docs/reports/AI_STACK_RELEASE_READINESS_CHECKLIST.md`, this gate file, `docs/reports/AI_STACK_M11_CLOSURE_REPORT.md`
- **Repo hygiene:** `.gitignore` — ignore `backend/var/improvement/` so test-run JSON artifacts are not committed.

## Design decisions

- Reuse **`X-WoS-Trace-Id`** end-to-end instead of introducing a second correlation scheme.
- World-Engine uses a **separate contextvar namespace** (`wos_we_trace_id`) to avoid accidental cross-import coupling with the Flask backend package on `sys.path`.
- **`repro_metadata`** is the single nested object for reviewers to inspect versions, routing, retrieval profile, model outcome flags, and host version hints.
- Governance APIs reuse **`FEATURE_MANAGE_GAME_OPERATIONS`** to avoid new feature-flag rollout for the same operational audience.
- Story turn audit at World-Engine uses **SHA-256 hashes** of player input for privacy-aware structured logs.

## Migrations / compatibility

- No database migrations. API responses are **additive** (`trace_id`, `repro_metadata`, `bridge_error`, governance JSON fields).

## Tests run (exact commands)

From repository root (adjust paths as needed on Unix):

```powershell
cd backend
python -m pytest tests/test_m11_ai_stack_observability.py tests/test_game_service.py::TestGameServiceClient::test_internal_request_includes_trace_header_when_configured tests/test_session_routes.py::TestCapabilityAuditEndpoint tests/test_improvement_routes.py tests/test_writers_room_routes.py tests/test_observability.py -q --tb=short
```

```powershell
cd ..
python -m pytest wos_ai_stack/tests/test_langgraph_runtime.py -q --tb=short
```

```powershell
cd world-engine
python -m pytest tests/test_trace_middleware.py tests/test_story_runtime_api.py -q --tb=short
```

```powershell
cd ..\administration-tool
python -m pytest tests/test_routes.py::test_html_routes_render_expected_templates tests/test_manage_game_routes.py -q --tb=short
```

**Note:** Full monorepo `pytest` from repo root was not executed here due to `app` package name collision; run package-scoped suites as above (or set `PYTHONPATH=backend` explicitly for full backend suite from root).

## Acceptance criteria

| Criterion | Status |
|-----------|--------|
| M11.1 Architecture doc | Pass |
| M11.2 Trace propagation (canonical path) | Pass |
| M11.3 Structured audit / events | Pass |
| M11.4 Diagnostics / evidence access | Pass |
| M11.5 Version / reproducibility metadata | Pass |
| M11.6 Governance surfaces (API + admin UI) | Pass |
| M11.7 Failure visibility | Pass (bridge + graph errors; see limitations) |
| M11.8 Release readiness checklist | Pass |
| M11.9 Automated tests | Pass |

## Required gate answers

### What exact trace path is canonical end-to-end?

`Client → Flask api_v1 (ensure_trace_id) → game_service internal httpx (X-WoS-Trace-Id) → World-Engine middleware → StoryRuntimeManager.execute_turn → RuntimeTurnGraphExecutor.run → graph_diagnostics.repro_metadata.trace_id`.

### Which layers are fully covered vs partial?

| Layer | Coverage |
|-------|----------|
| Backend API v1 | Full (header + `g.trace_id`) |
| Backend → World-Engine story HTTP | Full |
| World-Engine middleware | Full |
| LangGraph runtime turn graph | Full (`repro_metadata`) |
| Writers-Room / improvement HTTP | Trace id in response + `workflow.run` audit |
| MCP standalone tools | **Partial** (still may mint independent trace unless extended) |
| Legacy in-process backend AI turn | Partial (contextvar when present; not canonical) |

### What structured audit records exist and where?

- **stdout JSON** via `wos.audit` (backend) and `wos.world_engine.audit` (World-Engine).
- **DB activity log** for `session_evidence_view` on governance API use.

### What governance surface is canonical for human review?

- **`GET /api/v1/admin/ai-stack/session-evidence/<session_id>`** (aggregated bundle).
- Supporting: capability audit, session turn JSON, improvement list API, AI Stack administration-tool page.

### What metadata is captured for reproducibility?

`repro_metadata`: `ai_stack_semantic_version`, `runtime_turn_graph_version`, `graph_name`, `trace_id`, `story_runtime_core_version` (distribution metadata when installed), `routing_policy` + `routing_policy_version`, selected model/provider, retrieval domain/profile/status/hit_count, model attempt/success/fallback flags, `module_id`, `session_id`, `host_versions` (includes `world_engine_app_version`).

### What failure classes are newly visible?

- **`world_engine_unreachable`** on session turn (`502`) and capability audit / evidence bundle (`bridge_errors`).
- **`graph_execution_exception`** audit before re-raise from graph invoke.
- **`graph_diagnostics.errors`** for fallback / adapter issues already tracked inside the graph.

### What remains deferred before “production-grade”?

- Unified trace for **MCP operator CLI** when not passing through backend headers.
- Centralized **log aggregation** and retention policies (environment-specific).
- Stronger **redaction policy** for `raw_input` in diagnostics if exported broadly.
- Full **CI** run matrix from a single entrypoint with explicit `PYTHONPATH` documented.

## Known limitations

- Evidence bundle uses **live** fetches to World-Engine; historical snapshots are not a time-series DB.
- `story_runtime_core` version reads **distribution** metadata (`importlib.metadata`); editable installs may show `unknown`.

## Risks left open

- Misconfigured `PLAY_SERVICE_INTERNAL_URL` still blocks all story evidence (now explicit in API responses).
- Verbose diagnostics could leak sensitive player content if exposed to the wrong role—mitigated by moderator/admin + feature gating, not by content redaction in every field.

## Recommendation

**Proceed** — canonical path meets trace + audit + governance + reproducibility + test bar. Treat MCP standalone trace alignment as a post-M11 hardening item.
