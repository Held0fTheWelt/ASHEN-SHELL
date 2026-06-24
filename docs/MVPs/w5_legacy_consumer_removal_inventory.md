# W5 — Phase 6A Legacy Localization Consumer-Removal Inventory

**Phase:** 6A — Inventory and planning only. **No code is removed in this phase.**

**Phase 6B-0 status:** R1–R5 (the rename items) are **complete**. The function `validate_w5_actor_situation` is now `validate_w5_actor_tracking`, the `failure_class` string is now `"w5_actor_tracking_validation"`, and the four docstring/ADR/migration-doc references now point at the renamed-current files. No runtime behavior, fallback, substrate writer, or W5 flag was touched. The rest of this inventory (S, C, A, T, D, U entries) remains as written: Phase 6B-1 may now proceed to default-on flag rollout.

**Phase 6B-5A status:** [ADR-0065](docs/architecture/components/world-engine/architecture) is authored as the narrator strict default-on ADR and test plan. Phase 6B-5A changes documentation only: no runtime behavior changed, no flags were flipped, no legacy branches were removed, and the next executable step is the Phase 6B-5B strict-mode parity-test rewrite.

**Phase 6B-6A status:** ADR-0066 authored (Proposed). Full dependency audit completed. No code changed. Phase was the audit/planning step for Phase 6B-6B removal.

**Phase 6B-8 status:** [ADR-0068](docs/architecture/components/world-engine/architecture) is **Accepted under operator waiver** (2026-05-28). Runtime removal is executed: `w5_ast_narrator_strict_enabled()`, `NarratorStrictOffDeprecationWarning`, `_strict_off_deprecation_warned`, `_emit_strict_off_deprecation_warning()`, `_transition_facts()`, the strict-off `source_facts["transition_from_previous"]` insertion, and narrator strict/parity admin metadata are removed. `W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off` no longer changes narrator behavior because the narrator runtime no longer reads it. The operator explicitly waived ADR-0067 criteria 1 and 2: repo-local config evidence is accepted as sufficient, and the release-cycle waiting period is waived.

**Phase 6B-8.1 status:** No-legacy audit and stale documentation cleanup **complete** (2026-05-28). Stale references to `transition_from_previous`, `_legacy_compat`, `narrator_strict`, and `legacy_transition_parity` as current behavior are updated with historical markers. Production docstrings, test function names, and inventory table rows updated; ADR historical sections unchanged. See `docs/MVPs/w5_actor_tracking_migration.md §Phase 6B-8.1` for the full audit classification list.

**Phase 6B-6B status:** `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` **retired** (2026-05-23). All runtime references removed: flag resolver function deleted, `_legacy_compat` insertion branch deleted, `w5.narrator_legacy_compat_diagnostics_enabled` metadata key deleted, `demoted_to_legacy_compat` parity label retired. ADR-0068 later removed `w5.legacy_transition_parity` and `removed_by_6b5e_policy` from current narrator admin metadata. Inventory script updated to exclude `.worktrees/`, `.claude/worktrees/`, `.state_tmp/` auxiliary workspaces. ADR-0066 status: **Accepted**. See [ADR-0066](docs/architecture/components/world-engine/architecture).

**Phase 6B-5B status:** Strict-mode parity tests are rewritten as semantic W5-authority contracts rather than legacy field-presence checks. Two new test files prove the strict-off / strict-on contract end-to-end: `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` and `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py`. Both postures continue to work: strict-off keeps `transition_from_previous` first-class with the legacy fallback prompt paragraph and `legacy_compat_visible` admin label; strict-on demotes the same payload to `source_facts._legacy_compat["transition_from_previous"]` with `authority = "w5_projection"`, removes top-level `transition_from_previous`, names `source_facts.w5_projection` as the sole actor-situation authority in the narrator prompt, mentions all five W5 summaries, uses `where_summary.location_changed` as the scene-shift signal, keeps How first-class with the full attribute list, and marks inferred Why as soft / never-spoken-as-fact. Admin diagnostics always read W5 history first and switch only the legacy-parity label by posture. Phase 6B-5B is a test-contract phase: no runtime behavior changed, `W5_AST_NARRATOR_STRICT_ENABLED` remains opt-in / default-off, `transition_from_previous` and `_legacy_compat` are not removed, malformed-W5 and explicit-opt-out safety fallbacks remain testable, and no committed event is mutated. Required gates re-verified: MVP03 LDSS gate, MVP04 observability gate, langfuse docker config, the strict-migration tests from Phase 6B-3B, the narrator-projection wiring tests from Phase 6B-1, the W5 inventory test, and the new Phase 6B-5B parity files all pass with zero failures. The next executable step is the Phase 6B-5C default-on flip.

**Phase 6B-5C status:** `W5_AST_NARRATOR_STRICT_ENABLED` is now **default-on** (opt-out semantics). Explicit disable (`W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off`) remains supported. No `transition_from_previous` or `_legacy_compat` data surface removed. No committed event mutated. All gate tests passed with zero failures at flip time.

**Phase 6B-5D status:** The strict-off narrator prompt fallback paragraph has been **removed**. `source_facts.w5_projection` is now the actor-situation authority in **all** prompt postures. The strict-off (`W5_AST_NARRATOR_STRICT_ENABLED=false`) prompt branch no longer instructs the narrator to use `transition_from_previous` as a fallback; any `transition_from_previous` or `_legacy_compat` data present in source_facts is explicitly labelled as "legacy compatibility information only and is not authoritative narrator guidance." The strict-on prompt is unchanged (sole authority + explicit "Do not consult" prohibition). No data surface was removed: `source_facts["transition_from_previous"]` is still emitted under explicit opt-out (data-level compatibility preserved), `_legacy_compat` breadcrumbs still exist under strict-on, malformed-W5 safety fallbacks are intact, and no committed event is mutated. Affected test files: `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` (two tests renamed/rewritten), `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` (one test rewritten). The next step is Phase 6B-5E: decide whether `_legacy_compat["transition_from_previous"]` is removed or further demoted (separate ADR required before removal).

**Authoritative ADR:** [ADR-0063 — W5 Actor Tracking](docs/architecture/components/world-engine/architecture).

**Migration plan:** [w5_actor_tracking_migration.md](./w5_actor_tracking_migration.md).

**Active packages (the only places W5 lives):**

- `ai_stack/actor_tracking/` — core W5 models, extractor, projections, validation, diagnostics.
- `world-engine/app/story_runtime/manager/actor_tracking/` — runtime manager helpers and the player-shell W5 view fallback layer.

**Forbidden packages (must never appear):**

- `ai_stack/actor_situation/` — not present in working tree; not referenced by any active import.
- `ai_stack/w5_actor_situation/` — not present in working tree; not referenced by any active import.

As of Phase 6A, the residual mentions of `actor_situation` / `w5_actor_situation` in active code were (a) a function name `validate_w5_actor_situation()`, (b) a `failure_class` string, and (c) docstring references to renamed-away doc files. All were inventoried below and have since been resolved by Phase 6B-0 (see the "Phase 6B-0 status" note above). The only remaining mention is one historical sentence in `ai_stack/actor_tracking/__init__.py` that documents the prior package names for readers tracing the migration; it is not a current-state claim.

---

## Inventory method

1. Grep across the entire repository for every legacy surface enumerated by the Phase 6A scope:
   - `current_room`, `current_room_id`, `current_area`, `previous_room_id`
   - `actor_locations`, `participant.current_room_id`, `snapshot.current_room`
   - `visible_room_ids`, `RuntimeVisibilityPolicy.visible_occupants`
   - `complete_actor_locations_for_gathering`, `gathering_scene_id`, `derived_gathering_room_id`
   - `transition_from_previous.location_changed`
   - direct `environment_state.*` localization reads outside substrate/extractor/compatibility layers
   - forbidden package names (`ai_stack/actor_situation`, `ai_stack/w5_actor_situation`)
2. Cross-reference each match against the current architecture:
   - Is the file the substrate writer (kept)?
   - Is it the W5 extractor (kept)?
   - Is it the compatibility fallback (kept until removal)?
   - Or is it a higher-level consumer still bypassing W5?
3. Confirm the absence of forbidden package directories on disk.
4. Confirm there is **no `import` of either forbidden package** anywhere in active code.
5. Classify and group findings by recommended action.

This inventory was assembled without changing runtime behavior, without enabling any W5 flag, and without removing any legacy code or test.

The `'fy'-suites/delagecy/` reports and `audit_*.json` snapshots are also excluded from the consumer-removal scope; they are read-only audit artifacts that mirror legacy strings as data — they do not consume the legacy surfaces at runtime.

---

## Classification taxonomy

| Tag | Meaning |
|-----|---------|
| `substrate_keep` | Low-level committed substrate writer/reader. Stays in Phase 6B/6C. |
| `w5_authority_consumer_should_migrate` | Higher-level consumer still reading legacy localization directly. Must migrate to a W5 projection before its legacy read can be removed. |
| `compatibility_alias_keep_temporarily` | Explicit Phase 5A/5B compatibility fallback or alias. Keep while the corresponding W5 flag stays optional. |
| `remove_in_phase_6b` | Code/comment/log line that can be deleted once Phase 6B is approved. |
| `rename_in_phase_6b` | Code that survives 6B but should be renamed for naming consistency (e.g., `w5_actor_situation` → `w5_actor_tracking`). |
| `test_only_update` | Test fixture or assertion. Migrate to W5-aware assertions before removing the producer; the test itself is not the consumer. |
| `doc_only_update` | Docstring, ADR text, design log. Update or remove text without behavioral impact. |
| `unrelated_keep` | Mention happens to overlap a legacy keyword but is not the legacy surface (e.g., a CHANGELOG entry, an unrelated dataclass). |

---

## Summary by classification

| Classification | Count |
|----------------|-------|
| `substrate_keep` | 8 |
| `w5_authority_consumer_should_migrate` | 11 |
| `compatibility_alias_keep_temporarily` | 9 |
| `remove_in_phase_6b` | 0 (Phase 6B will introduce the first deletion candidates; nothing is approved for deletion in 6A) |
| `rename_in_phase_6b` | 5 |
| `test_only_update` | 13 |
| `doc_only_update` | 12 |
| `unrelated_keep` | 4 |

**Forbidden package imports found:** 0.

**Phase 6B-1 safe to begin:** Yes, conditionally — see *Recommended Phase 6B removal order* below. Conditions (2) and (3) below are now satisfied by Phase 6B-0; only condition (1) remains as an operational decision: (1) Director gathering, NPC planning, narrator composition, validation, and player shell must each have their W5 flag enabled by default before their legacy fallback can be removed; ~~(2)~~ ✅ the `validate_w5_actor_situation` function and `failure_class = "w5_actor_situation_validation"` string have been renamed to their `*_actor_tracking` analogues; ~~(3)~~ ✅ the four docstring/ADR references to renamed-away files have been repaired. Substrate writers (`apply_action_to_environment_state`, backend/world-engine `engine.py` MOVE_ACTOR effects, the Participant dataclass `current_room_id` field) are explicitly out of scope for 6B per the migration plan.

---

## Substrate writers / readers — `substrate_keep`

These are the low-level committed-substrate writers and the W5 extractor's substrate input. They remain in place until a later, separately-scoped ADR consolidates them.

| # | File | Symbol / scope | Legacy field used | Role | W5 replacement exists? | Recommended action | Risk if removed too early | Required tests before removal |
|---|------|----------------|-------------------|------|------------------------|--------------------|---------------------------|-------------------------------|
| S1 | `ai_stack/contracts/environment_state_contracts.py` | `apply_action_to_environment_state` (`L375+`), `normalize_environment_state` (`L260+`), `_visible_room_ids` (`L155`), `project_environment_state_view` (`L515+`) | `current_room_id`, `previous_room_id`, `current_area`, `actor_locations`, `visible_room_ids` | Substrate writer/reader. Single source of truth for the committed environment-state dict. The W5 extractor reads its output. | N/A — this is the substrate that W5 reads from. | **Keep.** Migration plan §"Target architecture" makes `environment_state` the low-level substrate. | Breaks every higher-level consumer including W5 extraction. | All `ai_stack/tests/test_environment_state_contracts.py` plus W5 extractor regression. |
| S2 | `backend/app/runtime/engine.py` `L46-L347` and `world-engine/app/runtime/engine.py` `L46-L358` | `RuntimeEngine`, MOVE_ACTOR effect handlers, build of `RuntimeSnapshot.current_room` | `actor.current_room_id`, `Participant.current_room_id`, `RuntimeSnapshot.current_room` | Substrate writer for participant location and snapshot composer for the legacy participant lane. | N/A — W5 reads downstream of this commit. | **Keep.** Migration plan defers consolidation of the runtime-engine substrate writers. | Breaks every Backend/World-Engine runtime turn end-to-end. | `world-engine/tests/test_runtime_engine.py`, `test_runtime_commands.py`, `test_runtime_visibility.py`. |
| S3 | `backend/app/runtime/models.py:32` and `world-engine/app/runtime/models.py:25` | `Participant.current_room_id: str` | Participant dataclass field | Persisted runtime participant identity. | N/A. | **Keep.** | Breaks persistence + store recovery (json/sqlalchemy/recovery tests). | `test_store_json.py`, `test_store_sqlalchemy.py`, `test_store_recovery.py`. |
| S4 | `backend/app/runtime/manager.py:144,234` and `world-engine/app/runtime/manager.py:192,239,301,535` | `RuntimeManager` initial-room assignment + move resolution | `current_room_id` | Substrate writer at instance creation; engine-side reader. | N/A. | **Keep.** | Breaks instance bootstrap. | `world-engine/tests/test_runtime_manager.py`. |
| S5 | `backend/app/runtime/visibility.py`, `world-engine/app/runtime/visibility.py` | `RuntimeVisibilityPolicy.visible_occupants`, `RuntimeVisibilityPolicy.is_target_visible`, `build_current_room_payload` | `viewer.current_room_id`, `actor.current_room_id`, `visible_occupants` list | Engine-level visibility policy for the legacy runtime substrate. Lives parallel to W5 perception/audibility facts. | Partial — W5 carries `where.visibility_audibility` per-actor, but Phase 5B has not migrated this engine policy. | **Keep.** Document as substrate-tied. | Breaks legacy visibility test suite and snapshot construction. | `world-engine/tests/test_runtime_visibility.py`, `test_ws_runtime_commands_and_isolation.py`. |
| S6 | `ai_stack/actor_tracking/extractor.py:161-167` | `extract_w5_snapshot_from_committed_event` actor-location read | `environment_state_after.actor_locations` | The pure W5 extractor reads the substrate `actor_locations` map to build OBSERVED `where.scene_location` facts. | This IS the W5 producer. | **Keep.** | Breaks every W5 snapshot. | `ai_stack/tests/test_w5_actor_tracking_extractor.py`. |
| S7 | `ai_stack/actor_tracking/validation.py:170-208` | `_allowed_location_ids`, `_block_location` | reads `current_room_id`, `current_room` from frames/blocks | Validation entry point — reads frame substrate to compare against W5 facts. Must accept legacy frame schema until producers also migrate. | Hybrid. | **Keep** as substrate read. Remove the legacy keys from the *allowed set* only after every block producer emits `where.scene_location`. | False rejections / continuity break errors. | `ai_stack/tests/test_w5_actor_tracking_validation.py`. |
| S8 | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` `L319-L376` | `_transition_facts` (`location_changed`, `scene_changed`, `transition_from_previous`) | builds `source_facts.transition_from_previous.location_changed` from `previous_*` ↔ `current_*` substrate | Substrate-derived transition block used by the GoC narrator path as the legacy transition input. Phase 2 keeps it as fallback alongside `w5_projection.where_summary.location_changed`. | Yes — `where_summary.location_changed` mirrors it (see `ai_stack/actor_tracking/projection.py:214-221`). | ~~**Keep** until narrator flag flips to W5-only default.~~ **Removed by ADR-0068** (Phase 6B-8, 2026-05-28). `_transition_facts` and the `source_facts["transition_from_previous"]` insertion are deleted; `where_summary.location_changed` is the sole location-shift signal. | (historical) | `ai_stack/tests/test_god_of_carnage_narrator_path.py`, `world-engine/tests/test_goc_narrator_path_opening.py`, `world-engine/tests/test_story_runtime_w5_narrator_projection.py`. |

---

## Higher-level consumers still reading legacy directly — `w5_authority_consumer_should_migrate`

These consumers should ultimately read a W5 projection (or accept one as an injected substrate) instead of reaching for the legacy substrate. They are **not** removed in Phase 6B; Phase 6B retires their *legacy-only fallback* once a W5 flag is on by default.

| # | File | Symbol | Legacy field used | Role | W5 replacement exists? | Recommended action | Risk if removed too early | Required tests before removal |
|---|------|--------|-------------------|------|------------------------|--------------------|---------------------------|-------------------------------|
| C1 | `ai_stack/langgraph/runtime_executor/director_location_completion.py` | `complete_actor_locations_for_gathering`, `complete_actor_locations_for_gathering_with_optional_w5_projection`, `_w5_director_projection_failure_reason` | reads `actor_locations`, writes `gathering_scene_id` | Director-Pause input completion. Phase 3A wires the optional W5 projection here; legacy completion still runs as baseline. | Yes — Phase 3A `build_w5_projection_for_director` exposes `derived_actor_locations`. | **Keep both code paths.** Phase 6B may drop the *legacy-only* code path *only* after `W5_AST_DIRECTOR_PROJECTION_ENABLED` is the default. | Director-Pause regresses to "missing_actor_locations" for any session predating the W5 default. | `ai_stack/tests/test_phase1_live_wiring.py` (full file), `ai_stack/tests/test_pr_c_director_pause_mode.py`. |
| C2 | `ai_stack/langgraph/runtime_executor/director_w5_location_projection.py` | `_pr_c_director_w5_projection_fragment` | reads `where_summary.derived_actor_locations` from W5 projection; writes `derived_actor_locations`, `derived_actor_locations_source` diagnostics | W5 → Director adapter. Already migrated but still wraps legacy completion. | Yes (this *is* the W5 adapter). | **Keep.** No change in 6B. | None — this is the W5-aware path. | Same as C1. |
| C3 | `ai_stack/langgraph/runtime_executor/executor_action_resolution_start.py:L150-L182` | inline `actor_locations` source resolution + `current_room_id` extraction (`_pr_c_env_state`) | reads `environment_state.actor_locations`, `environment_state.current_room_id` | Live-fix Phase-1 wiring that feeds Director-Pause inputs at action-resolution start. | Partially — same data is in W5 snapshot's `where_summary.facts.scene_location`, but the adapter is in `director_location_completion.py`, not here. | **Migrate** to consume the W5 projection directly when `W5_AST_DIRECTOR_PROJECTION_ENABLED` is on; retain the legacy read as fallback for one phase. | Director-Pause input goes blank for legacy turns mid-flight. | `ai_stack/tests/test_phase1_live_wiring.py`, `tests/smoke/test_thin_path_pr_c_director_pause_live_smoke.py`. |
| C4 | `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py:L11-L96` | `_pr_c_actor_locations_raw`, `_pr_c_actor_locations`, `_pr_c_gathering_scene_id`, `_pr_c_w5_director_projection` | mirror of C3 at commit-side | Same flow at commit-side, including the optional `w5_director_projection` diagnostic payload. | Same as C3. | **Migrate** in lockstep with C3. | Same as C3. | Same as C3. |
| C5 | `ai_stack/story_runtime/player_action_resolution.py:142,350,366,390-455` | `_current_area_from_affordance_model`, `_local_context_player_change_safe`, `_resolve_target_id` | reads `current_room_id`, `current_location_id`, `current_area` | Player-action interpretation reads the legacy localization keys from the affordance model / surface. | Not directly. W5 player-shell projection exists but is consumer-side, not producer-side. | **Migrate** to read `w5_player_view.where_summary.scene_location` when present; keep legacy fallback. | Player movement target resolution silently fails for affordances that lack the legacy keys. | `ai_stack/tests/test_player_action_resolution.py`, `ai_stack/tests/test_free_player_action_resolution_contract.py`. |
| C6 | `ai_stack/story_runtime/semantic_planner/semantic_scene_planner.py:679-680` | `_anchor_room_id_from_env` | `env.get("current_room_id") or env.get("current_area")` | Semantic planner fallback chain. | Indirect via W5 `where_summary.scene_location`. | **Migrate** to consume W5 if a planner-scoped projection is added; otherwise keep as benign fallback. | Semantic planner returns `None` for anchor room when both legacy keys absent. | `ai_stack/tests/test_semantic_scene_planner.py`. |
| C7 | `ai_stack/contracts/narrator_consequence_contracts.py:26-280` | `narrator_consequence` payload builder | reads/writes `current_area`, `from_area`, `to_area` on the `current_player_local_context` substrate | Narrator-consequence contract still composes movement metadata from legacy localization fields. | Partial — W5 `where_summary.location_changed` exists; transition `kind` does not yet have a W5 equivalent. | **Migrate** to read W5 first, fall back to legacy. Coordinate with narrator path (S8). | Narrator loses movement framing. | `ai_stack/tests/test_narrator_consequence_contract.py`. |
| C8 | `ai_stack/story_runtime/narrative/sensory_context_engine.py:154,167` | `_current_area_from_affordance` chain | `to_area`, `current_area`, `from_area` | Sensory context engine fallback for stage-level area. | Partial. | **Migrate** to read W5 `where_summary.scene_location`; keep legacy fallback. | Sensory engine produces blank stage on partial substrate. | `ai_stack/tests/test_information_disclosure_contracts.py`, ambient sensory tests. |
| C9 | `ai_stack/language_io/language_adapter.py:338-346`, `ai_stack/module_runtime_policy.py:247` | adapter payload field `current_area` | reads `interaction_surface.current_area` and builds outgoing payload | Language adapter passes the legacy area along; user-facing surface for input interpretation. | Not directly. | **Migrate** in a future phase together with adapter contract refresh (out of scope for Phase 6B). | Language adapter loses scene-anchor in payload. | `ai_stack/tests/test_langgraph_runtime.py`. |
| C10 | `world-engine/app/story_runtime/runtime_world.py:239-401` | `build_runtime_world_from_environment` | builds `runtime_world.current_room_id` from `environment_state`, fills props/actors per-room | Mid-level projector that pre-dates W5. Higher-level consumers read `runtime_world.current_room_id`. | Partially — W5 player-shell view supersedes this for player-facing consumers, but `runtime_world` is still the projection seed. | **Migrate** higher-level callers to W5 (already largely done in Phase 5A/5B); keep `runtime_world` as the substrate projection seed. | Player shell, opening rendering, scene presenter all read from this. | `world-engine/tests/test_story_runtime_runtime_world.py`. |
| C11 | `world-engine/app/story_runtime/manager/dramatic_context_authority.py:210` | reads `session.environment_state.current_room_id` for authority context | direct substrate read | Authority/context composer for dramatic generation. | Not yet — Director-style W5 projection exposes scene_location but not the wider authority context. | **Migrate** to W5 director projection input. | Authority context loses anchor room. | `world-engine/tests/test_story_runtime_w5_narrator_projection.py`, dramatic-authority-specific tests. |

---

## Compatibility aliases — `compatibility_alias_keep_temporarily`

These are the explicit Phase 5A/5B fallbacks that the migration plan keeps until W5 is the default for the corresponding consumer.

| # | File | Symbol | Legacy field used | Role | W5 replacement exists? | Recommended action | Risk if removed too early | Required tests before removal |
|---|------|--------|-------------------|------|------------------------|--------------------|---------------------------|-------------------------------|
| A1 | `world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py:50-59` | `_fallback_current_room_id` | reads `runtime_world.current_room_id`, `environment_state.current_room_id`, `environment_state.current_area` | Player-view fallback when `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` is off or W5 snapshot missing. Documented Phase 5B compatibility. | Yes — `build_w5_projection_for_player_shell`. | **Keep** until Phase 5C makes W5 the player-shell default. | Player UI shows blank room when flag disabled or W5 missing on the very next deploy. | `backend/tests/test_w5_player_shell_payload.py`, `world-engine/tests/test_story_runtime_w5_player_view.py`. |
| A2 | `backend/app/api/v1/game_routes.py:486-549` | `_attach_w5_player_view_to_view` (effective) | reads `runtime_world.current_room_id`, then prefers `w5_player_view.where_summary.scene_location.value` | Backend route that prefers W5 over legacy when present. | Yes. | **Keep** the fallback. Remove the legacy fallback only when frontend supports W5-only payloads. | Frontend loses `current_room_id`. | `backend/tests/test_play_service_client.py`, `test_player_session_live_opening_contract.py`, `test_game_service_play_http.py`. |
| A3 | `world-engine/app/story_runtime/manager/session/session_lifecycle.py:21` and `manager/runtime_config.py:221` | snapshot composers | `current_room_id` field on emitted snapshot | Snapshot serializers keep `current_room_id` for legacy WS subscribers. | Yes. | **Keep** until WebSocket subscribers consume W5. | WS clients lose `viewer_room_id`. | `world-engine/tests/test_ws_state_transitions.py`, `test_ws_runtime_commands_and_isolation.py`. |
| A4 | `world-engine/app/story_runtime_shell_readout.py:147-180` | `_environment_state_readout`, `_environment_state_brief_readout` | `current_room_id`, `current_area`, `previous_room_id`, `visible_room_ids` | Operator/debug shell readout. | Indirect — admin W5 view exists, but shell readout is a separate diagnostic channel. | **Keep** but consider routing through W5 admin diagnostics in Phase 6C. | Operator readout loses room context. | Manual shell-readout regression. |
| A5 | `world-engine/diagnostics/story_runtime/create_session_runtime_template.py:87-148,344` | template builder | `current_room_id`, `current_area` from world/state | Diagnostic creation template. | None — diagnostic substrate only. | **Keep.** | Diagnostic template build fails. | `world-engine/tests/test_story_runtime_runtime_world.py`. |
| A6 | `world-engine/app/story_runtime/manager/diagnostics_api.py:70-94` | `_w5_runtime_metadata_for_session` | reads `transition_from_previous.location_changed` from any narrator block when computing W5 admin metadata | Phase 4B admin diagnostic bridge. | Yes (W5 itself), but the bridge keeps the legacy parity check. | **Keep**. The bridge intentionally inspects both. | Admin diagnostics loses parity check. | `world-engine/tests/test_story_runtime_w5_admin_diagnostics.py`. |
| A7 | `world-engine/app/story_runtime/manager/narrator_output_prompts.py:48-56` | narrator system-prompt text | mentions `transition_from_previous.location_changed`, `transition_from_previous.directed_transition.kind` | Phase 2 prompt explicitly tells the narrator W5 is primary and `transition_from_previous` is fallback. This is the contractual fallback signal. | Yes. | **Keep** prompt as-is until W5 narrator flag is permanently on; then prune the fallback paragraph. | Narrator loses fallback instruction. | `world-engine/tests/test_story_runtime_w5_narrator_projection.py`. |
| A8 | `world-engine/app/story_runtime/manager/opening_fallback_observability.py:233` | docstring + diagnostic | mentions `transition_from_previous` as fallback | Opening-path observability comment. | Yes. | **Keep**; prune comment in 6B. | None (comment-only). | `world-engine/tests/test_goc_narrator_path_opening.py`. |
| A9 | `ai_stack/actor_tracking/projection.py:588-826,628-660` | `build_w5_projection_for_director` + player-shell projection internals | populates `where_summary.derived_actor_locations`, `where_summary.location_changed` | The W5 projection itself exposes a compatibility map keyed by actor ID so Director can keep its existing pause semantics. | This IS the W5 producer. | **Keep.** Plan-of-record per Phase 3A. | Director-Pause loses its bridge. | `ai_stack/tests/test_w5_actor_tracking_projection.py`. |

---

## Rename targets — `rename_in_phase_6b`

Naming-only items. They survive 6B but must be renamed for consistency with the new `actor_tracking` package name.

| # | Status | File | Symbol | Old name | New name | Note |
|---|--------|------|--------|----------|----------|------|
| R1 | ✅ done (Phase 6B-0) | `ai_stack/actor_tracking/validation.py` (definition) and `__init__.py` (re-export) | function `validate_w5_actor_situation` | `validate_w5_actor_situation` | `validate_w5_actor_tracking` | Function and re-export renamed. Production callsite in `ai_stack/story_runtime/turn/god_of_carnage_turn_seams_validation.py` and all 12 test callsites in `ai_stack/tests/test_w5_actor_tracking_validation.py` updated atomically. No backward alias retained. |
| R2 | ✅ done (Phase 6B-0) | `ai_stack/story_runtime/turn/god_of_carnage_turn_seams_validation.py` | string literal `failure_class = "w5_actor_situation_validation"` | `"w5_actor_situation_validation"` | `"w5_actor_tracking_validation"` | Diagnostic string surfaces through Langfuse metadata. No production consumer/filter asserts the old value. |
| R3 | ✅ done (Phase 6B-0) | `ai_stack/actor_tracking/models.py` | docstring | `docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view` | `docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view` | Pure doc fix. |
| R4 | ✅ done (Phase 6B-0) | `ai_stack/actor_tracking/__init__.py` and `ai_stack/actor_tracking/extractor.py` | docstring | `docs/MVPs/w5_actor_situation_migration.md` | `docs/MVPs/w5_actor_tracking_migration.md` | Pure doc fix. `__init__.py` retains one historical sentence noting prior package names. |
| R5 | ✅ done (Phase 6B-0) | `ai_stack/actor_tracking/projection.py` | docstring | `docs/MVPs/w5_actor_situation_migration.md` | `docs/MVPs/w5_actor_tracking_migration.md` | Same as R4. |

---

## Tests — `test_only_update`

Tests that assert legacy localization fields directly. They are valid as-is; they need to evolve in lockstep with their producer. **None of these tests are weakened in Phase 6A.**

| # | File | Test / assertion | Legacy field used | Role | Recommended action |
|---|------|-------------------|-------------------|------|--------------------|
| T1 | `ai_stack/tests/test_environment_state_contracts.py:56,87-88,127` | substrate roundtrip on `current_room_id`/`previous_room_id`/`actor_locations`/`visible_room_ids` | full set | Substrate contract test. | **Keep.** Substrate stays. |
| T2 | `ai_stack/tests/test_w5_actor_tracking_extractor.py:44-46` | builds `environment_state` with `current_room_id`, `previous_room_id`, `actor_locations` as W5 extractor input | full set | Extractor regression. | **Keep.** |
| T3 | `ai_stack/tests/test_phase1_live_wiring.py` (1,000+ lines using `actor_locations`/`current_room_id`/`gathering_scene_id`) | full Director-Pause + Phase-1 wiring | full set | Director-Pause contract. | **Keep** as semantic tests; do not field-presence-collapse. |
| T4 | `ai_stack/tests/test_pr_c_director_pause_mode.py` (24 calls) | `compute_gathering_state(actor_locations=…)` | `actor_locations` | Director-Pause semantics. | **Keep.** |
| T5 | `ai_stack/tests/test_w5_actor_tracking_projection.py` (5 location_changed tests, derived_actor_locations parity) | `where_summary.location_changed`, `derived_actor_locations` | full set | W5 projection regression. | **Keep.** Includes legacy-parity test that is critical for migration safety. |
| T6 | `ai_stack/tests/test_w5_actor_tracking_validation.py` (12 calls to `validate_w5_actor_situation`) | validation entry point | rename target R1 | Validation regression. | **Update callsites** alongside R1 rename. Do not weaken assertions. |
| T7 | `ai_stack/tests/test_god_of_carnage_narrator_path.py:30-44` | `source_facts.transition_from_previous.location_changed` and `kind=="opening_start"` | transition block | Narrator-path semantics. | **Keep.** Mirrors A7 fallback. |
| T8 | `backend/tests/test_w5_player_shell_payload.py:30-136` | fallback-vs-W5 mismatch parity, includes string-source check for `app.js` | `current_room_id`, `snapshot.current_room` | Player shell payload regression. | **Keep**, but loosen the JS source-string check only when frontend is upgraded. |
| T9 | `backend/tests/runtime/test_runtime_manager_engine.py`, `test_runtime_core.py` | `Participant.current_room_id` constructor + comparisons | `current_room_id` (dataclass field) | Substrate engine tests. | **Keep.** |
| T10 | `world-engine/tests/test_runtime_visibility.py` (8 tests), `test_runtime_commands.py` (10 tests), `test_runtime_engine.py` (4 tests), `test_runtime_manager.py` (2 tests) | participant location + room moves | `current_room_id` | Substrate engine + visibility regression. | **Keep.** |
| T11 | `world-engine/tests/test_ws_state_transitions.py`, `test_ws_runtime_commands_and_isolation.py` (6 hits) | `viewer_room_id`, `current_room`, `visible_occupants` | snapshot fields | WebSocket transport regression. | **Keep.** |
| T12 | `world-engine/tests/test_story_runtime_w5_player_view.py:150-183` | flag-off fallback parity | `current_room_id` | Phase 5B fallback test. | **Keep.** |
| T13 | `world-engine/tests/test_story_runtime_w5_narrator_projection.py` (legacy parity tests at `L137-L290`) | `transition_from_previous.location_changed` ↔ `where_summary.location_changed` parity | both | Phase 2 parity regression. | **Keep.** Critical migration-safety net. |

---

## Documentation — `doc_only_update`

| # | File | Section | Action |
|---|------|---------|--------|
| D1 | `docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view:84` | "Target architecture (later phases)" — already lists legacy fields. | **Keep** as historical reference. |
| D2 | `docs/architecture/components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority:52,72-74,169,176` | Director-Pause input contract — references `actor_locations`. | **Keep** until Phase 6B re-publishes the Director input as the W5 projection map. |
| D3 | `docs/architecture/components/ai-stack/architecture.md#d7-player-guidance-and-souffleuse-lanes:131` | Resolver/director input. | **Keep**, footnote-link to W5 in Phase 6B. |
| D4 | `docs/MVPs/w5_actor_tracking_migration.md` | Add Phase 6A entry (this Phase). | **Update** with Phase 6A status (handled below). |
| D5 | `docs/MVPs/MVP_World_Of_Shadows_Canonical_Implementation_Bundle/runtime_state_and_session_contracts.md:27-30,703-706` | Lists legacy substrate fields as canonical. | **Annotate** in 6B that these are substrate-only; higher-level consumers must read W5. |
| D6 | `docs/implementation_logs/w5_actor_tracking_piv.md:8,13,18` | PIV log mentions legacy `actor_locations`. | **Keep** as history. |
| D7 | `docs/implementation_logs/pr_c_director_pause_mode_piv.md:132` | mentions legacy fallback line and a path that has since been refactored (`langgraph_runtime_executor.py:6340-6343` — that file no longer exists at those lines). | **Refresh path** in 6B to point at the new split files in `ai_stack/langgraph/runtime_executor/`. |
| D8 | `docs/MVPs/npc_interactivity_piv_log.md:33` | references W5 `actor_locations` enrichment. | **Keep** as history; mark phase complete in 6B. |
| D9 | `NPC_INTERACTION_AND_INTERACTIVITY_PLAN.md:232,257,426,499` | Plan doc references `runtime_world.actor_locations`. | **Keep** as plan doc. |
| D10 | `ai_stack/actor_tracking/models.py:3`, `__init__.py:5`, `extractor.py:5`, `projection.py:8` | docstrings reference renamed-away files. | **Update in Phase 6B** (these are rename targets R3/R4/R5). |
| D11 | `ai_stack/langgraph/runtime_executor/director_location_completion.py:27-58,101-108,114-147` and `director_w5_location_projection.py:11-70`, `executor_action_resolution_start.py:150-180`, `executor_action_resolution_commit.py:11-78` | Docstring blocks of refactored runtime executor modules. They describe legacy + W5 behavior. | **Keep** until C1–C4 migrate. |
| D12 | `CHANGELOG.md:2606,2782` | historical entries mentioning `current_room` / `visible_occupants`. | **Keep** as history. |

---

## Unrelated / overlapping mentions — `unrelated_keep`

| # | File | Note |
|---|------|------|
| U1 | `'fy'-suites/delagecy/**` reports, `'fy'-suites/docify/**` baselines | These are audit/legacy-tracker artifacts mirroring the strings as data. They do not consume the surfaces at runtime. Out of Phase 6B scope. |
| U2 | `audit_turn1.json`, `audit_turn2.json`, …, `audit_state_*.json` | Frozen audit snapshots. Out of scope. |
| U3 | `writers-room/app/models/runtime_load_orders.md:283` | Documentation example uses `{{current_room_id}}` as a Jinja-style placeholder for an authoring template — not a runtime consumer. |
| U4 | `engine_run_last.txt`, `failing-tests.txt`, `tests/reports/_stage*.log` | Run logs. Out of scope. |

---

## Highest-risk legacy consumers

Ranked by blast radius if their legacy read is removed before W5 takes over.

1. **`ai_stack/contracts/environment_state_contracts.py`** (`substrate_keep`, S1) — every higher-level consumer and the W5 extractor depend on this.
2. **`backend/app/runtime/engine.py` + `world-engine/app/runtime/engine.py`** (S2) — every committed turn writes through these.
3. **`ai_stack/langgraph/runtime_executor/director_location_completion.py` + `executor_action_resolution_*.py`** (C1, C3, C4) — Director-Pause is composed here per turn; their legacy fallback is the only path when `W5_AST_DIRECTOR_PROJECTION_ENABLED=0`.
4. **`world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py`** (A1) — the player-shell fallback. Removing prematurely breaks every UI session in deploys without W5 default-on.
5. **`world-engine/app/story_runtime/runtime_world.py`** (C10) — mid-level projector that seeds the legacy `runtime_world.current_room_id`. Many downstream consumers still read it.
6. **`ai_stack/contracts/narrator_consequence_contracts.py`** (C7) — narrator movement framing depends on legacy `current_area`/`from_area`/`to_area`.
7. **`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`** (S8) — produces the `transition_from_previous` block consumed by narrator prompts and W5 parity tests.

---

## Recommended Phase 6B removal order

Phase 6B is the **first** phase that may remove code. It must proceed in this order; each step is independently testable.

1. **Rename phase (low-risk, doc + naming only).** Apply R1–R5: rename `validate_w5_actor_situation` → `validate_w5_actor_tracking`, the `failure_class` string, and the four docstring/ADR references. Update the 12 test callsites in `test_w5_actor_tracking_validation.py` and the two callsites in `god_of_carnage_turn_seams_validation.py`. **Test:** `python tests/run_tests.py --suite mvp1` (or equivalent) plus targeted ai_stack tests.

2. **Default-on Director projection.** Make `W5_AST_DIRECTOR_PROJECTION_ENABLED=1` the default. Keep the legacy completion as fallback. Run all gating gates (MVP1–MVP4). **Test:** `pytest ai_stack/tests/test_phase1_live_wiring.py ai_stack/tests/test_pr_c_director_pause_mode.py` plus smoke `tests/smoke/test_thin_path_pr_c_director_pause_live_smoke.py`.

3. **Default-on Narrator projection.** Make `W5_AST_NARRATOR_PROJECTION_ENABLED=1` the default. **Test:** `pytest world-engine/tests/test_story_runtime_w5_narrator_projection.py world-engine/tests/test_goc_narrator_path_opening.py ai_stack/tests/test_god_of_carnage_narrator_path.py`.

4. **Default-on NPC projection.** Make `W5_AST_NPC_PROJECTION_ENABLED=1` the default. **Test:** scoped W5 + NPC planner suites.

5. **Default-on Validation.** Make `W5_AST_VALIDATION_ENABLED=1` the default. **Test:** `pytest ai_stack/tests/test_w5_actor_tracking_validation.py`.

6. **Default-on Player Shell.** Make `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED=1` the default. **Test:** `pytest backend/tests/test_w5_player_shell_payload.py world-engine/tests/test_story_runtime_w5_player_view.py`.

7. **Migrate higher-level consumers** (C5–C11): make each of them prefer the W5 projection unconditionally, with the legacy substrate read only as last-chance fallback.

8. **Remove single-purpose legacy-only fallbacks** in the rename + flag-on consumers (C1–C4 legacy-only path, A7/A8 prompt paragraphs that mention `transition_from_previous` as fallback).

9. **Update docs** (D7, D10) to remove the renamed-away references and stale path pointers.

Phase 6B **does not** touch S1–S8 (substrate) or A1–A9 in a way that breaks the compatibility contract. Substrate consolidation is a separate, later ADR.

---

## Conditions on Phase 6B start

Phase 6B may begin once:

- [x] This inventory has been written and reviewed.
- [x] Forbidden packages (`ai_stack/actor_situation`, `ai_stack/w5_actor_situation`) are confirmed absent. ✅
- [x] No active code imports either forbidden package. ✅
- [x] Active W5 packages (`ai_stack/actor_tracking`, `world-engine/app/story_runtime/manager/actor_tracking`) are the only W5 surfaces. ✅
- [x] The five W5 flags (Director, Narrator, NPC, Validation, Player Shell) have been flipped to default-on in a single coordinated commit (Phase 6B-1). The legacy fallbacks remain in place; explicit env opt-out (`0/false/no/off`) restores pre-6B-1 behavior.
- [x] The rename items (R1–R5) are landed as Phase 6B-0. The rest of 6B (consumer migration) can now use the new names.

---

## Phase 6B-1 — default-on consumer flags (complete)

Phase 6B-1 flips the five W5 consumer flags to default-on as a single coordinated change. The change is intentionally narrow: only the *default value* of each resolver is flipped, and every legacy fallback branch is preserved.

**Files changed (defaults flipped):**

| Flag | Resolver location | Behavior under default-on |
|------|-------------------|---------------------------|
| `W5_AST_DIRECTOR_PROJECTION_ENABLED` | `ai_stack/langgraph/runtime_executor/director_location_completion.py` (SOURCE_LINES `w5_ast_director_projection_enabled`) | Director/Gathering reads typed W5 projection as actor-location substrate; legacy `complete_actor_locations_for_gathering` remains as fallback. ADR-0061 pause semantics unchanged. |
| `W5_AST_NARRATOR_PROJECTION_ENABLED` | `world-engine/app/story_runtime/manager/opening_fallback_observability.py::_w5_ast_narrator_projection_enabled` | Narrator `source_facts` gets typed `w5_projection`; legacy `transition_from_previous` block remains as fallback. |
| `W5_AST_NPC_PROJECTION_ENABLED` | `ai_stack/langgraph/runtime_executor/reaction_order_governance.py` (SOURCE_LINES `w5_ast_npc_projection_enabled`) | NPC planning gets actor-specific typed W5 projection; legacy NPC context remains as fallback. |
| `W5_AST_VALIDATION_ENABLED` | `ai_stack/actor_tracking/validation.py::w5_ast_validation_enabled` | W5 validation runs after Actor Lane has accepted; Actor Lane remains authoritative; legacy seam stays canonical. |
| `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` | `world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py::_w5_ast_frontend_player_view_enabled` | Player-shell state exposes typed `w5_player_view` and `feature_flags`; legacy `current_room` / `current_room_id` remains as fallback. |

Reporter helper `ai_stack/actor_tracking/diagnostics.py::_flag_enabled` was updated in lockstep so `w5_projection_flag_states()` and `build_w5_runtime_metadata()` accurately reflect runtime gate state.

**Explicit opt-out preserved.** Every resolver still honors `0/false/no/off` (case-insensitive) as an explicit disable. This is regression-pinned in `ai_stack/tests/test_w5_actor_tracking_phase_6b1_default_on_flags.py`.

**No legacy code removed yet.** Phase 6B-1 deliberately keeps every legacy fallback branch — narrator transition block, Director baseline completion, NPC legacy context, validation seam fallback, `current_room` / `current_room_id` — so opting any single flag out reverts the corresponding consumer to its exact pre-6B-1 path.

**No committed-output mutation.** Default-on does not change committed events. The only new fields visible under default-on are the W5 diagnostics/metadata that were already produced under explicit opt-in (e.g., `w5_director_projection_used`, `w5_player_view_diagnostics`, `feature_flags.W5_AST_FRONTEND_PLAYER_VIEW_ENABLED`, `w5_runtime_metadata.w5_projection_flags_used`).

**Next phase — Phase 6B-2 (planned).** Inspect which fallback branches are now dead under default config. Candidates to investigate (informational, not removed in 6B-1):

- C1 / C4 legacy-only Director completion paths under `complete_actor_locations_for_gathering_with_optional_w5_projection` when the flag is enabled.
- Narrator-only `transition_from_previous` enrichment branches that are never selected when the W5 projection succeeds.
- NPC legacy context fields that are still attached even when W5 projection succeeded.
- Player-shell legacy `current_room` extraction when `w5_player_view` has a valid location.
- Reporter `w5_validation_fallback_reason` emissions that only fire when an operator explicitly opts out.

Substrate writers (S1–S8) and the `Participant.current_room_id` dataclass field remain out of scope for 6B.

---

## Phase 6B-2 — Fallback / dead-branch inventory under default-on W5 (complete)

**Goal:** With all five W5 consumer flags default-on (Phase 6B-1), produce a precise inventory of every remaining legacy fallback branch and classify each one so Phase 6B-3 can remove or migrate only the branches that are demonstrably safe to touch. **No legacy code is removed in Phase 6B-2.**

### Phase 6B-2 classification taxonomy

| Tag | Meaning |
|-----|---------|
| `keep_explicit_opt_out_fallback` | Branch is the path taken when an operator explicitly sets `W5_AST_*=0/false/no/off`. Must remain. |
| `keep_malformed_w5_safety_fallback` | Branch fires when the W5 snapshot is missing, malformed, or cannot project the consumer-specific information. Must remain — this is the safety net the migration plan promises. |
| `remove_dead_default_path_in_6b3` | Default-on never executes the branch; explicit opt-out and malformed-W5 safety are covered by *different* branches; deletion is safe and a small targeted test can pin it. |
| `migrate_to_w5_first_before_removal` | Legacy branch still produces a *parallel* value that is wired into a downstream consumer (prompt text, planner input, frontend payload). The branch cannot be removed until the downstream consumer is migrated to a W5-first contract. Marked for sequenced removal in a later 6B-3.x step. |
| `substrate_keep` | Substrate writer / reader / extractor input. Out of scope for 6B; deferred to a later substrate-consolidation ADR. |
| `test_only_update` | Test asserts a legacy-only field. The producer of the field stays, so the assertion stays; tracked for evolution in lockstep with its producer. |
| `doc_only_update` | Docstring, prompt paragraph, comment, or design-log entry that references the legacy fallback. Update or prune; no runtime impact. |
| `unknown_needs_runtime_trace` | Coverage of the branch under default-on cannot be proven from static reading and requires a live trace before classification. |

### Phase 6B-2 inventory method

1. Read every fallback site enumerated by Phase 6B-1's Phase-6B-2 backlog plus the wider 6A consumer set (C1–C11, A1–A9, S8).
2. For each site, decide which of four conditions actually fires the branch under the live Phase-6B-1 default-on configuration:
   - **D** — default-on happy path (W5 snapshot present and well-formed for that consumer);
   - **O** — explicit opt-out (`0/false/no/off`);
   - **M** — malformed/missing W5 snapshot (default-on but extraction failed or projection raised);
   - **L** — legacy/old-payload compatibility (sessions persisted before Phase 1 wire-in, or external clients that still expect the legacy field).
3. Cross-check static reading against the existing Phase 6B-1 regression suites (`test_w5_actor_tracking_phase_6b1_default_on_flags.py`, `test_story_runtime_w5_narrator_projection.py`, `test_story_runtime_w5_player_view.py`, `test_w5_actor_tracking_validation.py`, `test_npc_agency_planner.py`, `test_w5_actor_tracking_projection.py`) to confirm the conditions are pinned by tests.
4. Tag each branch with the 6B-2 taxonomy. A branch is only ever `remove_dead_default_path_in_6b3` when D ≠ taken AND O is covered by a *different* branch AND M is covered by a *different* branch AND L is either not applicable or covered separately.
5. Order the safe removals.

### Phase 6B-2 fallback branch table (default-on W5)

Conditions: D = default-on happy path; O = explicit opt-out; M = missing/malformed W5; L = legacy client / old session. ✓ = branch fires for that condition. ✗ = branch does not fire.

| # | File:Symbol | Branch | D | O | M | L | Classification | Required test before removal |
|---|-------------|--------|---|---|---|---|----------------|------------------------------|
| F1 | `ai_stack/langgraph/runtime_executor/director_w5_location_projection.py::complete_actor_locations_for_gathering_with_optional_w5_projection` — *eager* `baseline_completion = complete_actor_locations_for_gathering(...)` before the W5 attempt | Always-on baseline pre-compute | ✓ (wasted but its *output* is the safety net only when W5 fails) | ✓ (becomes the return value) | ✓ (becomes the return value) | n/a | `migrate_to_w5_first_before_removal` — the *function* is load-bearing for O+M; only the *eager* placement is wasted under D. Re-arrange to lazy (compute inside the `except` branch and inside the disabled-flag branch) is a 6B-3 optimization, not a 6B legacy removal. Output stays identical. | `test_phase1_live_wiring.py` happy-path assertion that `derived_actor_locations_source=="w5_projection"`; explicit-opt-out test in `test_w5_actor_tracking_phase_6b1_default_on_flags.py`; malformed-snapshot test that returns baseline. |
| F2 | same file — `if not enabled: return {"location_completion": baseline_completion, ...}` | Explicit-opt-out short-circuit | ✗ | ✓ | n/a | n/a | `keep_explicit_opt_out_fallback` | (already pinned by Phase 6B-1 default-on flag test). |
| F3 | same file — `except Exception as exc: diagnostics["w5_director_projection_failed"]=...; return baseline_completion` | Malformed-W5 safety return | ✗ | ✗ | ✓ | n/a | `keep_malformed_w5_safety_fallback` | (already pinned by `test_w5_actor_tracking_projection.py` Director failure cases). |
| F4 | second `complete_actor_locations_for_gathering(...)` *inside* the W5-success branch (lines 56–63) | Substrate re-use of fallback-actor-id + target-location + gathering_scene_id logic with W5-derived actor_locations as input | ✓ | ✗ | ✗ | n/a | `substrate_keep` — not a fallback; it is the consolidation of W5 + actor-lane completion. ADR-0061 pause semantics depend on it. | n/a. |
| F5 | `ai_stack/langgraph/runtime_executor/director_location_completion.py::complete_actor_locations_for_gathering` (legacy completion function itself, NPC fallback voting, gathering_scene_id derivation) | Legacy completion algorithm | ✓ (called from F1 and F4) | ✓ | ✓ | n/a | `substrate_keep` — single source of truth for actor-lane NPC fallback + gathering_scene_id derivation. F1/F4 both invoke it. Cannot be removed in 6B. | n/a. |
| F6 | `world-engine/app/story_runtime/manager/actor_tracking/w5_projection.py::_maybe_enrich_blocks_with_w5_narrator_projection` — `if not self._w5_ast_narrator_projection_enabled(): return source_blocks` | Opt-out short-circuit (no `w5_projection` key added) | ✗ | ✓ | n/a | n/a | `keep_explicit_opt_out_fallback` | (already pinned by `test_story_runtime_w5_narrator_projection.py` opt-out test). |
| F7 | same file — `except Exception as exc: session.diagnostics.append(...w5_narrator_projection_failed...); return source_blocks` | Malformed-W5 safety return | ✗ | ✗ | ✓ | n/a | `keep_malformed_w5_safety_fallback` | New Phase 6B-2 test: default-on happy path emits no `w5_narrator_projection_failed` diagnostic. |
| F8 | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py::_block` line 376 — `source_facts["transition_from_previous"] = _transition_facts(...)` | Always-write legacy transition block | ✓ (written alongside `w5_projection`) | ✓ | ✓ | ✓ | *(Phase 6B-2 classification, historical)* `migrate_to_w5_first_before_removal`. **Removed by ADR-0068** (Phase 6B-8, 2026-05-28): `_transition_facts` deleted; `source_facts["transition_from_previous"]` no longer emitted. | `test_god_of_carnage_narrator_path.py` and `test_goc_narrator_path_opening.py` now assert absence. |
| F9 | `ai_stack/langgraph/runtime_executor/reaction_order_governance.py::_build_w5_npc_projection_inputs` — `if not w5_ast_npc_projection_enabled(): return {}, []` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `keep_explicit_opt_out_fallback` | (already pinned by Phase 6B-1 flag test). |
| F10 | same file — `except Exception as exc: diagnostic["w5_npc_projection_failed"]=...` per-actor | Per-actor malformed-W5 safety | ✗ | ✗ | ✓ | n/a | `keep_malformed_w5_safety_fallback` | Existing `test_npc_agency_planner.py` failure-case coverage. |
| F11 | `ai_stack/langgraph/runtime_executor/npc_agency_projection.py` — `effective_npc_context_bundle` resolved by `resolve_w5_first_npc_context(...)` then passed into `build_npc_agency_simulation(...)` and the fallback `build_npc_agency_plan(...)` | Phase 6B-3C: W5-first selector. Under D the bundle is demoted to `_legacy_compat` and `effective_npc_context_bundle=None` is forwarded (the `npc_context_bundle` evidence row is absent). Under O / M / L the legacy bundle is forwarded verbatim. | ✗ (D forwards `None`) | ✓ | ✓ | ✓ | `keep_explicit_opt_out_fallback` / `keep_malformed_w5_safety_fallback` / `old_payload_legacy_fallback` — the bundle remains the planner substrate on the three non-`w5_projection` paths. Phase 6B-3C migrated the attachment site without deleting any branch. | ✅ Phase 6B-3C complete. Pinned by `ai_stack/tests/test_w5_actor_tracking_phase_6b3c_npc_planner_migration.py` plus the existing `test_npc_agency_planner.py`, `test_npc_agency_contracts.py`, `test_npc_agency_long_horizon_claim_readiness.py`, and `test_wave3_multi_actor_vitality.py` regressions. |
| F12 | `ai_stack/story_runtime/turn/god_of_carnage_turn_seams_validation.py::_apply_w5_validation_to_outcome` — `if not w5_ast_validation_enabled(): return outcome` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `keep_explicit_opt_out_fallback` | (already pinned by Phase 6B-1 validation flag test). |
| F13 | same file — `except Exception as exc: diagnostic = w5_validation_fallback(text)` | Malformed-W5 safety with `w5_validation_fallback_reason` | ✗ | ✗ | ✓ | n/a | `keep_malformed_w5_safety_fallback` | New Phase 6B-2 test: default-on happy path never sets `w5_validation_fallback_reason`. |
| F14 | `world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py::_maybe_build_w5_player_view_for_session` — `if not _w5_ast_frontend_player_view_enabled(): return None, None` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `keep_explicit_opt_out_fallback` | (already pinned by Phase 6B-1 player-view flag test). |
| F15 | same file — `except Exception as exc: return None, _player_view_diagnostics(used=False, failed=reason, ...)` | Malformed-W5 safety with `current_room_source="fallback"` | ✗ | ✗ | ✓ | n/a | `keep_malformed_w5_safety_fallback` | New Phase 6B-2 test: default-on happy path emits `current_room_source=="w5_player_view"` (not `"fallback"`). |
| F16 | same file — `_fallback_current_room_id(session)` reads `runtime_world.current_room_id` → `environment_state.current_room_id` → `environment_state.current_area` | Substrate fallback location resolver | ✓ (always computed for the `current_room_fallback_value` diagnostic and mismatch check) | ✓ | ✓ | ✓ | `substrate_keep` — reads committed substrate to surface the mismatch diagnostic. Tied to substrate S1/S2; deferred to later substrate-consolidation ADR. | n/a. |
| F17 | `backend/app/api/v1/game_routes.py::_player_shell_state_view` — `current_room_id` derivation chain (fallback first, then W5 override) | Compatibility alias on the player-shell payload | ✓ (frontend reads it) | ✓ | ✓ | ✓ | `migrate_to_w5_first_before_removal` — the field itself is a legacy *alias*; the frontend `app.js` reads it. Removal requires frontend upgrade and a follow-up ADR (currently A2 in the Phase 6A inventory). Sequenced beyond 6B-3. | `backend/tests/test_w5_player_shell_payload.py` (parity + mismatch), `test_play_service_client.py`, `test_player_session_live_opening_contract.py`. |
| F18 | `world-engine/app/story_runtime/manager/narrator_output_prompts.py` — narrator system-prompt paragraph instructing the LLM to use `transition_from_previous` as fallback | Prompt-text fallback instruction | ✓ (always sent in the prompt) | ✓ | ✓ | ✓ | *(Phase 6B-2 classification, historical)* `doc_only_update`. **Removed by ADR-0068** (Phase 6B-8): the legacy fallback paragraph is gone; the prompt now contains a single W5-only body that explicitly states `transition_from_previous` is absent. | `test_story_runtime_w5_narrator_strict_migration.py` asserts absence of legacy paragraph and presence of "that field is absent" wording. |
| F19 | `world-engine/app/story_runtime/manager/opening_fallback_observability.py` — comment-only mention of `transition_from_previous` | Comment-only legacy mention | n/a (comment) | n/a | n/a | n/a | *(Phase 6B-2 classification, historical)* `doc_only_update`. Comment updated by ADR-0068 to describe removal (historical_doc_ok). | n/a. |
| F20 | `world-engine/app/story_runtime/manager/diagnostics_api.py::get_w5_langfuse_metadata` — admin parity bridge | W5-first metadata; `w5.legacy_transition_parity` label | ✓ | ✓ | ✓ | ✓ | *(Phase 6B-2 classification, historical)* `substrate_keep`. **`w5.legacy_transition_parity` and `w5.narrator_strict_enabled` removed by ADR-0068** (Phase 6B-8). `w5.location_changed_this_turn` remains W5-history-derived; admin bridge no longer emits narrator strict/parity metadata. | `test_story_runtime_w5_narrator_strict_migration.py` and `test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` assert `w5.narrator_strict_enabled` and `w5.legacy_transition_parity` absent. |
| F21 | `ai_stack/langgraph/runtime_executor/executor_action_resolution_start.py` `L150-L182` — inline `environment_state.actor_locations` + `current_room_id` read that feeds Director-Pause inputs | C3 from Phase 6A: inline substrate read at action-resolution start | ✓ | ✓ | ✓ | ✓ | `migrate_to_w5_first_before_removal` — same call seeds F1's `actor_locations` and `environment_current_room_id`. Migration requires reading `where_summary.derived_actor_locations` first. Sequenced as 6B-3 step 2. | `test_phase1_live_wiring.py`, `tests/smoke/test_thin_path_pr_c_director_pause_live_smoke.py`. |
| F22 | `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py` `L11-L96` — commit-side mirror of F21 | C4 from Phase 6A | ✓ | ✓ | ✓ | ✓ | `migrate_to_w5_first_before_removal` — must move in lockstep with F21. Sequenced as 6B-3 step 2. | Same as F21. |
| F23 | `ai_stack/contracts/narrator_consequence_contracts.py` (C7) — narrator-consequence payload composes `current_area` / `from_area` / `to_area` | Higher-level consumer still reading legacy area metadata | ✓ | ✓ | ✓ | ✓ | `migrate_to_w5_first_before_removal` — narrator-consequence and sensory engine (C8) read W5 only if a new builder is added. Sequenced beyond 6B-3 (deferred to a later phase ADR). | `ai_stack/tests/test_narrator_consequence_contract.py`. |
| F24 | `world-engine/app/story_runtime/manager/session/session_lifecycle.py` and `manager/runtime_config.py` — snapshot composers emit `current_room_id` field on the live snapshot | A3 from Phase 6A: WebSocket transport compatibility | ✓ | ✓ | ✓ | ✓ | `compatibility_alias_keep_temporarily` (mapped to `migrate_to_w5_first_before_removal` for 6B-2 vocabulary) — old WS subscribers read `viewer_room_id`. Removal requires WS client upgrade. Sequenced beyond 6B-3. | `world-engine/tests/test_ws_state_transitions.py`. |
| F25 | `world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py::_fallback_current_room_id` → `runtime_world.current_room_id` (legacy field) | Substrate read for diagnostics | ✓ | ✓ | ✓ | ✓ | `substrate_keep` — see F16. Reads the substrate emitted by C10 (`runtime_world.py`). | n/a. |

### Phase 6B-2 summary by classification

| Classification | Count | Branches |
|----------------|------:|----------|
| `keep_explicit_opt_out_fallback` | 5 | F2, F6, F9, F12, F14 |
| `keep_malformed_w5_safety_fallback` | 5 | F3, F7, F10, F13, F15 |
| `substrate_keep` | 5 | F4, F5, F16, F20, F25 |
| `migrate_to_w5_first_before_removal` | 8 | F1, F8, F11, F17, F21, F22, F23, F24 |
| `remove_dead_default_path_in_6b3` | **0** | — |
| `doc_only_update` | 2 | F18, F19 |
| `unknown_needs_runtime_trace` | 0 | — |

### Phase 6B-2 result

**No branch is safe for an unconditional default-path deletion in Phase 6B-3.** Every fallback path that fires under default-on either (a) is the explicit opt-out path, (b) is the malformed-W5 safety net, (c) is substrate or substrate-derived, or (d) still feeds a downstream consumer that is not yet W5-first.

This is the **expected** result of Phase 6B-2: it confirms that Phase 6B-1's flag flips did not accidentally orphan any code, and that legacy fallback removal must proceed by *consumer migration*, not by branch deletion.

### Phase 6B-3 — recommended order (no deletions, only consumer migrations + lazy re-ordering)

Each step is independently testable. No step removes any legacy *function* — each step migrates a *call site* to read W5 first, with the legacy function still available as the malformed-W5 safety net.

1. **F1 lazy re-order (low-risk optimization, no contract change).** Move the eager `baseline_completion = complete_actor_locations_for_gathering(...)` call inside the two paths that actually return it (disabled-flag branch and `except` branch). The W5-success path becomes the only baseline call (which is the second one, F4). Output dict is identical bit-for-bit on D, O, and M paths.
   - **Test before:** add a Phase 6B-2 test asserting that on D, `derived_actor_locations_source == "w5_projection"` and `gathering_pause_source == "w5_projection"`; on M, `w5_director_projection_failed` is set and `source == "environment_state_with_actor_lane_fallback"`.
2. **F21 / F22 migration (C3 / C4 of Phase 6A).** Make `executor_action_resolution_start` and `executor_action_resolution_commit` read `w5_latest_snapshot.where_summary.derived_actor_locations` first; fall back to `environment_state.actor_locations` only when no snapshot is present.
   - **Test before:** assert in `test_phase1_live_wiring.py` that the Director-Pause input under D uses the W5-derived locations; under M reverts to legacy substrate.
3. **F8 + F18 + F19 sequenced removal (narrator transition fallback).**
   - First update `narrator_output_prompts.py` (F18) to drop the fallback paragraph behind a W5-narrator-strict flag, default-off.
   - Then turn the flag on after `test_story_runtime_w5_narrator_projection.py` is rewritten to assert W5-only narrator prompts.
   - Finally remove the `source_facts["transition_from_previous"] = …` line in `god_of_carnage_narrator_path.py` (F8) and prune the comment in `opening_fallback_observability.py` (F19).
   - **Test before each sub-step:** the parity tests `test_story_runtime_w5_narrator_projection.py:test_w5_narrator_projection_legacy_parity_*` must be rewritten in lockstep with each sub-step. Admin diagnostics F20 must be updated when F8 is removed.
4. **F11 migration (NPC planner W5-first).** Pass `npc_w5_situations` *first* into the planner contract; treat `npc_context_bundle` as a malformed-W5 fallback. Once `test_npc_agency_planner.py`, `test_npc_agency_contracts.py`, `test_npc_agency_long_horizon_claim_readiness.py`, and `test_wave3_multi_actor_vitality.py` all remain green with W5-first inputs, remove the bundle from the *non-fallback* call path (the bundle is still passed in malformed-W5 cases).
5. **F17 + F24 (player-shell `current_room_id` and WS `viewer_room_id`).** Out of 6B-3 scope. Requires frontend / WS client upgrade. Track as a separate ADR.
6. **F23 (`narrator_consequence_contracts.py` and C8 sensory engine).** Out of 6B-3 scope. Requires a new W5-first builder. Track as a separate ADR.

### Phase 6B-2 branches that must remain until a later ADR

- All five **opt-out short-circuits** (F2, F6, F9, F12, F14). They are the only paths that honor `W5_AST_*=0/false/no/off`. Removing them violates the Phase 6B-1 explicit-opt-out contract.
- All five **malformed-W5 safety returns** (F3, F7, F10, F13, F15). They are the safety net the migration plan commits to (Phase 5B: *"missing or malformed W5 snapshots fall back to legacy current_room without failing the turn"*).
- All **substrate reads** (F4, F5, F16, F20, F25) and the substrate writers S1–S8 from the Phase 6A inventory. Substrate consolidation is a separate, later ADR.
- The **compatibility aliases** (F17, F24) until the frontend and WebSocket clients are upgraded.
- The **narrator-consequence and sensory-engine legacy reads** (F23) until W5-first builders exist for those payloads.

### Phase 6B-2 — is targeted fallback removal safe to begin in Phase 6B-3?

**Yes, conditionally — and the conditions are scoped to consumer migration, not branch deletion.** Phase 6B-3 may begin with:

- The F1 lazy re-order (optimization, no contract change, no legacy removal).
- The F21 / F22 W5-first migration of the executor action-resolution inline reads.
- Sequenced removal of F8 / F18 / F19 only after their parity tests are rewritten and the admin parity bridge F20 is updated in lockstep.
- The F11 NPC planner W5-first migration once the planner test suites are confirmed green.

Phase 6B-3 may **not** delete any opt-out short-circuit, any malformed-W5 safety return, any substrate read, or any compatibility alias on the public payload contract. Each such removal requires its own ADR with the gates listed above.

---

## Phase 6B-3A — Director eager-baseline lazy reorder + Executor W5-first reads (complete)

**Phase:** 6B-3A is the first commit of Phase 6B-3. It lands the two consumer migrations that are demonstrably safe to execute without removing any opt-out short-circuit, malformed-W5 safety net, substrate read, or public compatibility alias. **No legacy code is removed in Phase 6B-3A.**

### Phase 6B-3A — what changed

| # | Change | File(s) | Effect |
|---|--------|---------|--------|
| F1 | Lazy re-order of the Director eager baseline | `ai_stack/langgraph/runtime_executor/director_w5_location_projection.py` (SOURCE_LINES of `complete_actor_locations_for_gathering_with_optional_w5_projection`) | The eager `baseline_completion = complete_actor_locations_for_gathering(...)` call at function entry is removed. The legacy completion now runs only inside the explicit-opt-out `if not enabled:` return path and the malformed-W5 `except Exception as exc:` return path. Output is bit-for-bit identical on D / O / M. F4 (the W5-success branch's `complete_actor_locations_for_gathering(...)` call) is preserved. |
| F21 | Inline `_pr_c_actor_locations_raw` substrate read becomes W5-first | `ai_stack/langgraph/runtime_executor/executor_action_resolution_start.py` (SOURCE_LINES of `_resolve_player_action`) | The inline `state.get("actor_locations")` → `environment_state.actor_locations` chain is wrapped in `resolve_w5_first_actor_locations(...)`. Under default-on the resolver prefers `where_summary.derived_actor_locations`. Under opt-out / malformed-W5 / old-payload it returns the legacy substrate verbatim. |
| F22 | `actor_locations_source` diagnostic emitted on `graph_diagnostics` | `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py` (SOURCE_LINES of `_resolve_player_action`) | After F1 is called, the commit side now emits `graph_diagnostics["actor_locations_source"] = {"source": …, "w5_snapshot_id"?: …, "failure_reason"?: …}` so admin diagnostics, Langfuse metadata, and downstream consumers can audit which read path the turn actually used. |

### Phase 6B-3A — what is preserved

- **Explicit opt-out fallback** (F2, F6, F9, F12, F14 in the Phase 6B-2 inventory) is unchanged. `W5_AST_DIRECTOR_PROJECTION_ENABLED=0/false/no/off` continues to revert F1, F21, F22 to the pre-Phase-6B-3A legacy substrate path.
- **Malformed/missing-W5 safety fallback** (F3, F7, F10, F13, F15) is unchanged. Missing or malformed snapshots continue to fall back to the legacy baseline at F1 with `w5_director_projection_failed` set, and to the legacy substrate at F21/F22 with `source == "malformed_w5_fallback"`.
- **Substrate writers and readers** (F4, F5, F16, F20, F25; S1–S8 in Phase 6A) are unchanged. `complete_actor_locations_for_gathering`, the W5 extractor, the environment-state substrate, and the `Participant.current_room_id` dataclass field are all preserved.
- **Public compatibility aliases** (`current_room`, `current_room_id`, `gathering_scene_id`, `complete_actor_locations_for_gathering`) are unchanged.
- **No committed event is mutated.** The `director_gathering_state` payload, the actor lane, the canonical path, `validation_outcome`, ADR-0033 commit semantics, and ADR-0061 pause semantics are unchanged. The new diagnostic lives entirely on `graph_diagnostics` (read-side observability surface).
- **How remains first-class. Inferred Why remains soft truth.** Neither dimension is collapsed by Phase 6B-3A.

### Phase 6B-3A — `actor_locations_source` classification

The new F21/F22 diagnostic `graph_diagnostics["actor_locations_source"]["source"]` is one of:

| `source` value | Meaning | When it fires |
|----------------|---------|---------------|
| `w5_projection` | The W5 projection won; the actor_locations come from `where_summary.derived_actor_locations`. | Default-on `D` path with a well-formed `w5_latest_snapshot` in state. |
| `explicit_opt_out_legacy` | The operator opted the Director projection out; the legacy substrate is used verbatim. | `W5_AST_DIRECTOR_PROJECTION_ENABLED` ∈ `{0, false, no, off}`. |
| `malformed_w5_fallback` | The snapshot was present but `build_w5_projection_for_director(...)` raised or returned no usable derived_actor_locations; the legacy substrate is used verbatim and `failure_reason` carries a compact error string. | Default-on `M` path. |
| `old_payload_legacy` | No `w5_latest_snapshot` is present in graph state (old session predating Phase 1 wire-in, or missing wire-in); the legacy substrate is used verbatim. | Default-on `L` path. |

### Phase 6B-3A — tests added

- `ai_stack/tests/test_w5_actor_tracking_phase_6b3a_consumer_migration.py`
  - `TestF1LazyReorder` — pins `D` happy path source classification, `D` parity with the legacy completion when fed W5-derived inputs, `O` envelope bit-for-bit parity, `O` via explicit argument vs env var parity, and `M` baseline + `w5_director_projection_failed`.
  - `TestF21F22ResolveW5FirstActorLocations` — pins the four-way classification (`w5_projection`, `explicit_opt_out_legacy`, `malformed_w5_fallback`, `old_payload_legacy`), the defensive-copy semantics for the legacy input, the explicit-argument-overrides-environment behavior, and the `legacy_actor_locations=None` tolerance.
  - `test_f1_lazy_reorder_preserves_f4_w5_success_completion_call` — pins that F4 (the W5-success completion call) survives the reorder.
- Existing suites continue to pin Phase 6B-3A's contract: `ai_stack/tests/test_phase1_live_wiring.py`, `ai_stack/tests/test_pr_c_director_pause_mode.py`, `ai_stack/tests/test_w5_actor_tracking_phase_6b1_default_on_flags.py`, `ai_stack/tests/test_w5_actor_tracking_phase_6b2_fallback_inventory.py`, `ai_stack/tests/test_w5_actor_tracking_projection.py`, `ai_stack/tests/test_w5_actor_tracking_validation.py`, `ai_stack/tests/test_environment_state_contracts.py`, and `tests/test_inventory_w5_legacy_consumers.py`.

### Phase 6B-3A — what Phase 6B-3 still has to do

| Sub-phase | Scope | Status |
|-----------|-------|--------|
| **6B-3A** | F1 lazy re-order + F21/F22 W5-first reads + diagnostics. | ✅ complete (Phase 6B-3A section above). |
| **6B-3B** | F8 / F18 / F19 / F20 narrator `transition_from_previous` migration behind the new opt-in `W5_AST_NARRATOR_STRICT_ENABLED` flag (default-off). Under strict-ON: `source_facts.transition_from_previous` is demoted into `source_facts._legacy_compat`, the narrator prompt fallback paragraph is replaced with a W5-only paragraph that preserves Who / Where / What / How / Why (How first-class, inferred Why soft), and the admin parity bridge labels legacy compat as `demoted_to_legacy_compat`. Legacy code is not deleted; the strict flag default-off preserves Phase 6B-3A behavior bit-for-bit. | ✅ complete (Phase 6B-3B section below). |
| **6B-3C** | F11 NPC planner W5-first migration: under default-on with at least one usable W5 NPC projection, `_build_npc_agency_plan_projection` forwards `effective_npc_context_bundle=None` to the planner so the `npc_context_bundle` evidence row is no longer emitted; under explicit opt-out / malformed-W5 / old-payload the legacy bundle is forwarded verbatim. Per-actor diagnostics carry `npc_context_source` / `npc_context_legacy_compat_visible` / `npc_context_fallback_reason`. No legacy code is removed. | ✅ complete (Phase 6B-3C section below). |
| later ADR | F17 player-shell `current_room_id` alias and F24 WS `viewer_room_id` alias. Requires frontend / WebSocket client upgrade. | out of 6B-3 scope. |
| later ADR | F23 `narrator_consequence_contracts.py` (C7) and the sensory engine (C8). Requires a new W5-first builder for movement framing and stage-level area. | out of 6B-3 scope. |

---

## Phase 6B-3B — Narrator `transition_from_previous` migration behind strict flag (complete)

**Phase:** 6B-3B is the second commit of Phase 6B-3. It migrates the F8 / F18 / F19 / F20 narrator-transition surfaces behind the new opt-in `W5_AST_NARRATOR_STRICT_ENABLED` flag without removing any legacy code, opt-out short-circuit, malformed-W5 safety net, substrate read, or public compatibility alias. **No legacy code is removed in Phase 6B-3B. No committed event is mutated.**

### Phase 6B-3B — what changed

| # | Change | File(s) | Effect |
|---|--------|---------|--------|
| Flag | New opt-in resolver `w5_ast_narrator_strict_enabled()` | `ai_stack/actor_tracking/diagnostics.py` SOURCE_LINES; re-exported by `ai_stack/actor_tracking/__init__.py`; included in `w5_projection_flag_states()` under the `"narrator_strict"` key. | Default-off (`False` on unset / empty / explicit `0/false/no/off`). `1/true/yes/on` (case-insensitive) → strict mode. Independent of `W5_AST_NARRATOR_PROJECTION_ENABLED`. |
| F8 | `source_facts.transition_from_previous` migrated behind strict flag | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py::_block` SOURCE_LINES | Strict-OFF (default): legacy `source_facts["transition_from_previous"] = _transition_facts(...)` preserved bit-for-bit. Strict-ON: top-level key omitted; same payload demoted into `source_facts["_legacy_compat"]["transition_from_previous"]` with `authority="w5_projection"` and a non-authoritative `notice`. Hard-cut directed-transition still inspectable under `_legacy_compat`. |
| F18 | Narrator prompt fallback paragraph migrated behind strict flag | `world-engine/app/story_runtime/manager/narrator_output_prompts.py::_narrator_path_output_prompt` SOURCE_LINES | Strict-OFF: legacy fallback paragraph + hard-cut directed-transition guidance preserved. Strict-ON: replaced by a W5-only paragraph that names `who_summary` / `where_summary` / `what_summary` / `how_summary` / `why_summary` explicitly, keeps How first-class (forbids folding into What), marks inferred Why as soft truth (never spoken as observed fact), and instructs the narrator to ignore `source_facts.transition_from_previous` and treat `source_facts._legacy_compat` as non-authoritative debug breadcrumbs. |
| F19 | Opening-fallback observability docstring wording | `world-engine/app/story_runtime/manager/opening_fallback_observability.py::_w5_ast_narrator_projection_enabled` SOURCE_LINES | Rewritten to W5-first / `transition_from_previous`-legacy-compatibility language. Explicitly documents that under strict mode the legacy block is demoted into `source_facts._legacy_compat` and the prompt fallback paragraph is removed. Resolver behavior unchanged. |
| F20 | Admin parity bridge labels W5-first source and demotes legacy parity surface under strict | `world-engine/app/story_runtime/manager/diagnostics_api.py::get_w5_langfuse_metadata` SOURCE_LINES | New diagnostic labels added to the langfuse metadata payload: `w5.location_changed_source` (`"w5_history_projection"` / `"w5_history_insufficient"`), `w5.location_changed_compute_failed` (set only on extraction error), `w5.narrator_strict_enabled` (mirrors resolver), `w5.legacy_transition_parity` (`"legacy_compat_visible"` under strict-OFF, `"demoted_to_legacy_compat"` under strict-ON). The primary `w5.location_changed_this_turn` signal is still computed from W5 history snapshots on both postures; `transition_from_previous.location_changed` is **not** read by the admin bridge under either posture. |

### Phase 6B-3B — what is preserved

- **Explicit opt-out fallback for narrator projection** (F6 in the Phase 6B-2 inventory) is unchanged. `W5_AST_NARRATOR_PROJECTION_ENABLED=0/false/no/off` still suppresses `source_facts.w5_projection` regardless of the strict flag.
- **Malformed/missing-W5 safety fallback for narrator projection** (F7) is unchanged. Malformed snapshots still record `w5_narrator_projection_failed` and return blocks unmodified.
- **Substrate writers and readers** (S1–S8 in Phase 6A; F4 / F5 / F16 / F20 / F25 in Phase 6B-2) are unchanged.
- **Public compatibility aliases** (`current_room`, `current_room_id`, `actor_locations`, `gathering_scene_id`, `complete_actor_locations_for_gathering`) are unchanged.
- **Legacy fallback function** `_transition_facts(...)` is still computed under both strict postures. Strict mode only changes where the resulting payload lands in `source_facts` (top-level vs `_legacy_compat`).
- **No committed event is mutated.** ADR-0033 commit semantics, the Actor Lane, the Canonical Path, `validation_outcome`, ADR-0061 pause semantics, ADR-0063 W5 semantics, and W5 validation semantics are unchanged.
- **How remains first-class. Inferred Why remains soft truth.** The strict-ON narrator prompt explicitly names How attributes (tone / manner / intensity / pace / physicality / method / style) and forbids folding them into What. Inferred Why is marked as soft truth and never described as observed fact.

### Phase 6B-3B — `w5.location_changed_source` and `w5.legacy_transition_parity` classification

The new F20 diagnostic labels are one of:

| Field | Value | Meaning |
|-------|-------|---------|
| `w5.location_changed_source` | `w5_history_projection` | Per-actor `where.value` comparison across `w5_history[-2]` and `w5_history[-1]` succeeded. |
| | `w5_history_insufficient` | Fewer than two W5 snapshots are available; `w5.location_changed_this_turn` defaults to `False`. |
| `w5.location_changed_compute_failed` | `True` | Extraction raised an exception; bridge falls back to `False` (non-authoritative diagnostic). Field is omitted when the compute succeeded. |
| `w5.narrator_strict_enabled` | `True` / `False` | Mirrors the resolver. |
| `w5.legacy_transition_parity` | `legacy_compat_visible` | Strict-OFF: operators may correlate against `source_facts.transition_from_previous` from committed narrator blocks. |
| | `demoted_to_legacy_compat` | Strict-ON: legacy parity surface is non-authoritative debug breadcrumb only. |

### Phase 6B-3B — tests added / updated

- `ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py` (new). Pins the strict-flag resolver contract (default-off / explicit on/off / independence from projection / reporter exposure) and the F8 source_facts contract under both postures (top-level vs `_legacy_compat` demotion, canonical-step / mandatory-beat parity, authored hard_cut breadcrumb survival).
- `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` (new). Pins the F18 prompt-text contract under both postures (legacy fallback paragraph vs W5-only paragraph; Who / Where / What / How / Why guidance preserved on every posture; How first-class; inferred Why marked as soft) and the F20 admin parity bridge labels under both postures (W5-history primary signal; legacy_compat_visible vs demoted_to_legacy_compat; strict-ON ignores stray legacy `transition_from_previous.location_changed=True` claims).
- `ai_stack/tests/test_w5_actor_tracking_phase_6b1_default_on_flags.py` and `ai_stack/tests/test_w5_actor_tracking_phase_6b2_fallback_inventory.py` (updated). Reporter-shape assertions now include `"narrator_strict": False` under default-off; the Phase 6B-1 default-on contract for the five consumer flags is unchanged.
- Existing suites continue to pin Phase 6B-3B's contract under strict-OFF: `world-engine/tests/test_story_runtime_w5_narrator_projection.py`, `world-engine/tests/test_goc_narrator_path_opening.py`, `ai_stack/tests/test_god_of_carnage_narrator_path.py`, `ai_stack/tests/test_actor_tracking_diagnostics.py`, `ai_stack/tests/test_w5_actor_tracking_projection.py`, `ai_stack/tests/test_w5_actor_tracking_validation.py`, `ai_stack/tests/test_w5_actor_tracking_phase_6b3a_consumer_migration.py`, and `tests/test_inventory_w5_legacy_consumers.py`.

### Phase 6B-3B — what Phase 6B-3 still has to do

| Sub-phase | Scope | Status |
|-----------|-------|--------|
| **6B-3C** | F11 NPC planner W5-first migration: under default-on with at least one usable W5 NPC projection, `_build_npc_agency_plan_projection` forwards `effective_npc_context_bundle=None` to the planner so the `npc_context_bundle` evidence row is no longer emitted; under explicit opt-out / malformed-W5 / old-payload the legacy bundle is forwarded verbatim. Per-actor diagnostics carry `npc_context_source` / `npc_context_legacy_compat_visible` / `npc_context_fallback_reason`. No legacy code is removed. | ✅ complete (Phase 6B-3C section below). |
| 6B-4 | Fresh consumer-removal inventory under default-on + Phase 6B-3A/B/C migrations: identify which legacy NPC context / narrator transition / Director eager-baseline branches are now demonstrably unreachable on D, O, M, and L; preserve all opt-out + malformed-W5 safety fallbacks. | planned. |
| later ADR | Permanently flip `W5_AST_NARRATOR_STRICT_ENABLED` to default-on once production-side parity tests are rewritten to assert W5-only narrator prompts; then physically remove the legacy `transition_from_previous` block, the unstrict prompt paragraph, and the legacy_compat debug surface. | out of 6B-3B scope. |
| later ADR | F17 player-shell `current_room_id` alias and F24 WS `viewer_room_id` alias. Requires frontend / WebSocket client upgrade. | out of 6B-3 scope. |
| later ADR | F23 `narrator_consequence_contracts.py` (C7) and the sensory engine (C8). Requires a new W5-first builder for movement framing and stage-level area. | out of 6B-3 scope. |

---

## Phase 6B-3C — NPC planner W5-first migration (complete)

**Phase:** 6B-3C is the third commit of Phase 6B-3. It migrates the F11 attachment site for `npc_context_bundle` behind a W5-first selector so NPC planning consumes the actor-specific Phase 3B W5 NPC projection (`target_consumer="npc"`) as the primary actor-situation authority under the default-on happy path. The legacy bundle remains forwarded verbatim under explicit opt-out, malformed/missing W5, and old-payload sessions. **No legacy code is removed in Phase 6B-3C. No committed event is mutated.**

### Phase 6B-3C — what changed

| # | Change | File(s) | Effect |
|---|--------|---------|--------|
| Resolver | New public helper `resolve_w5_first_npc_context(...)` | `ai_stack/langgraph/runtime_executor/reaction_order_governance.py` SOURCE_LINES; re-exported via `ai_stack.langgraph.runtime_executor.public`. | Four-way classification mirrors Phase 6B-3A's `resolve_w5_first_actor_locations`: `w5_projection` / `explicit_opt_out_legacy` / `malformed_w5_fallback` / `old_payload_legacy`. Returns `effective_npc_context_bundle` (the bundle to forward to the planner; `None` under `w5_projection`), `legacy_compat_npc_context_bundle` (the bundle when demoted under `w5_projection`, audit-only), `npc_context_legacy_compat_visible`, `npc_context_fallback_reason`. Explicit-argument override (`w5_npc_projection_enabled=...`) wins over env to keep mid-flight flag flips off a single turn. |
| F11 | NPC planner attachment site becomes W5-first | `ai_stack/langgraph/runtime_executor/npc_agency_projection.py` SOURCE_LINES (`_build_npc_agency_plan_projection`) | After `_build_w5_npc_projection_inputs(...)`, the projection wrapper calls `resolve_w5_first_npc_context(...)` and forwards `effective_npc_context_bundle` into `build_npc_agency_simulation(...)` / `build_npc_agency_plan(...)`. Under default-on with at least one usable W5 NPC projection, the planner receives `None` and the `npc_context_bundle` evidence row is absent from the simulation's `source_evidence`. Under explicit opt-out / malformed-W5 / old-payload, the bundle is forwarded verbatim (pre-Phase-6B-3C behaviour preserved). |
| Diagnostics | Per-actor F11 diagnostic back-fill | `ai_stack/langgraph/runtime_executor/reaction_order_governance.py` SOURCE_LINES (`_build_w5_npc_projection_inputs`) | Every per-actor row in `w5_npc_projection_diagnostics` carries three new keys: `npc_context_source` (`w5_projection` / `malformed_w5_fallback` / `old_payload_legacy`), `npc_context_legacy_compat_visible` (whether the bundle is in state AND demoted), `npc_context_fallback_reason` (compact reason on fallback paths only; `None` under `w5_projection`). Opt-out short-circuit (F9) is preserved bit-for-bit: the function still returns `({}, [])` so the dramatic packet continues to omit `w5_npc_projection_diagnostics`. |

### Phase 6B-3C — what is preserved

- **Explicit opt-out fallback for NPC projection** (F9 in the Phase 6B-2 inventory) is unchanged. `W5_AST_NPC_PROJECTION_ENABLED=0/false/no/off` still short-circuits to `({}, [])` and the legacy `npc_context_bundle` is forwarded into the planner as the only NPC planning substrate.
- **Per-actor malformed-W5 safety fallback** (F10) is unchanged. Each per-actor `w5_npc_projection_failed` reason is emitted exactly as before, and the legacy bundle is forwarded into the planner.
- **Substrate writers and readers** (S1–S8 in Phase 6A; F4 / F5 / F16 / F20 / F25 in Phase 6B-2) are unchanged.
- **Public compatibility aliases** (`current_room`, `current_room_id`, `actor_locations`, `gathering_scene_id`, `complete_actor_locations_for_gathering`) are unchanged.
- **Legacy fallback function `build_npc_context_bundle(...)`** (`ai_stack/rag/retrieval_context_bundles.py`) is still computed by the retrieval-context layer. Only the *attachment site* in the NPC agency planner contract is migrated. The bundle is still attached to graph state at the same wire-in point as before.
- **No committed event is mutated.** ADR-0033 commit semantics, the Actor Lane, the Canonical Path, `validation_outcome`, ADR-0061 pause semantics, ADR-0063 W5 semantics, and W5 validation semantics are unchanged. The new diagnostics live entirely on `w5_npc_projection_diagnostics` (read-side observability surface).
- **How remains first-class. Inferred Why remains soft truth.** The W5 NPC projection embedded in each NPC proposal preserves the top-level `how_summary` (never folded into `what_summary`) and marks inferred Why via `truth_attribution[...] == "inferred"`.
- **Privacy / actor_knowledge_scope** (Phase 3B contract) is unaffected. The W5 NPC projection still enforces per-actor visibility (target NPC sees its own private inferred Why; another actor's private/inferred Why is exposed only when `actor_knowledge_scope` allows the target NPC; player-private and GM/director-only facts never leak). The legacy bundle, when used, carries only `retrieval_plan` lane allow/block lists — the planner never reads `private_memory`.

### Phase 6B-3C — `npc_context_source` classification

The new per-actor diagnostic `npc_context_source` is one of:

| `npc_context_source` value | Meaning | When it fires |
|----------------------------|---------|---------------|
| `w5_projection` | At least one per-actor W5 NPC projection succeeded; W5 is the primary actor-situation authority for this turn. | Default-on `D` path with a well-formed `w5_latest_snapshot` containing the NPC. |
| `malformed_w5_fallback` | Default-on with a snapshot present but every per-actor `build_w5_projection_for_npc(...)` call raised; legacy bundle is the safety net. | Default-on `M` path. |
| `old_payload_legacy` | Default-on with no `w5_latest_snapshot` in graph state; legacy bundle is the pre-Phase-1-session fallback. | Default-on `L` path (and the per-actor failure reason is `missing_w5_latest_snapshot`). |
| *(not emitted)* | Explicit opt-out short-circuit returns `({}, [])`; the source classification is implicit in the env. | Explicit opt-out `O` path. |

### Phase 6B-3C — tests added

- `ai_stack/tests/test_w5_actor_tracking_phase_6b3c_npc_planner_migration.py` (new).
  - `TestResolveW5FirstNpcContext` — pins the resolver's four-way classification, defensive-copy semantics, explicit-argument-overrides-env behaviour, tolerance for `None` / empty-dict bundles / `None` diagnostics, and the distinction between `missing_w5_latest_snapshot` (→ `old_payload_legacy`) and other per-actor failures (→ `malformed_w5_fallback`).
  - `TestPerActorDiagnosticsBackfill` — pins the per-actor F11 diagnostic keys across D / D-with-bundle / L / M / opt-out.
  - `TestPlannerW5First` — pins the dramatic-packet routing contract: D — `npc_context_bundle` row absent from `source_evidence`, W5 row present, every proposal carries `actor_w5_situation`, How first-class, inferred Why soft, plan-shape stable; O — bundle row present, no W5 row, no diagnostics, no `actor_w5_situation`; M / L — bundle row present, per-actor diagnostics flag the appropriate fallback source.
  - `TestPrivacyPreserved` — pins target-NPC sees own private inferred Why; another NPC's private inferred Why without `actor_knowledge_scope` does not leak; legacy bundle's `private_memory` body never appears in `source_evidence` even under opt-out.
  - Module-level `test_build_npc_agency_simulation_with_none_bundle_omits_legacy_evidence_row` and `test_build_npc_agency_plan_with_none_bundle_omits_legacy_evidence_row` pin the planner-layer guarantee directly: forwarding `npc_context_bundle=None` removes the legacy evidence row and the W5 evidence row is present.
- Existing suites continue to pin Phase 6B-3C's contract:
  - `ai_stack/tests/test_npc_agency_planner.py` — default-on actor-specific NPC projection, opt-out, malformed-W5, W5 situation contract.
  - `ai_stack/tests/test_npc_agency_contracts.py` — NPC agency contract normalization stability.
  - `ai_stack/tests/test_npc_agency_long_horizon_claim_readiness.py` — long-horizon claim readiness under the migrated planner inputs.
  - `ai_stack/tests/test_wave3_multi_actor_vitality.py` — multi-actor vitality under default-on.
  - `ai_stack/tests/test_w5_actor_tracking_phase_6b1_default_on_flags.py`, `test_w5_actor_tracking_phase_6b2_fallback_inventory.py`, `test_w5_actor_tracking_phase_6b3a_consumer_migration.py`, `test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py` — Phase 6B-1/6B-2/6B-3A/6B-3B flag matrix and migration contracts.
  - `ai_stack/tests/test_phase_c_reaction_order_governance.py`, `test_vitality_telemetry_v1.py`, `test_actor_lane_absence_governance.py` — reaction-order / vitality / absence governance surfaces.
  - `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` — LDSS gate stability.
  - `tests/test_inventory_w5_legacy_consumers.py` — Phase 6A inventory and R1–R5 rename guarantees.

### Phase 6B-3C — what Phase 6B-3 still has to do (carry-over)

| Sub-phase | Scope | Status |
|-----------|-------|--------|
| 6B-4 | Fresh consumer-removal inventory pass. Run the inventory script over the working tree with Phase 6B-3A/B/C migrations in place and re-classify each legacy fallback branch under D / O / M / L. Only branches that fire on **none** of those four conditions are removal candidates. | ✅ complete (Phase 6B-4 section below). |
| later ADR | Permanently flip `W5_AST_NARRATOR_STRICT_ENABLED` to default-on once parity tests are rewritten; then physically remove the legacy `transition_from_previous` block, the unstrict prompt paragraph, and the legacy_compat debug surface. | out of 6B-3 scope. |
| later ADR | F17 player-shell `current_room_id` alias and F24 WS `viewer_room_id` alias. Requires frontend / WebSocket client upgrade. | out of 6B-3 scope. |
| later ADR | F23 `narrator_consequence_contracts.py` (C7) and the sensory engine (C8). Requires a new W5-first builder for movement framing and stage-level area. | out of 6B-3 scope. |

---

## Phase 6B-4 — Fresh post-migration legacy fallback inventory (complete)

**Phase:** 6B-4 is the post-migration inventory pass that follows the three sequenced consumer migrations of Phase 6B-3 (6B-3A: F1 lazy reorder + F21/F22 W5-first reads; 6B-3B: F8/F18/F19/F20 narrator strict; 6B-3C: F11 NPC planner W5-first). Phase 6B-4 is **inventory and planning only**. **No legacy code is removed in Phase 6B-4.** **No committed event is mutated.** **No flag default is changed.**

### Phase 6B-4 — goal

Determine which legacy branches remain reachable after F1/F21/F22/F8/F18/F19/F11 were migrated to W5-first behavior, and identify whether any branch is now safe for a future targeted removal phase (6B-5).

### Phase 6B-4 — classification taxonomy

Phase 6B-4 introduces a slightly broader closed taxonomy than 6B-2's so that the four reachability conditions D / O / M / L can be expressed independently:

| Tag | Meaning |
|-----|---------|
| `still_needed_explicit_opt_out` | Branch fires only when an operator sets `W5_AST_*=0/false/no/off`. Removing it violates the Phase 6B-1 explicit-opt-out contract. |
| `still_needed_malformed_w5_safety` | Branch fires only when the W5 snapshot is missing/malformed for that consumer. Removing it violates the Phase 5B "missing or malformed W5 falls back to legacy without failing the turn" promise. |
| `still_needed_old_payload_compatibility` | Branch fires only on sessions persisted before Phase 1 wire-in (no `w5_latest_snapshot` in graph state). Removing it breaks turn replay for those sessions. |
| `still_needed_public_client_compatibility` | Branch fires because a public WS/frontend payload contract names the legacy field. Removing it requires a separately-scoped client upgrade. |
| `substrate_keep_future_adr` | Substrate writer/reader. Substrate consolidation is deferred to a later, separately-scoped ADR. |
| `w5_first_migrated_keep_temporarily` | Phase 6B-3 migrated this call site to W5-first. The legacy helper/branch is kept as the O / M / L safety net and as the debug breadcrumb when an opt-in strict flag (e.g. `W5_AST_NARRATOR_STRICT_ENABLED`) is still default-off. |
| `newly_dead_candidate_for_6b5` | Default-on never executes the branch AND O is covered by a *different* branch AND M is covered by a *different* branch AND L is covered separately AND removal does not touch a public payload contract. Phase 6B-4 finds **zero** such branches. |
| `needs_dedicated_adr_before_removal` | Removing the branch is technically possible but requires its own ADR (parity-test rewrite, client upgrade, prompt-text contract migration, etc.). |
| `test_only_update` | Test fixture or assertion. Migrate in lockstep with its producer; never weakened by the inventory pass. |
| `doc_only_update` | Docstring/comment/prompt-text-only legacy reference. Pruning is purely cosmetic and may proceed in 6B-5. |
| `unknown_needs_runtime_trace` | Static reading cannot prove coverage; needs a live trace. Phase 6B-4 finds **zero** such branches. |

### Phase 6B-4 — inventory method

1. **Re-scan the working tree.** `scripts/inventory_w5_legacy_consumers.py` was extended with a `PHASE_6B4_CLASSIFICATION` map and a closed `PHASE_6B4_TAXONOMY` tuple so the human-readable scan output can hint the new classification per surface. The script remains non-failing.
2. **Re-classify every branch from the Phase 6B-2 inventory** (F1–F25) under the new taxonomy, using static reading + the Phase 6B-3A/B/C migration tests as the proof of D / O / M / L reachability.
3. **Re-classify higher-level consumers from the Phase 6A inventory** (C1–C11 / A1–A9 / S1–S8) that did not appear explicitly in 6B-2 to confirm none is newly dead.
4. **Add Phase 6B-4 proof tests** (`ai_stack/tests/test_w5_actor_tracking_phase_6b4_post_migration_inventory.py`) covering: F1 default-on no longer eager-runs legacy baseline; F21/F22 four-way classification; narrator strict default-off keeps legacy first-class; F11 default-on returns `effective_npc_context_bundle=None`; opt-out / malformed-W5 / old-payload still forward the legacy bundle; inventory-doc ↔ inventory-script taxonomy parity.
5. **Confirm zero forbidden-package imports** in active code via the existing inventory-script smoke gate.
6. **Document the result** in this Phase 6B-4 section.

### Phase 6B-4 — post-6B-3A/B/C branch table

Conditions: D = default-on happy path; O = explicit opt-out; M = malformed/missing W5; L = legacy client / old session. ✓ = branch fires for that condition. ✗ = branch does not fire. n/a = branch type does not exist for that condition.

| # | File:Symbol | Branch | D | O | M | L | 6B-4 classification | D/O/M/L primary | W5 replacement | Removal would break opt-out? | Removal would break malformed-W5 fallback? | Removal would break old session compat? | Removal would break public API/frontend/WS? | Recommended next action | Tests required before removal |
|---|-------------|--------|---|---|---|---|--------------------|-----------------|----------------|------------------------------|---------------------------------------------|-----------------------------------------|---------------------------------------------|-------------------------|--------------------------------|
| F1 | `director_w5_location_projection.py::complete_actor_locations_for_gathering_with_optional_w5_projection` — lazy baseline in `not enabled` + `except` branches | Phase 6B-3A lazy reorder + post-migration baseline placement | ✗ (D uses F4 W5-success branch) | ✓ | ✓ | ✓ via M | `w5_first_migrated_keep_temporarily` + `still_needed_explicit_opt_out` + `still_needed_malformed_w5_safety` | D=W5, O/M=legacy | `build_w5_projection_for_director` + F4 | yes | yes | yes | no | **Keep.** Both baseline calls are now load-bearing exactly where they belong. | Phase 6B-3A regression: `test_w5_actor_tracking_phase_6b3a_consumer_migration.py::TestF1LazyReorder`, `test_w5_actor_tracking_phase_6b4_post_migration_inventory.py::TestF1DefaultOnDoesNotEagerRunLegacyBaseline`. |
| F2 | same file — `if not enabled: return …` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `still_needed_explicit_opt_out` | O=legacy | n/a | yes | n/a | n/a | no | **Keep.** Pinned by Phase 6B-1 default-on flag test. | (already pinned). |
| F3 | same file — `except Exception as exc: …; return baseline` | Malformed-W5 safety return | ✗ | ✗ | ✓ | n/a | `still_needed_malformed_w5_safety` | M=legacy | n/a | n/a | yes | n/a | no | **Keep.** | `test_w5_actor_tracking_projection.py` Director failure cases. |
| F4 | same file — `complete_actor_locations_for_gathering(...)` inside W5-success branch | Substrate re-use of NPC fallback voting + gathering_scene_id derivation over W5-derived inputs | ✓ | ✗ | ✗ | ✗ | `substrate_keep_future_adr` | D=W5 inputs into the substrate consolidator | this IS the consolidation | no | no | no | no | **Keep.** ADR-0061 pause semantics depend on it. | n/a. |
| F5 | `director_location_completion.py::complete_actor_locations_for_gathering` | Legacy completion algorithm — NPC fallback voting + gathering_scene_id | ✓ via F4 | ✓ via F2 | ✓ via F3 | n/a | `substrate_keep_future_adr` | universal | this IS the producer | yes | yes | n/a | no | **Keep.** Single source of truth for the substrate. | n/a. |
| F6 | `world-engine/.../actor_tracking/w5_projection.py::_maybe_enrich_blocks_with_w5_narrator_projection` — `if not enabled: return source_blocks` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `still_needed_explicit_opt_out` | O=legacy | n/a | yes | n/a | n/a | no | **Keep.** | `test_story_runtime_w5_narrator_projection.py` opt-out test. |
| F7 | same file — `except Exception as exc: …; return source_blocks` | Malformed-W5 safety return | ✗ | ✗ | ✓ | n/a | `still_needed_malformed_w5_safety` | M=legacy | n/a | n/a | yes | n/a | no | **Keep.** | Phase 6B-2 default-on no-`w5_narrator_projection_failed` assertion. |
| F8 | `god_of_carnage_narrator_path.py::_block` — `source_facts["transition_from_previous"] = _transition_facts(...)` (strict-OFF) / `_legacy_compat["transition_from_previous"]` (strict-ON) | Always-write legacy transition payload (location depends on strict flag) | ✓ strict-OFF default; demoted strict-ON | ✓ | ✓ | ✓ | *(Phase 6B-4 classification, historical)* `w5_first_migrated_keep_temporarily` + `needs_dedicated_adr_before_removal`. **Removed by ADR-0068** (Phase 6B-8, 2026-05-28). `_transition_facts` deleted; no strict-off branch remains; `source_facts["transition_from_previous"]` and `_legacy_compat` are absent from all narrator blocks. | Not current runtime behavior. |
| F9 | `reaction_order_governance.py::_build_w5_npc_projection_inputs` — `if not enabled: return ({}, [])` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `still_needed_explicit_opt_out` | O=legacy | n/a | yes | n/a | n/a | no | **Keep.** | Phase 6B-1 NPC flag test. |
| F10 | same file — per-actor `except Exception as exc: …` | Per-actor malformed-W5 safety | ✗ | ✗ | ✓ | n/a | `still_needed_malformed_w5_safety` | M=per-actor legacy bundle remains primary | n/a | n/a | yes | n/a | no | **Keep.** | `test_npc_agency_planner.py` failure cases. |
| F11 | `npc_agency_projection.py::_build_npc_agency_plan_projection` — W5-first selector via `resolve_w5_first_npc_context(...)` | Default-on: planner receives `effective_npc_context_bundle=None`; O/M/L: legacy bundle is forwarded verbatim | ✗ (D forwards `None`) | ✓ | ✓ | ✓ | `w5_first_migrated_keep_temporarily` + `still_needed_explicit_opt_out` + `still_needed_malformed_w5_safety` + `still_needed_old_payload_compatibility` | D=W5 actor_w5_situation, O/M/L=legacy bundle | per-actor `build_w5_projection_for_npc` (`target_consumer="npc"`) | yes | yes | yes | no | **Keep.** Removal requires a follow-up ADR that retires the bundle even under O/M/L. | Phase 6B-3C `test_w5_actor_tracking_phase_6b3c_npc_planner_migration.py`; Phase 6B-4 `TestF11NpcDefaultOnReturnsNoneBundle`; existing `test_npc_agency_planner.py`, `test_npc_agency_contracts.py`, `test_npc_agency_long_horizon_claim_readiness.py`, `test_wave3_multi_actor_vitality.py`. |
| F12 | `god_of_carnage_turn_seams_validation.py::_apply_w5_validation_to_outcome` — `if not enabled: return outcome` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `still_needed_explicit_opt_out` | O=legacy | n/a | yes | n/a | n/a | no | **Keep.** | Phase 6B-1 validation flag test. |
| F13 | same file — `except Exception as exc: diagnostic = w5_validation_fallback(text)` | Malformed-W5 safety with `w5_validation_fallback_reason` | ✗ | ✗ | ✓ | n/a | `still_needed_malformed_w5_safety` | M=structural fallback | n/a | n/a | yes | n/a | no | **Keep.** | Phase 6B-2 default-on no-fallback-reason assertion. |
| F14 | `session_state_w5_view.py::_maybe_build_w5_player_view_for_session` — `if not enabled: return None, None` | Opt-out short-circuit | ✗ | ✓ | n/a | n/a | `still_needed_explicit_opt_out` | O=legacy | n/a | yes | n/a | n/a | no | **Keep.** | Phase 6B-1 player-view flag test. |
| F15 | same file — `except Exception as exc: return None, _player_view_diagnostics(used=False, failed=reason, ...)` | Malformed-W5 safety with `current_room_source="fallback"` | ✗ | ✗ | ✓ | n/a | `still_needed_malformed_w5_safety` | M=legacy | n/a | n/a | yes | n/a | no | **Keep.** | Phase 6B-2 player-view fallback-source assertion. |
| F16 | same file — `_fallback_current_room_id(session)` — `runtime_world.current_room_id` → `environment_state.current_room_id` → `environment_state.current_area` | Substrate fallback location resolver | ✓ (always computed for mismatch diagnostic) | ✓ | ✓ | ✓ | `substrate_keep_future_adr` | universal | substrate reads — substrate consolidation deferred | yes | yes | yes | yes | **Keep.** Substrate consolidation ADR is out of 6B scope. | n/a. |
| F17 | `backend/app/api/v1/game_routes.py::_player_shell_state_view` — `current_room_id` derivation chain (W5-preferred under default-on; legacy fallback retained) | Public compatibility alias on the player-shell payload | ✓ | ✓ | ✓ | ✓ | `still_needed_public_client_compatibility` + `needs_dedicated_adr_before_removal` | universal | W5 player-shell view (already preferred when valid) | yes | yes | yes | yes (frontend `app.js`) | **Keep.** Frontend upgrade is a separate ADR. | `backend/tests/test_w5_player_shell_payload.py`, `test_play_service_client.py`, `test_player_session_live_opening_contract.py`. |
| F18 | `narrator_output_prompts.py` — narrator system-prompt fallback paragraph naming `transition_from_previous` | Prompt-text fallback instruction (strict-OFF) / W5-only paragraph (strict-ON) | ✓ strict-OFF default | ✓ | ✓ | ✓ | *(Phase 6B-4 classification, historical)* `doc_only_update` + `needs_dedicated_adr_before_removal`. **Removed by ADR-0068** (Phase 6B-8): legacy fallback paragraph deleted; prompt is now W5-only with explicit "Do not consult transition_from_previous; that field is absent." | Not current runtime behavior. |
| F19 | `opening_fallback_observability.py::_w5_ast_narrator_projection_enabled` docstring | Comment / docstring legacy mention (already W5-first wording under Phase 6B-3B) | ✓ (always present) | ✓ | ✓ | ✓ | `doc_only_update` | n/a | n/a | n/a | n/a | n/a | n/a | **Keep wording.** Phase 6B-3B already rewrote it to W5-first language. Phase 6B-5 may prune the historical sentence after strict-on flip. | Phase 6B-3B docstring test. |
| F20 | `diagnostics_api.py::get_w5_langfuse_metadata` — admin parity bridge | W5-first metadata under both strict postures; `w5.legacy_transition_parity` label flips between `legacy_compat_visible` and `demoted_to_legacy_compat` | ✓ | ✓ | ✓ | ✓ | *(Phase 6B-4 classification, historical)* `w5_first_migrated_keep_temporarily` + `needs_dedicated_adr_before_removal`. **`w5.legacy_transition_parity` and `w5.narrator_strict_enabled` removed by ADR-0068** (Phase 6B-8): metadata keys deleted; `w5.location_changed_this_turn` computed from W5 history only. | Not current runtime behavior. |
| F21 | `executor_action_resolution_start.py::_resolve_player_action` — `resolve_w5_first_actor_locations(...)` at action-resolution start | Phase 6B-3A W5-first read | ✗ legacy under D; ✓ under O/M/L | ✓ | ✓ | ✓ | `w5_first_migrated_keep_temporarily` + `still_needed_explicit_opt_out` + `still_needed_malformed_w5_safety` + `still_needed_old_payload_compatibility` | D=W5; O/M/L=legacy | `where_summary.derived_actor_locations` | yes | yes | yes | no | **Keep helper.** Permanent removal requires retiring the legacy substrate read entirely (substrate ADR). | Phase 6B-3A `test_w5_actor_tracking_phase_6b3a_consumer_migration.py`, Phase 6B-4 `TestF21F22DefaultOnRemainsW5First`. |
| F22 | `executor_action_resolution_commit.py::_resolve_player_action` — `graph_diagnostics["actor_locations_source"]` emit | Commit-side mirror of F21 | ✓ | ✓ | ✓ | ✓ | `w5_first_migrated_keep_temporarily` | universal observability emitter | this IS the W5-aware diagnostic surface | no | no | no | no | **Keep.** Diagnostic surface is the new observability contract. | Same as F21. |
| F23 | `narrator_consequence_contracts.py` (C7) + `sensory_context_engine.py` (C8) — narrator-consequence payload + sensory engine read legacy `current_area` / `from_area` / `to_area` | Higher-level consumer still reading legacy area metadata | ✓ | ✓ | ✓ | ✓ | `still_needed_public_client_compatibility` + `needs_dedicated_adr_before_removal` | universal | W5-first builder does not exist yet | yes | yes | yes | yes (narrator-consequence contract is consumed downstream) | **Keep.** Requires a new W5-first movement-framing / stage-area builder (separate ADR). | `ai_stack/tests/test_narrator_consequence_contract.py`. |
| F24 | `session_lifecycle.py` + `runtime_config.py` snapshot composers + `world-engine/app/story_runtime_shell_readout.py` — `current_room_id` field on emitted snapshot / WS `viewer_room_id` | Public compatibility alias on the WS payload | ✓ | ✓ | ✓ | ✓ | `still_needed_public_client_compatibility` + `needs_dedicated_adr_before_removal` | universal | W5 player view (already exposed for new subscribers) | yes | yes | yes | yes (WebSocket client contract) | **Keep.** WS client upgrade is a separate ADR. | `world-engine/tests/test_ws_state_transitions.py`, `test_ws_runtime_commands_and_isolation.py`. |
| F25 | `session_state_w5_view.py::_fallback_current_room_id` → `runtime_world.current_room_id` | Substrate read for diagnostics | ✓ | ✓ | ✓ | ✓ | `substrate_keep_future_adr` | universal | substrate read | yes | yes | yes | yes | **Keep.** See F16. | n/a. |

### Phase 6B-4 — additional cross-checks

The Phase 6A C1–C11 / A1–A9 / S1–S8 entries that are not explicitly numbered above were re-scanned for newly dead candidates and all remain reachable under at least one of D / O / M / L:

- `C5` `player_action_resolution.py` legacy `current_room_id` / `current_area` reads — still primary on D (no W5-first builder for player-action affordance resolution yet); classification `needs_dedicated_adr_before_removal`.
- `C6` `semantic_scene_planner.py::_anchor_room_id_from_env` — still primary on D; benign fallback. `substrate_keep_future_adr`.
- `C9` `language_adapter.py::current_area` payload field — still primary on D. `still_needed_public_client_compatibility`.
- `C10` `runtime_world.py::build_runtime_world_from_environment` — substrate projector. `substrate_keep_future_adr`.
- `C11` `dramatic_context_authority.py` `environment_state.current_room_id` read — still primary on D. `needs_dedicated_adr_before_removal`.
- `A4` `world-engine/app/story_runtime_shell_readout.py` legacy readout — still used by operator shell. `still_needed_public_client_compatibility`.
- `A5` `world-engine/diagnostics/.../create_session_runtime_template.py` — diagnostic template builder. `substrate_keep_future_adr`.
- `S1`–`S8` substrate writers — `substrate_keep_future_adr`. Out of 6B scope.

### Phase 6B-4 — summary by classification

| Classification | Count | Branches |
|----------------|------:|----------|
| `still_needed_explicit_opt_out` | 5 | F2, F6, F9, F12, F14 |
| `still_needed_malformed_w5_safety` | 5 | F3, F7, F10, F13, F15 |
| `still_needed_old_payload_compatibility` | 0 (covered by F21/F22 + F11 multi-tag and by `needs_dedicated_adr_before_removal` for old-session-only re-renders) | — |
| `still_needed_public_client_compatibility` | 4 | F17, F23, F24 (and C9 language-adapter payload `current_area`) |
| `substrate_keep_future_adr` | 6 | F4, F5, F16, F25 (and C6, C10) |
| `w5_first_migrated_keep_temporarily` | 6 | F1, F8, F11, F20, F21, F22 |
| `newly_dead_candidate_for_6b5` | **0** | — |
| `needs_dedicated_adr_before_removal` | 6 | F8 (narrator strict permanent flip), F17, F18, F20, F23, F24 (and C5, C11) |
| `test_only_update` | unchanged from Phase 6A | T1–T13 |
| `doc_only_update` | unchanged from Phase 6A + F18, F19 | D1–D12 (+ F18, F19) |
| `unknown_needs_runtime_trace` | 0 | — |

> Multi-tag note: F1 / F11 / F21 are intentionally multi-tagged because the same call site is the W5-first read under D *and* the safety net for O / M / L. The summary counts them once per applicable tag.

### Phase 6B-4 — verification that Phase 6B-3A/B/C did not regress

- **F1 default-on no longer eager-runs the legacy baseline.** Pinned by `ai_stack/tests/test_w5_actor_tracking_phase_6b4_post_migration_inventory.py::TestF1DefaultOnDoesNotEagerRunLegacyBaseline` (D-source = `"w5_projection_with_actor_lane_fallback"`) and the existing `test_w5_actor_tracking_phase_6b3a_consumer_migration.py::TestF1LazyReorder`.
- **F21/F22 default-on W5 path is primary.** Pinned by `TestF21F22DefaultOnRemainsW5First` (four-way classification) and `test_w5_actor_tracking_phase_6b3a_consumer_migration.py::TestF21F22ResolveW5FirstActorLocations`.
- **F8 strict-OFF default keeps legacy `transition_from_previous` first-class; strict-ON demotes it.** Pinned by `TestF8F18F19F20NarratorStrictDefaultOffKeepsLegacyFirstClass` and `test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py::TestF8NarratorPathSourceFactsContract`.
- **F18 prompt is strict-W5 under the strict flag.** Pinned by `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` (strict-ON drops the legacy paragraph; strict-OFF retains it).
- **F19 wording is W5-first.** Pinned by the Phase 6B-3B docstring reorientation already in the resolver.
- **F20 admin metadata is W5-first under both strict postures.** Pinned by the Phase 6B-3B `test_story_runtime_w5_admin_diagnostics.py` assertions; legacy parity label flips between `legacy_compat_visible` (strict-OFF) and `demoted_to_legacy_compat` (strict-ON).
- **F11 NPC context is W5-first on default-on happy path; legacy bundle remains the planner substrate on O / M / L.** Pinned by `TestF11NpcDefaultOnReturnsNoneBundle` (all four conditions) and the existing Phase 6B-3C suite.

### Phase 6B-4 — result

**No branch is safe for an unconditional default-path deletion in Phase 6B-5.** Every fallback that fires under default-on is either (a) an explicit opt-out path, (b) a malformed-W5 safety net, (c) an old-payload safety net, (d) a public client payload alias, (e) substrate or substrate-derived, or (f) part of a contract that requires its own ADR before removal (narrator strict permanent flip, frontend / WS client upgrade, narrator-consequence W5-first builder).

This result confirms that Phase 6B-3A/B/C migrated the consumers correctly without orphaning any code: every legacy branch that still exists is load-bearing under exactly one of D / O / M / L, and the W5-first paths under D are observable via the Phase 6B-3A diagnostics (`actor_locations_source`, `w5_director_projection_used`, `npc_context_source`).

### Phase 6B-4 — branches that still must remain (and why)

- **F2 / F6 / F9 / F12 / F14** — the five explicit-opt-out short-circuits. Removing them violates the Phase 6B-1 explicit-opt-out contract (operators can re-enable pre-W5 behavior by exporting `W5_AST_*=0/false/no/off`).
- **F3 / F7 / F10 / F13 / F15** — the five malformed-W5 safety returns. Removing them violates the Phase 5B "missing or malformed W5 falls back to legacy without failing the turn" promise.
- **F4 / F5 / F16 / F25 / C6 / C10 / S1–S8** — substrate writers, readers, and substrate-derived projectors. Substrate consolidation is a separate, later ADR; W5 is downstream of these.
- **F8 / F18 / F19 / F20** — narrator transition surfaces. Permanent removal requires the strict-on permanent flip ADR (parity tests rewrite, admin label retire).
- **F17 / F24** — public WS / player-shell compatibility aliases. Removal requires client upgrade ADR.
- **F23 + C9** — narrator-consequence and sensory engine legacy reads. Removal requires a new W5-first movement-framing / stage-area builder ADR.
- **F11 legacy bundle on O / M / L** — the planner's fallback substrate when W5 cannot serve as the primary actor-situation authority. Removal requires a follow-up ADR retiring the bundle entirely (which would also require a Phase 4-style coverage decision for malformed-W5 NPC planning).

### Phase 6B-4 — recommended Phase 6B-5 plan

Phase 6B-5 is **not** a branch-deletion phase. It starts with the narrator strict default-on sequence and keeps each move independently testable.

1. **Phase 6B-5A — narrator strict default-on ADR and test plan.** ADR-0065 records the safety contract for promoting `W5_AST_NARRATOR_STRICT_ENABLED` from opt-in to default-on/permanent behavior. No runtime behavior changes, no flags flip, and no legacy branches are removed.

2. **Phase 6B-5B — strict-mode parity test rewrite.** Rewrite narrator projection, narrator prompt, and admin diagnostics tests so default-on strict mode is the expected semantic contract:
   - narrator projection tests prove W5 supplies current location, `location_changed`, and hard-cut guidance replacement;
   - narrator prompt tests prove no legacy `transition_from_previous` primary guidance remains;
   - admin diagnostics tests prove W5 metadata is primary and legacy transition evidence is demoted;
   - opt-out, malformed-W5, and old-payload compatibility remain covered while the rollback path exists.

3. **Phase 6B-5C — default-on flip.** Flip `W5_AST_NARRATOR_STRICT_ENABLED` to default-on only after 6B-5B gates are green. Explicit disable remains supported during rollout. No committed output may mutate.

4. **Phase 6B-5D — remove strict-off prompt fallback paragraph.** Remove the prompt text that still teaches the narrator to use legacy `transition_from_previous` as fallback guidance, after strict default-on has stabilized.

5. **Phase 6B-5E — remove or further demote `_legacy_compat["transition_from_previous"]`.** Decide whether the compatibility breadcrumb can be removed or must remain diagnostics-only. If public diagnostics change, record that decision in a follow-up ADR before removal.

6. **Phase 6B-5F — fresh post-default-on inventory.** Re-run the legacy-consumer inventory after strict default-on and reclassify all narrator strict branches as still-needed opt-out, malformed-W5 safety, old-payload compatibility, public compatibility, diagnostics-only, or newly dead.

**Narrator-consequence / sensory-engine W5-first builders (F23 + C9), frontend / WebSocket client upgrades (F17 + F24), NPC bundle retirement (F11), and substrate consolidation (S1–S8, F4 / F5 / F16 / F25, C6 / C10) are explicitly out of this narrator-strict sequence.** They remain deferred to future, separately scoped ADRs. The migration plan's "`environment_state` remains the low-level committed substrate" guarantee continues to hold.

### Phase 6B-4 — known unrelated issues observed during inventory

The Phase 6B-4 inventory pass did not touch world-engine HTTP routing, did not modify `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py`, and did not modify any LDSS / Wave3 test. During that inventory, unrelated gate issues were recorded separately. Phase 6B-4.5 subsequently repaired the stale MVP04 diagnostics-envelope route-oracle logic without changing W5/runtime behavior.

### Phase 6B-4 — is Phase 6B-5 targeted removal safe to begin?

**Yes, conditionally.** Phase 6B-5 may begin with 6B-5A (ADR-0065, complete) and then 6B-5B (strict-mode parity-test rewrite). Phase 6B-5 may **not** start by deleting any opt-out short-circuit, malformed-W5 safety net, old-payload compatibility, substrate read, public payload alias, or F8 / F18 / F19 / F20 strict-OFF branch before the ADR lands, parity tests are rewritten, and the default-on safety gates are green.

---

## Phase 6B-5E — `_legacy_compat` Transition Breadcrumb Consumer Classification

### Decision

**Option B accepted:** `_legacy_compat["transition_from_previous"]` is gated behind opt-in diagnostics flag `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` (default-off). See ADR-0065 Phase 6B-5E Decision section and migration doc Phase 6B-5E section for full rationale.

### Consumer Inventory (Phase 6B-5E scope)

| Consumer | Location | Classification |
|---|---|---|
| `_legacy_compat["transition_from_previous"]` insertion | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py::_block()` | ~~`gated_diagnostics_opt_in`~~ **retired_phase_6b6b** |
| `_legacy_compat["authority"]`, `_legacy_compat["notice"]` | same | ~~`gated_diagnostics_opt_in`~~ **retired_phase_6b6b** |
| `w5.legacy_transition_parity` label | `world-engine/app/story_runtime/manager/diagnostics_api.py::get_w5_langfuse_metadata()` | ~~**simplified_two_value_6b6b**~~ **removed_by_adr_0068_admin_metadata** |
| `w5.narrator_legacy_compat_diagnostics_enabled` | same | ~~`new_flag_report`~~ **retired_phase_6b6b** |
| Prompt guidance referencing `_legacy_compat` as possible breadcrumb | `world-engine/app/story_runtime/manager/narrator_output_prompts.py` | **updated_6b6b**; ADR-0068 later says "that field is absent" |
| Test assertions on `_legacy_compat` presence under strict-on | various `test_w5_actor_tracking_phase_6b5b_parity.py` etc. | **removed_phase_6b6b** |

### What Remains for Phase 6B-5F

The following surfaces still exist and require classification in the Phase 6B-5F fresh inventory:

- `transition_from_previous` **computation** under explicit strict-off (data generation; not included in strict-on source_facts).
- Explicit strict-off path (entire `else` branch in `_block()`).
- Malformed-W5 safety fallback (unchanged).
- Public compatibility aliases (unchanged).
- All substrate writers (unchanged).
- The `_legacy_compat` presence tests now split into flag-off and flag-on variants — flag-on tests will become newly-dead candidates if the diagnostics flag is permanently removed in a future ADR.

### Is Phase 6B-5F Fresh Inventory Safe to Begin?

**Yes.** Phase 6B-5E gate conditions are met:
- Default strict-on source_facts contains no `_legacy_compat`.
- Diagnostics flag opt-in supplies the breadcrumb for authorized parity audits.
- W5 `where_summary.location_changed` covers the location-shift signal.
- MVP03 and MVP04 gates remain green.
- No committed event was mutated.
- No opt-out, malformed-W5, or substrate surface was removed.

---

### Phase 6B-6A — Diagnostics Flag Retirement ADR + Dependency Audit

**Status: Complete (audit/planning only).** ADR-0066 authored, full dependency audit recorded. No code removed.

---

### Phase 6B-6B — Diagnostics Flag Removal (Complete, 2026-05-23)

**Status: Complete.** All removals executed per ADR-0066 §Rollout Plan. ADR-0066 status: **Accepted**.

**Inventory fix:** `.worktrees/phase-6b5f/` contained stale actor_situation references. Inventory script now excludes `.worktrees/`, `.claude/worktrees/`, `.state_tmp/` as non-active-source auxiliary workspaces. Tests assert these exclusions.

**Diagnostics flag retirement surface classification (post-6B-6B):**

| Symbol | File | Final Classification |
|--------|------|---------------------|
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` (env resolver) | `ai_stack/actor_tracking/diagnostics.py` | **retired_phase_6b6b** (deleted) |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (function + `__all__`) | `ai_stack/actor_tracking/diagnostics.py` | **retired_phase_6b6b** (deleted) |
| `narrator_legacy_compat_diagnostics` (flag-states key) | `ai_stack/actor_tracking/diagnostics.py` | **retired_phase_6b6b** (deleted) |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (export) | `ai_stack/actor_tracking/__init__.py` | **retired_phase_6b6b** (deleted) |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (import + call) | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | **retired_phase_6b6b** (deleted) |
| `_legacy_compat["transition_from_previous"]` write | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | **retired_phase_6b6b** (deleted) |
| imports | `world-engine/.../external_imports_core.py`, `_imports_00.py` | **retired_phase_6b6b** (deleted) |
| `legacy_compat_diag` + `w5.narrator_legacy_compat_diagnostics_enabled` | `world-engine/.../diagnostics_api.py` | **retired_phase_6b6b** (deleted) |
| `demoted_to_legacy_compat` parity label | `diagnostics_api.py::get_w5_langfuse_metadata()` | **retired_phase_6b6b**; ADR-0068 later removes the remaining parity key/value from current admin metadata |
| `W5_FLAGS` fixture entry + monkeypatches | 4 test files | **retired_phase_6b6b** (removed) |

**Post-ADR-0068 transition_from_previous behavior:**
- Explicit strict opt-out (`W5_AST_NARRATOR_STRICT_ENABLED=false`) no longer
  changes narrator behavior.
- New GoC narrator `source_facts` never emit top-level
  `transition_from_previous`.
- `w5.legacy_transition_parity`, `legacy_compat_visible`, and
  `removed_by_6b5e_policy` are no longer current narrator admin metadata.
- Malformed-W5 safety fallback is unchanged.

**See:** [ADR-0066](docs/architecture/components/world-engine/architecture) (Accepted).

---

### Phase 6B-7 — Strict-Off Deprecation (Complete, 2026-05-23)

**Phase 6B-6B status:** `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` **retired** (see above).

**Phase 6B-7 status:** Strict-off rollback surface **deprecated** by ADR-0067 and later **removed** by ADR-0068.

**What changed:**
- `NarratorStrictOffDeprecationWarning(DeprecationWarning)` added to `ai_stack/actor_tracking/diagnostics.py` and exported from the package.
- `w5_ast_narrator_strict_enabled()` emits this warning **once per process** when `W5_AST_NARRATOR_STRICT_ENABLED` is explicitly set to `0/false/no/off`.
- Warning is **not** emitted for unset/empty (strict-on default, no change).
- All strict-off rollback behavior preserved intact.

**Strict-off surface classification (Phase 6B-7):**

| Symbol | File | Classification |
|--------|------|---------------|
| `W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off` | env-var | **strict_off_rollback_deprecated** — ADR-0067; emits `NarratorStrictOffDeprecationWarning` |
| `w5_ast_narrator_strict_enabled()` strict-off branch | `ai_stack/actor_tracking/diagnostics.py` | **strict_off_rollback_deprecated** — retained; removal needs ADR-0068 |
| `source_facts["transition_from_previous"]` write | `god_of_carnage_narrator_path._narrator_block()` | **strict_off_rollback_deprecated** — present only under strict-off; not yet removed |
| `NarratorStrictOffDeprecationWarning` | `ai_stack/actor_tracking/diagnostics.py`, `__init__.py` | **new_phase_6b7** — public warning class for filter guards |
| `_strict_off_deprecation_warned` sentinel | `ai_stack/actor_tracking/diagnostics.py` | **new_phase_6b7** — module-level bool; tests reset via monkeypatch |

**Removed in Phase 6B-8 (ADR-0068):**
- `W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off` behavior change.
- `transition_from_previous` computation and first-class insertion under strict-off.
- `_strict_off_deprecation_warned` and `_emit_strict_off_deprecation_warning()`.
- Strict-off parity tests were rewritten to assert permanent strict-on behavior.

**Still present after Phase 6B-8:**
- Malformed-W5 safety fallback.
- Substrate writers/readers and public compatibility aliases.

**Removal criteria for final strict-off removal:** Superseded by
[ADR-0068](docs/architecture/components/world-engine/architecture),
Accepted under operator waiver on 2026-05-28.

**See:** [ADR-0067](docs/architecture/components/world-engine/architecture) (Accepted).

---

### Phase 6B-7.5 — ADR-0067 Removal-Readiness Audit (2026-05-23)

**Purpose:** Prove whether ADR-0068 final strict-off removal is safe to begin; produce the exact
implementation plan if it is. This is an audit + planning phase only. No runtime behavior removed.

---

#### ADR-0067 Five-Criteria Checklist

| # | Criterion | Current Evidence | Tests Proving It | Status |
|---|-----------|-----------------|-----------------|--------|
| 1 | **No active operator usage** — `W5_AST_NARRATOR_STRICT_ENABLED=false` not set in any prod/staging/preview deployment | Repo-local config (`.env`, `.env.*`, `docker-compose*.yml`, GitHub workflows, `settings*.py`, ops docs) contain **zero** assignments of `false/0/no/off` to this flag. Live/staging/cloud config is not available from the repository. | Operator config grep (see audit §below) | **WAIVED** — operator accepts repo-local config evidence as sufficient for ADR-0068 |
| 2 | **Warning observable in logs** — `NarratorStrictOffDeprecationWarning` in place for at least one release cycle without operator escalation | Release-cycle observation is not provable from repository evidence. | `test_w5_actor_tracking_phase_6b7_strict_off_deprecation.py` rewritten for removed-warning/no-warning behavior | **WAIVED** — operator waives release-cycle waiting period |
| 3 | **Parity test suite updated** — all strict-off rollback path tests removed or converted to strict-on-only | Strict-off rollback tests rewritten to assert permanent strict-on behavior. | ADR-0068 required tests | **MET by Phase 6B-8** |
| 4 | **Inventory updated** — `transition_from_previous` and `location_changed` removed from rollback taxonomy or reclassified | `transition_from_previous` reclassified as `removed_by_adr_0068`; `location_changed` remains W5 where_summary authority, not rollback. | `test_w5_actor_tracking_phase_6b7_strict_off_deprecation.py::test_phase_6b4_classification_marks_transition_removed` | **MET by Phase 6B-8** |
| 5 | **Dedicated removal ADR (ADR-0068)** written, reviewed, and Accepted | ADR-0068 exists and records the operator waiver. | ADR index + ADR document | **MET** |

**Overall readiness:** authorized by operator waiver in ADR-0068. Criteria 1
and 2 are explicitly waived; criteria 3 through 5 are satisfied by Phase 6B-8.

**Operator waiver before ADR-0068:**
- Repo-local config evidence is sufficient for this branch.
- The release-cycle waiting period is waived.

---

#### Operator / Deployment Audit

**Scope searched:**
- `.env`, `.env.*`, `docker-compose*.yml`, `docker-compose*.yaml`
- `.github/workflows/*.yml`, `.github/workflows/*.yaml`
- `settings*.py`
- `docs/` (ops docs, deployment docs, observability docs)
- `scripts/`

**Result:** No `.env`, docker-compose, GitHub workflow, or `settings*.py` file in this repository
sets `W5_AST_NARRATOR_STRICT_ENABLED` to any value. The flag name appears only in:
- `ai_stack/actor_tracking/diagnostics.py` — runtime resolver (expected)
- `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` — comment (expected)
- `ai_stack/tests/` and `world-engine/tests/` — `monkeypatch.setenv` in tests (expected)
- `docs/archive/adr-retired-2026/`, `docs/MVPs/` — documentation references (expected)

**Conclusion:** Repo-local operator config is **clean**. Live/staging/cloud
config is not available from the repository; ADR-0068 records the operator
waiver accepting repo-local evidence as sufficient for this branch.

---

#### Runtime Dependency Audit

All references to the removal-relevant symbols, classified by role:

| Symbol | File:Line | Classification | ADR-0068 Action |
|--------|-----------|---------------|-----------------|
| `W5_AST_NARRATOR_STRICT_ENABLED` (env read) | `ai_stack/actor_tracking/diagnostics.py` | `removed_by_adr_0068` | **Done** — narrator runtime no longer reads this env var |
| `_strict_off_deprecation_warned` sentinel | `ai_stack/actor_tracking/diagnostics.py` | `removed_by_adr_0068` | **Done** — sentinel and `_emit_strict_off_deprecation_warning()` removed |
| `w5_ast_narrator_strict_enabled()` | `ai_stack/actor_tracking/diagnostics.py` | `removed_by_adr_0068` | **Done** — function and public export removed |
| `NarratorStrictOffDeprecationWarning` class | `ai_stack/actor_tracking/diagnostics.py` | `removed_by_adr_0068` | **Done** — warning class removed; no tombstone retained |
| `NarratorStrictOffDeprecationWarning` export | `ai_stack/actor_tracking/__init__.py` | `removed_by_adr_0068` | **Done** — package export removed |
| `source_facts["transition_from_previous"]` write | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | `removed_by_adr_0068` | **Done** — strict-off branch removed |
| `_transition_facts()` method | `god_of_carnage_narrator_path.py` | `removed_by_adr_0068` | **Done** — method removed |
| `location_changed` in `_transition_facts()` | `god_of_carnage_narrator_path.py` | `removed_by_adr_0068` | **Done** with `_transition_facts()` |
| `scene_changed` in `_transition_facts()` | `god_of_carnage_narrator_path.py` | `removed_by_adr_0068` | **Done** with `_transition_facts()` |
| `directed_transition` in `_transition_facts()` | `god_of_carnage_narrator_path.py` | `removed_by_adr_0068` | **Done** with `_transition_facts()` |
| `where_summary.location_changed` | `ai_stack/actor_tracking/projection.py:214–221` | `strict_on_w5_primary_runtime` | **Keep** — W5 projection, not legacy |
| `location_changed` docstring refs | `ai_stack/actor_tracking/projection.py:660`, `diagnostics.py` | `doc_only` | **Update** — remove "mirrors `transition_from_previous`" language |
| `legacy_transition_parity` key | `world-engine/app/story_runtime/manager/diagnostics_api.py` | `removed_by_adr_0068_admin_metadata` | **Done** — narrator admin metadata key removed |
| `removed_by_6b5e_policy` | `world-engine/app/story_runtime/manager/diagnostics_api.py` | `removed_by_adr_0068_admin_metadata` | **Done** — former label no longer emitted |
| `npc_context_legacy_compat_visible` | `ai_stack/langgraph/runtime_executor/reaction_order_governance.py` | `unrelated` | **No change** — NPC planner compat flag; separate from narrator strict-off |
| `scene_changed` in `backend/` | `backend/app/runtime/narrative/` | `unrelated` | **No change** — backend narrative context; not W5 narrator path |

---

#### Test Dependency Audit

Historical tests that required the strict-off rollback path, with ADR-0068 disposition:

**Files with entire test scope gated on strict-off:**

| File | Test(s) | Disposition |
|------|---------|------------|
| `ai_stack/tests/test_god_of_carnage_narrator_path.py` | Historical strict-off fixture | **Rewritten** as strict-on-only source_facts assertions. |

**Files with mixed strict-on / strict-off tests:**

| File | Test(s) to DELETE | Tests to KEEP |
|------|------------------|--------------|
| `ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py` | Historical strict-off source_facts tests | **Rewritten** to assert explicit false is ignored and no transition is emitted. |
| `ai_stack/tests/test_w5_actor_tracking_phase_6b4_post_migration_inventory.py` | Historical strict-off source_facts tests | **Rewritten** to assert no transition under any env value. |
| `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py` | Historical strict-off parity tests | **Rewritten** to assert canonical output and W5 projection are stable under explicit false. |
| `ai_stack/tests/test_w5_actor_tracking_projection.py` | Historical strict-off parity reference | **Rewritten** to use W5 `where_summary.location_changed` authority. |
| `world-engine/tests/test_goc_narrator_path_opening.py` | Historical strict-off opening test | **Rewritten** to assert no transition in narrator source_facts. |
| `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` | Historical strict-off prompt/admin tests | **Rewritten** to assert explicit false is ignored and admin parity remains removed. |
| `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` | Historical strict-off prompt/admin tests | **Rewritten** to assert permanent strict-on behavior and W5 authority. |

**Files that test the deprecation mechanism (update at ADR-0068, not delete now):**

| File | Current role | ADR-0068 update |
|------|-------------|-----------------|
| `ai_stack/tests/test_w5_actor_tracking_phase_6b7_strict_off_deprecation.py` | Formerly tested warning emission and rollback behavior | **Rewritten** to test the removed state: explicit false is silently ignored, no warning is emitted, and inventory verifies `removed_by_adr_0068`. |

**Summary counts:**
- Historical strict-off test functions were deleted or rewritten as strict-on-only assertions.
- Projection parity now uses W5 `where_summary.location_changed`.
- Deprecation-warning tests now pin removed-warning/no-warning behavior.

---

#### Exact ADR-0068 Removal Scope (Executed)

ADR-0068 removes the following — and only the following:

**`ai_stack/actor_tracking/diagnostics.py`:**
- `w5_ast_narrator_strict_enabled()` function and public export removed.
- `_strict_off_deprecation_warned` module-level sentinel removed.
- `_emit_strict_off_deprecation_warning()` helper function removed.
- `NarratorStrictOffDeprecationWarning` class and public export removed.
- Docstrings that reference the old strict-off posture updated where they describe current behavior.

**`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`:**
- `_transition_facts()` method removed entirely. This eliminates `location_changed`, `scene_changed`, `directed_transition` fields from the legacy transition path.
- Strict-off branch in `_block()` removed: no `if not w5_ast_narrator_strict_enabled()` block and no `transition_payload` assignment remain.
- Current comment records ADR-0068 permanent strict-on behavior.

**`scripts/inventory_w5_legacy_consumers.py`:**
- `transition_from_previous` remains tracked but is reclassified as `removed_by_adr_0068`.
- `location_changed` is classified as W5 where_summary location-shift authority, not rollback.
- `PHASE_6B4_CLASSIFICATION["transition_from_previous"]` records ADR-0068 removal.
- `PHASE_6B4_TAXONOMY` no longer contains `strict_off_rollback_deprecated`; it includes `removed_by_adr_0068`.
- Phase 6B-7.5 readiness section records criteria 1 and 2 as waived and criteria 3 through 5 as met.

**`docs/MVPs/w5_legacy_consumer_removal_inventory.md`:**
- Phase 6B-8 section records the removal.
- Phase 6B-7 and Phase 6B-7.5 sections show removed/waived status.

**`world-engine/app/story_runtime/manager/diagnostics_api.py`:**
- `w5.narrator_strict_enabled` metadata removed.
- `w5.legacy_transition_parity` metadata removed.
- `removed_by_6b5e_policy` and `legacy_compat_visible` are no longer emitted
  narrator admin values.

**`docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view`:**
- Written and marked Accepted under operator waiver.
- References ADR-0067 and records criteria 1 and 2 as waived.
- Includes the removal diff at function and branch level.
- Includes rollback plan.
- Confirms no narrator prompt, parity test, or admin diagnostic reads `transition_from_previous` as narrator authority after removal.

**What ADR-0068 must NOT touch:**
- Malformed-W5 safety fallback (separate code path)
- Public compatibility aliases (substrate writers/readers, W5 projection surfaces)
- Any committed event structure
- ADR-0033, ADR-0061, ADR-0063, ADR-0065, ADR-0066, ADR-0067 constraints

---

#### Phase 6B-8 Runtime Status

ADR-0068 changes only the narrator strict-off rollback path:
- `W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off` no longer changes behavior.
- `transition_from_previous` is no longer emitted by new narrator source_facts.
- Malformed-W5 safety fallback remains unchanged.
- Strict-off parity tests are rewritten to assert permanent strict-on behavior.
- `NarratorStrictOffDeprecationWarning` and `w5_ast_narrator_strict_enabled`
  are no longer importable.
- `w5.narrator_strict_enabled` and `w5.legacy_transition_parity` are no longer
  current narrator admin metadata.
- Substrate writers/readers, public compatibility aliases, committed events, and
  committed output remain unchanged.

**See:** [ADR-0068](docs/architecture/components/world-engine/architecture) (Accepted).

---

### Phase 6B-8 — Strict-Off Rollback Removal (Complete, 2026-05-28)

**Current source_facts shape:** `w5_projection` is the sole actor-situation
authority. `transition_from_previous` and `_legacy_compat` are absent from new
GoC narrator blocks. `where_summary.location_changed` remains the location-shift
source. How remains first-class. Inferred Why remains soft truth.

**Inventory reclassification:** `transition_from_previous` is
`removed_by_adr_0068`; remaining hits are documentation, tests, or historical
fixtures. Remaining legacy surfaces are current-room, visibility,
actor-location, public payload, or NPC planner compatibility surfaces; they are
not narrator strict-off rollback.

**Recommended next phase:** Phase 6B-8.1 no-legacy audit: remove stale
documentation language that describes retired narrator strict-off intermediate
states as current behavior, then continue substrate/public payload compatibility
consolidation under a separate ADR.

---

### Phase 6B-9 — W5 WS compat alias comments + world-engine UI W5-first (Complete, 2026-05-29)

**ADR:** ADR-0069 (Accepted)

Preparatory steps: compat alias comments added to `RuntimeSnapshot.viewer_room_id`
and `RuntimeSnapshot.current_room`; `world-engine/app/web/static/app.js` `currentRoom()`
upgraded to W5-first; inventory scanner extended with `viewer_room_id` surface;
gap-doc test added. No aliases removed.

**WS surface status (post 6B-9):** `viewer_room_id` and `current_room` are compat aliases.
`w5_player_view` and `feature_flags` are absent from `RuntimeSnapshot` — gap documented.

---

### Phase 6B-10 — Wire w5_player_view into RuntimeSnapshot + WS payloads (Complete, 2026-05-29)

**ADR:** ADR-0069 (Accepted)

`RuntimeSnapshot` in both `backend/app/runtime/models.py` and
`world-engine/app/runtime/models.py` now carries:

- `w5_player_view: dict[str, Any] | None = None`
- `feature_flags: dict[str, Any] | None = None`

`RuntimeEngine.build_snapshot()` (both engines) always emits `feature_flags`
(from env `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED`). `w5_player_view` is `None`
in the base WS path (RuntimeEngine has no story session access); it is populated
when a caller passes it explicitly or via `instance.metadata["_w5_player_view"]`.

**Gap closed:** `test_ws_runtime_snapshot_w5_player_view_gap_is_documented` removed.
4 positive WS payload assertion tests added.

**WS surface status (post 6B-10):**

| Field | Status |
|-------|--------|
| `viewer_room_id` | compat alias — **keep** (ADR-0069; removal deferred to future ADR) |
| `current_room` | compat alias — **keep** (ADR-0069; removal deferred to future ADR) |
| `w5_player_view` | **present** — `None` in base WS path; callers may populate |
| `feature_flags` | **present** — always emits `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` |

**Next phase:** 6B-11 — Production WS `w5_player_view` population.
Requires: confirmed `w5_player_view` population in production WS sessions, documented
client upgrade window, separate ADR.

---

### Phase 6B-11 — Production WS w5_player_view population + alias deprecation (Complete, 2026-05-29)

**ADR:** ADR-0069 (Accepted)

`RuntimeManager.build_snapshot()` and `broadcast_snapshot()` now populate
`RuntimeSnapshot.w5_player_view` from the bound `StorySession.w5_latest_snapshot`
whenever a valid player-scoped projection exists. The production bridge is
per-viewer direct kwargs into `RuntimeEngine.build_snapshot()`, not a run-scoped
`instance.metadata["_w5_player_view"]` cache.

`viewer_room_id`, `current_room`, and HTTP/player-shell `current_room_id` are now
deprecated public aliases for the compatibility window. They remain present and
must not be removed before a future dedicated removal ADR records client
migration evidence.

**WS diagnostic status (post 6B-11):**

| Field | Status |
|-------|--------|
| `w5_player_view` | present and non-null when valid W5 exists |
| `feature_flags` | present on every WS RuntimeSnapshot |
| `metadata.w5_player_view_diagnostics.ws_w5_player_view_source` | `w5_projection`, `missing_w5`, `malformed_w5`, or `legacy_only` |
| `metadata.w5_player_view_diagnostics.ws_current_room_aliases_deprecated` | true |
| `viewer_room_id` | deprecated compat alias — keep during migration window |
| `current_room` | deprecated compat alias — keep during migration window |

**Next phase:** 6B-12 public alias deprecation metadata and client fallback
warning. Do not remove substrate fields, `actor_locations`, or
`complete_actor_locations_for_gathering`.

---

### Phase 6B-12 — Public alias deprecation metadata + compatibility window (Complete, 2026-05-29)

**ADR:** ADR-0069 (Accepted)

Public room aliases are observable deprecated compatibility aliases, not active
authority:

| Surface | Phase 6B-12 classification |
|---------|----------------------------|
| `w5_player_view` | `public_authority` |
| `viewer_room_id` | `deprecated_public_client_alias_keep` |
| `current_room` | `deprecated_public_client_alias_keep` |
| `current_room_id` | `deprecated_public_client_alias_keep` for public player-shell payload; `substrate_keep_future_adr` for participant/runtime substrate |
| `runtime_world.current_room_id` / `environment_state.current_room_id` | `substrate_keep_future_adr` |
| `actor_locations` | `substrate_keep_future_adr` |
| `complete_actor_locations_for_gathering` | `substrate_keep_future_adr` |

**Payload metadata:** WS `RuntimeSnapshot.metadata.deprecations.room_aliases`
and HTTP/player-shell `deprecations.room_aliases` advertise replacement
`w5_player_view`, authority path
`w5_player_view.where_summary.current_visible_location`, alias set
`viewer_room_id/current_room/current_room_id`, and future-ADR removal policy.

**Client behavior:** frontend helpers read W5 first and emit a one-time
developer-console warning only when they fall back to legacy `current_room`
while W5 is enabled. The W5-success path does not warn.

**Next phase:** 6B-13 alias-usage telemetry and client-readiness gate. Public
alias removal is still deferred and requires a future ADR.

---

### Phase 6B-13 — Alias usage telemetry + client-readiness gate (Complete, 2026-05-29)

**ADR:** ADR-0069 (Accepted)

Public room aliases remain deprecated compatibility aliases, and their continued
emission is now observable:

| Surface | Phase 6B-13 status |
|---------|--------------------|
| `w5_player_view` | public authority; W5 location authority present in production-like WS payload tests |
| `viewer_room_id` | deprecated public alias; still emitted |
| `current_room` | deprecated public alias; still emitted on WS payloads and retained for malformed-W5 fallback |
| `current_room_id` | deprecated public alias on HTTP/player-shell payload; substrate fields remain out of removal scope |

**Telemetry:** WS payloads emit
`RuntimeSnapshot.metadata.deprecated_alias_usage`; HTTP/player-shell payloads emit
`deprecated_alias_usage` when `current_room_id` is emitted. The object contains
`room_aliases_emitted`, `w5_player_view_present`,
`w5_player_view_authority`, `aliases`, `phase: "6B-13"`, and
`removal_blocked_until: "client_readiness_evidence"`. It does not emit raw W5
history or private facts.

**Readiness gate:** `scripts/inventory_w5_legacy_consumers.py` now reports:

| Field | Value |
|-------|-------|
| `public_aliases_still_emitted` | `true` |
| `w5_player_view_authority_present` | `true` |
| `frontend_helpers_prefer_w5` | `true` |
| `legacy_fallback_still_tested` | `true` |
| `removal_ready` | `false` |
| `reason` | `client_readiness_window_active` |

**Removal decision:** alias removal remains blocked. Evidence required before a
future removal ADR: production-like WS payloads continue to show W5 authority,
supported frontend/WS clients read W5 before aliases, fallback warning/telemetry
shows no supported-client dependency, and docs describe aliases only as deprecated
compatibility.

**Next phase:** 6B-14 can prepare the public alias removal ADR only after the
client-readiness evidence exists; it is not safe to remove aliases yet.

---

### Phase 6C-0 — Narrator consequence / sensory location-framing inventory (Complete, 2026-05-29)

**ADR:** [ADR-0070](docs/architecture/components/world-engine/architecture)

Phase 6C-0 inventories internal narrative framing surfaces. It does not remove
public aliases, substrate fields, malformed-W5 fallback, or committed events.

| Surface | Classification | Runtime role | W5 replacement surface | Risk / required evidence |
|---------|----------------|--------------|--------------------------|--------------------------|
| `ai_stack/contracts/narrator_consequence_contracts.py::_current_context_area` | `w5_first_migration_candidate` | Reads `player_local_context.current_location_id/current_area` and `scene_affordances.current_area` as current narrative area | `W5Projection(target_consumer="narrator").where_summary.current_location` or `scene_location.value` | High; prove narrator consequence parity and retained malformed-W5 fallback |
| `ai_stack/contracts/narrator_consequence_contracts.py::_base_local_context_transition` | `w5_first_migration_candidate` | Emits `from_area`, `to_area`, `from_location_id`, `to_location_id` | `w5_location_framing.v1` derived from narrator `where_summary.previous_location/current_location/location_changed` | High; compatibility fields must remain until downstream tests migrate |
| `ai_stack/contracts/narrator_consequence_contracts.py::build_narrator_consequence_plan` | `w5_first_migration_candidate` | Chooses area-transition consequence from legacy transition plus authored scene-affordance detail | W5-first transition framing while authored detail remains text source | Medium-high; no committed output change without focused tests |
| `ai_stack/contracts/narrator_consequence_contracts.py::build_updated_player_local_context` | `w5_first_migration_candidate` | Carries `current_area/current_location_id/previous_area` across turns | W5-derived compatibility local context after helper adoption | High; affects later turns |
| `ai_stack/story_runtime/narrative/sensory_context_engine.py::_current_location_id` | `w5_first_migration_candidate` | Chooses sensory `location_id` from `to_area/current_area/from_area`, prior truth, scene id, or affordance fallback | W5-first `current_location_id` from location framing | Medium-high; sensory layer selection may change |
| `ai_stack/story_runtime/narrative/sensory_context_engine.py::_append_location_layers` | `w5_first_migration_candidate` | Emits room ambient and entry sensory layers for selected location | W5 framing source decides movement/entry requiredness; authored palette remains text source | Medium; evidence refs and requiredness need tests |
| `ai_stack/language_io/language_adapter.py::_interaction_surface_cached` | `w5_first_migration_candidate` | Seeds cached semantic interaction surface `current_area` from authored layout | Runtime overlay should prefer W5 framing without poisoning cached authored content | Medium; cache/runtime separation must be explicit |
| `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py::_resolve_player_action` | `w5_first_migration_candidate` | Calls narrator consequence contracts through SOURCE_LINES after action resolution inputs are available | Thread W5 location framing into contract inputs additively | High; graph state updates are committed turn metadata |
| `ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py::_derive_sensory_context` | `w5_first_migration_candidate` | Passes `local_context_transition` into sensory derivation | Pass W5 location framing before legacy transition fallback | Medium-high; aspect ledger diagnostics need coverage |
| `ai_stack/contracts/environment_state_contracts.py::_apply_environment_movement/apply_action_to_environment_state` | `substrate_keep_future_adr` | Writes `current_room_id/current_area/previous_room_id/previous_area` and `actor_locations` | Out of scope; remains W5 extraction substrate | Very high; future substrate ADR only |
| `backend/app/runtime/models.py::RuntimeSnapshot.viewer_room_id/current_room` | `public_compatibility_keep` | Deprecated public WS aliases | `w5_player_view.where_summary.current_visible_location` | Removal blocked by Phase 6B-13 client-readiness gate |
| `backend/app/api/v1/game/player_shell_state_projection.py::build_player_shell_state_view` | `public_compatibility_keep` | Deprecated HTTP/player-shell `current_room_id` alias and telemetry | `w5_player_view.where_summary.current_visible_location` | Removal blocked by ADR-0069 |
| `world-engine/app/story_runtime/manager/dramatic_context_authority.py::_phase1_canonical_context_for_session` | `needs_dedicated_adr` | Reads `environment_state.current_room_id` for Director-Pause canonical context | Future Director/canonical-path W5 projection decision | High; not part of narrator/sensory migration |
| `backend/app/runtime/narrative/short_term_context.py::ShortTermContext.build` | `unrelated_domain_use` | Backend session-history `scene_changed` flag | None for Phase 6C-0 | Low; not narrator consequence location framing |
| `ai_stack/tests/test_narrator_consequence_contract.py` | `test_only_update` | Locks current `from_area/to_area/current_area` expectations | Update with W5 helper and compatibility assertions in implementation phase | Required before runtime migration |
| ADR/docs references | `doc_only_update` | Describe prior/public alias migration | Reference ADR-0070 for internal narrator/sensory framing | Keep docs aligned |

**Implementation plan summary:**

- Add `ai_stack/actor_tracking/location_framing.py`.
- Derive `current_location_id`, `previous_location_id`, `from_location_id`,
  `to_location_id`, and `location_changed` from narrator W5 `where_summary`.
- Preserve compatibility `from_area/to_area` outputs during the migration window.
- Keep malformed-W5 safety fallback to legacy transition fields.
- Keep public aliases and substrate writers untouched.
- Keep How first-class and inferred Why soft truth through helper output and
  tests.

**Runtime implementation in 6C-0:** deferred. The affected code crosses committed
consequence metadata, sensory-context targets, carried player local context, and
LangGraph SOURCE_LINES. Phase 6C-1 should implement the helper first, then migrate
contract callsites with parity fixtures.

---

### Phase 6C-1 — W5 location-framing helper added (Complete, 2026-05-30)

**ADR:** [ADR-0070](docs/architecture/components/world-engine/architecture)

Phase 6C-1 adds the helper and optional additive input points. It does not remove
legacy fields and does not make the default graph synthesize
`w5_location_framing` yet.

| Surface | Phase 6C-1 status | Notes |
|---------|-------------------|-------|
| `ai_stack/actor_tracking/location_framing.py` | `implemented_w5_first_helper` | `build_w5_location_framing()` coerces `W5Projection` / `W5Snapshot` / persisted dicts through typed W5 models and emits compact framing only |
| `location_framing_to_local_context_transition()` | `implemented_compat_adapter` | Produces `from_area`, `to_area`, `current_area`, `location_changed`, and `scene_changed` compatibility fields from W5 framing |
| `ai_stack/contracts/narrator_consequence_contracts.py` | `additive_input_ready` | Optional `w5_location_framing` can annotate transition/consequence diagnostics; callers without the field keep legacy behavior |
| `ai_stack/story_runtime/narrative/sensory_context_engine.py` | `additive_input_ready` | Optional `w5_location_framing` is preferred for sensory `location_id` and emits compact diagnostics when provided |
| LangGraph runtime executor SOURCE_LINES | `additive_passthrough_ready` | Pass through `state["w5_location_framing"]` only when already present; no default synthesis yet |
| `ai_stack/language_io/language_adapter.py` | `deferred_to_6c2_or_later` | Cached authored `current_area` remains content fallback; runtime overlay must avoid poisoning module cache |
| Public room aliases | `public_compatibility_keep` | Still governed by ADR-0069 and Phase 6B-13 client-readiness gate |
| `environment_state` / `actor_locations` / `complete_actor_locations_for_gathering` | `substrate_keep_future_adr` | Not touched by Phase 6C-1 |

**Helper output shape:** `w5_location_framing.v1` contains
`current_location`, `previous_location`, `scene_location`,
`location_changed`, `scene_changed`, compatibility `from_location/from_area`,
`to_location/to_area`, `current_area`, `source`, `fallback_reason`,
`source_attribution`, `truth_attribution`, `how_summary`, `why_summary`,
`has_how`, `has_inferred_why`, and `warnings`.

**Fallback behavior:** missing or malformed W5 returns `source:
"legacy_fallback"` when fallback locations are supplied, otherwise
`source: "missing_w5"` or `source: "malformed_w5"`. Fallbacks are diagnostics,
not crashes.

**Next removal decision:** no removal is authorized. Phase 6C-2 must prove graph
construction of `w5_location_framing` and narrator consequence parity before any
default-source switch. Public alias removal remains separately blocked by the
ADR-0069 readiness gate.

---

### Phase 6C-2 — Graph-owned W5 location-framing synthesis (Complete, 2026-05-30)

**ADR:** [ADR-0070](docs/architecture/components/world-engine/architecture)

Phase 6C-2 makes W5 location framing available by default inside the graph while
preserving legacy fallback and output parity. It does not remove
`current_area/from_area/to_area`, public room aliases, substrate fields,
`actor_locations`, `complete_actor_locations_for_gathering`, or malformed-W5
safety fallback.

| Surface | Phase 6C-2 status | Notes |
|---------|-------------------|-------|
| `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py::_resolve_player_action` | `graph_owned_synthesis` | Synthesizes `state["w5_location_framing"]` from `w5_latest_snapshot` through `build_w5_location_framing()` when no caller-provided framing exists |
| `state["w5_location_framing"]` | `additive_graph_state` | Emits `w5_location_framing.v1` with source, current/previous/scene location, `location_changed`, compatibility `current_area/from_area/to_area`, attribution, How/Why summaries, and fallback reason |
| `graph_diagnostics.w5_location_framing` | `compact_diagnostics` | Records source, fallback reason, `w5_location_changed`, `w5_current_location`, and `w5_previous_location`; no raw W5 history is emitted |
| `ai_stack/contracts/narrator_consequence_contracts.py` | `parity_proven_additive_input` | Receives synthesized framing and retains legacy transition fallback; compatibility fields remain present |
| `ai_stack/story_runtime/narrative/sensory_context_engine.py` | `parity_proven_additive_input` | Receives synthesized framing when present and retains legacy `current_area/current_room` fallback when W5 is missing |
| `ai_stack/language_io/language_adapter.py` | `deferred_to_6c3_or_later` | Runtime overlay remains pending; cached authored `current_area` must not be overwritten by live W5 state |

**Parity evidence:** focused tests prove W5 and legacy agree for current
location, previous/current movement framing, `location_changed` /
`scene_changed`, same-location sensory resolution, missing/malformed W5
fallback, How as first-class state, and inferred Why as soft truth. Runtime tests
also call `_resolve_player_action` directly to prove graph-owned synthesis and
missing-W5 fallback execute, rather than merely checking field presence.

**Next removal decision:** no removal is authorized. Phase 6C-3 may begin the
W5-first authority switch for narrator consequence and sensory-context location
decisions behind broader live-turn parity fixtures. Public alias removal remains
blocked by ADR-0069.

---

### Phase 6C-3 — W5-first narrator/sensory location authority switch (Complete, 2026-05-30)

**ADR:** [ADR-0070](docs/architecture/components/world-engine/architecture)

Phase 6C-3 changes authority order only: valid W5 location framing is now the
primary source for narrator-consequence and sensory-context location decisions.
It does not remove legacy fields or public aliases.

| Surface | Phase 6C-3 status | Notes |
|---------|-------------------|-------|
| `ai_stack/actor_tracking/location_framing.py` | `w5_first_authority` | Defines valid W5 as `source == "w5_projection"` with a present current/scene/to location; legacy wins for missing, malformed, incomplete, or explicitly unsuitable W5 |
| `location_framing_to_local_context_transition()` | `authority_switch_complete` | Emits compatibility `current_area/from_area/to_area` from W5 when valid; preserves legacy movement target when pre-commit W5 reports no location change |
| `ai_stack/contracts/narrator_consequence_contracts.py` | `w5_first_authority` | `build_local_context_transition()` prefers valid W5 framing and reports `location_framing_authority` / `local_context_transition_source` diagnostics |
| `ai_stack/story_runtime/narrative/sensory_context_engine.py` | `w5_first_authority` | Sensory `location_id` resolves from valid W5 first, with legacy transition/current-area fallback retained |
| `ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py::_resolve_player_action` | `diagnostics_extended` | Graph diagnostics preserve W5 source/fallback fields and add authority/source labels from the resulting local transition |
| Public room aliases | `public_compatibility_keep` | Still governed by ADR-0069; no alias removal |
| `environment_state` / `actor_locations` / `complete_actor_locations_for_gathering` | `substrate_keep_future_adr` | Not touched by Phase 6C-3 |

**Fallback conditions:** `missing_w5`, `malformed_w5`, incomplete W5 location,
old payloads without `w5_location_framing`, and pre-commit W5 that reports
`location_changed=false` while the current action has a fresh legacy movement
target.

**Next removal decision:** no removal is authorized. Phase 6C-4 should be a fresh
inventory and targeted cleanup plan, not a deletion pass.

---

### Phase 6C-4 — post-authority inventory and cleanup plan (Complete, 2026-05-30)

**ADR:** [ADR-0070](docs/architecture/components/world-engine/architecture)

Phase 6C-4 reclassifies the remaining narrator-consequence / sensory-context
location references after the W5-first authority switch. This phase is inventory
and cleanup planning only. It does not remove runtime legacy fields.

| Surface | Phase 6C-4 classification | W5 replacement exists | Default happy path uses W5 | Removal would break fallback | Recommended action |
|---------|---------------------------|-----------------------|----------------------------|------------------------------|--------------------|
| `ai_stack/actor_tracking/location_framing.py::location_framing_is_valid_w5` | `w5_first_authority` | Yes | Yes | No | Keep as central authority predicate |
| `location_framing_to_local_context_transition()` | `w5_first_authority` | Yes | Yes | Yes | Keep `current_area/from_area/to_area` as compatibility/fallback fields until a removal ADR |
| `narrator_consequence_contracts.py::_current_context_area` | `w5_first_authority` | Yes | Yes | Yes | Keep legacy reads only as malformed-W5 / old-payload fallback |
| `narrator_consequence_contracts.py::build_local_context_transition` | `w5_first_authority` | Yes | Yes | Yes | Keep transition compatibility keys; do not treat them as authority when W5 is valid |
| `narrator_consequence_contracts.py::build_narrator_consequence_plan` | `w5_first_authority` | Yes | Yes | Yes | Keep compatibility transition inputs until consequence-realization fixtures migrate |
| `narrator_consequence_contracts.py::build_updated_player_local_context` | `legacy_fallback_keep` | Yes | No | Yes | Keep carried local-context aliases until a W5-native carried-context ADR exists |
| `sensory_context_engine.py::_current_location_id` | `w5_first_authority` | Yes | Yes | Yes | Keep legacy location fallback for malformed W5 and old payloads |
| `sensory_context_engine.py::_append_location_layers` | `legacy_fallback_keep` | Yes | Yes | Yes | Keep authored detail selection stable; do not migrate requiredness yet |
| `executor_action_resolution_commit.py::_resolve_player_action` | `w5_first_authority` | Yes | Yes | Yes | Keep graph-owned synthesis and diagnostics; no runtime deletion in 6C-4 |
| `executor_symbolic_meta_genre_derivation.py::_derive_sensory_context` | `w5_first_authority` | Yes | Yes | Yes | Keep both W5 framing and legacy transition arguments |
| `language_adapter.py::_interaction_surface_cached` | `legacy_fallback_keep` | No runtime overlay yet | No | Yes | Keep as authored content fallback; do not poison cached surface with runtime W5 |
| `RuntimeSnapshot.viewer_room_id/current_room` | `public_alias_keep` | Yes | No | Yes | Governed by ADR-0069; public alias removal remains blocked |
| `player_shell_state_projection.py::build_player_shell_state_view` | `public_alias_keep` | Yes | No | Yes | Keep `current_room_id` alias until readiness gate proves removal safe |
| `environment_state_contracts.py` movement substrate | `substrate_keep_future_adr` | No | Yes as substrate | Yes | Keep substrate writers/readers for future ADR |
| `ShortTermContext.build scene_changed` | `unrelated_domain_use` | No | Yes | No | Leave out of narrator/sensory W5 cleanup |

**Safe cleanup performed:**

- Updated stale location-framing test wording from additive-only to W5-first
  authority wording.
- Added Phase 6C-4 inventory/report output to
  `scripts/inventory_w5_legacy_consumers.py`.
- Added proof tests for compatibility-field authority, no raw W5 history
  emission, and JSON/human inventory output.

**Cleanup deliberately not performed:**

- No `current_area/from_area/to_area` runtime field removal.
- No `current_room/current_room_id/viewer_room_id` public alias removal.
- No substrate field, `actor_locations`, or
  `complete_actor_locations_for_gathering` removal.
- No malformed-W5 or old-payload fallback removal.
- No committed event or committed output mutation.

**Required evidence before a future removal ADR:**

- Default valid W5 path reports `location_framing_authority="w5"`.
- Missing/malformed W5 reports `location_framing_authority="legacy_fallback"`.
- `local_context_transition_source` reports `w5_location_framing` or `legacy`
  correctly.
- Compatibility fields are proven fallback/compatibility rather than authority
  when W5 is valid.
- No raw W5 history is emitted in narrator/sensory diagnostics.
- How remains first-class and inferred Why remains soft truth.
- MVP03 and MVP04 gates remain green.

**Next removal decision:** no runtime removal is authorized by 6C-4. The next
phase should be targeted doc/test cleanup or a removal-ADR draft only after
fresh parity evidence proves fallback windows can close.

---

### Phase 6C-5 — removal-readiness ADR and targeted cleanup (Complete, 2026-05-30)

**ADR:** [ADR-0071](docs/architecture/components/world-engine/architecture)

Phase 6C-5 creates the removal-readiness ADR for narrator-consequence and
sensory-context legacy area fields. It does not remove runtime fields.

**Covered legacy fields:**

- `current_area`
- `from_area`
- `to_area`
- legacy `local_context_transition` area fields where they are
  compatibility/fallback values
- `scene_changed` / `location_changed` legacy framing where
  `w5_location_framing` already supplies authority

**Out of scope:**

- public `current_room/current_room_id/viewer_room_id` aliases
- `runtime_world.current_room_id`
- `environment_state.current_room_id`
- `actor_locations`
- `complete_actor_locations_for_gathering`
- NPC context bundle fallback
- malformed-W5 fallback
- old-payload fallback
- substrate consolidation

**Removal-readiness checklist:**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| W5 location framing is synthesized in graph state on default path | PASS | Phase 6C-2 graph-owned synthesis in `_resolve_player_action` |
| Narrator consequence uses W5 when valid | PASS | Phase 6C-3 `build_local_context_transition()` authority switch |
| Sensory context uses W5 when valid | PASS | Phase 6C-3 `_current_location_id()` W5-first resolution |
| Malformed/missing W5 fallback remains tested | PASS | Location-framing fallback tests |
| Old payload fallback remains tested | PASS | Old-payload path without `w5_location_framing` keeps legacy transition |
| Parity tests prove output equivalence where W5 and legacy agree | PASS | Narrator/sensory same-location parity tests |
| No production default path depends on legacy area fields as authority | PASS | Phase 6C-4 classifies area fields as compatibility/fallback |
| Docs/tests no longer describe legacy fields as primary | PASS | Phase 6C-4/6C-5 doc/test cleanup |
| Public aliases are unaffected | PASS | ADR-0069 remains owner |
| Substrate fields are unaffected | PASS | Substrate fields remain future-ADR surfaces |
| Downstream consumers can run without area-field presence except via explicit shim | BLOCKED | Transition compatibility fields still feed consequence realization, sensory layers, carried local context, and old-payload fallback |
| Removal rollback plan is implemented and test-backed | BLOCKED | ADR-0071 defines rollback shape; no removal-phase shim test exists yet |

**Result:** `removal_ready=false`.

**Remaining blockers:**

- Compatibility field presence is still required by downstream transition
  consumers.
- Malformed-W5 and old-payload fallback windows remain active.
- No removal-phase compatibility shim has been implemented or tested.
- No production-like runtime trace proves zero dependency on area-field
  presence.

**Targeted cleanup performed:**

- Created Proposed ADR-0071.
- Added Phase 6C-5 removal-readiness checklist to inventory JSON and human
  output.
- Updated docs/tests to state that `current_area/from_area/to_area` are
  fallback/compatibility fields, not authority.

**Cleanup deliberately not performed:**

- No `current_area/from_area/to_area` runtime field removal.
- No malformed-W5 or old-payload fallback removal.
- No public alias or substrate field removal.
- No committed output or committed event mutation.

**Next removal decision:** actual area-field removal is not safe to begin.
Phase 6C-6 should either prove a compatibility shim that makes area-field
presence optional for W5-native consumers, or gather production-like dependency
evidence before a removal phase.

---

### Phase 6C-6 — explicit legacy area compatibility shim (Complete, 2026-05-31)

Phase 6C-6 implements the compatibility shim required by ADR-0071. It does not
remove runtime fields.

**Shim APIs:**

- `w5_location_framing_to_legacy_area_fields()`
- `build_legacy_area_compat_from_w5_location_framing()`
- `ensure_legacy_area_fields_for_compat()`

**Source labels:**

- `w5_location_framing` — valid W5 framing derived the compatibility fields.
- `legacy_fallback` — W5 was missing or incomplete and legacy values were kept.
- `malformed_w5_fallback` — malformed W5 was ignored and legacy values were kept.
- `old_payload_fallback` — no W5 framing field existed on the payload.

**Updated classifications:**

| Classification | Meaning |
|---|---|
| `w5_native_no_area_dependency` | W5-native narrator/sensory path can operate without direct `current_area/from_area/to_area` input |
| `area_compat_shim` | Legacy fields are emitted through the named compatibility shim |
| `legacy_fallback_keep` | Legacy values remain fallback for missing/incomplete W5 |
| `malformed_w5_safety_keep` | Malformed-W5 safety path is retained |
| `old_payload_compat_keep` | Old payloads without `w5_location_framing` remain supported |
| `removal_candidate_needs_final_adr` | Candidate for a future accepted removal phase, not for this phase |
| `public_alias_keep` | Public room aliases remain ADR-0069-owned |
| `substrate_keep_future_adr` | Substrate fields remain future-ADR surfaces |

**Readiness checklist update:**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Downstream narrator/sensory consumers can run without area-field presence except through explicit shim | PASS | Phase 6C-6 W5-native tests run without direct area fields |
| Removal rollback plan is implemented and test-backed | PASS | `ensure_legacy_area_fields_for_compat()` is non-mutating and test-backed |
| ADR-0071 is accepted for actual runtime field removal | BLOCKED | ADR-0071 remains Proposed |
| Production-like downstream trace proves zero unsupported area-field dependency | BLOCKED | Static/unit proof exists; final trace evidence is still pending |

**Still not removed:**

- `current_area`
- `from_area`
- `to_area`
- public `current_room/current_room_id/viewer_room_id` aliases
- substrate fields
- actor-location substrate
- malformed-W5 fallback
- old-payload fallback
- NPC context fallback

**Result:** `removal_ready=false`. The shim makes actual removal closer, but a
future accepted phase must still prove production-like dependency readiness
before deleting runtime fields.

---

### Phase 6C-7 / 6C-8 — dependency evidence and removal-readiness audit (Complete, 2026-05-31)

Phase 6C-7/6C-8 performs the production-like dependency evidence pass requested
by ADR-0071. It does not remove runtime fields.

**Evidence method:**

- Static grep for `current_area`, `from_area`, `to_area`,
  `legacy_area_compat`, `w5_location_framing`, `location_framing_authority`,
  `local_context_transition_source`, `scene_changed`, and `location_changed`.
- Curated runtime-surface review for narrator consequence, sensory context,
  LangGraph SOURCE_LINES, language adapter, semantic content-frame fallback,
  tests, and docs.
- Focused proof tests for W5-native no-area behavior, shimmed compatibility,
  malformed-W5 fallback, old-payload fallback, no raw W5 history, How, and
  inferred Why.

**Dependency classification summary:**

| Classification | Count | Meaning |
|---|---:|---|
| `area_compat_shim` | 1 | Explicit shim derives compatibility area fields |
| `shimmed_compatibility_dependency` | 2 | Runtime emits area fields through the shimmed transition shape |
| `malformed_w5_safety_dependency` | 2 | Legacy fields still protect malformed-W5 fallback |
| `old_payload_compat_dependency` | 1 | Legacy fields still protect old payloads |
| `w5_native_no_area_dependency` | 1 | W5-native path does not need direct area fields |
| `blocker_requires_refactor` | 2 | Removal requires a dedicated refactor first |
| `public_or_substrate_out_of_scope` | 1 | Outside ADR-0071 removal scope |
| `test_only_legacy_dependency` | 1 | Test-only guard |
| `doc_only_legacy_dependency` | 1 | Documentation only |

**Blocking runtime dependencies:**

| Surface | Classification | Why removal is blocked |
|---|---|---|
| `build_updated_player_local_context()` | `blocker_requires_refactor` | Carries `current_area/current_location_id/previous_area` between turns from `to_area` |
| `_current_context_area()` | `malformed_w5_safety_dependency` | Needs legacy fallback when W5 is missing/malformed or old payloads arrive |
| `sensory_context_engine._current_location_id()` | `old_payload_compat_dependency` | Uses `to_area/current_area/from_area` after W5 for sensory old-payload fallback |
| LangGraph `_resolve_player_action` | `malformed_w5_safety_dependency` | Builds legacy fallback from player local context / environment state |
| `language_adapter._interaction_surface_cached()` | `blocker_requires_refactor` | Still exposes content-derived `current_area` outside the shim |
| semantic content-frame fallback | `public_or_substrate_out_of_scope` | Reads `environment_state.current_area/current_room_id`; future planner/substrate ADR |

**Narrow safe scope:**

- W5-native narrator/sensory consumers can run without direct
  `current_area/from_area/to_area` input when valid `w5_location_framing` is
  present.
- Legacy compatibility consumers can receive area fields through
  `legacy_area_compat.v1`.

**Result:** `removal_ready=false`.

**Safe cleanup performed:**

- Added Phase 6C-7/8 dependency-evidence inventory and report output.
- Updated ADR-0071 readiness with exact remaining blockers.
- Kept compatibility fields, fallbacks, public aliases, substrate fields,
  committed events, and committed output unchanged.

**Next recommended work package:**

Phase 6C-9 should add a W5-native carried-local-context helper, design a
language-adapter runtime overlay that does not poison cached authored content,
and rerun this dependency evidence before any accepted runtime field removal.
