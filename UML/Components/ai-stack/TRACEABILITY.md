# ai-stack TRACEABILITY

| Diagram | Claim | Source | Test / gate |
| --- | --- | --- | --- |
| c4-context | In-process from world-engine only | `world-engine/app/story_runtime/manager/` | `test_goc_mvp01_mvp02_foundation_gate.py` |
| c4-container | Graph executor + GoC seams | `ai_stack/langgraph/langgraph_runtime.py` | `ai_stack/tests/` |
| primary sequence | Proposal → validate seam | `god_of_carnage_turn_seams.py` | GoC integration tests |
| SAD D1 | Proposal-only outputs | ai-stack SAD §9 D1 | ADR-0004 gate paths |
| SAD D5 | Director thin path | `director_realization_composer.py` | ADR-0062 tests |
