# MVP Completion - Capability Chain

**Viewpoint:** `component`
**Concern:** Launch, semantics, agency, commit, rendering and evidence must all connect

[PlantUML source](capability-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Experience Launch | Bind module, role, run and session | Correct experience identity | [`frontend/static/play_session_start.js`](../../../../frontend/static/play_session_start.js) |
| Player Semantics | Preserve free player intent beyond canned choices | Semantic action intent | [`ai_stack/story_runtime/player_action_resolution.py`](../../../../ai_stack/story_runtime/player_action_resolution.py) |
| NPC Agency | Produce motivated autonomous reactions | Character knowledge and goal bounds | [`ai_stack/story_runtime/npc_agency/npc_agency_planner.py`](../../../../ai_stack/story_runtime/npc_agency/npc_agency_planner.py) |
| Authoritative Commit | Apply accepted dramatic outcome to live truth | World-engine-only commit | [`world-engine/world_engine/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/world_engine/story_runtime/narrative_commit_resolution.py) |
| Player Rendering | Expose speaker, action and dramatic blocks | Committed typed blocks | [`frontend/static/play_block_renderer.js`](../../../../frontend/static/play_block_renderer.js) |
| Operational Evidence | Prove the same path through tests and trace artifacts | Reproducible source-located evidence | [`tests/reports/MVP_Live_Runtime_Completion/MVP5_OPERATIONAL_EVIDENCE.md`](../../../../tests/reports/MVP_Live_Runtime_Completion/MVP5_OPERATIONAL_EVIDENCE.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Experience Launch | Player Semantics | opens interaction | bound role and session | [`frontend/static/play_session_start.js`](../../../../frontend/static/play_session_start.js) |
| Player Semantics | NPC Agency | triggers dramatic response | interpreted intent and context | [`ai_stack/story_runtime/player_action_resolution.py`](../../../../ai_stack/story_runtime/player_action_resolution.py) |
| NPC Agency | Authoritative Commit | proposes outcome | uncommitted candidate | [`world-engine/world_engine/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/world_engine/story_runtime/governed_runtime_adapters.py) |
| Authoritative Commit | Player Rendering | publishes blocks | accepted result only | [`world-engine/world_engine/api/story_ws.py`](../../../../world-engine/world_engine/api/story_ws.py) |
| Player Rendering | Operational Evidence | is proven by | observable assertion and trace | [`tests/e2e/test_final_goc_annette_alain_e2e.py`](../../../../tests/e2e/test_final_goc_annette_alain_e2e.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
