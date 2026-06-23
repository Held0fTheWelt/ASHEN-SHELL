# turn-execution-canonical TRACEABILITY

| Diagram | Claim | Source | Test / gate |
| --- | --- | --- | --- |
| c4-context | Ingress → commit → project | `turn_execution_contract.md` | GoC contract tests |
| c4-container | world-engine owns commit | world-engine SAD D1 | foundation gate |
| canonical sequence | Single turn path | `StoryRuntimeManager.execute_turn` | `test_story_runtime_api.py` |
| ADR-0038 | Open exception for full single-path | world-engine SAD D5 | ROLLOUT |
