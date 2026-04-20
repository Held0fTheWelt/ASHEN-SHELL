# ADR-0002: Backend session surface quarantine and authority labeling

## Status

Accepted

## Context

The backend still exposes session-shaped and operator-facing surfaces that are useful for bootstrap, diagnostics, tests, and MCP-style tooling.
Without explicit quarantine and labeling, future implementation cycles could attach to those surfaces as if they were authoritative session-truth surfaces.

That would create a drift pattern where backend-local session paths are mistaken for player-facing canonical truth.

## Decision

1. ADR-0001 remains the **sole normative owner** of runtime authority.
2. ADR-0002 does **not** define runtime authority. It defines the narrower rules for **backend session-surface quarantine**, **backend authority labeling**, and allowed backend use of non-authoritative session-shaped surfaces under the ADR-0001 authority model.
3. Backend session-shaped routes remain **quarantined** compatibility, bootstrap, or operator surfaces unless a future ADR explicitly reclassifies them.
4. Backend session surfaces must be documented and implemented so they cannot be mistaken for player/public truth boundaries.
5. MCP/operator access may use these backend surfaces only within the allowed governance scope and with no claim that they replace the world-engine authority model.



## Governed surface families

ADR-0002 currently governs only backend-side runtime/session-shaped surfaces that can be mistaken for live runtime authority if left unlabeled:

- **backend-local session compatibility surfaces**
  - `backend/app/api/v1/session_routes.py`
  - `backend/app/runtime/session_store.py`
  - `backend/app/services/session_service.py`
- **backend operator/admin bridge surfaces touching live runtime**
  - `backend/app/api/v1/world_engine_console_routes.py`

It does **not** reclassify these surfaces into runtime authority. It governs how they may continue to exist while ADR-0001 remains in force.

## What quarantine means in the current package

**Permitted today**

- expose backend-local, volatile, clearly warned session-shaped data for compatibility, tests, MCP, or bounded operator use;
- bridge to the world-engine for authoritative state, diagnostics, and turn execution;
- keep explicit warnings, auth/capability controls, and non-authoritative labeling in responses and code comments;
- keep unresolved retirement timing open when real callers/tests/operator flows still depend on a surface.

**Forbidden today**

- presenting any backend-local session surface as canonical player/public runtime truth;
- expanding backend-local session storage into a durable or cross-process runtime authority layer;
- treating operator/admin bridges as evidence that Flask hosts the live run;
- claiming retirement is complete before code, callers, tests, and review evidence actually support that claim.

## Current package status

| Surface | Current role class | Current status |
|---|---|---|
| `backend/app/api/v1/session_routes.py` | `compatibility_only`, `bridge_consumer`, `pending_retirement` | still present; may expose volatile local state and bridge to world-engine, but is not runtime authority |
| `backend/app/runtime/session_store.py` | `volatile_local_state`, `retained_for_tests`, `pending_retirement` | still present; process-local compatibility store only |
| `backend/app/services/session_service.py` | `compatibility_only`, `bridge_consumer`, `pending_retirement` | still present; local bootstrap helper only, with deferred methods intentionally unimplemented |
| `backend/app/api/v1/world_engine_console_routes.py` | `operator_support`, `bridge_consumer` | intentionally retained admin/operator bridge; not part of the current retirement-open trio |

## Closure-readiness distinctions

ADR-0002 now distinguishes four different states that must not be blurred:

- **quarantined but present** — a backend session-shaped surface still exists and is governed as non-authoritative;
- **retained operator support** — a surface is intentionally kept for admin/operator observation or operation against world-engine and is **not** automatically part of the retirement-open subset;
- **retirement-open** — a surface remains present, governed, and still needs dependency/validation evidence before any honest retirement-ready claim could be made;
- **retirement-ready / retired** — only after code/classification/dependency evidence and re-audit proof show that the surface is no longer required or has been explicitly reclassified without authority drift.

## Retirement timing remains intentionally undecided

This package does **not** claim a completed retirement timeline for the backend-local session trio.
Retirement can only be claimed after a later re-audit verifies the concrete evidence listed in:

- `governance/V24_BACKEND_TRANSITIONAL_RETIREMENT_LEDGER.md`
- `docs/technical/architecture/backend-runtime-classification.md`
- `tests/smoke/test_backend_transitional_retirement_surface_contracts.py`

Until then, ADR-0002 governs **quarantine and labeling**, not successful retirement completion.

### Compact closure-readiness checks

A future retirement claim is honest only if all of the following are true for the relevant surface:

1. the surface is removed or explicitly reclassified in code and docs;
2. the caller/test/operator dependency that kept it alive is proven migrated, replaced, or no longer needed;
3. retained operator support is not falsely bundled into the retirement-open subset; and
4. re-audit evidence confirms that world-engine remains the only runtime authority boundary.

## Runtime-critical implementation surfaces

- `backend/app/api/v1/session_routes.py`
- `backend/app/runtime/session_store.py`
- `backend/app/services/session_service.py`
- `backend/app/api/v1/world_engine_console_routes.py`
- `backend/app/services/game_service.py`
- `ai_stack/mcp_canonical_surface.py`

## Validation anchors

- `backend/tests/test_session_routes.py`
- `backend/tests/test_session_api_contracts.py`
- `backend/tests/test_world_engine_backend_api_contracts.py`
- `backend/tests/services/test_session_service.py`
- `tests/smoke/test_backend_transitional_retirement_surface_contracts.py`

## Related

- [ADR-0001: Runtime authority in world-engine](adr-0001-runtime-authority-in-world-engine.md)
- [Runtime authority and state flow](../technical/runtime/runtime-authority-and-state-flow.md)
- [Backend runtime classification](../technical/architecture/backend-runtime-classification.md)
- [MCP technical integration](../technical/integration/MCP.md)
- [Normative contracts index](../dev/contracts/normative-contracts-index.md)
- [Backend transitional retirement ledger](../../governance/V24_BACKEND_TRANSITIONAL_RETIREMENT_LEDGER.md)

## POST-locality final resolution addendum

This pass narrowed the last dominant backend-local blocker further.

### Additional narrowing achieved

- POST-created bound sessions now minimize local compatibility state immediately after successful authoritative binding.
- `snapshot`, `state`, and `diagnostics` no longer silently perform unbound local fallback by default.
- Those surfaces now require either authoritative `world_engine_story_session_id` or explicit compatibility opt-in (`allow_backend_local_fallback=1`).

### What still remains

- POST still creates backend-local `SessionState`.
- Explicit compatibility fallback still exists for `snapshot`, `state`, and `diagnostics`.
- `session_store.py` still matters because POST bootstrap and explicit compatibility residue still exist.


## POST-locality final resolution addendum

This pass did not remove POST local bootstrap, but it did isolate it more cleanly in code shape.
`create_local_bootstrap_session(...)` is now the explicit bootstrap helper, while `create_session(...)` remains only compatibility alias residue.
