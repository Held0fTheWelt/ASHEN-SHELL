# backend — Software Architecture (arc42)

**Component:** backend · **Folder:** `backend/` · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Flask platform service: REST `/api/v1`, authentication, forum/news/wiki persistence, content module
load/compile, governance routes, and **proxy** integration with world-engine for live play.

### 1.1 Quality goals

| Goal | Scenario |
| --- | --- |
| No runtime authority | No code path commits live narrative state |
| Stable proxy | `game_service` is the only production play integration |
| Clear transitional code | Deprecated in-process runtime is test-only |

## 2. Constraints

- ADR-0002 quarantine: session surface must not compete with world-engine.
- CORS must include frontend origins.
- Legacy `/` redirect is technical backend home, not player UI.

## 3. Context & Scope

In scope: API, auth, DB, content compile, play bootstrap. Out of scope: turn graph, narrative commit.

## 4. Solution Strategy

- HTTP client to `PLAY_SERVICE_INTERNAL_URL` for story operations.
- Keep reusable schemas/presenters as canonical reusable logic per classification doc.
- Route admin and player UIs only through documented APIs.

## 5. Building Block View

| Block | Path |
| --- | --- |
| API v1 | `backend/app/api/v1/` |
| Game proxy | `backend/app/services/game/game_service.py` |
| Content | `backend/app/content/` |
| Governance | `backend/app/services/governance/` |
| Transitional runtime | `backend/app/runtime/` (deprecated for live play) |

## 6. Runtime View

Player turn: frontend → `game_routes` → `game_service` HTTP → world-engine → response mapping.

## 7. Deployment View

Flask app with alembic migrations; shares secrets with world-engine for tickets.

## 8. Crosscutting Concepts

- Model routing: `backend/app/runtime/model_routing.py` (adapter choice, traces).
- Operational governance routes tested in `backend/tests/test_operational_governance_*.py`.

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Backend session quarantine | Accepted | ADR-0002 |
| D2 | Frontend/backend restructure | Accepted | ADR-0016 |
| D3 | Test suite split in orchestrator | Accepted | ADR-0037 |
| D4 | Security governance admin plane | Accepted | ADR-0052 |

### D1: Backend session / transitional runtime surface - quarantine and retirement

**Status:** 
**Origin:** ADR-0002 (retired 2026-06-23)

**Context.** The platform historically exposed backend-local session and runtime-shaped APIs. The world-engine is the **authoritative** live and story runtime for committed play state. A large transitional surface on the backend increases the risk that tools, tests, or new features attach to the wrong authority layer (audit finding class "backend transitional session drift").

**Package immutability (historical MVP ADR-002 wording):** A package version, once built and stored under `versions/<package_version>/`, is **immutable**. `active/` is a **pointer** to a version, never the storage location of mutable content. Consequences: package promotion is pointer movement plus event log; rollback is pointer movement; audit history is lossless; preview vs active comparisons are reliable. (Source: [`02_architecture_decisions.md`](../../../MVPs/MVP_Narrative_Governance_And_Revision_Foundation/02_architecture_decisions.md) — index only; **operational detail lives in this ADR and linked architecture docs**.)

**Decision.** 1. **Inventory** all backend routes and services under `backend/app/runtime/`, `session_start.py`, and session-related API modules (normative list: **Appendix A**).
2. **Classify** each entry point as: **retire** (remove when no caller), **quarantine** (explicit non-authoritative labeling, narrow compatibility window), or **compat** (documented operator-only surface with no player truth claims).
3. **Quarantine** non-authoritative surfaces in naming and documentation so they cannot be mistaken for production authority (prefixes, deprecation notices, ADR links).

**Consequences.** - Positive: Reduced drift; clearer onboarding for engineers.
- Negative: Migration work for any remaining callers of retired surfaces; coordination with product for compat timelines.

**Implementation status.** **Implemented — matches ADR (inventory complete; retirement ongoing).**

- Backend transitional session surfaces are inventoried and classified; documented in `docs/technical/architecture/backend-runtime-classification.md`.
- The former backend session API route and flat session service surfaces are retired; the remaining backend-local compatibility store lives at `backend/app/runtime/session/session_store.py` and is classified non-authoritative per the ADR.
- Governance investigation confirms `CTR-ADR-0002-BACKEND-SESSION-QUARANTINE` is implemented; validated by `backend/tests/test_session_routes.py` and `backend/tests/test_world_engine_console_routes.py`.
- One open gap: the ADR cites "Appendix A" (normative surface list) as a living artifact — retirement timeline for remaining transitional shims is intentionally unresolved (`CNF-RUNTIME-SPINE-TRANSITIONAL-RETIREMENT`). No action required before marking Accepted; tracking continues in governance audit.

**Testing.** - **Inventory / classification:** verify Appendix A style lists stay current when new session routes land.
- **Review gate:** any new `backend/app/runtime/` or session API must declare retire | quarantine | compat per this ADR.
- **Failure mode:** undocumented player-truth claims on backend paths or missing deprecation labels on transitional shims.

**Evidence.** `docs/architecture/project/components/backend/architecture.md#d1-backend-session-quarantine` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Frontend / Backend Restructure (separate Backend and administration-tool frontend)

**Status:** 
**Origin:** ADR-0016 (retired 2026-06-23)

**Context.** An architectural decision was made to split the repository into a `Backend/` process (data, API, auth, dashboard, persistence, tests) and a lightweight `administration-tool/` frontend (public landing, news pages, static assets) that consumes the Backend API. This move preserves existing auth patterns and avoids duplicating business logic.

**Decision.** - Move data, API, auth, migrations, and protected UI (dashboard, game-menu) into `Backend/`.
- Implement a thin `administration-tool/` frontend that serves public pages and consumes `Backend` APIs only.
- Keep login/register/dashboard in `Backend/` (session + CSRF); `administration-tool/` contains only public pages and static assets.
- Implement `News` (or `Post`) model and `/api/v1/news` in Backend; frontend consumes it.
- Use `FRONTEND_URL` configuration to coordinate redirects and origin-dependent behavior.

**Consequences.** - Repository reorganization required: files moved with `git mv`, import path updates, and CI adjustments.
- Backend storage and instance paths must be updated and accounted for in deployment/dockers.
- Public pages may require CORS or reverse-proxy configuration to access Backend APIs.

**Implementation status.** **Implemented — restructure is complete and stable.**

- `frontend/` is the canonical player/public web frontend (Flask, `frontend/app/__init__.py` creates the app, `frontend/app/routes_play.py` handles play routes).
- `administration-tool/` is the separate admin/management frontend that proxies to backend API (confirmed by `tools/_extract_admin_route_registration.py`, `README.md` service table, and `docs/development/LocalDevelopment.md`).
- `backend/` owns data, API, auth, migrations, and game-menu — no player canonical HTML hosting.
- `FRONTEND_URL` configuration coordinates redirects; `backend/` redirects `GET /` to `/backend` (operator/developer surface).
- Docker Compose starts all three services separately: `backend`, `frontend`, `administration-tool`.
- `News` (or `Post`) model and `/api/v1/news` exist in backend; administration-tool consumes via API.
- Status promoted from "Proposed" because the restructure has been live for multiple MVPs.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/components/backend/architecture.md#d2-frontendbackend-restructure` (archived — see `docs/archive/adr-retired-2026/`)

### D3: Backend test suite split in canonical orchestrator

**Status:** 
**Origin:** ADR-0037 (retired 2026-06-23)

**Context.** The backend pytest tree under `backend/tests/` grew to thousands of tests and long wall-clock times for `python tests/run_tests.py --suite backend`. Developers need **fast, scoped runs** without abandoning the single canonical entrypoint (`tests/run_tests.py` per project discipline). Cross-folder selection for flat top-level test files also required **explicit domain markers** in `backend/pytest.ini`. Optional **pytest-xdist** parallelization must remain **off by default** and must not break ordering-sensitive or timing-sensitive tests.

**Decision.** 1. **Canonical full gate unchanged:** `python tests/run_tests.py --suite backend` remains the authoritative “run the entire backend pytest tree” command for CI and merge gates.
2. **Directory-based sub-suites** are registered as additional `--suite` choices (`backend_runtime`, `backend_observability`, `backend_services`, `backend_content`, `backend_routes_core`, `backend_mcp`, `backend_rest`). They share `cwd=backend/` and reuse `backend/pytest.ini`. **`backend_rest`** collects `backend/tests` while **ignoring** paths already covered by the other sub-suites (and dedicated `writers_room` / `improvement` slices).
3. **Coverage gates on sub-suites:** orchestrator sets **`supports_coverage=False`** for these sub-suites so partial runs do not enforce the backend-wide `--cov-fail-under` against incomplete execution.
4. **Domain axis:** `--domain <name>` maps to pytest `-m` using markers registered in `backend/pytest.ini` (`auth`, `observability`, `runtime`, `routes_core`, `content`, `services`, `writers_room`, `improvement`, `mvp_handoff`). It **combines with `--scope`** via logical **and** (e.g. `contract and auth`).
5. **`@pytest.mark.serial`:** ordering-sensitive or wall-clock-sensitive tests are tagged `serial`. When `--parallel` is used, the runner executes **two passes**: parallel workers with `-m "… and (not serial)"` plus **`--dist loadfile`**, then a **sequential** pass with `-m "… and (serial)"`. Exit code **5** (no tests collected) on the serial pass is acceptable when no serial tests match the selection.
6. **Dependencies:** `pytest-xdist` is listed in `backend/requirements-test.txt`; parallel execution is opt-in via `--parallel [auto|N]`.

**Consequences.** **Positive:** Faster feedback via sub-suites and optional parallel full-backend runs; cross-folder domain filtering for marked modules; CI can stay pinned to `--suite backend`.

**Negative / risks:** Parallel runs can hide shared-state bugs unless tests are isolated or marked `serial`. Domain markers require ongoing hygiene on new top-level test files.

**Follow-ups:** Optional Stage 4 (changed-file / test-impact selection) remains out of scope until explicitly approved.

**Testing.** - **Verify:** `python tests/run_tests.py --suite backend --quick` matches prior green counts for the full backend tree.
- **Verify:** `python tests/run_tests.py --suite backend --quick --parallel auto` completes with the same pass/skip totals (two internal passes).
- **Failure modes:** Drift between documented suite keys and `SUITE_CONFIGS` in `tests/run_tests.py`; missing marker registration in `backend/pytest.ini` breaking `--domain`.

**Evidence.** `docs/architecture/project/components/backend/architecture.md#d3-test-suite-split-in-orchestrator` (archived — see `docs/archive/adr-retired-2026/`)

### D4: Security governance admin plane

**Status:** Accepted · **Migrated from:** ADR-0052

**Decision.** Security governance mutations route through backend admin control plane with documented browser mutation boundaries.

**Evidence.** [`backend/app/services/governance/`](../../../../backend/app/services/governance/), [security-governance SAD D3](../../project/security-governance/architecture.md#d3-security-governance-admin-control-plane).

## 10. Quality Requirements

`backend/tests/`, `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py`, `python tests/run_tests.py --suite backend`.

## 11. Risks & Technical Debt

Transitional `SessionState` paths still in tree for tests—must not be mounted as live API.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| game_service | HTTP client facade to play service |
