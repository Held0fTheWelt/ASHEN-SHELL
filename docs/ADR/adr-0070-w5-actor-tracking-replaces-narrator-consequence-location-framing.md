---
adr: "0070"
title: "W5 Actor Tracking Replaces Narrator Consequence Location Framing"
status: Accepted
date: 2026-05-29
replaces: []
superseded_by: []
---

# ADR-0070: W5 Actor Tracking Replaces Narrator Consequence Location Framing

## Status

Accepted for planning and next-phase implementation.

Phase 6C-0 creates the ADR, inventory, and implementation plan only. It does
not change runtime narrator consequence, sensory-context, public payload, or
substrate behavior.

## Context

The player-facing payload migration is complete through Phase 6B-13:
`w5_player_view` is the public player-facing authority, while public
`current_room/current_room_id/viewer_room_id` aliases remain deprecated
compatibility fields. Alias removal is still blocked by the client-readiness
gate.

Higher-level narrative movement/location framing still has separate legacy
surfaces:

- `ai_stack/contracts/narrator_consequence_contracts.py` derives
  `current_area`, `from_area`, `to_area`, and player local-context updates from
  `player_local_context` and `scene_affordances`.
- `ai_stack/story_runtime/narrative/sensory_context_engine.py` derives room
  sensory layers from `local_context_transition.to_area/current_area/from_area`
  before it falls back to prior sensory state, scene id, or
  `scene_affordances.current_area`.
- `ai_stack/language_io/language_adapter.py` seeds cached interaction surfaces
  with authored `current_area`.
- LangGraph runtime executor SOURCE_LINES call the narrator consequence and
  sensory-context contracts with the legacy transition shape.

Those fields are not public compatibility aliases. They are internal narrative
framing contracts, and migrating them can change committed consequence metadata
and sensory-context target selection. That requires a dedicated implementation
phase with parity fixtures.

## Decision

Narrator consequence and sensory-engine location framing will become W5-first.
The replacement authority is the existing W5 Actor Tracking projection surface:

- `W5Projection(target_consumer="narrator")`
- `where_summary.current_location`
- `where_summary.scene_location.value`
- `where_summary.previous_location`
- `where_summary.location_changed`
- `source_attribution` and `truth_attribution`
- `how_summary.facts`
- `why_summary.facts`

`How remains first-class`: `how_summary` must stay a separate dimension and may
inform posture, manner, pace, physicality, intensity, and sensory emphasis. It
must not be folded into `what_summary` or hidden inside a generic transition
string.

`inferred Why remains soft truth`: inferred `why_summary` facts may explain
possible motive or dramatic pressure, but they must remain attributed as
inferred/director-assigned/canonical as appropriate. They must not be promoted
to observed truth by narrator consequence or sensory-context framing.

## Target Projection Shape

The next implementation phase should add a small helper under
`ai_stack/actor_tracking/location_framing.py`:

```python
build_w5_location_framing(
    projection,
    *,
    previous_projection=None,
    legacy_fallback=None,
) -> dict[str, Any]
```

Target output:

```json
{
  "schema_version": "w5_location_framing.v1",
  "source": "w5_projection",
  "target_consumer": "narrator",
  "current_location_id": "salon",
  "previous_location_id": "hallway",
  "from_location_id": "hallway",
  "to_location_id": "salon",
  "location_changed": true,
  "transition_type": "movement",
  "how_summary": { "facts": {} },
  "why_summary": { "facts": {} },
  "source_attribution": {},
  "truth_attribution": {},
  "legacy_fallback_used": false
}
```

Compatibility conversion may be provided by:

```python
location_framing_to_local_context_transition(
    framing,
    *,
    legacy_transition=None,
) -> dict[str, Any]
```

That conversion can preserve `from_area`, `to_area`, `from_location_id`, and
`to_location_id` during the migration window while making W5 the source of
truth.

## Deriving From / To / location_changed

The derivation order is:

1. Read current location from `where_summary.current_location`.
2. If absent, read `where_summary.scene_location.value`.
3. Read previous location from `where_summary.previous_location` when present.
4. Read `location_changed` from `where_summary.location_changed` when present.
5. If `location_changed` is missing but current and previous locations are both
   present, derive it from `current_location_id != previous_location_id`.
6. Set `from_location_id` to previous location when `location_changed` is true;
   otherwise keep it as previous/current for compatibility with existing
   transition consumers.
7. Set `to_location_id` to current location when a current location exists.
8. Preserve legacy transition fallback only when the W5 projection is missing or
   malformed.

`from_area` and `to_area` are migration aliases of `from_location_id` and
`to_location_id` during the compatibility window. They are not the authority.

## Out Of Scope

This ADR does not remove or mutate:

- public current_room/current_room_id/viewer_room_id aliases
- WebSocket compatibility aliases
- HTTP/player-shell compatibility aliases
- `runtime_world.current_room_id`
- `environment_state.current_room_id/current_area/previous_room_id/previous_area`
- `actor_locations`
- `complete_actor_locations_for_gathering`
- NPC context bundle fallback
- malformed-W5 safety fallback
- committed events or historical diagnostics

Substrate writers/readers remain `substrate_keep_future_adr`. Public payload
aliases remain governed by ADR-0069 and the Phase 6B-13 readiness gate.

## Rollout Plan

1. Phase 6C-0: record ADR-0070, inventory, and implementation plan. No runtime
   behavior changes.
2. Phase 6C-1: add `ai_stack/actor_tracking/location_framing.py` and focused
   tests for W5 projection to location-framing derivation.
3. Phase 6C-2: synthesize `state["w5_location_framing"]` inside the LangGraph
   runtime from `w5_latest_snapshot` through the W5 location-framing helper,
   then pass it additively into narrator consequence and sensory-context
   surfaces while preserving legacy `current_area/from_area/to_area` parity.
4. Phase 6C-3: begin the W5-first authority switch for narrator consequence
   and sensory-context location decisions behind parity fixtures. Legacy
   fallback remains available.
5. Phase 6C-4: update language-adapter runtime overlay behavior if needed,
   without poisoning cached authored `current_area` content.
6. Phase 6C-5: consider legacy internal field removal only after live evidence
   and a dedicated removal decision. Public alias removal remains governed by
   ADR-0069, not this ADR.

## Implementation Plan

Expected helper module:

- `ai_stack/actor_tracking/location_framing.py`

Expected files to touch in the implementation phase:

- `ai_stack/actor_tracking/__init__.py`
- `ai_stack/contracts/narrator_consequence_contracts.py`
- `ai_stack/story_runtime/narrative/sensory_context_engine.py`
- `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py`
- `ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py`
- `ai_stack/langgraph/langgraph_synthetic_action_resolution.py`
- `ai_stack/tests/test_narrator_consequence_contract.py`
- `ai_stack/tests/test_sensory_context_engine.py`
- `ai_stack/tests/test_w5_actor_tracking_projection.py`
- `world-engine/tests/test_story_runtime_w5_narrator_projection.py`

Compatibility posture:

- W5-first when a valid narrator projection contains a location authority.
- Legacy `current_area/from_area/to_area` fallback when W5 is missing or
  malformed.
- Existing `from_area/to_area` outputs may remain during the internal migration
  window, but their source should be W5 location framing.
- No public alias removal.
- No substrate writer removal.

Feature flag:

- No strict-off rollback flag is approved by this ADR.
- A diagnostic or shadow-comparison flag may be introduced only if the
  implementation phase needs live parity evidence.

## Tests And Acceptance Criteria

Phase 6C implementation is acceptable when:

- W5 location framing helper derives current/from/to/location_changed from
  narrator W5 projection.
- Missing or malformed W5 falls back to legacy transition fields without a
  graph crash.
- `narrator_consequence_contracts.py` prefers W5 for movement/location framing
  while preserving compatibility keys.
- `sensory_context_engine.py` prefers W5 for location layer selection.
- How remains first-class in helper output and downstream tests.
- inferred Why remains soft truth and does not become observed truth.
- Public room aliases remain untouched and governed by ADR-0069.
- Substrate writers remain untouched.
- No private NPC inferred Why leaks into public/player surfaces.
- Required tests cover narrator consequence, sensory context, W5 projection,
  LangGraph callsites, and inventory.

## Phase 6C-1 Implementation Note

Phase 6C-1 implements the helper surface described above without changing the
default runtime graph source:

- `ai_stack/actor_tracking/location_framing.py` owns
  `build_w5_location_framing()` and
  `location_framing_to_local_context_transition()`.
- Helper output schema is `w5_location_framing.v1`.
- Dict payloads are accepted only by coercing them through `W5Projection.from_dict`
  or `W5Snapshot.from_dict` / `build_w5_projection_for_narrator`.
- Optional narrator consequence and sensory-context inputs may receive
  `w5_location_framing`; callers that omit it retain legacy behavior.
- LangGraph SOURCE_LINES only pass through `state["w5_location_framing"]` when
  it already exists. Phase 6C-1 does not synthesize that state field.
- Missing/malformed W5 returns fallback-compatible diagnostics instead of
  raising.
- How remains first-class in `how_summary`; inferred Why remains soft truth in
  `truth_attribution`.

## Phase 6C-2 Implementation Note

Phase 6C-2 makes W5 location framing graph-owned but does not complete the
default authority switch:

- `executor_action_resolution_commit.py` / `_resolve_player_action` SOURCE_LINES
  synthesize `state["w5_location_framing"]` when a caller has not already
  provided it.
- The synthesis reads `w5_latest_snapshot` only through
  `build_w5_location_framing()`, preserving typed W5 model coercion and avoiding
  raw W5 history emission.
- The graph stores compact diagnostics under
  `graph_diagnostics.w5_location_framing`, including source, fallback reason,
  current/previous location, and location-changed status.
- `build_local_context_transition()`, `build_narrator_consequence_plan()`, and
  `derive_sensory_context()` receive the additive W5 framing field while legacy
  fallback remains intact.
- A parity guard preserves an already computed legacy movement target when
  pre-commit W5 says `location_changed=false`.
- No public aliases, substrate fields, committed events, `actor_locations`,
  `complete_actor_locations_for_gathering`, or `current_area/from_area/to_area`
  compatibility fields are removed.

## Phase 6C-3 Implementation Note

Phase 6C-3 completes the first authority-order switch without deleting legacy
fields:

- Valid W5 location framing is `source == "w5_projection"` with a present
  current, scene, or target location value.
- `build_local_context_transition()` and `derive_sensory_context()` prefer valid
  W5 framing for location decisions.
- Legacy fallback remains authoritative for missing, malformed, or incomplete
  W5, old payloads without graph-owned framing, and pre-commit W5 that reports
  no location change while the current action has a fresh legacy movement target.
- Diagnostics include `location_framing_authority` (`"w5"` or
  `"legacy_fallback"`) and `local_context_transition_source`
  (`"w5_location_framing"` or `"legacy"`).
- How remains first-class; inferred Why remains soft truth.
- No public aliases, substrate fields, committed events, `actor_locations`,
  `complete_actor_locations_for_gathering`, or `current_area/from_area/to_area`
  compatibility fields are removed.

## Rejected Alternatives

1. **Remove `from_area/to_area/current_area` immediately.**
   Rejected because internal tests and committed consequence/sensory metadata
   still consume these fields.

2. **Treat public `current_room/current_room_id/viewer_room_id` aliases as part
   of this migration.**
   Rejected because ADR-0069 owns public payload aliases and removal is blocked
   by the Phase 6B-13 readiness gate.

3. **Move substrate writers to W5 in the same phase.**
   Rejected because `environment_state` and `actor_locations` remain substrate
   inputs to W5 extraction and need a future substrate ADR.

4. **Let narrator prompts infer movement framing directly.**
   Rejected because W5 Actor Tracking is the deterministic authority. Prompt
   inference would reintroduce false-green narrator behavior.

5. **Promote inferred Why into observed transition cause.**
   Rejected because inferred Why remains soft truth under ADR-0063/ADR-0068
   constraints.
