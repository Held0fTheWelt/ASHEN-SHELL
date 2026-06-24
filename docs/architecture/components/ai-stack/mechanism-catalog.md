# ai-stack Mechanism Catalog

**Owner:** [ai-stack SAD](architecture.md)
**Status:** mixed mechanism catalog
**Last reconciled:** 2026-06-23

| ID | Mechanism | Definition | Normative sources | UML / evidence | Proof state |
| --- | --- | --- | --- | --- | --- |
| AI-M01 | Proposal-only graph | LangGraph stages emit proposals; world-engine validates and commits. | [SAD D1](architecture.md#d1-proposal-only-outputs) | [primary sequence](../../../../UML/Components/ai-stack/sequence/ai-stack-primary-turn-sequence.md) | Implemented |
| AI-M02 | Quality lab MCP diagnostics | Read-only MCP layer analyzes runtime, judge, and Langfuse evidence. | [SAD D2](architecture.md#d2-quality-lab-mcp-runtime-diagnostics-and-judge-guided-improvement) | [C4 context](../../../../UML/Components/ai-stack/components/c4-context.md) | Partial |
| AI-M03 | RAG context fabric | Routes retrieval domains with authority boundaries per mode. | [SAD D3](architecture.md#d3-runtime-rag-context-fabric-routing-and-authority-boundaries) | [d3 decision](../../../../UML/Components/ai-stack/decisions/d3-rag-fabric.md) | Implemented |
| AI-M04 | Memory indexes | Retrieval write contracts for runtime memory surfaces. | [SAD D4](architecture.md#d4-runtime-memory-indexes-and-retrieval-write-contracts) | [d4 decision](../../../../UML/Components/ai-stack/decisions/d4-memory-indexes.md) | Partial |
| AI-M05 | Director thin path | Resolver → Director → narrator for default realization. | [SAD D5](architecture.md#d5-director-thin-path-realization) | [world-engine D4](../world-engine/architecture.md#9-architecture-decisions) | Implemented |
| AI-M06 | Semantic scene planner | Bounded planner projects scene intent without commit authority. | [SAD D6](architecture.md#d6-bounded-semantic-scene-planner) | [evidence matrix](evidence-matrix.md) | Partial |
| AI-M07 | Souffleuse lanes | Inner-voice composition with voice-profile discipline. | [SAD D7](architecture.md#d7-souffleuse-inner-voice-composition) | [d7 decision](../../../../UML/Components/ai-stack/decisions/d7-souffleuse.md) | Partial |
| AI-M08 | Role-aware decision log | Canonical `parsed_decision` in `AIDecisionLog`. | [SAD D8](architecture.md#d8-role-aware-aidecisionlog-and-parsedroleawaredecision) | `backend/tests/runtime/test_ai_decision_logging.py` | Implemented |
| AI-M09 | ProposalSource gating | Responder-only enforcement via `ProposalSource` enum. | [SAD D9](architecture.md#d9-proposalsource-enum-and-responder-only-gating) | `backend/tests/runtime/test_responder_gating.py` | Implemented |
| AI-M10 | Research draft-only | Research may draft change, never publish canon directly. | [SAD D10](architecture.md#d10-research-may-draft-change-but-may-not-publish-change) | [evidence matrix](evidence-matrix.md) | Implemented |
| AI-M11 | Meta-narrative aspects | Opt-in and adaptive meta-awareness runtime aspects. | [SAD D13](architecture.md#d13-opt-in-meta-narrative-awareness-runtime-aspect), [D14](architecture.md#d14-adaptive-meta-narrative-awareness-and-fourth-wall-play) | [d14 decision](../../../../UML/Components/ai-stack/decisions/d14-adaptive-meta-narrative.md) | Partial |
| AI-M12 | Capability authority | Semantic capability selection and validator dispatch sidecar. | [SAD D12](architecture.md#d12-controlled-runtime-capability-authority) | `ai_stack/tests/test_capability_selector.py` | Partial |
| AI-M13 | Director pulse bus | Shadow/dual-mode block stream and NPC motivation scoring. | [SAD D16](architecture.md#d16-director-driven-pulse-and-block-stream-bus) | [d16 decision](../../../../UML/Components/ai-stack/decisions/d16-director-pulse-block-stream.md) | Implemented |
| AI-M14 | Director gathering pause | Gathering waits while player remains free during co-presence breaks. | [SAD D15](architecture.md#d15-director-pause-mode-for-gathering-interruption) | [d15 decision](../../../../UML/Components/ai-stack/decisions/d15-director-pause.md) | Proposed |
