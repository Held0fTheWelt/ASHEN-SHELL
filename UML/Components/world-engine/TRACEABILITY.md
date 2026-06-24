# world-engine TRACEABILITY

| Diagram | Decision | Claim | Source | Test / gate |
| --- | --- | --- | --- | --- |
| c4-context | D1 | Backend proxies play to world-engine | `backend/app/services/game/game_service.py` | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` |
| c4-container | D1 | Dual managers in one app | `world-engine/app/main.py` | `world-engine/tests/test_story_runtime_api.py` |
| c4-component | D2, D5 | validate → commit seams | `ai_stack/story_runtime/god_of_carnage/god_of_carnage_turn_seams.py` | GoC integration tests |
| primary sequence | D4, D5 | execute_turn orchestration | `world-engine/app/story_runtime/manager/` | `world-engine/tests/test_story_runtime_api.py` |
| degraded sequence | D3 | live_success gate | `ai_stack/story_runtime/live_runtime_commit_semantics.py` | `tests/gates/test_adr_live_runtime_commit_semantics_gate.py` |
| session states | D7 | StorySession lifecycle | `world-engine/app/story_runtime/manager/` | `world-engine/tests/test_story_runtime_runtime_world.py` |
| d6-w5-actor-tracking | D6 | W5 actor topology projection | `ai_stack/story_runtime/runtime_aspect_ledger/` | `tests/gates/test_adr_0039_pi_scope.py` |
| d14-semantic-input-ingress | D14 | Semantic translation ingress | `world-engine/app/story_runtime/` | `tests/gates/test_adr0055_semantic_ingress_gate.py` |
