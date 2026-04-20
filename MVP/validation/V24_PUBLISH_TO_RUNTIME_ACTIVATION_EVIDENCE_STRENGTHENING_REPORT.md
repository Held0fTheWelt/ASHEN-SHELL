# V24 Publish-to-Runtime Activation Evidence Strengthening Report

## Executive summary

This wave targeted the strongest remaining publish-to-runtime activation seam:

- published backend canon could override builtin runtime templates,
- but the runtime catalog did not cleanly revert when published content disappeared from the backend feed,
- and run detail provenance reflected the current catalog source rather than the template source actually activated for that run.

The implementation hardens that seam by:

1. reverting stale `backend_published` template overrides back to builtin templates when the backend published feed no longer exposes them,
2. persisting activation-time template provenance on each bootstrapped run,
3. using activation-time provenance in run details so existing runs keep their true bootstrap source and template summary even after later catalog changes.

This strengthens the MVP evidence that published canon is the active runtime path when available, while also making the unpublish/deactivation boundary explicit and bounded.

## Targeted seam

The targeted seam was:

**publish-state changes in the backend content feed were not fully reflected in runtime catalog fallback semantics, and run-detail provenance could drift after bootstrap because it was derived from the current catalog rather than the run's activation-time template.**

## Changed files

- `world-engine/app/runtime/manager.py`
- `world-engine/tests/test_runtime_manager.py`
- `backend/tests/test_backend_playservice_integration.py`

## What changed

### Runtime catalog fallback hardening

`RuntimeManager.sync_templates()` now actively removes stale `backend_published` overrides when the backend published feed no longer returns them.

Behavior now is:

- if a builtin template exists for that template id, the runtime catalog reverts to the builtin template and marks the source as `builtin`;
- if no builtin template exists, the stale remote-only template is removed from the active catalog.

This removes ambiguity where a previously published override could remain active in the runtime catalog after the backend feed stopped publishing it.

### Activation-time provenance capture

At run bootstrap and persisted-instance normalization, the runtime now records activation-time template provenance in instance metadata:

- `template_activation_source`
- `template_activation_template`

The stored activation snapshot includes:

- template id
- title
- kind
- join policy
- min humans to start

### Run detail provenance hardening

`RuntimeManager.get_run_details()` no longer reports `template_source` and template summary solely from the current runtime catalog.

Instead it resolves them from activation-time metadata first, with current-catalog fallback only when the run does not yet carry activation metadata.

This means:

- an existing run started from published canon continues to report `backend_published` and its published template summary even if the backend later unpublishes that template;
- a new run created after unpublish cleanly reports `builtin` and the builtin template summary.

## What did not change

This wave did **not**:

- redesign publishing architecture,
- change Writers’ Room governance flow,
- make backend authoritative for gameplay truth,
- collapse retrieval/model output into canonical truth,
- change shell response shape,
- broaden into OpenAPI/Postman/documentation cleanup.

## Authority and publishing boundary preservation

Authority boundaries remain intact:

- backend published content remains the canonical published-content feed,
- world-engine remains the active authoritative runtime consumer,
- activation provenance is recorded as runtime metadata for honesty and continuity only,
- no new truth owner was introduced,
- retrieval/model output still does not become canonical runtime truth by side effect.

## Validation performed

### Executed successfully

1. Syntax validation:
   - `python -m py_compile world-engine/app/runtime/manager.py world-engine/tests/test_runtime_manager.py backend/tests/test_backend_playservice_integration.py`

2. Runtime-manager executable proof:
   - `cd world-engine && pytest -q tests/test_runtime_manager.py -q`

   Result: **PASS**

   This includes the new test proving:
   - published override is active when available,
   - runtime catalog reverts to builtin after published removal,
   - existing runs preserve published activation provenance,
   - new runs after removal use builtin provenance.

### Attempted but environment-blocked in this container

3. Backend bridge integration pytest:
   - `cd backend && pytest -q tests/test_backend_playservice_integration.py -q`

   Result: **BLOCKED BY ENVIRONMENT**

   Failure in this container occurred during backend app import through `tests/conftest.py` because `langchain_core` is not installed here.

4. Live mutable-feed backend→play-service script execution:
   - attempted separately outside full backend pytest to validate the new mutable published-feed scenario,
   - world-engine startup in this container was blocked by the AI stack import/export environment (`RuntimeTurnGraphExecutor` export path during `uvicorn` startup).

## Validation results

### Strongly executable proof now present

- runtime-side activation fallback/provenance proof is now directly executable and passing,
- a real backend integration test for the mutable published-feed scenario now exists in the package, even though this container could not execute the full backend stack path.

### Environment-bounded proof still not executed here

The bridge/full live-stack validation remains bounded in this container by missing heavy AI/runtime dependencies and startup/export environment issues, not by the targeted publish-to-runtime code path itself.

## Integration-readiness impact

This wave materially improves frozen-repo integration readiness by making two assumptions explicit and testable:

1. **Published canon wins when available** — runtime catalog can activate backend-published templates.
2. **Removal of published canon does not silently corrupt active runs** — existing runs keep their real activation provenance, while new runs revert to builtin fallback when the published feed no longer provides the template.

Frozen-repo integration should preserve:

- backend published-content feed as the canonical activation source,
- runtime-side bootstrap provenance capture,
- explicit fallback to builtin only when the backend published feed no longer exposes the template.

## Remaining bounded residue

1. **Full backend bridge execution in this container remains blocked by environment**
   - backend pytest import path requires dependencies not installed here (`langchain_core` and related stack),
   - live `uvicorn` world-engine startup in this container is additionally bounded by the AI stack export/import environment.

2. **Remote-only template persistence across restart remains bounded**
   - active in-memory runs preserve activation provenance,
   - but a fully removed remote-only template after process restart would require broader persisted template snapshotting if continued execution after restart were required.
   - That is beyond this wave and beyond the current MVP seam targeted here.

## Wave closure judgment

**Reduced but still open.**

Why:

- the targeted activation seam itself was materially fixed and strongly improved,
- runtime-side executable proof is now strong,
- but the full backend bridge/live-stack activation evidence could not be executed in this container due environment/runtime dependency blockers.

So the implementation seam is reduced to a bounded remainder, but strict closure on full executable proof is still environment-bounded here.

## Re-audit hook

A strict re-audit should verify:

1. stale backend-published template overrides now revert cleanly to builtin when removed from the backend published feed,
2. run-detail `template_source` reflects activation-time provenance rather than later catalog drift,
3. existing runs started from published canon keep their published provenance after unpublish,
4. new runs created after unpublish use builtin fallback explicitly,
5. remaining bridge/full-stack proof is treated as bounded residue unless executed in a complete environment.

## Recommended next wave

**Live activation proof execution hardening for full backend↔world-engine startup path**

Scope:

- do not redesign publish/runtime architecture,
- do not reopen shell or backend retirement,
- focus only on making the heavy environment/runtime import path executable enough to run the strengthened backend bridge activation tests end to end.
