# MVP3 Handoff — Live Dramatic Scene Simulator

**From**: MVP 3 — Live Dramatic Scene Simulator  
**To**: MVP 4 — Diagnostics, Narrative Gov, Langfuse  
**Date**: 2026-04-25

---

## Live Turn Contract

### SceneTurnEnvelope.v2

Added to every `execute_turn` result for God of Carnage solo sessions:

```json
{
  "contract": "scene_turn_envelope.v2",
  "content_module_id": "god_of_carnage",
  "runtime_profile_id": "god_of_carnage_solo",
  "runtime_module_id": "solo_story_runtime",
  "selected_player_role": "annette",
  "human_actor_id": "annette",
  "npc_actor_ids": ["alain", "veronique", "michel"],
  "visible_scene_output": {
    "contract": "visible_scene_output.blocks.v1",
    "blocks": [...]
  },
  "diagnostics": {
    "live_dramatic_scene_simulator": {
      "status": "evidenced_live_path",
      "invoked": true,
      "entrypoint": "story.turn.execute",
      "decision_count": 3,
      "output_contract": "visible_scene_output.blocks.v1",
      "scene_block_count": 3,
      "visible_actor_response_present": true,
      "legacy_blob_used": false,
      "story_session_id": "<uuid>",
      "turn_number": 1,
      "input_hash": "sha256:mock-<16-hex>",
      "output_hash": "sha256:mock-<16-hex>"
    },
    "npc_agency": {
      "primary_responder_id": "veronique",
      "secondary_responder_ids": ["alain"],
      "visible_actor_response_present": true,
      "npc_agency_plan_count": 1
    },
    "actor_lane_enforcement": {
      "human_actor_id": "annette",
      "ai_allowed_actor_ids": ["alain", "michel", "veronique"],
      "ai_forbidden_actor_ids": ["annette"],
      "validation_ran_before_commit": true
    }
  }
}
```

---

## Runtime State Provenance

- `human_actor_id` and `npc_actor_ids` read from `session.runtime_projection` (set at session creation)
- `_extract_actor_lane_context` in `StoryRuntimeManager` extracts the lane context
- LDSS is called in `_finalize_committed_turn` AFTER validation and commit

---

## AI Proposal Shape

MVP3 uses **deterministic mock output** via `build_deterministic_ldss_output()` in `ai_stack/live_dramatic_scene_simulator.py`.

The mock always produces:
1. One narrator block (inner perception, non-dialogue-recap)
2. One primary NPC actor_line
3. One secondary NPC actor_action (when 2+ NPCs)

MVP4 can replace the mock with a real LangGraph node by:
1. Implementing a real LDSS generation node in `ai_stack/`
2. Passing the LDSSInput to it
3. Replacing the `build_deterministic_ldss_output()` call in `run_ldss()` with the real AI call

---

## Validated Committed Result Shape

The `scene_turn_envelope` key in the execute_turn response contains the full `SceneTurnEnvelopeV2`.

Key fields for MVP4:
- `diagnostics.live_dramatic_scene_simulator.status` → `"evidenced_live_path"`
- `diagnostics.live_dramatic_scene_simulator.invoked` → `true`
- `visible_scene_output.blocks` → typed blocks for frontend rendering

---

## NPC Initiative Behavior

- Primary responder: first available NPC in priority order (veronique → alain → michel)
- Secondary responder: next available NPC
- NPCs can act without being directly addressed
- NPCs can reference each other (NPC-to-NPC via target_actor_id)
- Human actor never appears as actor_id in any block

---

## Actor-Lane Enforcement Behavior

- `validate_actor_lane_blocks()` runs before commit, before response packaging
- `validate_visitor_absent_from_blocks()` runs before commit
- `validate_dramatic_mass()` runs before commit
- `validate_passivity()` runs before commit
- All validators are in `ai_stack/live_dramatic_scene_simulator.py`
- Engine-level `validate_actor_lane_output()` from `world-engine/app/runtime/actor_lane.py` is the MVP2 seam

---

## Dramatic Validation Behavior

- `validate_dramatic_mass()`: requires at least 1 `actor_line`/`actor_action`/`environment_interaction` with `actor_id`
- `validate_passivity()`: equivalent check — passivity guard
- `validate_narrator_voice()`: rejects dialogue_summary, forced_player_state, hidden_npc_intent

---

## Fallback Behavior

- `build_deterministic_ldss_output()` is the fallback/mock for all non-AI turns
- If proposal fails validation: `_build_rejected_ldss_output()` returns `system_degraded_notice` block
- Fallback never commits illegal state

---

## API Response Shape

HTTP endpoint: `POST /api/story/sessions/{session_id}/turns`  
Response: `{"session_id": str, "turn": {... existing fields ..., "scene_turn_envelope": SceneTurnEnvelope.v2}}`

---

## Source / Test Evidence Paths

| Evidence | Path |
|---|---|
| LDSS module | `ai_stack/live_dramatic_scene_simulator.py` |
| Manager integration | `world-engine/app/story_runtime/manager.py:_build_ldss_scene_envelope` |
| Gate tests | `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` |
| Integration tests | `world-engine/tests/test_mvp3_ldss_integration.py` |
| Source locator | `tests/reports/MVP_Live_Runtime_Completion/MVP3_SOURCE_LOCATOR.md` |
| Operational evidence | `tests/reports/MVP_Live_Runtime_Completion/MVP3_OPERATIONAL_EVIDENCE.md` |

---

## Known Limitations

1. **Deterministic mock only**: MVP3 uses a rule-based mock for LDSS generation. Real AI-driven NPC dialogue requires MVP4 wiring.
2. **Object admission**: Affordance validation is implemented but admitted_objects list is currently empty for most sessions. MVP4 can populate this from canonical content.
3. **Narrator validator**: Regex-based pattern matching. Sufficient for tests; MVP4 can strengthen with semantic validation.
4. **ADRs not written**: ADR-011, ADR-012, ADR-013 not yet created (documentation-only, does not block MVP4 implementation).

---

## Safe Assumptions for MVP 4 / MVP 5

- `scene_turn_envelope` is always present in `execute_turn` result for GoC solo sessions
- `diagnostics.live_dramatic_scene_simulator.status == "evidenced_live_path"` when LDSS ran
- `visible_scene_output.blocks` is typed and non-empty for valid turns
- `human_actor_id` is never in any block's `actor_id` field
- `visitor` never appears in any block
- `actor_lane_enforcement.validation_ran_before_commit == true` always
