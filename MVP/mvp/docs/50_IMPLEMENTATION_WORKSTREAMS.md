# 50 — Implementation Workstreams

## Workstream A — Runtime authority and session truth

Goal: keep world-engine authoritative while allowing backend and operator surfaces to observe safely.

Primary paths:
- `world-engine/app/`
- `backend/app/api/v1/session_routes.py`
- `backend/app/services/game_service.py`
- `backend/app/runtime/session_store.py`
- `backend/tests/runtime/`
- `world-engine/tests/`

Typical implementation points:
- session creation and binding,
- turn execution proxying,
- diagnostics/state read-only mirrors,
- bridge failure envelopes,
- truth-boundary enforcement.

## Workstream B — Runtime-safe MCP surface

Goal: expose session tools without granting false authority from the wrong service.

Primary paths:
- `tools/mcp_server/`
- `backend/app/mcp_client/`
- `backend/app/api/v1/session_routes.py`
- `ai_stack/mcp_canonical_surface.py`

Typical implementation points:
- `wos.session.get`
- `wos.session.state`
- `wos.session.logs`
- `wos.session.diag`
- `wos.session.execute_turn`
- registry descriptors and operating-profile gating.

## Workstream C — Player route purity and launch flow

Goal: keep player/public routes clean while preserving launch/bootstrap behavior.

Primary paths:
- `frontend/`
- `backend/app/web/`
- `backend/app/config.py`
- `tests/e2e/`
- `tests/smoke/`

Typical implementation points:
- launcher/bootstrap/ticket flow,
- redirects,
- shell bootstrap,
- route purity,
- no operator leakage.

## Workstream D — AI stack runtime integration

Goal: keep generative behavior governed, inspectable, and aligned to committed runtime truth.

Primary paths:
- `ai_stack/`
- `story_runtime_core/`
- `world-engine/app/runtime/`
- `backend/app/runtime/`

Typical implementation points:
- LangGraph node contracts,
- retrieval and packaging seams,
- preview versus commit separation,
- diagnostics references,
- fallback and degraded behavior.

## Workstream E — Governance and review surfaces

Goal: expose the right information to the right audience without collapsing player/operator separation.

Primary paths:
- `administration-tool/`
- `backend/app/api/v1/ai_stack_governance_routes.py`
- `backend/app/services/`
- `writers-room/`

Typical implementation points:
- inspector bundles,
- governance reports,
- review-bound surfaces,
- incident visibility,
- authoring/admin quality workflows.

## Workstream F — Validation and release honesty

Goal: prevent closure theater.

Primary paths:
- `tests/`
- service test suites,
- implementation-facing docs,
- this MVP package.

Typical implementation points:
- missing tests,
- docs/code/test drift,
- stale readiness claims,
- incomplete validation reporting.
