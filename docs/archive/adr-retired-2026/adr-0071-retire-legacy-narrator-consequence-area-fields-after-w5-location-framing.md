---
adr: "0071"
title: "Retire Legacy Narrator Consequence Area Fields After W5 Location Framing"
status: Proposed
date: 2026-05-30
replaces: []
superseded_by: []
---

# ADR-0071: Retire Legacy Narrator Consequence Area Fields After W5 Location Framing

## Status

Proposed.

Phase 6C-5 defines removal readiness only. It does not remove
`current_area`, `from_area`, `to_area`, malformed-W5 fallback, old-payload
fallback, public aliases, substrate fields, or committed output.

Phase 6C-6 implements the compatibility shim described by this ADR:
`w5_location_framing_to_legacy_area_fields()`,
`build_legacy_area_compat_from_w5_location_framing()`, and
`ensure_legacy_area_fields_for_compat()`. The shim is test-backed and proves
W5-native narrator/sensory consumers can operate without direct
`current_area/from_area/to_area` input while legacy consumers still receive
derived compatibility fields. Removal is still not approved.

## Context

ADR-0070 moved narrator-consequence and sensory-context location decisions to
W5-first behavior. After Phase 6C-4:

- Graph state synthesizes `w5_location_framing` on the default path.
- Valid W5 framing is authority when `source == "w5_projection"` and a usable
  current, scene, or target location exists.
- `build_local_context_transition()` and `derive_sensory_context()` prefer
  valid W5 framing.
- `location_framing_authority` reports `"w5"` or `"legacy_fallback"`.
- `local_context_transition_source` reports `"w5_location_framing"` or
  `"legacy"`.
- `current_area`, `from_area`, and `to_area` remain compatibility/fallback
  fields in the local-context transition shape.

The remaining question is not whether W5 is authority. It is whether removing
the legacy area fields from narrator-consequence and sensory-context consumers
is safe without breaking fallback paths, old payloads, tests, diagnostics, or
downstream consequence realization.

## Covered Fields

This ADR covers internal narrator/sensory location-framing compatibility fields:

- `current_area`
- `from_area`
- `to_area`
- legacy `local_context_transition` area fields when they are compatibility or
  fallback values rather than authority
- `scene_changed` / `location_changed` legacy framing only where W5
  `w5_location_framing.location_changed` already supplies authority

## Explicitly Out Of Scope

This ADR does not cover:

- public `current_room`, `current_room_id`, or `viewer_room_id` aliases
- `runtime_world.current_room_id`
- `environment_state.current_room_id`
- `environment_state.current_area`
- `actor_locations`
- `complete_actor_locations_for_gathering`
- NPC context bundle fallback
- malformed-W5 fallback
- old-payload fallback
- substrate consolidation

Those surfaces remain governed by ADR-0069, ADR-0070, or future substrate/public
compatibility ADRs.

## Decision

Removal is not approved yet.

The legacy area fields may be retired from narrator-consequence and
sensory-context runtime consumers only after the readiness checklist in this
ADR is fully satisfied and a follow-up removal phase proves the code change with
semantic parity tests. Until then, they remain compatibility/fallback fields.

W5 location framing remains the authority for valid default-path decisions.
Legacy fields are allowed only as:

- malformed-W5 fallback
- missing-W5 fallback
- old-payload fallback
- compatibility output for downstream consumers that still expect the old
  transition shape
- historical test/doc references clearly marked as such

## Removal Preconditions

Before any runtime field removal, all of the following must be true:

1. W5 location framing is synthesized in graph state on the default path.
2. Narrator consequence uses W5 framing when valid.
3. Sensory context uses W5 framing when valid.
4. Malformed and missing W5 fallback remains tested.
5. Old-payload fallback remains tested.
6. Parity tests prove output equivalence where W5 and legacy agree.
7. No production default path depends on `current_area`, `from_area`, or
   `to_area` as authority.
8. Docs and tests no longer describe legacy area fields as primary authority.
9. Public aliases are unaffected and remain governed by ADR-0069.
10. Substrate fields are unaffected and remain governed by future substrate
    ADRs.
11. Downstream narrator consequence realization and sensory-context consumers
    can run without requiring area-field presence except through an explicit
    compatibility shim.
12. A rollback plan exists that can restore compatibility field emission without
    changing committed events.
13. ADR-0071 is accepted for actual runtime field removal.
14. Production-like downstream traces prove zero unsupported dependency on
    direct area-field presence.

## Fallback Policy

Fallbacks must remain deterministic and non-crashing:

- If W5 is valid, W5 supplies location authority.
- If W5 is missing, malformed, incomplete, or explicitly unsuitable for a
  current pre-commit movement target, legacy fallback supplies the decision.
- If old payloads lack `w5_location_framing`, the legacy transition path remains
  available.
- Fallback diagnostics must continue to distinguish `"w5"` from
  `"legacy_fallback"`.
- The Phase 6C-6 compatibility shim may emit only these source labels:
  `"w5_location_framing"`, `"legacy_fallback"`,
  `"malformed_w5_fallback"`, or `"old_payload_fallback"`.

## Malformed-W5 And Old-Payload Policy

Malformed W5 and old payloads are not failure cases for this migration. They are
supported compatibility windows. Removing area fields is unsafe until those
windows are either closed by a separate decision or replaced by a smaller
compatibility shim with equivalent tests.

## Test Gates Before Removal

Required gates before any removal phase:

- `python scripts/inventory_w5_legacy_consumers.py`
- `pytest -q tests/test_inventory_w5_legacy_consumers.py`
- `pytest -q ai_stack/tests/test_w5_actor_tracking_location_framing.py`
- `pytest -q ai_stack/tests/test_w5_actor_tracking_projection.py ai_stack/tests/test_w5_actor_tracking_validation.py`
- `pytest -q tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py`
- `pytest -q tests/gates/test_goc_mvp04_observability_diagnostics_gate.py tests/test_local_langfuse_docker_config.py`
- focused narrator-consequence, sensory-context, and LangGraph runtime tests
  that assert semantic output parity rather than field presence only

The removal phase must also prove:

- valid W5 path uses `location_framing_authority="w5"`
- fallback path uses `location_framing_authority="legacy_fallback"`
- `local_context_transition_source` is correct for both paths
- no raw W5 history is emitted
- How remains first-class
- inferred Why remains soft truth

## Rollout Plan

1. Phase 6C-5: create this Proposed ADR and readiness checklist; do not remove
   runtime fields.
2. Phase 6C-6: add the explicit compatibility shim needed to make area-field
   presence optional for W5-native consumers.
3. Phase 6C-7: perform a final removal-readiness audit and collect
   production-like dependency evidence.
4. Later accepted removal phase: if readiness is fully green, remove the runtime dependency on
   area-field authority while preserving any explicitly approved compatibility
   output.
5. Later phase: remove compatibility output only if a separate inventory shows
   no supported fallback/public/substrate dependency.

## Rollback Plan

If a future removal phase regresses runtime behavior, rollback by restoring the
compatibility field projection from `w5_location_framing` into the
`local_context_transition` shape. The rollback must not mutate committed events
or reinterpret W5 history.

Phase 6C-6 makes that rollback path explicit through
`ensure_legacy_area_fields_for_compat()`, which derives
`current_area/from_area/to_area` from valid W5 framing and preserves legacy
values when W5 is missing, malformed, or an old payload has no W5 framing.

## Phase 6C-6 Readiness Update

The compatibility-shim criterion is now satisfied:

- `w5_location_framing_to_legacy_area_fields()` derives
  `current_area/from_area/to_area` from valid `w5_location_framing.v1`.
- Missing W5 uses `old_payload_fallback` or `legacy_fallback`.
- Malformed W5 uses `malformed_w5_fallback`.
- The shim is non-mutating and emits no raw W5 history.
- How remains first-class via W5 framing; inferred Why remains soft truth and
  is not promoted to observed truth.

`removal_ready` remains false because this ADR is still Proposed.

## Phase 6C-7/6C-8 Readiness Update

Phase 6C-7/6C-8 collected dependency evidence across narrator consequence,
sensory context, LangGraph SOURCE_LINES, language-adapter surfaces, tests, and
inventory output. The evidence proves a narrow safe scope, but not global
runtime field removal.

**Narrow safe scope:** W5-native narrator/sensory consumers can run without
direct `current_area/from_area/to_area` input when valid
`w5_location_framing` is present. Legacy compatibility consumers can receive
those fields through `legacy_area_compat.v1`.

**Readiness table:**

| Dependency | Classification | W5 primary by default | Removal result |
|---|---|---:|---|
| `w5_location_framing_to_legacy_area_fields()` | `area_compat_shim` | yes | Keep; this is the rollback/compat shim |
| `location_framing_to_local_context_transition()` | `shimmed_compatibility_dependency` | yes | Keep until LocalContextTransition contract changes |
| `_current_context_area()` | `malformed_w5_safety_dependency` | yes | Removal breaks malformed-W5 / old-payload fallback |
| `build_local_context_transition()` | `shimmed_compatibility_dependency` | yes | Removal changes transition metadata shape |
| `build_updated_player_local_context()` | `blocker_requires_refactor` | yes | Removal changes carried local context and committed output metadata |
| `sensory_context_engine._current_location_id()` | `old_payload_compat_dependency` | yes | Removal breaks sensory old-payload fallback |
| LangGraph `_resolve_player_action` | `malformed_w5_safety_dependency` | yes | Removal breaks graph fallback synthesis |
| LangGraph sensory derivation | `w5_native_no_area_dependency` | yes | No removal needed; keep W5 threading |
| `language_adapter._interaction_surface_cached()` | `blocker_requires_refactor` | no | Needs non-cached W5 runtime overlay design |
| semantic planner content-frame fallback | `public_or_substrate_out_of_scope` | no | Out of ADR-0071; future planner/substrate ADR |

**Result:** `removal_ready=false`.

**Remaining blockers:**

- ADR-0071 remains Proposed.
- `build_updated_player_local_context()` still consumes `to_area/current_area`
  to carry player-local context between turns.
- `_current_context_area()` and `_current_location_id()` still require legacy
  area fields for malformed-W5 and old-payload fallback.
- `language_adapter._interaction_surface_cached()` still exposes
  content-derived `current_area` outside the shim.
- Semantic planner content-frame fallback reads `environment_state.current_area`
  / `current_room_id` and is out of this ADR's removal scope.
- Removing the runtime fields globally would change committed output metadata.

The next larger package should add a W5-native carried-local-context helper and
a language-adapter/runtime-overlay design, then rerun dependency evidence before
any accepted removal phase.

## Accepted Risks

- Keeping compatibility fields longer creates some duplicate location metadata.
- Removing them too early risks malformed-W5 and old-payload regressions.
- Phase 6C-7/6C-8 evidence proves nonzero dependency; keeping the fields is the
  safer migration posture until the listed blockers are refactored.

## Rejected Alternatives

1. **Remove `current_area/from_area/to_area` immediately.**
   Rejected because fallback and compatibility consumers remain intentionally
   supported after Phase 6C-4.

2. **Fold public room aliases into this removal ADR.**
   Rejected because public aliases are governed by ADR-0069 and client-readiness
   telemetry.

3. **Remove substrate location fields at the same time.**
   Rejected because substrate fields feed commits, W5 extraction, and future
   substrate ADR work.

4. **Treat malformed-W5 fallback as obsolete because W5 is now default.**
   Rejected because default authority and fallback safety are separate
   guarantees.
