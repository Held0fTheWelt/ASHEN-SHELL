# world-engine Evidence Matrix

**Owner:** [world-engine SAD](architecture.md) · [Mechanism catalog](mechanism-catalog.md)
**Last reconciled:** 2026-06-23

| Mechanism ID | Claim | Source | Test / gate | Proof state |
| --- | --- | --- | --- | --- |
| WE-M01 | Backend proxies play; engine owns commit | `world-engine/app/story_runtime/manager/` | `world-engine/tests/test_story_runtime_api.py` | Implemented |
| WE-M02 | Validator blocks unapproved proposals | `ai_stack/story_runtime/god_of_carnage/god_of_carnage_turn_seams.py` | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` | Implemented |
| WE-M03 | Degraded adapters set `live_success=false` | `ai_stack/story_runtime/live_runtime_commit_semantics.py` | `tests/gates/test_adr_live_runtime_commit_semantics_gate.py` | Implemented |
| WE-M04 | Thin path realization for default turns | `ai_stack/story_runtime/director/` | `world-engine/tests/test_story_runtime_api.py` | Implemented |
| WE-M05 | Single persist path per turn | `world-engine/app/story_runtime/manager/` | `tests/gates/test_canonical_turn_lifecycle_gate.py` | Partial |
| WE-M08 | Preview stores isolated from live sessions | `world-engine/app/story_runtime/manager/` | `world-engine/tests/test_preview_session_isolation.py` | Implemented |
| WE-M10 | Semantic ingress before structural guards | `world-engine/app/story_runtime/` | `tests/gates/test_adr0055_semantic_ingress_gate.py` | Partial |
| WE-M11 | Actor tracking projection on ledger | `ai_stack/story_runtime/runtime_aspect_ledger/` | `tests/gates/test_adr_0039_pi_scope.py` | Partial |
