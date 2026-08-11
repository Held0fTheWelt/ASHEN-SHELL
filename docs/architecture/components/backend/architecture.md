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

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Flask platform and control plane for identity, community, content governance, persistence and the proxy boundary to world-engine.

**Authority rule:** Backend owns platform data and governed operator state; world-engine owns live narrative state.

**Git/archaeology scope:** `backend`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Platform ownership, operator delegation and live-runtime authority | [Backend — System Context](../../../../UML/Components/backend/components/c4-context.md) | Backend owns platform data and governed operator state; world-engine owns live narrative state. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

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
| Retired transitional runtime | `tests/gates/test_runtime_sessions_table_absent.py` (former `backend/app/runtime/` removed in Wave 6 G2) |
| Platform services | `backend/app/` |
| Schema history | `backend/migrations/`, `backend/alembic/` |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound structural decomposition

Only elements that participate in a container or component view are listed as building blocks. Actors, runtime states, data types and deployment nodes remain in their proper viewpoints instead of being misrepresented as structural decomposition.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| Authentication API (`auth`) | `component` | Issue and revoke platform sessions and tokens | Password/session/refresh-token policy | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Content Services (`content_service`) | `component` | Compile, review and publish authored content versions | Immutable version plus active pointer | [`backend/app/services/game/game_content_service.py`](../../../../backend/app/services/game/game_content_service.py) |
| Game API (`game_api`) | `component` | Create run bindings and proxy live play operations | No backend-local narrative commit | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game Service (`game_service`) | `component` | Call world-engine and map service responses | Internal HTTP and signed ticket | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Governance Services (`governance`) | `component` | Validate provider, route, security and runtime settings | Audit-producing admin mutation boundary | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| API v1 (`api`) | `container` | Expose platform, play-proxy and admin HTTP contracts | Blueprint routes with auth and rate limits | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| Domain Services (`services`) | `container` | Implement platform and governance use cases | Transaction-scoped service operations | [`backend/app/services/__init__.py`](../../../../backend/app/services/__init__.py) |
| Observability (`observability`) | `container` | Record platform traces, metrics and diagnostic evidence | Trace correlation with redaction | [`backend/app/observability/__init__.py`](../../../../backend/app/observability/__init__.py) |
| Persistence Models (`models`) | `container` | Represent backend and narrative-governance durable truth | SQLAlchemy models and Alembic schema | [`backend/app/models/__init__.py`](../../../../backend/app/models/__init__.py) |
| Retired Transitional Runtime (`compat`) | `container` | Document absence of former backend/app/runtime live-session surfaces | Retired; never player truth authority | [`tests/gates/test_runtime_sessions_table_absent.py`](../../../../tests/gates/test_runtime_sessions_table_absent.py) |
| World Engine (`world`) | `system` | Own live story sessions and commits | Internal story HTTP API plus signed ticket | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Player turn: frontend → `game_routes` → `game_service` HTTP → world-engine → response mapping.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| How backend creates trace/ticket context and delegates the live turn | `sequence` | [Backend — Player Turn Proxy](../../../../UML/Components/backend/sequence/play-proxy-sequence.md) | 5 |
| Authorization, validation, persistence and audit of operator changes | `sequence` | [Backend — Governed Admin Mutation](../../../../UML/Components/backend/sequence/governed-admin-mutation-sequence.md) | 3 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. A sequence or activity view must form one connected runtime path; a list of unrelated calls does not qualify as an end-to-end scenario. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

Flask app with alembic migrations; shares secrets with world-engine for tickets.

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

| Concern | Model | Nodes / stores |
| --- | --- | --- |
| Backend process, persistence, shared governance store and world-engine boundary | [Backend — Deployment](../../../../UML/Components/backend/deployment/backend-deployment.md) | Browser Clients, Backend Process, Backend Database, Redis, World Engine Process |

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

- Model routing: `backend/app/model_governance/model_routing.py` (adapter choice, traces).
- Operational governance routes tested in `backend/tests/test_operational_governance_*.py`.

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| API v1 | Retired Transitional Runtime | no longer routes through retired runtime package | absence enforced; never player truth authority | [`tests/gates/test_runtime_sessions_table_absent.py`](../../../../tests/gates/test_runtime_sessions_table_absent.py) |
| API v1 | Domain Services | invokes use cases | validated request DTOs | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| Authentication API | Domain Services | authenticates | identity and token services | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Content Services | Persistence Models | persists package lifecycle | immutable versions and events | [`backend/app/services/game/game_content_service.py`](../../../../backend/app/services/game/game_content_service.py) |
| Game API | Game Service | delegates live operation | proxy-only service seam | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game Service | World Engine | calls story API | ticketed HTTP request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Governance Services | Persistence Models | persists settings and audit | validated governance transaction | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Alembic Schema | Persistence Models | versions | Alembic migration history | [`backend/migrations/env.py`](../../../../backend/migrations/env.py) |
| Persistence Models | Narrative Governance Models | contains | governance read model ownership | [`backend/app/models/world_engine/__init__.py`](../../../../backend/app/models/world_engine/__init__.py) |
| Persistence Models | Platform Models | contains | platform ownership | [`backend/app/models/backend/__init__.py`](../../../../backend/app/models/backend/__init__.py) |
| Domain Services | Persistence Models | reads/writes durable truth | transaction boundary | [`backend/app/extensions.py`](../../../../backend/app/extensions.py) |
| Domain Services | Observability | emits evidence | redacted trace correlation | [`backend/app/observability/trace.py`](../../../../backend/app/observability/trace.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Backend session quarantine | Accepted | ADR-0002 |
| D2 | Frontend/backend restructure | Accepted | ADR-0016 |
| D3 | Test suite split in orchestrator | Accepted | ADR-0037 |
| D4 | Security governance admin plane | Accepted | ADR-0052 |

### D1: Backend session / transitional runtime surface - quarantine and retirement

**Status:** Accepted
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
- The former backend session API route, flat session service surfaces, and `tests/gates/test_runtime_sessions_table_absent.py` are retired. SQL `runtime_sessions` was dropped in Wave 6 G2 (Alembic 049); live session authority remains exclusively in world-engine.
- Governance investigation confirms `CTR-ADR-0002-BACKEND-SESSION-QUARANTINE` is implemented; validated by `backend/tests/test_session_routes.py` and `backend/tests/test_world_engine_console_routes.py`.
- One open gap: the ADR cites "Appendix A" (normative surface list) as a living artifact — retirement timeline for remaining transitional shims is intentionally unresolved (`CNF-RUNTIME-SPINE-TRANSITIONAL-RETIREMENT`). No action required before marking Accepted; tracking continues in governance audit.

**Testing.** - **Inventory / classification:** verify Appendix A style lists stay current when new session routes land.
- **Review gate:** any new `backend/app/runtime/` or session API must declare retire | quarantine | compat per this ADR.
- **Failure mode:** undocumented player-truth claims on backend paths or missing deprecation labels on transitional shims.

**Evidence.** `docs/architecture/components/backend/architecture.md#d1-backend-session-quarantine` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Frontend / Backend Restructure (separate Backend and administration-tool frontend)

**Status:** Accepted
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

**Evidence.** `docs/architecture/components/backend/architecture.md#d2-frontendbackend-restructure` (archived — see `docs/archive/adr-retired-2026/`)

### D3: Backend test suite split in canonical orchestrator

**Status:** Accepted
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

**Evidence.** `docs/architecture/components/backend/architecture.md#d3-test-suite-split-in-orchestrator` (archived — see `docs/archive/adr-retired-2026/`)

### D4: Security governance admin plane

**Status:** Accepted · **Migrated from:** ADR-0052

**Decision.** Security governance mutations route through the backend admin
control plane with documented browser mutation boundaries. The service layer
owns policy validation, credential handling and audit semantics; browser and
administration-tool routes may only invoke that boundary. This prevents
presentation code from becoming an alternative authority, keeps mutation
authorization consistent across operator surfaces and gives tests one
enforceable location for denial, confirmation and evidence behavior.

**Evidence.** [`backend/app/services/governance/`](../../../../backend/app/services/governance/), [security-governance SAD D3](../../project/security-governance/architecture.md#d3-security-governance-admin-control-plane).

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D1`, `D2`, `D4` | Platform ownership, operator delegation and live-runtime authority | `context` | [Backend — System Context](../../../../UML/Components/backend/components/c4-context.md) |
| `D1`, `D2` | API, service, persistence, compatibility and observability boundaries | `container` | [Backend — Runtime Containers](../../../../UML/Components/backend/components/c4-container.md) |
| `D1`, `D4` | Identity, play proxy, content and governance collaborations | `component` | [Backend — Core Components](../../../../UML/Components/backend/components/c4-component.md) |
| `D1` | How backend creates trace/ticket context and delegates the live turn | `sequence` | [Backend — Player Turn Proxy](../../../../UML/Components/backend/sequence/play-proxy-sequence.md) |
| `D4` | Authorization, validation, persistence and audit of operator changes | `sequence` | [Backend — Governed Admin Mutation](../../../../UML/Components/backend/sequence/governed-admin-mutation-sequence.md) |
| `D1`, `D2` | Separation of platform truth, narrative governance read models and schema evolution | `class` | [Backend — Persistence Ownership Model](../../../../UML/Components/backend/classes/backend-persistence-model.md) |
| `D2`, `D4` | Backend process, persistence, shared governance store and world-engine boundary | `deployment` | [Backend — Deployment](../../../../UML/Components/backend/deployment/backend-deployment.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

- Accepted decisions must resolve to executable backend source or an explicit
  gate contract.
- Public API and schema units inside the declared scan boundary must remain
  represented by a building block.
- Context, container, component and class views must stay source-linked and
  within the legibility bounds enforced by architecture assurance.
- Verification includes `backend/tests/`,
  `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py`, and
  `python tests/run_tests.py --suite backend`.

## 11. Risks & Technical Debt

Transitional `SessionState` paths still in tree for tests—must not be mounted as live API.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

Backend is the largest tracked area and changed heavily in services, API and runtime. Models distinguish durable platform ownership, proxy-only play paths and quarantined compatibility runtime.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 936 | 791 | 2409 | 278 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| `DRIFT-004` | `conflicting` | Authored content truth has several executable projections | Keep YAML modules as authored truth, generate or validate a versioned compiled content contract once, and make world-engine/AI consumers read that contract through anti-corruption adapters. |
| `DRIFT-008` | `open_target` | Observability contracts are fragmented across services | Define a minimal TurnTrace contract with propagated identity, owned spans, explicit gaps and redaction. Each service adapts locally but must satisfy the shared trace tree. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

| Term | Meaning |
| --- | --- |
| game_service | HTTP client facade to play service |
