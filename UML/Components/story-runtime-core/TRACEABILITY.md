# story-runtime-core TRACEABILITY

| Diagram | Decision | Claim | Source | Test / gate |
| --- | --- | --- | --- | --- |
| c4-context | D1 | Shared runtime types | see component SAD | `story_runtime_core/tests/` |
| c4-container | D1 | Branching, templates, delivery helpers | `story_runtime_core/` | `story_runtime_core/tests/` |
| d2-turn-envelope | D2 | Turn envelope (partial; contracts in ai_stack) | mechanism catalog SR-M02 | `tests/gates/` (partial) |
| d3-aspect-ledger-contracts | D3 | Aspect ledger vocabulary | mechanism catalog SR-M03 | `tests/gates/` (partial) |
| d4-language-adapter-compat-seam | D4 | Language shim → ai_stack.language_io | SAD D2 | `story_runtime_core/tests/test_language_adapter.py` |
| language-resolution-chain | D4 | Ingress/egress language chain vs executor | world-engine D10/D14 | `ai_stack/tests/test_langgraph_runtime.py` |
| story-runtime-core-shared-import-sequence | D1 | Import-only; no commit authority | SAD §3 | `tests/gates/` |
