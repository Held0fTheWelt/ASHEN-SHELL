---
id: SAD-PROJECT-MVP-LIVE-RUNTIME-COMPLETION
status: accepted
type: project-sad
owns-adrs: []
uml-package: UML/Project/mvp-live-runtime-completion
components: [world-engine, frontend, ai-stack, content-authority]
---
# MVP Live Runtime Completion — Software Architecture (arc42, project-wide)

**Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Program SAD for the MVP_Live_Runtime_Completion package: locator-first guides, operational evidence,
and 24 MVP-scoped ADRs that implement the God of Carnage live runtime path.

The program gates expansion: each MVP wave completes locator and operational evidence artifacts before
closure. Technical decisions in MVP ADRs are absorbed into component SADs; this project SAD tracks
program status, guide order, and which evidence files prove live-runtime claims.

## 2. Constraints

- `god_of_carnage` canonical module; `god_of_carnage_solo` is a runtime profile.
- Mandatory gates: `docker-up.py`, `tests/run_tests.py`, GitHub workflows.

## 3. Context & Scope

Guides under [`docs/MVPs/MVP_Live_Runtime_Completion/`](../../../MVPs/MVP_Live_Runtime_Completion/README.md); ADRs under `docs/ADR/MVP_Live_Runtime_Completion/`.

## 4. Solution Strategy

Each MVP completes SOURCE_LOCATOR and OPERATIONAL_EVIDENCE artifacts before closure.

## 5. Building Block View

| MVP wave | Primary SAD |
| --- | --- |
| MVP1 identity | world-engine, content-authority |
| MVP2 actor lanes | world-engine, ai-stack |
| MVP3 LDSS | ai-stack, world-engine |
| MVP4 observability | observability-traceability |
| MVP5 frontend blocks | frontend |

## 6. Runtime View

See [mvp-live-runtime-completion UML](../../../../UML/Project/mvp-live-runtime-completion/README.md).

## 7. Deployment View

Documented in MVP guides and admin setup docs.

## 8. Crosscutting Concepts

MVP scope and anti-creep policy (formerly `mvp_definition`) are defined in §2 Constraints and the live-runtime guides.

## 9. Architecture Decisions

MVP ADRs map to component SADs §9; this project SAD indexes them:

| MVP ADR | Absorbed by |
| --- | --- |
| mvp1-001 | world-engine + content-authority |
| mvp1-002 | world-engine |
| mvp1-003 | world-engine |
| mvp1-005 | content-authority |
| mvp1-006 | quality-gates |
| mvp1-016 | quality-gates |
| mvp2-003..016 | world-engine / ai-stack |
| mvp3-007 | superseded exception |
| mvp3-011..013 | ai-stack / world-engine |
| mvp4-001..010 | observability / admin / quality-gates |
| mvp5-001..003 | frontend |

### ADR-0022: MVP Expansion Decision Rule — when not to expand the platform

**Status:** 
**Origin:** ADR-0022 (retired 2026-06-23)

**Context.** During MVP validation we need clear exit and expansion criteria to avoid premature allocation of engineering effort. The `ROADMAP_MVP_WORLD_OF_SHADOWS.md` documents an evidence-driven rule describing when to expand the platform.

**Decision.** - Use the observed runtime advantage metric (evaluator evidence) to decide expansion.
- If the difference between runtime and control is assessed as *weak*, do NOT expand the platform; instead, first address experiential gaps.
- Expansion proceeds only when evidence shows a clear or sufficient advantage.

**Consequences.** - Roadmap gating: teams must provide evaluator evidence before larger platform investments.
- Short-term work focuses on corrective passes rather than expansion epics.

**Implementation status.** **Decision in force as a governance principle; no automated gate exists.**

- The expansion decision rule (require evaluator evidence of runtime advantage before expanding the platform) is referenced in `docs/MVPs/` roadmap documents.
- MVP progression itself follows this rule: MVP1→MVP2→MVP3→MVP4 required demonstrated value before expanding.
- No automated "expansion gate" system exists; the rule is enforced by engineering convention and ADR governance.
- Status promoted from "Proposed" because the decision is actively applied to MVP planning and has guided the current MVP sequence.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/project/mvp-live-runtime-completion/architecture.md#adr-0022-mvp-expansion-decision-rule-when-not-to-expand-the-platform` (archived — see `docs/archive/adr-retired-2026/`)

### ADR-0032: MVP4 Live Runtime Setup Requirements

**Status:** 
**Origin:** ADR-0032 (retired 2026-06-23)

**Context.** MVP4 is no longer defined by the original defect list alone. The live path has since been reworked across backend, frontend, play-service, observability, and governance storage.

The current requirements need to describe the implementation that now actually exists:

- backend forwards complete governed runtime projections
- world-engine rejects invalid governed session creates
- opening and turn diagnostics include truthful cost summaries
- deterministic phases are recorded truthfully as zero-token/zero-cost work
- `narrator_streaming` is forwarded through the live contract
- governance, cost, and evaluation data are available through backend operator routes
- Docker uses Redis to keep runtime-governance truth coherent across workers

This ADR supersedes earlier statements that treated the following as still-open core truths:

- actor ownership is generally lost in the live handoff
- `can_execute` may validly be `true` with an empty story window
- diagnostics errors are swallowed as normal behavior
- deterministic opening behavior is itself an MVP4 contract failure

Those are no longer the right baseline.

**Decision.** MVP4 is defined by the following runtime requirements.

### 1. Governed session-create handoff is complete and enforced

Backend-to-world-engine session creation for governed live modules must carry:

- `selected_player_role`
- `human_actor_id`
- `npc_actor_ids`
- `actor_lanes`
- runtime/content identity fields needed for the profile handoff

World-engine must reject incomplete or inconsistent governed requests with a hard contract error exposed as HTTP `400`.

This is now a required live invariant, not a best-effort enrichment.

Backend acceptance of a World-Engine `opening_turn` is also governed: the
opening must carry canonical commit evidence (`canonical_turn_id` and
`turn_aspect_ledger`). Backend player-session tests must mock current
World-Engine story-session payloads, not legacy opening stubs without canonical
evidence.

### 2. Opening and turn execution must be truthful, not cosmetically "live"

The system may use deterministic runtime phases such as LDSS, but they must be represented honestly:

- deterministic phases report `0` token usage and `0` cost
- cost attribution marks the work as non-billable deterministic execution
- later provider-backed phases can contribute real provider usage without being mixed with invented token numbers

MVP4 does not require every opening to be provider-backed. It requires the system to tell the truth about what happened.

### 3. Diagnostics are mandatory execution truth

Each committed turn must carry a diagnostics envelope that can explain:

- validation outcome
- quality class and degradation signals
- route/execution provenance
- cost summary and phase costs
- narrator streaming state when present

Diagnostics construction failures are not acceptable silent warnings on the happy path.

### 4. Frontend playability must follow story-window truth

The player-facing bundle must not present a session as executable when the story window is empty.

Current contract:

- `can_execute` is derived from real story-window entry count
- `narrator_streaming` is promoted through backend and frontend payloads
- empty-state behavior is explicit rather than silently interactive

### 5. Operator truth is part of MVP4

MVP4 is not only the player runtime. It also includes operator-visible truth for:

- session summary
- truthful daily and weekly cost reports
- token budget status
- active overrides
- evaluation recent-turns, baselines, and regression checks

These surfaces must be backed by the same runtime diagnostics and cost data produced by the live path.

### 6. Shared governance storage is required in Docker

For local Docker runtime, governance truth must survive multiple backend workers.

Therefore the standard MVP4 Docker setup includes:

- Redis service in Compose
- `REDIS_URL` in bootstrap environment
- backend initialization that attaches Redis-backed JSON storage when available

In-process fallback remains acceptable outside Docker or as degraded local fallback, but it is not the canonical Docker implementation.

**Consequences.** ### Positive

- MVP4 is now documented as a truthful runtime contract instead of a stale bug ledger.
- Deterministic runtime work is accounted for without fake cost inflation.
- Operator dashboards and evaluation flows are part of the live-runtime requirement set.
- Docker deployment expectations now match the multi-worker backend reality.

### Negative / risks

- Any future docs that describe MVP4 purely as "provider-backed opening" will be misleading.
- If Redis is removed from Docker without replacement, operator truth becomes worker-local and unreliable.

**Implementation status.** **Implemented — all six MVP4 runtime requirements are in place.**

1. Governed session-create handoff: complete `runtime_projection` with actor ownership forwarded from `backend/app/api/v1/game_routes.py` → `world-engine/app/api/http.py`; incomplete requests rejected with HTTP 400 (`StorySessionContractError`).
2. Truthful opening/turn execution: deterministic phases report `0` token/cost; `quality_class` distinguishes live vs. degraded.
3. Diagnostics envelope: each committed turn carries validation outcome, quality class, route provenance, cost summary, narrator streaming state, `canonical_turn_id`, and `turn_aspect_ledger`.
4. `can_execute` derived from real story-window entry count; `narrator_streaming` propagated through backend and frontend payloads.
5. Operator routes: `/api/v1/admin/mvp4/` exposes session summary, cost reports, token budget, evaluations.
6. Shared governance storage: Redis-backed JSON storage initialized in `backend/app/factory_app.py`; `REDIS_URL` in bootstrap environment.
- `world-engine/app/story_runtime/manager/` and `world-engine/app/api/http.py` are the primary implementation files.

**Evidence.** `docs/architecture/project/project/mvp-live-runtime-completion/architecture.md#adr-0032-mvp4-live-runtime-setup-requirements` (archived — see `docs/archive/adr-retired-2026/`)

### MVP1-001: Experience Identity

**Status:** Accepted
**Origin:** MVP1-001 (retired 2026-06-23)

**Context.** The God of Carnage solo experience had no formal separation between its content module (`god_of_carnage`) and its runtime profile (`god_of_carnage_solo`). The template system treated `god_of_carnage_solo` as a content template with roles, rooms, and props — conflating runtime configuration with story truth. The human role was `visitor`, a synthetic identity not present in the canonical play. This created an invalid experience identity where the runtime could not prove which content backed the session.

**Decision.** 1. `god_of_carnage` is the canonical content module. It owns all story truth: characters, scenes, relationships, escalation axes, props, and endings. It lives at `content/modules/god_of_carnage/`.

2. `god_of_carnage_solo` is a runtime profile only. It does not own story truth. It binds to `god_of_carnage` content. It is resolved by the runtime profile resolver at `world-engine/app/runtime/profiles.py`.

3. `visitor` is removed from the live God of Carnage solo path. It must not appear as a role, actor, session participant, prompt responder, or lobby seat.

4. The player must choose either `annette` or `alain` before a session can be created. Missing or invalid selections fail with structured error codes.

**Consequences.** - Any session creation for God of Carnage solo must supply `runtime_profile_id=god_of_carnage_solo` and `selected_player_role=annette|alain`
- Live path (FIX-004) rejects `template_id=god_of_carnage_solo` directly — profile resolution is mandatory
- `visitor` must never be reintroduced in any role, prompt, lobby seat, or compatibility fallback (FIX-007 validates all surfaces)
- Unselected guest roles converted to NPC participants in solo story runtime (FIX-003)
- Template story truth (beats, props, actions) must be empty — all derived from canonical content (FIX-002)

**Affected services.** - `story_runtime_core/goc_solo_builtin_roles_rooms.py` — removed visitor, added annette/alain as HUMAN roles
- `world-engine/app/runtime/profiles.py` — new runtime profile resolver (MVP1-P01)
- `world-engine/app/api/http.py` — CreateRunRequest extended with runtime_profile_id, selected_player_role
- `world-engine/app/runtime/manager.py` — _bootstrap_instance extended with preferred_role_id
- `backend/app/services/game/game_service.py` — create_run extended with runtime_profile_id, selected_player_role
- `backend/app/api/v1/game_routes.py` — game_create_run and game_player_session_create extended

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP1-002: Runtime Profile Resolver

**Status:** Accepted
**Origin:** MVP1-002 (retired 2026-06-23)

**Context.** No runtime profile concept existed in the codebase before MVP1. Templates (ExperienceTemplate) served as both content configuration and runtime identity. This made it impossible to distinguish "this is the content" from "this is the runtime mode".

**Decision.** Create `world-engine/app/runtime/profiles.py` with a `RuntimeProfileResolver` pattern:

- `resolve_runtime_profile(runtime_profile_id)` resolves a profile id to a `RuntimeProfile` object
- `RuntimeProfile` contains: `runtime_profile_id`, `content_module_id`, `runtime_module_id`, `runtime_mode`, `selectable_player_roles`, `forbidden_story_truth_fields`
- `validate_selected_player_role(role, profile)` validates the player's role selection
- `build_actor_ownership(role, profile)` produces `human_actor_id`, `npc_actor_ids`, `actor_lanes`, `visitor_present`
- `assert_profile_contains_no_story_truth(profile_dict)` enforces content boundary

Error codes emitted by the resolver:
- `runtime_profile_required`
- `runtime_profile_not_found`
- `runtime_profile_not_content_module` (enforced via content module directory check)
- `selected_player_role_required`
- `invalid_selected_player_role`
- `selected_player_role_not_canonical_character`
- `invalid_visitor_runtime_reference`
- `runtime_profile_contains_story_truth`

**Consequences.** - MVP2 can import `resolve_runtime_profile` from `app.runtime.profiles`
- The resolver is currently hard-coded for `god_of_carnage_solo`; future profiles require adding cases
- `RuntimeProfileError` is a structured ValueError subclass with `.code` and `.details`

**Affected services.** - `world-engine/app/runtime/profiles.py` (NEW)
- `world-engine/app/api/http.py` — consumes resolver in `create_run` handler

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP1-003: Role Selection and Actor Ownership

**Status:** Accepted
**Origin:** MVP1-003 (retired 2026-06-23)

**Context.** The previous GoC solo template had a single HUMAN role (`visitor`) that was automatically assigned. There was no player choice and no way to associate a canonical story character with the human actor. The player was not a character — they were a nameless visitor.

**Decision.** 1. The player must choose `annette` or `alain` before session creation. This choice is mandatory.

2. The chosen role is preserved as `selected_player_role` (`annette`/`alain`) and resolves through content identity to the canonical human-controlled `human_actor_id` (`annette_reille`/`alain_reille`). The live story-session contract must compare the resolved actor identity, not raw string equality.

3. All other canonical God of Carnage characters (`alain`/`annette`, `veronique`, `michel`, depending on choice) become NPC dramatic actors.

4. `build_actor_ownership()` produces the authoritative `human_actor_id`, `npc_actor_ids`, and `actor_lanes` map for MVP2 consumption.

5. The `CreateRunRequest` in `world-engine/app/api/http.py` now accepts `selected_player_role`. The `world-engine/app/runtime/manager.py:_bootstrap_instance` accepts `preferred_role_id`.

**Consequences.** - Sessions where neither annette nor alain is selected are rejected at the API level
- `selected_player_role` remains the player-facing role slug while `human_actor_id` is the canonical runtime actor ID
- The two human-selectable lobby seats (annette, alain) both exist in the template; the unselected one remains an empty lobby seat
- MVP2 receives `human_actor_id` and `npc_actor_ids` from the `CreateRunResponse`

**Affected services.** - `story_runtime_core/goc_solo_builtin_roles_rooms.py` — annette and alain are HUMAN+can_join, both start in hallway
- `world-engine/app/runtime/manager.py` — `create_run()` and `_bootstrap_instance()` extended
- `world-engine/app/runtime/profiles.py` — `validate_selected_player_role()`, `build_actor_ownership()`
- `world-engine/app/api/http.py` — `create_run` handler wires profile resolution to manager

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP1-005: Canonical Content Authority

**Status:** Accepted
**Origin:** MVP1-005 (retired 2026-06-23)

**Context.** The `god_of_carnage_solo` ExperienceTemplate in `story_runtime_core/` owned role descriptions, NPC voice strings, room layouts, props, actions, and beats — story truth that belongs exclusively to the canonical content module at `content/modules/god_of_carnage/`. This created two competing authorities: the runtime template and the content YAML. Changes to character identity, NPC voice, room/object truth, or canonical path beats required updates in two places, with no guarantee of consistency.

FIX-006 of the MVP1 audit cycle identified that the role IDs (`annette`, `alain`, `veronique`, `michel`) in the runtime template must derive from canonical content, not be maintained independently.

**Decision.** 1. **`content/modules/god_of_carnage/`** is the sole canonical content authority for God of Carnage story truth: character identities, relationships, locations, objects, canonical path steps, escalation policy, beats, content-access rules, and NPC voice intent.

   The current authored story spine is **not** `scenes.yaml`. Directed story truth lives in `canonical_path/index.yaml` and the numbered `canonical_path/*.yaml` step files. `scene_graph.yaml` is retained only as a runtime/compatibility node index over canonical path and location IDs; it must not become a second scene-description database.

2. **`god_of_carnage_solo` ExperienceTemplate** (in `story_runtime_core/`) is runtime scaffolding only — it provides the game-engine participation model (lobby seats, room graph, action menus). It does not author story truth.

3. **Runtime profile** (`world-engine/app/runtime/profiles.py`) resolves canonical actor IDs from the modular character content under `content/modules/god_of_carnage/characters/` at runtime via `_resolve_goc_content()`, not from hardcoded constants.

4. **Role IDs** in the ExperienceTemplate are character slugs (`annette`, `alain`, `veronique`, `michel`), not runtime actor IDs. They must resolve through `characters/index.yaml` to the canonical per-character documents in `characters/definitions/*.yaml`, where `actor_id` / `runtime_actor_id` defines the runtime actor identity. The joinable player role subset (`annette`, `alain`) must additionally resolve through the runtime profile's selectable-role mapping. This is enforced by `test_goc_solo_runtime_projection_is_derived_from_canonical_content`.

5. **`god_of_carnage_solo` runtime module** cannot own characters, rooms, objects, canonical path steps, relationships, or endings as story truth. `assert_profile_contains_no_story_truth()` enforces this for profile dicts.

6. Backend transitional continuity helpers may expose progression momentum
   (`momentum=resolving`, `momentum=stalled`, etc.) as context-selection
   rationale, but they must not infer GoC ending previews unless the active
   `ContentModule` exposes authored `ending_conditions`. The current GoC
   module shape intentionally omits legacy standalone `endings.yaml`; tests
   must not require `approaching_resolution` for this module.

7. Canonical GoC YAML is UTF-8 content. Tests and loaders that parse
   `content/modules/god_of_carnage/**/*.yaml` must open files with explicit
   UTF-8 encoding so Windows locale defaults such as `cp1252` do not become a
   second, accidental content contract.

**Consequences.** - Any change to canonical character slugs in `characters/index.yaml` or `characters/definitions/*.yaml` must be reflected in the ExperienceTemplate role IDs
- Test `test_goc_solo_runtime_projection_is_derived_from_canonical_content` will fail if a template role no longer resolves through the character index to a canonical actor ID, or if a joinable player role is missing from the runtime profile's selectable-role mapping
- The runtime profile produces a `content_hash` from canonical character content in `build_actor_ownership()`, enabling drift detection
- MVP 2 can trust that `human_actor_id` and `npc_actor_ids` in the handoff trace back to canonical content
- Foundation gates must verify the active content shape (`canonical_path/` plus `scene_graph.yaml`) and must not require legacy flat story files such as `scenes.yaml`, `transitions.yaml`, `triggers.yaml`, or `endings.yaml`.
- Lore/direction continuity tests for GoC must treat resolving momentum as a
  bounded context signal, not as proof that an authored ending exists.
- Content parse tests must be locale-independent and read canonical YAML as
  UTF-8, matching the authored repository content.

**Affected services.** - `content/modules/god_of_carnage/module.yaml` — canonical module metadata and file registry
- `content/modules/god_of_carnage/canonical_path/index.yaml` and numbered `canonical_path/*.yaml` — directed story spine and beat authority
- `content/modules/god_of_carnage/scene_graph.yaml` — runtime node index over canonical path/location IDs; not a story-truth replacement for `canonical_path/`
- `content/modules/god_of_carnage/characters/index.yaml` and `characters/definitions/*.yaml` — canonical authority for character IDs
- `world-engine/app/runtime/profiles.py` — `_resolve_goc_content()` reads canonical character content, produces content hash
- `story_runtime_core/goc_solo_builtin_roles_rooms.py` — role IDs must match canonical character slugs
- `world-engine/tests/test_mvp1_experience_identity.py` — `TestStoryTruthBoundary` and `TestContentResolvedRoleMapping`

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP1-006: Evidence-Gated Architecture Capabilities

**Status:** Accepted
**Origin:** MVP1-006 (retired 2026-06-23)

**Context.** Previous capability reports in the system could claim "implemented" status without concrete source anchors or behavioral tests. This led to false confidence in features that were not actually functioning in the live path.

**Decision.** All capability reports produced by this system must:

1. Include `source_anchors` — real file paths and function names for each implemented capability
2. Use `"status": "missing"` for capabilities that are not yet implemented — never static success
3. Be backed by passing tests named in the `tests` field
4. Not claim "implemented" for any capability that lacks at least one source anchor
5. For Capability Matrix rows, use stable semantic runtime names and follow the promotion rules in [`capability_matrix_live_claim_gates.md`](../../../MVPs/capability_matrix_live_claim_gates.md)
6. Keep local verification history in [`capability_matrix_verification_log.md`](../../../MVPs/capability_matrix_verification_log.md), not embedded as current truth

The capability evidence report for MVP1 is at `tests/reports/MVP_Live_Runtime_Completion/MVP1_CAPABILITY_EVIDENCE.md` and the test `test_ldss_capability_added_to_e0_report_requires_source_anchor` validates this rule.

Error code for violation: `capability_evidence_missing_source_anchor`

**Consequences.** - LDSS, Narrative Gov, and Langfuse are explicitly marked `missing` in the MVP1 capability report
- Implemented capabilities (profile resolution, role selection, visitor removal) have concrete source anchors
- MVP4 must provide real source anchors when it marks diagnostics capabilities as `implemented`
- Capability Matrix promotions require code, tests, runtime wiring, ADR relation, anti-hardcoding coverage, and any required live/staging/Langfuse/MCP evidence; a local PASS line alone is not enough

**Affected services.** - `tests/reports/MVP_Live_Runtime_Completion/MVP1_CAPABILITY_EVIDENCE.md` (NEW)
- `world-engine/tests/test_mvp1_experience_identity.py:TestCapabilityEvidence`

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP1-016: Operational Test and Startup Gates

**Status:** Accepted
**Origin:** MVP1-016 (retired 2026-06-23)

**Context.** The MVP_Live_Runtime_Completion guide requires that every MVP prove its implementation through operational gates: docker-up.py, tests/run_tests.py (tests/run_tests.py), GitHub workflows, and TOML/tooling. Without these gates, documentation and test results in isolation cannot prove the live path works.

**Decision.** The following operational gate requirements apply to MVP1 and all subsequent MVPs:

1. **`docker-up.py`**: Must exist and start backend, frontend, play-service. Must report failed services and exit nonzero. MVP1 does not modify docker-up.py but confirms it exists.

2. **`tests/run_tests.py`** (equivalent of guide's `tests/run_tests.py`): Must include MVP1 tests in the engine and backend suites. MVP1 tests are placed in `world-engine/tests/` and `backend/tests/` which are covered by `--suite engine` and `--suite backend`.

3. **GitHub workflows**: Must include MVP1 tests or equivalent suites:
   - `.github/workflows/engine-tests.yml` — covers `world-engine/tests/` (includes `test_mvp1_experience_identity.py`)
   - `.github/workflows/backend-tests.yml` — covers `backend/tests/` (includes `test_mvp1_session_identity.py`)

4. **TOML/tooling**: `pyproject.toml` and service TOMLs must not exclude MVP1 test paths.

5. **Operational evidence artifact**: Must be written to `tests/reports/MVP_Live_Runtime_Completion/MVP<N>_OPERATIONAL_EVIDENCE.md`.

6. **Source locator artifact**: Must be written to `tests/reports/MVP_Live_Runtime_Completion/MVP<N>_SOURCE_LOCATOR.md` before any code patching.

**Consequences.** - No MVP is closed without an operational evidence artifact
- No MVP patches code before completing the source locator artifact
- Pre-existing test failures that are unrelated to the MVP must be documented and explained in the operational evidence artifact

**Affected services.** - `docker-up.py` (confirmed valid, not modified)
- `tests/run_tests.py` (confirmed valid, engine/backend suites cover MVP1 tests)
- `.github/workflows/engine-tests.yml` (confirmed covers world-engine/tests/)
- `.github/workflows/backend-tests.yml` (confirmed covers backend/tests/)
- `tests/reports/MVP_Live_Runtime_Completion/MVP1_OPERATIONAL_EVIDENCE.md` (NEW)
- `tests/reports/MVP_Live_Runtime_Completion/MVP1_SOURCE_LOCATOR.md` (NEW)

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP2-003: NPC Coercion Rejection and StateDeltaBoundary

**Status:** Accepted
**Origin:** MVP2-003 (retired 2026-06-23)

**Context.** While ADR-MVP2-004 prevents the AI from speaking or acting *as* the human actor, a separate violation is possible: an NPC action that *controls the outcome* of the human actor without speaking as them. Examples:
- "Alain forces Annette to apologize." — NPC determines human speech
- "Véronique makes Alain leave the room." — NPC determines human movement
- "Michel decides that Annette feels ashamed." — NPC assigns human emotion

Additionally, the runtime had no mechanism preventing state deltas from mutating protected story truth fields (canonical_scene_order, canonical_characters, selected_player_role, human_actor_id, actor_lanes). An AI-generated state delta could silently change the player's selected role or rewrite canonical scene structure.

**Decision.** ### NPC Coercion

1. **`validate_npc_action_coercion()`** in `world-engine/app/runtime/actor_lane.py` enforces that NPC actions targeting the human actor may not constitute control. Classification uses structured fields first (coercion_type, action_type against `_COERCIVE_ACTION_TYPES`), then text-level analysis as supplementary evidence. This is not a pure string match.

2. Allowed: NPC pressures, challenges, addresses, interrupts, provokes, accuses, taunts, or appeals to the human actor. These are social influences, not outcome determinations.

3. Rejected: NPC forces, makes, compels, commands, orders, decides for, assigns emotion to, or controls the human actor's speech, action, movement, belief, decision, consent, or physical state. Error code: `npc_action_controls_human_actor`.

4. NPC-to-NPC coercive actions are not restricted by this rule (human actor boundary only).

5. The live LangGraph validation path mirrors the same structured coercion taxonomy through `ai_stack.contracts.dramatic_capability_contracts.NPC_COERCIVE_ACTION_TYPES`. When a structured NPC action targets the human actor and uses a coercive action/coercion type, `RuntimeAspectLedger.npc_authority` records `npc_action_controls_human_actor`, `RuntimeAspectLedger.capability_selection` records `npc.force_player_speech.forbidden`, and final validation rejects before commit.

6. `npc_action_controls_human_actor` is recoverable for self-correction feedback, but it is not eligible for degraded commit. The model may retry with corrected actor boundaries; the bad turn must not become committed story truth.

### StateDeltaBoundary

7. **`StateDeltaBoundary`** in `world-engine/app/runtime/models.py` defines `protected_paths` (canonical story truth and identity fields) and `allowed_runtime_paths` (runtime-only mutable fields).

8. **`validate_state_delta()`** in `world-engine/app/runtime/state_delta.py` rejects any delta whose path matches or is under a protected path. Error codes: `protected_state_mutation_rejected`, `state_delta_boundary_violation`.

9. **`run_commit_seam()`** in `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py` accepts `candidate_deltas` and `state_delta_boundary`. The live executor `_commit_seam()` forwards these fields from `RuntimeTurnState`, so protected path mutations are rejected at the commit seam before any write occurs.

10. Protected paths include: `canonical_scene_order`, `canonical_characters`, `canonical_relationships`, `canonical_content_truth`, `content_module_id`, `selected_player_role`, `human_actor_id`, `actor_lanes`.

11. Allowed runtime paths include: `runtime_flags`, `turn_memory`, `scene_pressure`, `admitted_objects`, `relationship_runtime_pressure`.

12. A blocked candidate delta returns `commit_applied=False`, carries `state_delta_rejection`, and is written into the commit aspect with `failure_class=hard_contract_failure`.

**Consequences.** - NPCs retain full dramatic freedom but cannot determine the human actor's outcomes
- Structured NPC coercion is rejected in the same authority ledger used by final validation, not only in isolated unit helpers
- Canonical scene order, character definitions, and identity fields cannot be mutated by runtime deltas
- A rejected commit from a protected delta returns `commit_applied=False` with `state_delta_rejection` in the result
- Unknown paths are rejected by default (`reject_unknown_paths=True`) — only explicitly listed allowed paths can be mutated
- ADR-0039 boundary: tests must assert taxonomy, error codes, ledger fields, commit flags, and capability violations, not copied prose examples

**Affected services.** - `world-engine/app/runtime/models.py` — `StateDeltaBoundary`, `StateDeltaValidationResult`
- `world-engine/app/runtime/actor_lane.py` — `validate_npc_action_coercion()`, `_COERCIVE_ACTION_TYPES`, `_ALLOWED_PRESSURE_VERBS`
- `world-engine/app/runtime/state_delta.py` — `validate_state_delta()`, `validate_state_deltas()`, `build_default_goc_boundary()`
- `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py` — `run_commit_seam()` extended with `candidate_deltas`
- `ai_stack/contracts/dramatic_capability_contracts.py` — shared NPC coercion taxonomy and forbidden capability mapping
- `ai_stack/langgraph/langgraph_runtime_executor.py` — live authority-aspect and commit-seam wiring
- `ai_stack/story_runtime/story_runtime_playability.py` — retry/degraded-commit policy for coercion failures

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP2-004: Actor-Lane Enforcement

**Status:** Accepted
**Origin:** MVP2-004 (retired 2026-06-23)

**Context.** MVP1 established that the player selects `annette` or `alain` and that the unselected canonical characters become NPC dramatic actors. However, there was no mechanism preventing the AI from generating lines, actions, emotional states, or decisions for the selected human actor. The AI had authority over all actor output slots, including the human player's slot.

Additionally, the responder nomination seam (`build_responder_and_function()` in `ai_stack/story_runtime/director/god_of_carnage_scene_director.py`) had no guard preventing the human actor from being nominated as a scene responder — an AI-generated response that would silently puppet the player.

**Decision.** 1. **ActorLaneContext** is assembled at runtime bootstrap from the MVP1 `build_actor_ownership()` handoff. It carries `human_actor_id`, `actor_lanes`, `ai_allowed_actor_ids`, and `ai_forbidden_actor_ids`. The human actor is always in `ai_forbidden_actor_ids`.

2. **`validate_actor_lane_output()`** in `world-engine/app/runtime/actor_lane.py` rejects any AI candidate block (spoken line, actor action, emotional state, decision) whose `actor_id` or `speaker_id` matches `human_actor_id`. Error code: `ai_controlled_human_actor`.

3. **`validate_responder_plan()`** in `world-engine/app/runtime/actor_lane.py` rejects any responder plan where the `primary_responder_id` or any `secondary_responder_ids` entry is the human actor. Error code: `human_actor_selected_as_responder`.

4. **`run_validation_seam()`** in `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py` is extended with an optional `actor_lane_context` dict parameter. When provided, it scans the AI generation's structured output (spoken_lines, action_lines, emotional_shift, responder nominations) for human-actor violations **before** the dramatic-effect gate runs. This ensures enforcement happens before response packaging and before commit.

5. **Enforcement order**: runtime bootstrap → ActorLaneContext assembly → AI candidate generation → actor-lane validation → responder validation → response packaging. Validation that only filters after commit is a gate failure.

6. **visitor** is rejected from all actor lane seams with error code `invalid_visitor_runtime_reference`.

7. **`actor_lane_validation_too_late`** error code is raised if validation is called after a candidate is already marked as committed.

8. **GoC actor identity aliases** are resolved before actor-lane comparison. A selected role slug, display name, first name, and canonical runtime actor id all refer to the same lane when they resolve to the same content character record. For example, `annette` and `annette_reille` must both forbid AI output on Annette's human slot; this check must fire before dramatic-effect validation.

**Consequences.** - AI cannot generate any output for the selected human actor's slot in any scene turn
- Human actor can only speak or act via player input, never via AI generation
- NPC actors retain full dramatic freedom to speak, act, address, challenge, and interact with both the human actor and each other
- Actor-lane enforcement is resilient to role-slug/runtime-id drift between bootstrap, scene director output, and model structured output
- `run_commit_seam()` receives a rejected `validation_outcome` when human actor enforcement fires, ensuring `commit_applied=False`
- `run_visible_render()` emits `render_downgrade` when enforcement fires

**Affected services.** - `world-engine/app/runtime/models.py` — `ActorLaneContext`, `ActorLaneValidationResult`
- `world-engine/app/runtime/actor_lane.py` — `build_actor_lane_context()`, `validate_actor_lane_output()`, `validate_responder_plan()`
- `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py` — `_check_human_actor_violations()`, `run_validation_seam()` extended with `actor_lane_context`
- `ai_stack/story_runtime/director/god_of_carnage_scene_director.py` — `build_responder_and_function()` (responder nomination seam — receives validation in MVP3)

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP2-015: Canonical, Typical, and Similar Environment Affordances

**Status:** Accepted
**Origin:** MVP2-015 (retired 2026-06-23)

**Context.** The runtime AI had no formal classification for environment objects it could reference or use in scene turns. Any object — a minor prop like a water glass or a plot-changing item like a legal contract — could be introduced without restriction. This created the risk of:
- AI inventing canonical story truth through object introduction (e.g., a new character prop that redefines the scene)
- Major or dangerous objects appearing with no canonical backing
- Objects being committed to persistent state when they should only be staged temporarily

**Decision.** All environment objects entering the runtime must be classified by source_kind before use. Three tiers are defined:

1. **`canonical_content`**: The object is explicitly present in the canonical content module (`content/modules/god_of_carnage/`). Admitted with `commit_allowed=True`, `temporary_scene_staging=False`.

2. **`typical_minor_implied`**: The object is a minor, plausible, contextually implied prop that does not change plot truth (e.g., a water glass in a living room). Admitted with `temporary_scene_staging=True`, `commit_allowed=False`. Not committed to persistent runtime state.

3. **`similar_allowed`**: The object is similar to a known canonical object and passes the similarity test. Requires a non-empty `similarity_reason`. Admitted with `commit_allowed=False`.

Objects with missing or invalid `source_kind` are rejected with `object_source_kind_required`. `similar_allowed` without `similarity_reason` is rejected with `similar_allowed_requires_similarity_reason`. Major, dangerous, or plot-changing objects (weapons, explosives, plot documents) without `canonical_content` backing are rejected with `environment_object_not_admitted`.

An `ObjectAdmissionRecord` is produced for every admitted or rejected object, carrying the full classification decision and commit policy.

### Relationship to Pi15 EnvironmentState

Pi15 adds a durable `EnvironmentState`, but it does **not** loosen this ADR. `EnvironmentModel` may normalize canonical layout/object YAML into room and prop state, and `StorySession.environment_state` may persist canonical-content objects, actor locations, visible rooms, salient objects, and recent environment events. Typical or similar objects remain temporary staging unless they pass the admission contract with `commit_allowed=True`.

Environment state is therefore a projection of admitted/canonical environment truth, not a second object-authority surface. Model-generated props cannot become persistent story truth by appearing in narration, local context, render support, or shell readout.

**Consequences.** - The AI may only reference objects that have been explicitly admitted with a valid source_kind
- Typical minor props are available for scene staging but cannot be committed to story truth
- No object can create new canonical story truth at runtime
- The `god_of_carnage_solo` runtime template continues to own no props (`props=[]` in the template); canonical module content may still define layout/object truth that Pi15 normalizes into environment state
- Player-visible environment projections remain projections of committed state and admitted/canonical content, not proof that narration invented a new persistent object

**Affected services.** - `world-engine/app/runtime/models.py` — `ObjectAdmissionRecord`, `VALID_SOURCE_KINDS`
- `world-engine/app/runtime/object_admission.py` — `admit_object()`, `validate_object_admission()`
- `ai_stack/contracts/environment_state_contracts.py` — canonical `EnvironmentModel` / durable `EnvironmentState` helpers
- `ai_stack/story_runtime/player_action_resolution.py` — action affordance context bound to current environment state
- `ai_stack/langgraph/langgraph_runtime_executor.py` — environment state initialization, generation context, commit-time mutation, render context
- `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py` — render support marker for bound environment state
- `world-engine/app/story_runtime/manager/` — `StorySession.environment_state` persistence and get-state diagnostics
- `world-engine/app/story_runtime_shell_readout.py` — shell projection of current environment state

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP2-016: Operational Test and Startup Gates

**Status:** Accepted
**Origin:** MVP2-016 (retired 2026-06-23)

**Context.** MVP1 established `docker-up.py`, `tests/run_tests.py`, GitHub workflows, and TOML/tooling as mandatory operational gates. MVP2 adds new test suites and artifacts that must be covered by the same infrastructure. A partial implementation (feature code present, test runner not updated) does not satisfy the gate.

**Decision.** 1. **`tests/run_tests.py --mvp2`** runs the world-engine engine suite, which includes all MVP2 test files:
   - `test_mvp2_runtime_state_actor_lanes.py` (Waves 2.1–2.2)
   - `test_mvp2_npc_coercion_state_delta.py` (Wave 2.3)
   - `test_mvp2_object_admission.py` (Wave 2.4)
   - `test_mvp2_operational_gate.py` (Wave 2.5 operational checks)

2. **`.github/workflows/mvp2-tests.yml`** covers all four MVP2 test files plus MVP1 regression. It triggers on changes to MVP2 source files, test files, content, and the workflow itself. No suite is silently skipped.

3. **`world-engine/pyproject.toml`** `testpaths = ["tests"]` picks up all MVP2 test files automatically (no manual entry required).

4. **`docker-up.py gate`** must report failure non-silently when services are unreachable. This behavior was verified in MVP1 (exit code 2 when backend is unreachable). MVP2 adds no new services but must not break startup.

5. **Required MVP2 report artifacts** must exist for the gate to pass:
   - `tests/reports/MVP_Live_Runtime_Completion/MVP2_SOURCE_LOCATOR.md`
   - `tests/reports/MVP_Live_Runtime_Completion/MVP2_OPERATIONAL_EVIDENCE.md`
   - `tests/reports/MVP_Live_Runtime_Completion/GOC_MVP2_HANDOFF_TO_MVP3.md`

6. **Required MVP2 ADRs** must exist:
   - `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions`
   - `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions`
   - `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions`

**Consequences.** - Any MVP2 test file removed or renamed without updating `mvp2-tests.yml` will break the workflow
- `tests/run_tests.py --mvp2` delegates to `tests/run_tests.py --suite engine`, which runs all world-engine tests including MVP2 files
- The operational evidence artifact must list concrete test files and markers, not just suite names

**Affected services.** - `tests/run_tests.py` — `--mvp2` flag added
- `.github/workflows/mvp2-tests.yml` — new workflow
- `world-engine/pyproject.toml` — `testpaths = ["tests"]` (unchanged; picks up MVP2 files)
- `world-engine/tests/test_mvp2_operational_gate.py` — operational gate tests

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP3-007: Minimum Agency Baseline Superseded by LDSS

**Status:** Accepted
**Origin:** MVP3-007 (retired 2026-06-23)

**Context.** Prior to MVP3, the runtime had a minimum agency baseline that defined a floor for NPC behavior. This floor was defined as "at least one visible NPC actor response per turn" and was enforced through passivity checks in the existing graph pipeline.

MVP3 introduces the Live Dramatic Scene Simulator (LDSS), which supersedes the minimum agency baseline with a richer contract: NPCs must not only respond but must do so with dramatic mass (actor lines, actions, or environment interactions), follow their own initiative, and act autonomously without waiting to be directly addressed.

The old minimum agency baseline (passive reactivity) is insufficient. NPCs must be assertive dramatic agents, not prompted responders.

**Decision.** 1. **The prior minimum agency baseline is superseded.** LDSS replaces it with a behavior contract that requires visible NPC actor responses (`actor_line`, `actor_action`, or `environment_interaction`) and prohibits narrator-only output as a complete turn.

2. **PassivityValidation** is the enforced gate. It requires at least one visible NPC block with a non-null `actor_id`. A turn consisting solely of narrator blocks is rejected with error code `no_visible_actor_response`.

3. **DramaticMassValidation** is the mass gate. It requires at least one NPC block of a visible type. A too-thin proposal (no NPC response) is rejected with error code `dramatic_alignment_insufficient_mass`.

4. **NPCAgencyPlan** is the initiative contract. LDSS must emit an `NPCAgencyPlan` identifying `primary_responder_id`, `secondary_responder_ids`, and per-NPC initiative intents. NPCs may speak without being directly addressed.

5. **NPC-to-NPC interaction** is valid and expected. A secondary NPC may react to the primary NPC's line without involving the human actor.

6. **The deterministic mock output** in `build_deterministic_ldss_output()` always satisfies these requirements, serving as a guaranteed valid fallback when no real AI call is available.

**Consequences.** - NPCs act autonomously and are assertive dramatic agents, not only reactive
- A turn with no visible NPC response is always rejected — no silent turns
- The deterministic mock guarantees at least one visible NPC response even without AI
- The gate for passivity runs before commit and before response packaging

**Affected services.** - `ai_stack/live_dramatic_scene_simulator.py` — `PassivityValidation`, `validate_passivity()`, `validate_dramatic_mass()`, `build_deterministic_ldss_output()`
- `world-engine/app/story_runtime/manager/` — `_build_ldss_scene_envelope()` (LDSS entry point post-commit)
- `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` — gates proving passivity and dramatic mass enforcement

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP3-011: Live Dramatic Scene Simulator Contract

**Status:** Accepted
**Origin:** MVP3-011 (retired 2026-06-23)

**Context.** Prior to MVP3, the story runtime returned raw visible output bundles (narration, spoken lines, action lines) from the LangGraph executor. This was sufficient for recap and dramatic_turn experience modes, but insufficient for live dramatic scene play where the player needs structured, typed scene blocks.

MVP3 introduces LDSS as a non-optional live-path component that wraps the turn's output in a validated `SceneTurnEnvelope.v2` with typed `SceneBlock` objects, NPC agency metadata, and live-path diagnostics.

**Decision.** 1. **`SceneTurnEnvelope.v2`** is the canonical output contract for God of Carnage solo turns. It is returned as `scene_turn_envelope` on the `execute_turn` response.

2. **`SceneBlock`** is the typed scene unit. Valid block types: `narrator`, `actor_line`, `actor_action`, `environment_interaction`, `system_degraded_notice`.

3. **`LDSSInput`** is the input contract: story session state, actor lane context, admitted objects, and player input.

4. **`LDSSOutput`** is the intermediate output: decision count, scene block count, visible actor response flag, NPC agency plan, and visible scene output.

5. **LDSS invocation point**: `_finalize_committed_turn()` in `world-engine/app/story_runtime/manager/` calls `_build_ldss_scene_envelope()` after validation and commit. LDSS runs on committed state only.

6. **LDSS diagnostics status**: The diagnostics field `diagnostics.live_dramatic_scene_simulator.status` reports the active LDSS outcome. Direct canonical-step LDSS envelope builds report `"approved"` when the authored canonical path step produced valid visible blocks. Full story-turn manager routes may project that same successful LDSS evidence as `"evidenced_live_path"` in higher-level runtime diagnostics. The diagnostics include `story_session_id`, `turn_number`, `input_hash`, `output_hash`, `decision_count`, `scene_block_count`, and `legacy_blob_used=false`.

7. **Legacy blob rejection**: The response packager must not use legacy text blobs as final output. `legacy_blob_used` must be `false` in diagnostics.

8. **Deterministic output sources**: When a resolvable `canonical_step_id` and canonical path bundle are present, LDSS renders deterministic visible scene blocks from authored canonical path truth. When no live/canonical visible generation is available, `build_deterministic_ldss_output()` returns an explicit `system_degraded_notice` with `status="degraded_error"` and a non-empty error code; it must not fabricate narrator/NPC story truth merely to satisfy validators.

**Consequences.** - Every God of Carnage solo turn produces `SceneTurnEnvelope.v2`
- Non-GoC sessions do not produce a scene envelope (LDSS is GoC-specific)
- The response is packaged from committed state, not raw AI output
- Diagnostics provide turn-level observability for MVP4 (Narrative Gov, Langfuse)
- A degraded LDSS fallback is valid as an error surface, not as a successful dramatic scene; gates that require NPC participation must use canonical-step or live-generated output.

**Affected services.** - `ai_stack/live_dramatic_scene_simulator.py` — `SceneTurnEnvelopeV2`, `SceneBlock`, `LDSSInput`, `LDSSOutput`, `run_ldss()`, `build_deterministic_ldss_output()`, `build_scene_turn_envelope_v2()`
- `world-engine/app/story_runtime/manager/` — `_build_ldss_scene_envelope()`, LDSS import, call in `_finalize_committed_turn`
- `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py`
- `world-engine/tests/test_mvp3_ldss_integration.py`

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP3-012: NPC Free Dramatic Agency

**Status:** Accepted
**Origin:** MVP3-012 (retired 2026-06-23)

**Context.** MVP2 established that NPCs are AI-controlled actors and the human actor is protected from AI control. MVP3 must go further: NPCs must have genuine free dramatic agency — the ability to initiate, address each other, react without being prompted, and pursue their own dramatic line within the scene.

A passive NPC that only responds when directly addressed violates the live dramatic scene simulator contract. NPCs must be assertive, autonomous dramatic agents.

**Decision.** 1. **NPCAgencyPlan** is the initiative contract. LDSS emits an `NPCAgencyPlan` per turn with `primary_responder_id`, `secondary_responder_ids`, and `npc_initiatives` (per-NPC intent, allowed block types, and target actor).

2. **Primary NPC initiative**: The primary responder speaks or acts first. Selection priority: `veronique` → `alain` → `michel` (Véronique is the most dramatically assertive in God of Carnage).

3. **Secondary NPC initiative**: The secondary NPC reacts to the primary NPC or to the scene state. This is NPC-to-NPC interaction — the human actor is not required as a bridge.

4. **No direct address required**: NPCs may speak or act without being addressed by name in the player's input. Player input is dramatic context, not a command prompt.

5. **Responder candidate exclusion**: Human actor and `visitor` are never in the responder candidate set. `validate_responder_candidates()` enforces this.

6. **Multiple NPC participation**: More than one NPC may participate in a single turn (primary + secondary). `NPCAgencyPlan.secondary_responder_ids` lists additional participants.

7. **NPC-to-NPC `target_actor_id`**: A block may target another NPC as its `target_actor_id`. This proves NPC-to-NPC dramatic exchange without human actor mediation.

**Consequences.** - NPCs are autonomous dramatic agents, not prompted responders
- Human actor is never in the responder candidate set
- `visitor` is never in the responder candidate set
- Multi-NPC turns are valid and expected when 2+ NPCs are in the session
- Responder selection is traceable in `diagnostics.npc_agency`

**Affected services.** - `ai_stack/live_dramatic_scene_simulator.py` — `NPCAgencyPlan`, `NPCInitiative`, `validate_responder_candidates()`, `_select_primary_responder()`, `build_deterministic_ldss_output()`
- `ai_stack/contracts/npc_agency_contracts.py` — shared runtime contract normalization for the current `npc_agency_simulation.v1` surface, durable closure constants, human/visitor exclusion, and the internal `npc_agency_plan.v1` adapter.
- `ai_stack/story_runtime/npc_agency/npc_agency_planner.py` — deterministic independent NPC roster planner for `npc_agency_simulation.v1`, including candidate scoring, carry-forward pressure, and NPC-to-NPC target graph projection.
- `ai_stack/story_runtime/npc_agency/npc_agency_long_horizon.py` — deterministic `npc_long_horizon_state.v1`, `npc_intention_thread.v1`, `npc_private_plan.v1`, and `npc_plan_conflict_resolution.v1` builders.
- `ai_stack/story_runtime/npc_agency/npc_agency_claim_readiness.py` — evidence gate for bounded, live-staging-ready, and full long-horizon claim states.
- `ai_stack/story_runtime/npc_agency/npc_agency_realization.py` — shared realization, validation, and durable closure helpers for `npc_initiative_realization_v1`, `npc_initiative_validation_v1`, and `npc_agency_closure.v1`.
- `ai_stack/story_runtime/runtime_aspect_ledger/__init__.py` — `npc_agency` runtime aspect projection for candidate, planned, realized, missing, carry-forward, closure, and scoring evidence.
- `ai_stack/story_runtime/story_runtime_playability.py` — recoverable rewrite feedback for missing required NPC initiative without allowing degraded commit to hide it.
- `ai_stack/langgraph/langgraph_runtime_executor.py` — model-visible current NPC agency simulation projection, bounded initiative directives, validation-aspect wiring, and self-correction trigger surface.
- `ai_stack/telemetry/actor_survival_telemetry.py` — vitality telemetry projection of candidate, planned, realized, missing, required, and carry-forward NPC initiatives.
- `ai_stack/story_runtime/narrative_runtime_agent.py` — ruhepunkt pressure analysis reads the v1 `npc_initiatives` contract.
- `world-engine/app/story_runtime/commit_models.py` — persists `npc_agency_simulation`, long-horizon state, private plans, conflict resolution, `npc_agency_closure`, and unresolved carry-forward rows in committed planner truth.
- `world-engine/app/story_runtime/manager/` — rehydrates carry-forward planner truth and emits Langfuse NPC agency spans and deterministic scores.
- `backend/app/services/story_runtime/operator_turn_history_service.py` — exposes operator-facing NPC agency breakdowns from telemetry, aspect ledger, and committed closure truth.
- `tools/mcp_server/handlers/langfuse_verify/` — exposes NPC agency deterministic scores and matrix columns through MCP Langfuse verification.
- `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` — `test_mvp3_gate_npcs_act_without_direct_address`, `test_mvp3_gate_multiple_npcs_can_participate`, `test_mvp3_gate_responder_candidates_exclude_human_and_visitor`
- `ai_stack/tests/test_npc_agency_planner.py` — current simulation, independent roster planning, durable carry-forward, and closure coverage.
- `ai_stack/tests/test_npc_agency_contracts.py` — adapter normalization, required realization, NPC-to-NPC target, and human/visitor exclusion coverage for current contract surfaces.
- `ai_stack/tests/test_narrative_runtime_agent.py` — coverage that `NarrativeRuntimeAgent` consumes v1 `npc_initiatives`.

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP3-013: Narrator Inner Voice Contract

**Status:** Accepted
**Origin:** MVP3-013 (retired 2026-06-23)

**Context.** The narrator block type exists in the LDSS scene output. Without a contract, the narrator could degrade into a dialogue summarizer, a state-setter that forces player emotions, or a hidden-intent revealer that undermines dramatic tension.

All three of these uses violate the player experience contract: the narrator must be the player's inner perception and orientation voice — not a recapper, not a puppeteer, and not an oracle.

**Decision.** 1. **Narrator is inner perception / orientation only.** The narrator block describes what the player character notices, perceives, feels inclined toward, or senses — from the player's point of view. It does not summarize what happened.

2. **Three rejected narrator modes are enforced:**
   - `dialogue_summary`: narrator recaps or summarizes dialogue between characters (e.g., "Véronique and Alain argue while Michel becomes uncomfortable"). Error code: `narrator_dialogue_summary_rejected`.
   - `forced_player_state`: narrator tells the player how they feel or what they decide (e.g., "You decide that Alain is right and feel ashamed"). Error code: `narrator_forces_player_state`.
   - `hidden_npc_intent`: narrator reveals undisclosed NPC internal motivation (e.g., "You can see through Alain's composure; he secretly wants this to end"). Error code: `narrator_reveals_hidden_intent`.

3. **`validate_narrator_voice()`** in `ai_stack/live_dramatic_scene_simulator.py` enforces these rejections using pattern matching. Valid narrator blocks are approved.

4. **Valid narrator example**: "You notice the pause before Alain answers; it feels less like uncertainty than calculation." — This is inner perception, not dialogue recap, not forced state, not hidden intent.

5. **Narrator is optional**: Not every turn requires a narrator block. When narrator blocks are present, they must pass `validate_narrator_voice()`.

**Consequences.** - Narrator cannot degrade into a game-master summarizer
- Player emotional state is always player-controlled, not narrator-assigned
- NPC hidden motivations remain hidden (dramatic tension preserved)
- The deterministic mock produces narrator blocks that always pass validation

**Affected services.** - `ai_stack/live_dramatic_scene_simulator.py` — `validate_narrator_voice()`, `_NARRATOR_DIALOGUE_SUMMARY_PATTERNS`, `_NARRATOR_FORCED_STATE_PATTERNS`, `_NARRATOR_HIDDEN_INTENT_PATTERNS`
- `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` — narrator voice tests

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-001: Observability, Diagnostics, and Trace Infrastructure

**Status:** ACCEPTED
**Origin:** MVP4-001 (retired 2026-06-23)

**Context.** MVP3 established the Live Dramatic Scene Simulator (LDSS) as the core narrative engine. MVP4 must provide complete observability into what LDSS is doing, why, and whether output quality meets acceptable thresholds. This observability is non-negotiable for:

- **Operator trust**: Showing that AI decisions are traceable, not opaque
- **Compliance auditing**: Logging all decision points with acceptance/rejection status
- **Cost governance**: Tracking token usage and applying cost-aware degradation
- **Quality assurance**: Recording baseline turns and auto-tuning evaluation rubrics
- **Root cause analysis**: Correlating Langfuse traces with runtime diagnostics for debugging

**Constraints**:
- Must not break existing MVP1-3 contracts (backward compatible)
- Must support tiered visibility (operator, Langfuse, super-admin contexts)
- Must enable trace ID correlation across diagnostics, spans, and logs
- Must provide non-placeholder evidence (reject static/mock data)
- Must work with real Langfuse v4 SDK (Phase B) and local trace export (Phase A fallback)

---

**Decision.** **Phase A (Degradation Timeline & Cost Summary)**: Extend `DiagnosticsEnvelope` dataclass with three new fields:

1. **`degradation_timeline: list[DegradationEvent]`**
   - Records every degradation event during turn execution
   - Each event: marker (e.g., "FALLBACK_USED"), severity (minor/moderate/critical), timestamp, recovery status, latency
   - Used to understand why output quality is degraded

2. **`cost_summary: dict`**
   - Placeholder in Phase A (all zeros)
   - Schema: `{input_tokens: 0, output_tokens: 0, cost_usd: 0.0, cost_breakdown: {}}`
   - Phase B fills with real token counts and cost breakdown (LDSS, Narrator, other)

3. **`to_response(context: str) -> dict`** method for tiered visibility
   - `context="operator"`: Redacts input_hash, output_hash, cost_summary (sensitive info)
   - `context="langfuse"`: Shows hashes, excludes debug_payload (full technical data)
   - `context="super_admin"`: Complete unredacted envelope (for deep debugging)

**Why this approach**:
- Extends existing `DiagnosticsEnvelope` (no breaking changes)
- Degradation timeline answers "what went wrong" (marker + severity + recovery)
- Cost summary field ready for Phase B without refactoring
- `to_response()` method enables same envelope object to serve multiple audiences without code duplication
- Tiered visibility prevents accidental exposure of sensitive data (hashes, debug payloads) to operators

**Alternatives considered**:
1. Create separate envelope types per visibility level (rejected: explosion of dataclasses, harder to maintain)
2. Redact in HTTP response handler (rejected: logic scattered, harder to test in isolation)
3. Use a single `visibility_level` string field (rejected: less type-safe, requires string parsing)

---

**Consequences.** ### Affected Services/Files

| Service | File | Change |
|---------|------|--------|
| ai_stack | `ai_stack/telemetry/diagnostics_envelope.py` | Add DegradationEvent, extend DiagnosticsEnvelope, implement to_response() |
| world-engine | `world-engine/app/story_runtime/manager/` | Collect degradation_events during turn execution |
| world-engine | `world-engine/app/api/http.py` | Call `to_response(context="operator")` in HTTP responses |
| backend | `backend/app/observability/langfuse_adapter.py` | Phase B: fill cost_summary with real values |
| tests | `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` | 10 Phase A tests covering degradation timeline, cost summary, tiered visibility |

### Data Contracts

**DiagnosticsEnvelope now includes**:
```python
degradation_timeline: list[DegradationEvent]  # Empty if no degradation
cost_summary: dict  # {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
```

**DegradationEvent structure**:
```python
@dataclass
class DegradationEvent:
    marker: str  # e.g., "FALLBACK_USED", "RETRY_ACTIVE"
    severity: str  # "minor", "moderate", "critical"
    timestamp: str  # ISO8601
    recovery_successful: bool
    recovery_latency_ms: int | None
    context_snapshot: dict  # e.g., {"turn_number": 42}
    span_ids: list[str]  # Empty in Phase A, filled in Phase B
```

### Phase B/C Dependencies

- **Phase B** (Langfuse): Fills cost_summary with real token counts and cost_breakdown
- **Phase C** (Governance): Uses degradation_timeline to implement cost-aware degradation (LDSS shortening when budget critical)
- **Phase C** (Evaluation): Uses quality_class + degradation_signals to train auto-tuning evaluator

### Backward Compatibility

✅ **No breaking changes**:
- New fields have sensible defaults (empty list, zero dict)
- Existing code reading DiagnosticsEnvelope continues to work
- `to_response()` method is new, doesn't modify existing behavior
- HTTP endpoints can opt-in to redaction gradually

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-002: Langfuse Integration & Real Trace Generation

**Status:** ACCEPTED
**Origin:** MVP4-002 (retired 2026-06-23)

**Context.** Phase A established the data structures and tiered visibility for diagnostics. Phase B must connect those diagnostics to real, external observability infrastructure via Langfuse v4 SDK. This enables:

- **Real trace generation**: Every turn execution produces a Langfuse trace with span hierarchy
- **Cost visibility**: Token consumption tracked per LDSS block, Narrator block, and other LLM calls
- **Span instrumentation**: LDSS execution, Narrator generation, scene block processing each get their own span
- **Trace correlation**: Same trace_id appears in diagnostics, Langfuse dashboard, and logs for RCA
- **Cost breakdown**: Operator can see which components consumed tokens (LDSS vs Narrator vs other)

**Constraints**:
- Must use real Langfuse v4 SDK (not mock)
- Traces must be deterministic and reproducible in local test environment
- Token costs must be calculated (even if estimated) per provider and model
- Span hierarchy must follow narrative execution flow (turn → scene blocks → validation → narrator)
- trace_id must correlate across DiagnosticsEnvelope, Langfuse API, and structured logs
- Must support both online (Langfuse cloud) and offline (local trace export) modes

---

**Decision.** **Phase B (Real Traces & Cost Tracking)**: Implement `LangfuseAdapter` with v4 SDK and populate `cost_summary` with real token counts.

### 1. **LangfuseAdapter Class** (`backend/app/observability/langfuse_adapter.py`)

```python
class LangfuseAdapter:
    def __init__(self, api_key: str | None, enabled: bool = True):
        self.enabled = enabled
        self.api_key = api_key
        self.client = Langfuse(api_key=api_key) if enabled and api_key else None
        self.traces: dict[str, Trace] = {}
    
    def create_span_context(self, trace_id: str, span_name: str, 
                           span_type: str = "generation") -> SpanContext:
        """Create a new span for tracing."""
        if not self.enabled or not self.client:
            return NoOpSpanContext()
        trace = self.client.trace(id=trace_id)
        span = trace.span(name=span_name, type=span_type)
        return span
    
    def calculate_token_cost(self, model: str, input_tokens: int, 
                            output_tokens: int) -> dict:
        """Calculate cost for a given model and token counts."""
        costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            # Default pricing
            "default": {"input": 0.001, "output": 0.002}
        }
        pricing = costs.get(model, costs["default"])
        return {
            "input_cost": (input_tokens / 1000) * pricing["input"],
            "output_cost": (output_tokens / 1000) * pricing["output"],
            "total_cost": (input_tokens / 1000) * pricing["input"] + 
                         (output_tokens / 1000) * pricing["output"]
        }
    
    def flush(self):
        """Flush pending traces to Langfuse."""
        if self.enabled and self.client:
            self.client.flush()
    
    def record_validation(self, trace_id: str, validation_type: str, 
                         passed: bool, latency_ms: int):
        """Record validation decision as span."""
        if not self.enabled:
            return
        # Implemented in test suite
```

### 2. **Span Instrumentation**

**LDSS Block Spans** (`ai_stack/langgraph/langgraph_runtime.py`):
- Create span when entering LDSS graph execution
- Record input (scene setup, character state), output (scene block)
- Tag with turn_number, scene_index
- Close span when LDSS completes (success or error)

**Narrator Block Spans**:
- Create span for narrator generation
- Record input (LDSS output, narrative context), output (narrator text)
- Tag with generation model, input/output token counts
- Calculate cost using LangfuseAdapter

**Scene Block Spans** (per block within LDSS):
- Create child spans for each scene block decision
- Record block type (dialogue, action, consequence)
- Tag with block_index, character involved

### 3. **cost_summary Population**

Extend `build_diagnostics_envelope()` to accept and populate `cost_summary`:

```python
def build_diagnostics_envelope(
    *,
    # ... existing parameters ...
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_breakdown: dict | None = None,
) -> DiagnosticsEnvelope:
    """Build envelope with real token counts from Phase B."""
    cost_summary = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": _calculate_total_cost(input_tokens, output_tokens),
        "cost_breakdown": cost_breakdown or {}
    }
    # ... rest of envelope construction ...
```

### 4. **Trace ID Correlation**

Ensure same `trace_id` flows through:
1. `DiagnosticsEnvelope.langfuse_trace_id` 
2. Langfuse SDK span context
3. Structured log context (logging.LogRecord.trace_id)
4. HTTP request context (X-Trace-ID header)

**Why this approach**:
- Langfuse v4 SDK is stable and widely used (battle-tested in production)
- Span hierarchy mirrors execution flow (turn → blocks → validation → narrator)
- Cost calculation decoupled from trace generation (can be estimated or real)
- Trace ID correlation enables RCA linking diagnostics → Langfuse dashboard → logs
- Offline mode (local trace export) works even if Langfuse cloud unavailable
- Token counts in cost_summary enable Phase C cost-aware degradation

**Alternatives considered**:
1. Custom trace format (rejected: reinvents Langfuse, loses ecosystem integrations)
2. Trace generation only at HTTP response time (rejected: misses internal span hierarchy)
3. Simple token counting without cost breakdown (rejected: loses operator cost visibility)
4. No local fallback, require Langfuse always (rejected: fails in offline/dev environments)

---

**Consequences.** ### Affected Services/Files

| Service | File | Change |
|---------|------|--------|
| backend | `backend/app/observability/langfuse_adapter.py` | Implement LangfuseAdapter with v4 SDK |
| ai_stack | `ai_stack/telemetry/diagnostics_envelope.py` | Populate cost_summary with real values |
| ai_stack | `ai_stack/langgraph/langgraph_runtime.py` | Instrument LDSS and Narrator with spans |
| world-engine | `world-engine/app/story_runtime/manager/` | Pass token counts to build_diagnostics_envelope |
| backend | `backend/app/observability/logging_config.py` | Add trace_id to log context |
| tests | `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` | 10 Phase B tests covering Langfuse spans and costs |

### Data Contracts

**LangfuseAdapter methods**:
```python
create_span_context(trace_id: str, span_name: str) -> SpanContext
calculate_token_cost(model: str, input_tokens: int, output_tokens: int) -> dict
flush() -> None
```

**DiagnosticsEnvelope Phase B fields** (from Phase A):
```python
cost_summary: dict  # Now populated with real values
# {
#   "input_tokens": 1234,
#   "output_tokens": 567,
#   "cost_usd": 0.045,
#   "cost_breakdown": {
#     "ldss_generation": 0.025,
#     "narrator_generation": 0.015,
#     "other": 0.005
#   }
# }

langfuse_trace_id: str | None  # trace ID for Langfuse correlation
langfuse_status: str  # "enabled" | "disabled" | "error"
```

**Span structure**:
```
turn_{trace_id}
├── ldss_generation_{block_index}
│   └── scene_block_decision
├── dramatic_validation
└── narrator_generation
```

### Phase B/C Dependencies

- **Phase C** (Governance): Uses cost_summary to enforce token budget and trigger cost-aware degradation
- **Phase C** (Evaluation): Uses langfuse_trace_id to link Langfuse dashboard with evaluation results
- **MVP5** (Session Replay): Fetches Langfuse trace data to correlate with diagnostics envelope

### Backward Compatibility

✅ **No breaking changes**:
- cost_summary defaults to zeros if not provided (Phase A behavior)
- LangfuseAdapter can be disabled (langfuse_status="disabled")
- Span instrumentation is internal (doesn't affect DiagnosticsEnvelope public API)
- Existing HTTP endpoints continue to work (just return non-zero cost_summary values)

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-003: Evaluation Pipeline & Quality Rubric

**Status:** ACCEPTED
**Origin:** MVP4-003 (retired 2026-06-23)

**Context.** MVP3 produced narrative output via LDSS. MVP4 must measure whether that output meets quality thresholds and enable iterative improvement. This requires:

- **Baseline establishment**: Recording canonical turns to establish quality floor
- **Quality dimensions**: Evaluating multiple aspects (coherence, authenticity, agency, immersion)
- **Auto-tuning**: Adjusting evaluation rubric weights based on production failures
- **Regression detection**: Identifying when quality drops below baseline
- **Operator feedback loop**: Recording human evaluation scores to retrain rubric weights

**Constraints**:
- Quality rubric must be persistent and versioned
- Dimensions must be measurable (not subjective)
- Auto-tuning must be safe (not regress below baseline)
- Evaluation must work with both real output and mock/test data
- Turn scores must be tied to specific session/turn IDs for reproducibility

---

**Decision.** **Phase C (Quality Evaluation & Rubric)**: Implement `EvaluationPipeline` with versioned `QualityRubric`, turn score recording, and auto-tuning weights.

### 1. **QualityDimension Enum** (`ai_stack/quality_lab/evaluation_pipeline.py`)

```python
class QualityDimension(Enum):
    COHERENCE = "coherence"         # Story makes logical sense
    AUTHENTICITY = "authenticity"   # Characters feel genuine and consistent
    PLAYER_AGENCY = "player_agency" # Player's choices visibly impact story
    IMMERSION = "immersion"         # World feels vivid and alive
```

### 2. **QualityRubric Dataclass**

```python
@dataclass
class RubricDimension:
    name: QualityDimension
    description: str
    score_range: tuple[float, float]        # (min, max) e.g. (0, 5)
    automated_eval: bool                    # Can automated tools evaluate?
    human_eval_required: bool               # Requires human annotation?
    weight: float = 1.0                     # Importance multiplier

@dataclass
class QualityRubric:
    rubric_id: str                                  # Unique identifier
    version: str                                    # Semantic version
    dimensions: list[RubricDimension]              # The 4 dimensions
    pass_threshold: float = 3.5                    # Score >= 3.5 passes
    last_updated: str = ""                         # ISO8601 timestamp
    last_tuned_by: str | None = None              # Who last updated weights?
    tuning_reason: str | None = None              # Why weights changed
```

### 3. **TurnScore Dataclass**

```python
@dataclass
class TurnScore:
    session_id: str
    turn_number: int
    trace_id: str
    
    scores: dict[QualityDimension, float]         # {COHERENCE: 4.2, ...}
    weighted_score: float                          # Average with rubric weights
    pass_status: bool                              # weighted_score >= pass_threshold?
    
    evaluator_type: str                            # "automated" | "human"
    evaluator_id: str | None                       # Who evaluated? (for human)
    evaluation_timestamp: str                      # ISO8601
    notes: str | None                              # Human annotation notes
```

### 4. **EvaluationPipeline Class**

```python
class EvaluationPipeline:
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
        self.current_rubric: QualityRubric | None = None
        self.baseline: dict[str, TurnScore] | None = None
    
    def get_rubric(self, version: str | None = None) -> QualityRubric:
        """Fetch current or specific rubric version."""
        if version:
            rubric = self.storage.get_rubric(version)
        else:
            rubric = self.storage.get_latest_rubric()
        
        if rubric is None:
            # Return default rubric with 4 dimensions, equal weights, pass_threshold=3.5
            return self._default_rubric()
        
        return rubric
    
    def _default_rubric(self) -> QualityRubric:
        """Default rubric: 4 dimensions, equal weights, threshold 3.5."""
        return QualityRubric(
            rubric_id="default",
            version="1.0.0",
            dimensions=[
                RubricDimension(
                    name=QualityDimension.COHERENCE,
                    description="Story narrative flows logically",
                    score_range=(0, 5),
                    automated_eval=True,
                    human_eval_required=False,
                    weight=1.0
                ),
                RubricDimension(
                    name=QualityDimension.AUTHENTICITY,
                    description="Characters feel genuine and consistent",
                    score_range=(0, 5),
                    automated_eval=True,
                    human_eval_required=True,
                    weight=1.0
                ),
                RubricDimension(
                    name=QualityDimension.PLAYER_AGENCY,
                    description="Player choices visibly impact story",
                    score_range=(0, 5),
                    automated_eval=True,
                    human_eval_required=True,
                    weight=1.0
                ),
                RubricDimension(
                    name=QualityDimension.IMMERSION,
                    description="World feels vivid and alive",
                    score_range=(0, 5),
                    automated_eval=True,
                    human_eval_required=True,
                    weight=1.0
                ),
            ],
            pass_threshold=3.5
        )
    
    def record_turn_score(self, score: TurnScore) -> None:
        """Record evaluated turn score."""
        self.storage.save_turn_score(score)
    
    def get_baseline(self) -> dict[str, TurnScore]:
        """Fetch canonical baseline turns."""
        if self.baseline is None:
            self.baseline = self.storage.get_baseline_turns()
        return self.baseline
    
    def check_baseline_regression(self, recent_score: TurnScore) -> bool:
        """Detect if recent turn scores regressed below baseline."""
        baseline = self.get_baseline()
        if not baseline:
            return False  # No baseline, can't detect regression
        
        # Compare recent score against baseline average
        baseline_avg = sum(s.weighted_score for s in baseline.values()) / len(baseline)
        return recent_score.weighted_score < (baseline_avg * 0.9)  # 10% below triggers
    
    def auto_tune_weights(self, failure_pattern: dict[QualityDimension, int]) -> None:
        """Adjust rubric weights based on production failures.
        
        failure_pattern: {COHERENCE: 3, AUTHENTICITY: 5, ...}
        Dimensions with more failures get higher weights.
        """
        rubric = self.get_rubric()
        total_failures = sum(failure_pattern.values())
        
        if total_failures == 0:
            return  # No failures, no tuning needed
        
        # Adjust weights proportionally to failure count
        for dimension in rubric.dimensions:
            failures = failure_pattern.get(dimension.name, 0)
            new_weight = 1.0 + (failures / max(total_failures, 1))
            dimension.weight = new_weight
        
        # Normalize weights to sum to 4 (4 dimensions)
        total_weight = sum(d.weight for d in rubric.dimensions)
        for dimension in rubric.dimensions:
            dimension.weight = dimension.weight * 4 / total_weight
        
        rubric.last_updated = datetime.now(timezone.utc).isoformat()
        rubric.last_tuned_by = "auto_tuner"
        rubric.tuning_reason = "Production failure pattern detected"
        
        self.storage.save_rubric(rubric)
        self.current_rubric = rubric
```

### 5. **Baseline & Regression Detection**

Canonical baseline turns (stored in evaluations database):
```python
baseline_turns = {
    "god_of_carnage_turn_1": TurnScore(..., weighted_score=4.2, pass_status=True),
    "god_of_carnage_turn_2": TurnScore(..., weighted_score=4.1, pass_status=True),
    "annette_turn_5": TurnScore(..., weighted_score=3.8, pass_status=True),
}
```

Regression detection triggers cost-aware degradation in Phase C:
```python
if pipeline.check_baseline_regression(recent_score):
    # Downgrade LDSS config (shorter context, simpler decision tree)
    # Or fallback to narrator-only mode (skip LDSS)
```

**Why this approach**:
- 4 dimensions cover narrative pillars (logic, character, choice, immersion)
- Rubric is versioned (can evolve without breaking old evaluations)
- Auto-tuning learns which dimensions fail most in production
- Baseline detection prevents silent quality regression
- Turn scores are tied to session/turn/trace for reproducibility
- Weights are adjustable (manual override for operator control)

**Alternatives considered**:
1. Single monolithic quality score (rejected: loses visibility into which aspects fail)
2. Hardcoded rubric weights (rejected: can't adapt to real production patterns)
3. Only human evaluation (rejected: too slow for real-time feedback)
4. Only automated evaluation (rejected: can't capture subjective experiences like immersion)

---

**Consequences.** ### Affected Services/Files

| Service | File | Change |
|---------|------|--------|
| ai_stack | `ai_stack/quality_lab/evaluation_pipeline.py` | Implement EvaluationPipeline, QualityRubric, TurnScore |
| backend | `backend/app/evaluations/storage.py` | Persist rubrics and turn scores |
| world-engine | `world-engine/app/story_runtime/manager/` | Call record_turn_score() after turn evaluation |
| backend | `backend/app/api/evaluations.py` | HTTP endpoints for rubric CRUD and score recording |
| tests | `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` | 6 Phase C evaluation tests |

### Data Contracts

**QualityRubric contract**:
```python
{
    "rubric_id": "default",
    "version": "1.0.0",
    "dimensions": [
        {
            "name": "COHERENCE",
            "description": "Story narrative flows logically",
            "score_range": [0, 5],
            "automated_eval": true,
            "human_eval_required": false,
            "weight": 1.0
        },
        # ... 3 more dimensions ...
    ],
    "pass_threshold": 3.5,
    "last_updated": "2026-04-30T12:00:00Z",
    "last_tuned_by": "auto_tuner",
    "tuning_reason": "Production failure pattern detected"
}
```

**TurnScore contract**:
```python
{
    "session_id": "session-abc123",
    "turn_number": 1,
    "trace_id": "trace-xyz789",
    "scores": {
        "COHERENCE": 4.2,
        "AUTHENTICITY": 3.9,
        "PLAYER_AGENCY": 4.1,
        "IMMERSION": 3.7
    },
    "weighted_score": 4.0,
    "pass_status": true,
    "evaluator_type": "human",
    "evaluator_id": "operator-001",
    "evaluation_timestamp": "2026-04-30T12:00:00Z",
    "notes": "Slight immersion dip but overall strong turn"
}
```

### Phase C Dependencies

- **Governance**: Cost-aware degradation uses baseline regression detection to trigger budget conservation
- **Audit Trail**: Each rubric change logged as OverrideAuditEvent (who changed weights, when, why)
- **Narrative Gov**: Health panels show current rubric version and tuning status

### Backward Compatibility

✅ **No breaking changes**:
- EvaluationPipeline returns default rubric if none exists (graceful default)
- TurnScore is new dataclass (doesn't affect existing DiagnosticsEnvelope)
- Auto-tuning is optional (can be disabled per-deployment)
- Existing HTTP endpoints unaffected (new endpoints added for eval API)

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-004: Narrative Governance Health Panels & Operator Control

**Status:** ACCEPTED
**Origin:** MVP4-004 (retired 2026-06-23)

**Context.** MVP4 collects observability data (diagnostics, traces, evaluations, audit logs). Operators need a unified dashboard view of system health, enabling real-time decisions like:

- Should I degrade LDSS (shorter context) to save budget?
- Is actor lane enforcement stable or drifting?
- Are we tracking toward baseline or regressing?
- Which narrative Gov overrides are active and why?

These decisions require structured health panels that surface operator-critical signals without overwhelming with raw data.

**Constraints**:
- Health panels must be real-time (within 1 second of turn execution)
- Must aggregate data from multiple sources (LDSS, Narrator, actor lanes, evaluations)
- Must be actionable (not just metrics—show what to do)
- Must respect tiered visibility (operator sees different panels than super-admin)
- Must support drill-down (click panel → see underlying diagnostics)

---

**Decision.** **Phase C (Narrative Governance Panels)**: Implement `NarrativeGovSummary` dataclass with 6 operator-facing health panels.

### 1. **NarrativeGovSummary Dataclass** (`ai_stack/telemetry/diagnostics_envelope.py`)

```python
@dataclass
class HealthPanel:
    name: str                       # "Actor Lane Health", "LDSS Status", etc.
    status: str                     # "healthy" | "warning" | "critical"
    value: str | float              # Current reading (e.g., "4.2/5.0")
    threshold_warning: float | str | None  # When does it enter warning?
    threshold_critical: float | str | None # When does it enter critical?
    last_updated: str               # ISO8601 timestamp
    drill_down_url: str | None      # Link to detailed diagnostics

@dataclass
class NarrativeGovSummary:
    session_id: str
    turn_number: int
    timestamp: str
    
    # Health panels
    panels: dict[str, HealthPanel]
    
    # Recommended actions (operator guidance)
    recommended_actions: list[str]  # ["Reduce LDSS context", "Check actor lane 3", ...]
    
    # Current constraints
    cost_budget_remaining_usd: float
    cost_budget_percent_used: float
    
    # Evaluation status
    quality_score: float
    quality_trend: str              # "improving" | "stable" | "degrading"
    
    # Override status
    active_overrides: list[str]     # Which Gov overrides are active?
```

### 2. **Health Panels (6 total)**

#### Panel 1: Actor Lane Health
```python
HealthPanel(
    name="actor_lane_health",
    status="healthy" if all lanes healthy else "warning" if some lanes degraded else "critical",
    value=f"{healthy_lanes}/{total_lanes} lanes active",
    threshold_warning=0.75,  # 75% healthy
    threshold_critical=0.5,  # 50% healthy
    drill_down_url="/api/v1/admin/narrative-gov/{session_id}/actor-lanes"
)
```
Monitors: Are all actor lanes producing output? Are lane decisions stable?

#### Panel 2: LDSS Status
```python
HealthPanel(
    name="ldss_status",
    status="healthy" if execution_successful else "degraded" if with_fallback else "error",
    value=f"{block_count} blocks, {avg_latency_ms}ms avg",
    threshold_warning=500,  # latency_ms > 500 → warning
    threshold_critical=1000, # latency_ms > 1000 → critical
    drill_down_url="/api/v1/admin/narrative-gov/{session_id}/ldss-blocks"
)
```
Monitors: Is LDSS executing smoothly? Are fallbacks being triggered?

#### Panel 3: NPC Agency Pressure
```python
HealthPanel(
    name="npc_agency_pressure",
    status="healthy" if pressure_low else "warning" if pressure_moderate else "critical",
    value=f"{agency_pressure_percent:.0f}% (low=healthy)",
    threshold_warning=50,  # Pressure > 50% is concerning
    threshold_critical=80, # Pressure > 80% is critical
    drill_down_url="/api/v1/admin/narrative-gov/{session_id}/npc-agency"
)
```
Monitors: Are NPC decisions crowding out player choice?

#### Panel 4: Narrator Validation Strictness
```python
HealthPanel(
    name="narrator_validation_strictness",
    status="healthy" if 0.3 <= strictness <= 0.7 else "warning" if strictness < 0.2 or strictness > 0.8 else "critical",
    value=f"{strictness:.2f} (0=permissive, 1=strict)",
    threshold_warning=(0.2, 0.8),  # Outside this range → warning
    threshold_critical=(0.0, 1.0),
    drill_down_url="/api/v1/admin/narrative-gov/{session_id}/narrator-validation"
)
```
Monitors: Is narrator validation appropriately balanced?

#### Panel 5: Affordance Tier Tracking
```python
HealthPanel(
    name="affordance_tier_tracking",
    status="healthy" if tier_active else "warning",
    value=f"Tier {current_tier} ({scenario_type})",
    threshold_warning=None,
    threshold_critical=None,
    drill_down_url="/api/v1/admin/narrative-gov/{session_id}/affordance-tiers"
)
```
Monitors: What story complexity tier is active? Has it changed recently?

#### Panel 6: Cost Budget Tracking
```python
HealthPanel(
    name="cost_budget_tracking",
    status="healthy" if cost_used < 0.8 else "warning" if cost_used < 0.95 else "critical",
    value=f"${cost_used:.2f} / ${cost_budget:.2f} ({percent_used:.0f}%)",
    threshold_warning=0.8,  # 80% → warning
    threshold_critical=0.95, # 95% → critical
    drill_down_url="/api/v1/admin/narrative-gov/{session_id}/cost-tracking"
)
```
Monitors: How much token budget remains?

### 3. **Recommended Actions**

Auto-generated based on panel states:
```python
def generate_recommended_actions(summary: NarrativeGovSummary) -> list[str]:
    actions = []
    
    # Cost-aware actions
    if summary.panels["cost_budget_tracking"].status == "critical":
        actions.append("Reduce LDSS context window (cost critical)")
    elif summary.panels["cost_budget_tracking"].status == "warning":
        actions.append("Consider shortening narrator blocks (cost at 80%)")
    
    # Quality actions
    if summary.quality_trend == "degrading":
        actions.append("Increase narrator validation strictness")
        actions.append("Check LDSS block outputs for coherence")
    
    # Agency actions
    if summary.panels["npc_agency_pressure"].status == "critical":
        actions.append("Reduce NPC decision frequency")
        actions.append("Increase player affordances")
    
    # Lane actions
    if summary.panels["actor_lane_health"].status == "critical":
        actions.append(f"Investigate degraded lanes: {degraded_lane_names}")
    
    return actions
```

### 4. **build_narrative_gov_summary() Function**

```python
def build_narrative_gov_summary(
    session_id: str,
    turn_number: int,
    ldss_state: dict,
    actor_lanes: dict,
    evaluation_result: EvaluationResult,
    cost_tracking: CostTracking,
    overrides: list[OverrideAuditEvent]
) -> NarrativeGovSummary:
    """Synthesize health panels from runtime state."""
    
    # Panel 1: Actor Lane Health
    healthy_lanes = sum(1 for lane in actor_lanes.values() if lane["status"] == "healthy")
    actor_panel = HealthPanel(
        name="actor_lane_health",
        status="healthy" if healthy_lanes == len(actor_lanes) else "warning",
        value=f"{healthy_lanes}/{len(actor_lanes)} lanes active",
        drill_down_url=f"/api/v1/admin/narrative-gov/{session_id}/actor-lanes"
    )
    
    # Panel 2: LDSS Status
    ldss_panel = HealthPanel(
        name="ldss_status",
        status="healthy" if ldss_state["success"] else "degraded" if ldss_state["fallback_used"] else "error",
        value=f"{ldss_state['block_count']} blocks, {ldss_state['latency_ms']}ms",
        drill_down_url=f"/api/v1/admin/narrative-gov/{session_id}/ldss-blocks"
    )
    
    # Panel 3-6: (similar construction)
    
    # Recommended actions
    actions = generate_recommended_actions(summary)
    
    return NarrativeGovSummary(
        session_id=session_id,
        turn_number=turn_number,
        timestamp=datetime.now(timezone.utc).isoformat(),
        panels={
            "actor_lane_health": actor_panel,
            "ldss_status": ldss_panel,
            # ... other panels ...
        },
        recommended_actions=actions,
        cost_budget_remaining_usd=cost_tracking["remaining"],
        cost_budget_percent_used=cost_tracking["percent_used"],
        quality_score=evaluation_result["weighted_score"],
        quality_trend=evaluation_result["trend"],
        active_overrides=[o.override_id for o in overrides if o.applied]
    )
```

### 5. **HTTP Endpoints**

```python
# GET /api/v1/admin/narrative-gov/{session_id}
# Returns NarrativeGovSummary for current turn
# Response includes all 6 health panels + recommended actions

# GET /api/v1/admin/narrative-gov/{session_id}/history
# Returns NarrativeGovSummary for all turns in session
# Enables trend analysis

# GET /api/v1/admin/narrative-gov/{session_id}/{panel_name}
# Returns detailed diagnostics for specific panel
# E.g., /narrative-gov/{session_id}/actor-lanes → full lane state
```

**Why this approach**:
- 6 panels cover all operator-critical signals (agency, budget, quality, lanes, narrator, affordances)
- Status (healthy/warning/critical) simplifies decision-making
- Recommended actions guide operators without requiring deep system knowledge
- Drill-down URLs enable investigation without overwhelming main dashboard
- Panels are real-time (constructed from DiagnosticsEnvelope + evaluation result)
- Backward compatible (NarrativeGovSummary is new, doesn't break existing contracts)

**Alternatives considered**:
1. Single "health score" 0-100 (rejected: loses visibility into which component is failing)
2. Raw metrics dashboard (rejected: too much data, not actionable)
3. AI-generated narrative about health (rejected: hard to verify, operator loses control)
4. Separate admin UI (rejected: requires MVP5, can't wait for observability)

---

**Consequences.** ### Affected Services/Files

| Service | File | Change |
|---------|------|--------|
| ai_stack | `ai_stack/telemetry/diagnostics_envelope.py` | Add HealthPanel and NarrativeGovSummary dataclasses |
| ai_stack | `ai_stack/telemetry/diagnostics_envelope.py` | Implement build_narrative_gov_summary() |
| world-engine | `world-engine/app/story_runtime/manager/` | Call build_narrative_gov_summary() after turn |
| world-engine | `world-engine/app/api/http.py` | Add /narrative-gov endpoints |
| backend | `backend/app/auth/admin_security.py` | Audit trail for override tracking |
| tests | `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` | 3 Phase C governance tests |

### Data Contracts

**HealthPanel contract**:
```python
{
    "name": "actor_lane_health",
    "status": "healthy",  # "healthy" | "warning" | "critical"
    "value": "3/3 lanes active",
    "threshold_warning": 0.75,
    "threshold_critical": 0.5,
    "last_updated": "2026-04-30T12:00:00Z",
    "drill_down_url": "/api/v1/admin/narrative-gov/{session_id}/actor-lanes"
}
```

**NarrativeGovSummary contract**:
```python
{
    "session_id": "session-abc123",
    "turn_number": 5,
    "timestamp": "2026-04-30T12:00:00Z",
    "panels": {
        "actor_lane_health": {...},
        "ldss_status": {...},
        "npc_agency_pressure": {...},
        "narrator_validation_strictness": {...},
        "affordance_tier_tracking": {...},
        "cost_budget_tracking": {...}
    },
    "recommended_actions": [
        "Reduce LDSS context window (cost critical)",
        "Investigate degraded lanes: Lane 2"
    ],
    "cost_budget_remaining_usd": 2.34,
    "cost_budget_percent_used": 0.75,
    "quality_score": 4.1,
    "quality_trend": "stable",
    "active_overrides": ["override-001", "override-003"]
}
```

### Phase C/MVP5 Dependencies

- **Phase C**: Narrative Gov panels drive cost-aware degradation decisions
- **Phase C**: Audit trail logs operator actions triggered by health panel insights
- **MVP5**: Admin UI embeds NarrativeGovSummary panels with interactive drill-down
- **MVP5**: Session Replay correlates health panel history with narrative output

### Backward Compatibility

✅ **No breaking changes**:
- NarrativeGovSummary is new dataclass (doesn't affect existing contracts)
- HTTP endpoints are new (no changes to existing ones)
- DiagnosticsEnvelope unchanged (HealthPanel and NarrativeGovSummary are separate)
- Existing observability flow unaffected

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-008: Diagnostics and Degradation Semantics

**Status:** Accepted
**Origin:** MVP4-008 (retired 2026-06-23)

**Context.** Prior to MVP4, the runtime produced quality_class and degradation_signals in internal graph state, but this was not surfaced in a standardized, operator-readable diagnostic contract. Operators could not tell from a turn response whether the output was normal, degraded, failed, or mock/static.

MVP4 introduces the DiagnosticsEnvelope contract to make quality and degradation evidence explicit and non-placeholder.

**Decision.** 1. **DiagnosticsEnvelope** is the canonical per-turn diagnostic surface. Contract: `diagnostics_envelope.v1`.

2. **Four quality outcomes** are defined:
   - `ok` / `normal` — canonical quality, no degradation
   - `ok_with_degradation` / `degraded` — committed but with known degradation signals
   - `failed` — validation rejected, commit not applied
   - `mock_static_invalid` — static fixture or placeholder; cannot be accepted as final proof

3. **Degraded output requires reasons**: If `quality_class == "degraded"`, `degradation_signals` must be non-empty. An empty degradation_signals list with degraded quality is rejected with `degraded_output_missing_reasons`.

4. **Validation before evidence claim**: `validate_evidence_consistency()` accepts LDSS proof statuses from the active runtime path: `"approved"` for direct canonical-step LDSS envelopes and `"evidenced_live_path"` for higher-level story-manager evidence projection. The validator also requires no LDSS error, `decision_count > 0`, and `scene_block_count > 0`. An envelope with only static success-looking fields and zero counts fails with `diagnostics_missing_evidence`; an unsupported or errored LDSS status fails with `diagnostics_missing_ldss_proof`.

5. **Response packaging is committed-state only**: `response_packaged_from_committed_state = True` is always set. Diagnostics never claim AI proposals as committed truth.

6. **TraceableDecision** records each runtime decision (responder plan, actor-lane validation, dramatic validation, commit) with `decision_id`, `status`, `input_refs`, `rejected_reasons`.

**Consequences.** - Every GoC solo turn produces a structured, non-placeholder DiagnosticsEnvelope
- Operators can tell exactly what happened: validation status, commit result, quality class, degradation signals
- Static fields claiming success without evidence are rejected by the validator
- Direct canonical-step LDSS diagnostics can remain truthful as `"approved"` while still satisfying diagnostics evidence consistency; the story manager may expose the same successful path as `"evidenced_live_path"` for operator-level summaries
- The world-engine execute-turn integration oracle allows slow local backend bootstrap while still failing with an explicit timeout diagnostic if the behavioral proof stalls

**Affected services.** - `ai_stack/telemetry/diagnostics_envelope.py` — `DiagnosticsEnvelope`, `validate_evidence_consistency()`, `build_diagnostics_envelope()`
- `world-engine/app/story_runtime/manager/` — `_finalize_committed_turn` adds `diagnostics_envelope` to event
- `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` — gate tests
- `tests/gates/we_contract_helpers.py` — behavioral integration oracle for the world-engine diagnostics test

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-009: Langfuse and Traceable Decisions

**Status:** Accepted
**Origin:** MVP4-009 (retired 2026-06-23)

**Context.** The live runtime makes multiple decisions per turn (responder plan, actor-lane validation, dramatic validation, commit). These decisions were not individually traceable. Operators had no way to correlate a turn response with a specific Langfuse trace or to inspect per-decision outcomes.

**Decision.** 1. **TraceableDecision** records each turn decision with `decision_id`, `decision_type`, `story_session_id`, `turn_number`, `status`, `trace_span_name`, `input_refs`, `selected_output_ref`, `rejected_reasons`.

2. **Decision types**: `npc_responder_plan`, `actor_lane_validation`, `dramatic_validation`, `engine_commit`.

3. **Langfuse is optional and disabled by default**. When disabled, `langfuse_status = "disabled"` is reported. The system never claims trace success when Langfuse is unconfigured.

4. **LocalTraceExport** is the test-friendly alternative to Langfuse. It is always generated by real test execution (not a static fixture). Contract: `langfuse_real_trace_evidence.v1`. `static_fixture = False` must be enforced. If `static_fixture = True`, the trace fails validation with `langfuse_mock_only_trace_not_final`.

5. **Trace ID correlation**: `trace_id` from the HTTP request header appears in `DiagnosticsEnvelope.trace_id`. This allows log/trace/diagnostics correlation without Langfuse.

6. **Secret redaction**: `redact_secrets()` removes any value whose key contains `secret`, `key`, `token`, `password`, `credential`, `auth`, `api_key`, `private`, `passphrase`, `access_token`.

7. **Span names**: Each TraceableDecision has a `trace_span_name` matching the Langfuse span hierarchy: `live_dramatic_scene_simulator.responder_plan`, `actor_lane_validation`, `dramatic_validation`, `commit_seam`.

**Consequences.** - Every turn has traceable per-decision records
- Langfuse disabled mode is safe and explicit (no false success)
- Test environments can prove the trace contract without Langfuse credentials
- Secrets are never in diagnostics or trace exports

**Affected services.** - `ai_stack/telemetry/diagnostics_envelope.py` — `TraceableDecision`, `LocalTraceExport`, `build_traceable_decisions()`, `build_local_trace_export()`, `redact_secrets()`
- `backend/app/observability/langfuse_adapter.py` — pre-existing Langfuse adapter (unchanged)
- `backend/app/observability/trace.py` — trace_id context var (unchanged)

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-010: Narrative Gov Operator Truth Surface

**Status:** Accepted
**Origin:** MVP4-010 (retired 2026-06-23)

**Context.** The administration-tool's Narrative Gov `runtime.html` page was a placeholder with no live data. Operators had no way to inspect the live runtime health of the God of Carnage session: content module load status, runtime profile boundary, LDSS health, actor lane enforcement, and degradation state.

**Decision.** 1. **NarrativeGovSummary** is the canonical operator health surface. Contract: `narrative_gov_summary.v1`. It is derived from real session diagnostics, not from static configuration.

2. **Six health panels** are required:
   - `content_module_health` — is canonical content loaded?
   - `runtime_profile_health` — is the profile story-truth-free?
   - `runtime_module_health` — is the runtime module story-truth-free?
   - `ldss_health` — does the last turn carry LDSS evidence (`approved` direct canonical-step proof or `evidenced_live_path` story-manager projection) with trace metadata?
   - `frontend_render_contract_health` — are scene blocks present and legacy blob absent?
   - `actor_lane_health` — is enforcement active? Is visitor absent?

3. **Source-backed**: NarrativeGovSummary is built by `get_narrative_gov_summary()` in `StoryRuntimeManager`, which scans live sessions for the most recent GoC session with a diagnostics_envelope. It is not hardcoded or static.

4. **API endpoint**: `GET /api/story/runtime/narrative-gov-summary` in world-engine returns the NarrativeGovSummary. The endpoint requires the internal API key.

5. **Administration-tool UI**: `runtime.html` fetches the summary via `/_proxy/api/story/runtime/narrative-gov-summary` and renders panels in the browser. If play-service is offline, the UI reports "unavailable."

6. **Visitor exclusion**: `actor_lane_health.visitor_present = False` is always enforced. `visitor` never appears in any health panel.

7. **Degradation health**: `degradation_health` shows `quality_class`, `degradation_signals`, and `status` (normal/degraded/failed). Operators can see at a glance whether the last turn was clean.

**Consequences.** - Operators can inspect live runtime health without reading logs
- The Narrative Gov surface is source-backed from real session diagnostics
- Stale/static operator evidence is rejected
- The UI degrades gracefully when play-service is unavailable

**Affected services.** - `ai_stack/telemetry/diagnostics_envelope.py` — `NarrativeGovSummary`, `build_narrative_gov_summary()`
- `world-engine/app/story_runtime/manager/` — `get_narrative_gov_summary()`
- `world-engine/app/api/http.py` — `GET /story/runtime/narrative-gov-summary`
- `administration-tool/templates/manage/narrative_governance/runtime.html` — 6 health panels with JS fetch

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP5-001: Modular Block Rendering Architecture

**Status:** ACCEPTED
**Origin:** MVP5-001 (retired 2026-06-23)

**Context.** MVP5 requires a frontend capable of rendering interactive text-adventure narratives with:
- Block-by-block scene composition (no single-blob rendering)
- Deterministic typewriter animation with test-mode virtual time control
- Skip/Reveal controls that work without runtime regeneration
- Full accessibility support (reduced motion, full text visibility)

The previous MVP4 frontend (`play_shell.js`) used monolithic rendering with a single HTML blob. This made it difficult to:
- Test individual block delivery
- Implement granular skip/reveal controls
- Support progressive reveal animations
- Maintain clean separation between rendering, animation, and state

---

**Decision.** Implement a **modular, single-responsibility architecture** with four independent JavaScript modules:

1. **BlockRenderer** — Pure DOM rendering, creates one `<div data-block-id>` per block
2. **TypewriterEngine** — Deterministic character delivery with VirtualClock for tests
3. **BlocksOrchestrator** — Centralized state management and coordination
4. **PlayControls** — Event handling for skip/reveal UI buttons

Each module has a single responsibility and exports a clean interface. Modules communicate via:
- Direct method calls (orchestrator → renderer/engine)
- DOM events (controls → orchestrator)
- Data attributes (renderer → DOM, useful for testing/debugging)

---

**Consequences.** ### Positive
✅ **Testability**: 76+ unit tests cover all four modules independently  
✅ **Deterministic Animation**: Test suite runs in 0.66s; no flaky timeouts  
✅ **Clean Contracts**: Each module has a clear public API  
✅ **Maintainability**: Adding new features (e.g., pause/resume) requires changes to 1–2 modules  
✅ **Accessibility**: Each block can respect system preferences independently  

### Negative
❌ **Module Coupling**: BlocksOrchestrator is the "hub" and knows about all other modules  
❌ **Setup Overhead**: Tests must initialize all four modules to test integration  
❌ **Global State**: `window.TEST_MODE` flag checked in VirtualClock (not ideal, but works for testing)  

### Mitigation
- Orchestrator interface is documented and versioned
- E2E tests verify full integration; unit tests verify individual contracts
- TEST_MODE is only used in non-production code paths

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP5-002: Virtual Clock for Deterministic Animation Testing

**Status:** ACCEPTED
**Origin:** MVP5-002 (retired 2026-06-23)

**Context.** Typewriter animation (progressive character reveal) is core to MVP5 narrative delivery. However, testing animation presents challenges:

- **Real Time Delays**: Waiting for actual animation makes tests slow (100ms+ per block)
- **Flakiness**: System load affects timing; tests fail randomly if animation is slightly slower
- **CI/CD Pipeline**: Slow tests increase feedback loop (commit → green light takes 5+ minutes)
- **Debugging**: Hard to understand why animation test failed (timing issue? code issue?)

We need a pattern that:
- Eliminates time delays from tests (run in milliseconds)
- Allows tests to control animation progression step-by-step
- Works seamlessly in both test and production modes
- Requires no external time-mocking libraries

---

**Decision.** Implement **VirtualClock** — a dual-mode clock that switches between:

1. **Test Mode** (`testMode=true`)
   - Virtual time controlled by test via `advanceBy(ms)`
   - No `requestAnimationFrame` loop; tests drive animation
   - Used in all unit and E2E tests

2. **Production Mode** (`testMode=false`)
   - Real time via `performance.now()`
   - Uses `requestAnimationFrame` for smooth 60fps animation
   - Default behavior in deployed frontend

### Implementation

```javascript
class VirtualClock {
  constructor(testMode = false) {
    this.test_mode = testMode;
    this.virtual_time = 0;  // Only used in test mode
    this.listeners = [];
  }

  advanceBy(ms) {
    if (!this.test_mode) throw Error("Test mode only");
    this.virtual_time += ms;
    this._notifyListeners();
  }

  now() {
    return this.test_mode ? this.virtual_time : performance.now();
  }

  start() {
    if (this.test_mode) return;  // Tests drive time, no loop
    const animate = () => {
      this._notifyListeners();
      this.requestId = requestAnimationFrame(animate);
    };
    this.requestId = requestAnimationFrame(animate);
  }
}
```

### TypewriterEngine Integration

```javascript
class TypewriterEngine {
  constructor(testMode = false) {
    this.clock = new VirtualClock(testMode);
    // ... rest of initialization
  }

  startDelivery(block) {
    // Calculate delivery duration at 44 cps
    const duration = (block.text.length / 44) * 1000;
    const queueItem = {
      block_id: block.id,
      text: block.text,
      start_time: this.clock.now(),  // Uses virtual or real time
      duration: duration,
    };
    this.queue.push(queueItem);
  }
}
```

### Test Usage

```javascript
// Setup
const engine = new TypewriterEngine(testMode = true);
engine.startDelivery({ id: "b1", text: "Hello world" });

// Delivery at 44 cps: "Hello world" (11 chars) = 250ms
// Test controls time:
engine.clock.advanceBy(250);  // Full delivery
assert(engine.visible_chars("b1") === 11);

// Or incremental:
engine.clock.advanceBy(50);   // ~2 chars
assert(engine.visible_chars("b1") === 2);
```

---

**Consequences.** ### Positive
✅ **Fast Tests**: 76+ animation tests run in 0.66 seconds (no waiting)  
✅ **Deterministic**: Same test produces same result every run (no flakiness)  
✅ **Explicit**: Test code clearly shows timing progression (advanceBy(250))  
✅ **No Dependencies**: No Jest, Sinon, or other test framework required  
✅ **Debuggable**: Test failure shows exact time step that failed  

### Negative
❌ **Dual Codepaths**: Production and test have slightly different clock logic (mitigated: same interface)  
❌ **Manual Time Advancement**: Tests must manually advance time (not automatic like setTimeout)  
❌ **Hidden Assumptions**: Tests must know "44 cps means 250ms for 11 chars" (mitigated: documented)  

### Mitigations
- Same VirtualClock interface used in both modes (testMode flag is only difference)
- Test utilities can provide helpers: `advanceByBlock(block)` calculates duration automatically
- Documentation in code explains the 44 cps rate and how to calculate duration

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)

### MVP5-003: Accessibility Mode & Reduced Motion Support

**Status:** ACCEPTED
**Origin:** MVP5-003 (retired 2026-06-23)

**Context.** MVP5 narrative frontend must be accessible to players with:
- **Visual sensitivities**: Motion-induced migraines, ADHD, vestibular disorders
- **Motor impairments**: Limited ability to read fast-moving text, need for slower or paused animation
- **Cognitive needs**: Preference for all content visible at once rather than progressive reveal
- **System Preferences**: Respecting OS-level `prefers-reduced-motion` media query

The challenge: Balance rich animation experience (typewriter effect is emotionally engaging) with accessibility requirements (animation can be harmful for some players).

---

**Decision.** Implement **dual-mode rendering** with two entry points:

1. **Standard Mode** (default)
   - Typewriter animation delivers characters progressively
   - Skip/Reveal controls allow player agency
   - Smooth transitions and visual feedback

2. **Accessibility Mode** (enabled by player preference or system setting)
   - All text visible immediately (typewriter disabled)
   - No animations or transitions
   - Static layout, full cognitive load at once
   - Respects system `prefers-reduced-motion: reduce` media query

### Implementation

#### BlocksOrchestrator API

```javascript
class BlocksOrchestrator {
  constructor(renderer, typewriter) {
    this.renderer = renderer;
    this.typewriter = typewriter;
    this.accessibility_mode = false;
    this.blocks = [];
  }

  setAccessibilityMode(enabled) {
    this.accessibility_mode = enabled;
    document.body.classList.toggle('accessibility-mode', enabled);
    
    if (enabled) {
      // Cancel any ongoing typewriter animations
      this.typewriter.revealAll();
      // Disable future animations
      this.typewriter.setConfig({ characters_per_second: Infinity });
    } else {
      // Reset to normal speed
      this.typewriter.setConfig({ characters_per_second: 44 });
    }
  }

  loadTurn(response) {
    const blocks = response.visible_scene_output.blocks || [];
    
    blocks.forEach(block => {
      this.renderer.render(block);
      
      if (!this.accessibility_mode) {
        // Start typewriter animation
        this.typewriter.startDelivery(block);
      }
      // In accessibility mode, all text is already visible (rendered with full text)
    });
    
    this.blocks = blocks;
  }
}
```

#### CSS Implementation

```css
/* Base block styling */
.scene-block {
  margin: 1rem 0;
  padding: 1rem;
  border-left: 4px solid #ccc;
  background-color: #f9f9f9;
  line-height: 1.6;
}

/* Block type variants */
.scene-block--narrator {
  border-left-color: #667eea;
  background-color: #f0f4ff;
}

.scene-block--actor_line {
  border-left-color: #f093fb;
  background-color: #fff0f8;
}

.scene-block--actor_action {
  border-left-color: #06b6d4;
  background-color: #f0f9ff;
}

.scene-block--stage_direction {
  border-left-color: #999;
  background-color: #f5f5f5;
  font-style: italic;
}

.scene-block--environmental {
  border-left-color: #10b981;
  background-color: #f0fdf4;
}

/* Accessibility mode: disable animations, increase contrast */
.accessibility-mode .scene-block {
  animation: none;
  transition: none;
  border-left-width: 6px;  /* Slightly thicker border for visibility */
}

.accessibility-mode .scene-block::after {
  content: '';  /* No animated pseudo-elements */
  display: none;
}

/* Respect system prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .scene-block {
    animation: none;
    transition: none;
  }
  
  .typewriter-char {
    animation: none;
  }
}
```

#### UI Control

```html
<!-- Accessibility mode toggle button -->
<button id="play-accessibility-mode" 
        class="accessibility-toggle"
        title="Enable accessibility mode (disable animations, show all text)">
  Accessibility Mode
</button>
```

```javascript
// In PlayControls.attachEventListeners():
const a11yBtn = document.getElementById('play-accessibility-mode');
if (a11yBtn) {
  a11yBtn.addEventListener('click', () => {
    const enabled = !this.orchestrator.accessibility_mode;
    this.orchestrator.setAccessibilityMode(enabled);
    a11yBtn.classList.toggle('active', enabled);
  });
}
```

---

**Consequences.** ### Positive
✅ **WCAG Compliant**: Respects prefers-reduced-motion (2.3.3), motion sickness safeguards  
✅ **Player Choice**: Accessibility mode is optional, not forced  
✅ **Testable**: E2E tests verify animation disabled and full text visible  
✅ **Low Overhead**: No performance impact in non-accessibility mode  
✅ **Graceful Degradation**: Works even if CSS disabled (full text always rendered)  

### Negative
❌ **Extra CSS**: ~80 lines added to stylesheet  
❌ **State Complexity**: Orchestrator tracks accessibility_mode flag  
❌ **Edge Cases**: Animation might be mid-delivery when mode toggled (mitigated: revealAll() cancels)  

### Mitigations
- CSS is organized and commented
- accessibility_mode is single boolean flag (not complex state)
- toggleAccessibilityMode() calls typewriter.revealAll() to handle mid-delivery edge case

---

**Evidence.** `docs/architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions` (archived — see `docs/archive/adr-retired-2026/`)
## 10. Quality Requirements

`python tests/run_tests.py --mvp1` … `--mvp4`; MVP evidence files under `tests/reports/`.

## 11. Risks & Technical Debt

Some MVP ADRs overlap main-series ADRs—component SAD is normative for technical truth.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Locator-first | Complete SOURCE_LOCATOR before code patches |
