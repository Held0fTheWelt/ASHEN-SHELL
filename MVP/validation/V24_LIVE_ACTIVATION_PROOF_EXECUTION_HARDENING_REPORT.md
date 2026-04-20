# V24 Live Activation Proof Execution Hardening Report

## Executive summary

This wave targeted the remaining execution blockers that prevented the strengthened publish-to-runtime activation proof from running through the real backend ↔ world-engine bridge path in the current package environment.

The two real blockers were:

1. **Backend import breadth**: backend test startup imported Writers’ Room services eagerly through route registration, which pulled in `langchain_core` even though the targeted activation proof does not exercise Writers’ Room endpoints.
2. **World-engine startup breadth**: the FastAPI app imported and instantiated the story runtime graph stack eagerly during process startup, which pulled in optional LangGraph/LangChain-heavy AI runtime pieces even though the targeted activation proof only requires the authoritative play runtime manager.

Both blockers were narrowed without changing publish/runtime semantics.

After hardening, the bridge-facing backend integration proofs now execute successfully in this environment, including the mutable published-feed activation scenario.

## Files changed

- `backend/app/api/v1/writers_room_routes.py`
- `world-engine/app/api/http.py`
- `world-engine/app/main.py`
- `validation/V24_LIVE_ACTIVATION_PROOF_EXECUTION_HARDENING_REPORT.md`

## Blockers targeted

### 1. Backend test import/startup blocker

`backend/tests/test_backend_playservice_integration.py` depends on the normal backend app bootstrap path. During import, `app/api/v1/writers_room_routes.py` imported Writers’ Room services eagerly, which in turn imported `langchain_core.documents.Document`.

That dependency is declared in project TOML files, but it is not required for the targeted publish-to-runtime activation proof itself.

### 2. World-engine startup blocker

`world-engine/app/main.py` imported `StoryRuntimeManager` eagerly and instantiated it during FastAPI lifespan startup. In this environment, optional AI graph exports were not available, so world-engine boot failed before `/api/health` and the play-service HTTP runtime became available.

Again, that story runtime path is not load-bearing for the targeted activation proof, which exercises:

- backend published feed consumption,
- runtime template synchronization,
- run creation / join / details / transcript / termination,
- and published→fallback activation behavior.

## What changed

### Backend: lazy Writers’ Room service import

`backend/app/api/v1/writers_room_routes.py` now loads Writers’ Room services lazily inside a helper instead of importing them at module import time.

Effect:
- normal route behavior stays unchanged when Writers’ Room endpoints are actually invoked,
- unrelated backend startup no longer fails on cold/minimal environments that lack Writers’ Room AI dependencies,
- the targeted bridge proof can use the real backend bootstrap path instead of a fake/minimal app.

### World-engine: bounded story-runtime soft failure in test-mode startup

`world-engine/app/main.py` no longer hard-requires `StoryRuntimeManager` during startup when running in test mode (or when explicitly allowed via `WOS_SOFT_DISABLE_STORY_RUNTIME_ON_IMPORT_ERROR=1`).

Effect:
- authoritative play runtime startup remains real,
- ticket manager and runtime manager still start normally,
- story runtime unavailability becomes explicit state instead of blocking the entire play-service process.

### World-engine: explicit 503 for story endpoints when story runtime is unavailable

`world-engine/app/api/http.py` no longer imports `StoryRuntimeManager` eagerly at module import time. Story endpoints resolve the manager dynamically.

If story runtime is unavailable, those endpoints now return an explicit `503 Story runtime unavailable: ...` instead of crashing process startup.

Effect:
- no silent semantic substitution,
- unrelated core play-service endpoints still execute,
- bounded failure remains explicit and authority-safe.

## What did not change

This wave did **not**:

- change publish-to-runtime activation semantics,
- redesign runtime, publishing, or session architecture,
- make backend authoritative for gameplay truth,
- collapse authoring/publishing/retrieval/runtime boundaries,
- broaden into general dependency modernization,
- claim story-runtime graph execution now works in this minimal environment.

The already-established semantics remain intact:

- published canon wins when available,
- stale published overrides revert cleanly,
- existing runs keep activation provenance,
- new runs after unpublish fall back explicitly to builtin content.

## TOML / dependency clarification

Relevant project declarations found during this wave:

- `backend/pyproject.toml`
- `world-engine/pyproject.toml`
- `ai_stack/pyproject.toml`

These files declare the heavy LangChain/LangGraph dependencies expected in a full repo environment. The blocker in this package session was not that those declarations were wrong, but that unrelated imports forced those optional-heavy surfaces into the targeted proof path before they were actually needed.

## Validation performed

### Syntax / compile checks

- `python -m py_compile backend/app/api/v1/writers_room_routes.py world-engine/app/api/http.py world-engine/app/main.py`

### Real bridge-facing activation proof

Executed successfully:

- `cd backend && pytest -q tests/test_backend_playservice_integration.py::test_backend_to_playservice_happy_path -q`
- `cd backend && pytest -q tests/test_backend_playservice_integration.py::test_backend_to_playservice_preserves_published_run_provenance_after_unpublish -q`
- `cd backend && pytest -q tests/test_backend_playservice_integration.py::test_backend_contract_failure_on_missing_required_field_with_live_playservice -q`

These tests start the real world-engine process via `uvicorn`, configure the backend to use that play-service bridge, and exercise the strengthened activation path.

## Validation results

All targeted validations passed.

Most importantly, the previously blocked backend ↔ world-engine bridge proof now executes successfully for:

- published template discovery through the backend feed,
- authoritative run creation on the play-service,
- run detail retrieval showing published activation,
- published-feed mutation / unpublish fallback behavior,
- preservation of published-origin run provenance after removal,
- and explicit builtin fallback for new runs created after removal.

## Proof execution statement

The strongest honest bridge-facing activation proof available in this environment now runs.

What is now directly executed and proven:

- the backend uses the published feed as canonical activation source,
- the world-engine syncs and activates that published template,
- backend calls across the bridge hit the live play-service process,
- published-origin runs retain their activation provenance after backend feed removal,
- new runs after removal fall back to builtin content.

What is still not claimed:

- that the optional story-runtime graph stack is fully available in this minimal environment,
- or that a broader full-stack story-runtime proof has now executed.

## Blocker reduction statement

### Fully removed

- **Backend import blocker**: eager Writers’ Room route imports no longer prevent backend startup for the targeted activation proof path.
- **World-engine startup blocker on the targeted proof path**: optional story-runtime import failure no longer prevents authoritative play-service startup in test-mode proof execution.

### Narrowed

- **Optional heavy AI runtime coupling**: still exists for story-runtime functionality, but is no longer load-bearing for the publish-to-runtime activation proof path.

### Remaining bounded residue

- In this minimal environment, the optional story-runtime graph stack may still be unavailable. That remains explicit and bounded to story endpoints via 503 rather than blocking the play-service process.

## Integration-readiness impact

This wave materially improves frozen-repo integration trustworthiness because the package now demonstrates the actual backend ↔ world-engine activation bridge in execution, not only runtime-local logic.

The porting blueprint should preserve:

- backend published feed as the canonical activation source,
- runtime activation provenance captured by the world-engine,
- play-service startup independence from unrelated optional story-runtime graph imports when executing bridge-only activation proofs.

## Wave closure judgment

**Closed.**

Reason:
- the previously blocked bridge-facing activation proof now executes successfully,
- the targeted blockers were narrowed or removed without changing activation semantics,
- remaining residue is explicit, bounded, and no longer blocks the targeted proof path.
