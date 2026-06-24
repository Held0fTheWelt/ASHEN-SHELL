# ai-stack TRACEABILITY

| Diagram | Decision | Claim | Source | Test / gate |
| --- | --- | --- | --- | --- |
| c4-context | D1 | Proposal-only boundary to world-engine | `ai_stack/langgraph/langgraph_runtime.py` | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` |
| c4-container | D3, D4 | RAG and memory fabric blocks | `ai_stack/rag/` | `ai_stack/tests/` |
| primary sequence | D5, D7 | Turn graph orchestration | `ai_stack/langgraph/` | `tests/gates/test_goc_mvp03_*` |
| d12-capability-authority | D12 | Capability selection projection | `ai_stack/capabilities/capability_selector.py` | `ai_stack/tests/test_capability_selector.py` |
| d16-director-pulse | D16 | Block stream parity | `ai_stack/story_runtime/director/` | `tests/gates/test_phase2_block_stream_gate.py` |
