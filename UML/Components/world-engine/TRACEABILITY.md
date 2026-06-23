# world-engine TRACEABILITY

| Diagram | Claim | Source | Test / gate |
| --- | --- | --- | --- |
| c4-context | Backend proxies play to world-engine | `backend/app/services/game/game_service.py` | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` |
| c4-container | Dual managers in one app | `world-engine/app/main.py` | `world-engine/tests/test_story_runtime_api.py` |
| c4-component | validate → commit seams | `ai_stack/story_runtime/god_of_carnage/god_of_carnage_turn_seams.py` | GoC integration tests |
| primary sequence | execute_turn orchestration | `world-engine/app/story_runtime/manager/` | `world-engine/tests/test_story_runtime_api.py` |
| degraded sequence | live_success gate | `ai_stack/story_runtime/live_runtime_commit_semantics.py` | `tests/gates/test_adr_live_runtime_commit_semantics_gate.py` |
| session states | StorySession lifecycle | `world-engine/app/story_runtime/manager/` | `world-engine/tests/test_story_runtime_runtime_world.py` |
