# MVP 2 Handoff: Runtime State, Actor Lanes, and Content Boundary → MVP 3

**Date**: 2026-04-29  
**From**: MVP 2 — Runtime State, Actor Lanes, and Content Boundary  
**To**: MVP 3 — Live Dramatic Scene Simulator (LDSS)

---

## What MVP 3 Must Consume from MVP 2

MVP 3 receives these contracts, data structures, and validation boundaries from MVP 2:

### 1. Runtime State Provenance

**Contract**: `runtime_state.v1`

**Dataclass**: `RuntimeState`
```python
class RuntimeState(BaseModel):
    contract: str = "runtime_state.v1"
    state_version: str = "runtime_state.goc_solo.v1"
    story_session_id: str
    run_id: str
    content_module_id: str
    content_hash: str
    runtime_profile_id: str
    runtime_profile_hash: str
    runtime_module_id: str
    runtime_module_hash: str
    current_scene_id: str
    selected_player_role: str
    human_actor_id: str
    actor_lanes: dict[str, str]  # actor_id -> "human" | "npc"
    admitted_objects: list[str]
```

**Validation**:
- Source hashes (`content_hash`, `runtime_profile_hash`, `runtime_module_hash`) enable auditability
- `actor_lanes` seed from MVP 1 (cannot be modified at runtime)
- `admitted_objects` list tracks objects blessed for scene rendering
- `state_version = "runtime_state.goc_solo.v1"` locks this to God of Carnage solo play

**MVP 3 Usage**:
- LDSS module receives `RuntimeState` at turn start
- Uses source hashes to validate that LDSS output is consistent with story truth
- Uses `actor_lanes` to enforce actor ownership in generated scene projections
- Uses `admitted_objects` to constrain environment detail generation

### 2. Story Session State

**Contract**: `story_session_state.v1`

**Dataclass**: `StorySessionState`
```python
class StorySessionState(BaseModel):
    contract: str = "story_session_state.v1"
    story_session_id: str
    run_id: str
    turn_number: int
    content_module_id: str
    runtime_profile_id: str
    runtime_module_id: str
    current_scene_id: str
    selected_player_role: str
    human_actor_id: str
    npc_actor_ids: list[str]
    visitor_present: bool
```

**Validation**:
- `turn_number` incremented by MVP 3 after each turn
- `visitor_present = False` guarantee (enforced by MVP 1, verified by MVP 2)
- `current_scene_id` updated by LDSS after scene transitions
- `npc_actor_ids` cannot be modified at runtime; defines NPC agency boundary

**MVP 3 Usage**:
- LDSS uses `turn_number` to track dramatic tempo (pressure buildup, peak, resolution)
- LDSS uses `current_scene_id` to constrain scene detail to canonical rooms/beats
- LDSS uses `npc_actor_ids` to generate independent NPC dialogue and agency
- Guarantees `visitor_present = False` so LDSS never generates visitor perspective

### 3. Actor Lane Context

**Contract**: `actor_lane_context.v1`

**Dataclass**: `ActorLaneContext`
```python
class ActorLaneContext(BaseModel):
    contract: str = "actor_lane_context.v1"
    content_module_id: str
    runtime_profile_id: str
    selected_player_role: str
    human_actor_id: str
    actor_lanes: dict[str, str]  # actor_id -> "human" | "npc"
    ai_allowed_actor_ids: list[str]  # Only NPC actors
    ai_forbidden_actor_ids: list[str]  # human_actor_id + removed actors
```

**Validation**:
- `human_actor_id` is always in `ai_forbidden_actor_ids`
- `ai_allowed_actor_ids` contains only actors marked "npc" in `actor_lanes`
- This is the canonical enforcement boundary for NPC autonomy

**MVP 3 Usage**:
- LDSS respects `ai_allowed_actor_ids` when generating NPC dialogue, actions, emotions
- LDSS never generates lines, actions, or decisions for `human_actor_id`
- LDSS validates responder selection against `ai_forbidden_actor_ids` before output

### 4. Object Admission Records

**Contract**: `object_admission_record.v1`

**Dataclass**: `ObjectAdmissionRecord`
```python
class ObjectAdmissionRecord(BaseModel):
    contract: str = "object_admission_record.v1"
    object_id: str
    source_kind: str | None  # "canonical_content" | "typical_minor_implied" | "similar_allowed"
    source_reference: str | None  # e.g., "goc_content.characters.alain"
    admission_reason: str | None
    similarity_reason: str | None  # Required when source_kind="similar_allowed"
    temporary_scene_staging: bool  # True for typical_minor_implied
    commit_allowed: bool  # True only for canonical_content
    status: str  # "admitted" | "rejected"
    error_code: str | None
    message: str | None
```

**Validation**:
- `canonical_content` objects: `commit_allowed = True`, can be persisted
- `typical_minor_implied` objects: `temporary_scene_staging = True`, scene-only, not persisted
- `similar_allowed` objects: requires `similarity_reason`, `commit_allowed = False`, scene-only

**MVP 3 Usage**:
- LDSS respects object admission records when rendering scene environment
- LDSS can include `admitted` objects in scene descriptions
- LDSS must reject output that references `rejected` objects
- LDSS must distinguish `temporary_scene_staging` objects as single-scene-only

### 5. State Delta Boundary

**Contract**: `state_delta_boundary.v1`

**Dataclass**: `StateDeltaBoundary`
```python
class StateDeltaBoundary(BaseModel):
    contract: str = "state_delta_boundary.v1"
    protected_paths: list[str] = [
        "canonical_scene_order",
        "canonical_characters",
        "canonical_relationships",
        "canonical_content_truth",
        "canonical_props",
        "canonical_endings",
        "content_module_id",
        "selected_player_role",
        "human_actor_id",
        "actor_lanes",
    ]
    allowed_runtime_paths: list[str] = [
        "runtime_flags",
        "turn_memory",
        "scene_pressure",
        "admitted_objects",
        "relationship_runtime_pressure",
    ]
    reject_unknown_paths: bool = True
```

**Validation**:
- Mutations to `protected_paths` are always rejected (canonical story truth is read-only)
- Mutations to `allowed_runtime_paths` are permitted (runtime state can evolve)
- Unknown paths are rejected when `reject_unknown_paths = True`

**MVP 3 Usage**:
- LDSS respects protected paths; cannot generate state mutations that violate boundaries
- LDSS can modify `runtime_flags` to track dramatic decisions
- LDSS can update `turn_memory` for turn-over-turn continuity
- LDSS can adjust `scene_pressure` to track emotional tension
- Commit seam enforces these boundaries before persisting state mutations

---

## Proof of MVP 2 Stop Condition

1. ✅ MVP 1 role ownership is consumed without rediscovery (tested: `test_runtime_state_contains_source_provenance`)
2. ✅ Actor-lane validation rejects AI output for the human actor at the live AI seam (tested: `test_ai_cannot_speak_for_human_actor`, `test_ai_cannot_act_for_human_actor`)
3. ✅ Human responder nomination is rejected before output packaging (tested: `test_human_actor_cannot_be_primary_responder`, `test_human_actor_cannot_be_secondary_responder`)
4. ✅ NPC coercion of human state/action is rejected (tested: `test_npc_action_cannot_force_human_response`)
5. ✅ Runtime profile/module story truth is structurally forbidden (tested: `test_runtime_profile_contains_no_story_truth`, `test_runtime_module_contains_no_goc_story_truth`)
6. ✅ Object admission and protected state mutation tests pass (tested: full object admission and state delta test suites)
7. ✅ Operational gate evidence is current (MVP2_OPERATIONAL_EVIDENCE.md)
8. ✅ MVP 2 handoff artifacts exist (this document)

---

## Contracts Consumed by MVP 3

### Primary Contracts (required for LDSS operation)

| Contract | Source | Purpose |
|----------|--------|---------|
| `runtime_state.v1` | MVP 2 | Supplies source hashes and admitted objects for scene rendering |
| `story_session_state.v1` | MVP 2 | Supplies turn number, scene, and role ownership for dramatic tracking |
| `actor_lane_context.v1` | MVP 2 | Defines human actor boundary and NPC autonomy constraint |
| `object_admission_record.v1` | MVP 2 | Admits objects to scenes; distinguishes canonical/typical/similar tier |
| `state_delta_boundary.v1` | MVP 2 | Protects canonical story truth from runtime mutation |

### Secondary Contracts (inherited from prior MVPs)

| Contract | Source | Purpose |
|----------|--------|---------|
| `runtime_profile.v1` | MVP 1 | Role/actor/scene mappings; resolved at session start |
| `experience_kind` | MVP 1 | Experience type (god_of_carnage_solo) |
| `participant_mode` | MVP 1 | Human/NPC designation |

---

## MVP 3 Implementation Constraints

### Must-Have for Scene Simulation

1. **Scene Director LDSS Module** — consumes `RuntimeState` and generates scene projection (rooms, occupants, visible actions)
2. **Actor Agency Layer** — respects `actor_lane_context` to generate independent NPC dialogue/actions
3. **Object Admission Enforcement** — respects `admitted_objects` list; rejects unknown objects
4. **State Delta Validation** — respects `state_delta_boundary` when generating runtime mutations
5. **Turn State Persistence** — increments `turn_number`, updates `current_scene_id`, persists allowed mutations

### Must NOT Implement

- ❌ Further relaxation of object admission tiers (tiers are locked by MVP 2 ADR)
- ❌ Modification of `actor_lanes` or `human_actor_id` at runtime (contracts are read-only)
- ❌ Visitor perspective or multi-human responder pools (visitor_present = False guarantee)
- ❌ Narrative governor or operator UI (deferred to MVP 4)
- ❌ Frontend interactivity (deferred to MVP 5)

### Must Validate Before Commit

1. Output responder is in `ai_allowed_actor_ids`
2. State mutations respect `state_delta_boundary`
3. Scene objects are in `admitted_objects` or qualify as `typical_minor_implied`
4. Scene detail does not contradict `runtime_state.content_hash` (canonical story truth)

---

## Deferred Admin Overrides (to MVP4 or future Admin Integration MVP)

The following operator surfaces are **infrastructure-locked but UI-deferred**:

### Object Admission Override Admin UI
- **Decision**: Operators may override object admission tier (canonical→typical, similar→canonical) with audit trail
- **Status**: Validator functions exist, tests verify rejection behavior, but no admin route/template/JS exists
- **Deferred to**: MVP4 (Narrative Gov integration) or explicit Admin Integration MVP
- **Proof**: ADRs adr-mvp2-015 (object admission tiers) and adr-mvp2-004 (actor lane enforcement) document the validation, not the override surface

### State Delta Boundary Override Admin UI
- **Decision**: Operators may override protected paths (e.g., unlock `canonical_scene_order` for emergency edits) with breakglass audit trail
- **Status**: Validator enforces boundaries, tests verify rejection behavior, but no admin route/template/JS exists
- **Deferred to**: MVP4 (Narrative Gov integration) or explicit Admin Integration MVP
- **Proof**: ADR adr-mvp2-003 (NPC coercion) documents boundaries; no admin routes exist yet

### Implementation Checklist (for assigning MVP)
When admin override UI is assigned, implement:
- [ ] `GET /api/v1/admin/game/object-admission-config` (read current overrides)
- [ ] `POST /api/v1/admin/game/object-admission-override` (create override with audit reason)
- [ ] `DELETE /api/v1/admin/game/object-admission-override/{id}` (revoke with audit)
- [ ] `GET /api/v1/admin/game/state-delta-config` (read protected paths)
- [ ] `POST /api/v1/admin/game/state-delta-override` (breakglass unlock with audit)
- [ ] Admin template: `administration-tool/templates/manage/game/object-admission-overrides.html`
- [ ] Admin JS: `administration-tool/static/manage_object_admission_overrides.js`
- [ ] Admin template: `administration-tool/templates/manage/game/state-delta-overrides.html`
- [ ] Admin JS: `administration-tool/static/manage_state_delta_overrides.js`
- [ ] Tests: Admin authorization, override persistence, audit trail logging
- [ ] ADR: Link to adr-mvp2-003, adr-mvp2-004, adr-mvp2-015 explaining why these surfaces were deferred

---

## Test Evidence

**Gate Status**: PASS  
**Total Tests**: 91 MVP2 tests passing  
**Test Suites**:
- `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` — 7 tests PASS
- `world-engine/tests/test_mvp2_npc_coercion_state_delta.py` — 5 tests PASS
- `world-engine/tests/test_mvp2_object_admission.py` — 6 tests PASS
- `world-engine/tests/test_mvp2_operational_gate.py` — operational gate tests PASS
- Additional integration tests in engine suite — all PASS

**Command Evidence**:
```bash
cd D:\WorldOfShadows
python tests/run_tests.py --mvp2
# Result: 91 tests passed, 0 failed, 0 skipped
```

---

## Handoff Readiness

This handoff is **complete and ready** for MVP 3 implementation.

MVP 3 will consume:
- Runtime state with source provenance
- Story session state with turn tracking
- Actor lane context with human actor boundary
- Object admission records with tier-based staging
- State delta boundary with protected paths

**Status**: MVP 2 complete, operational gates verified, all required artifacts present.
