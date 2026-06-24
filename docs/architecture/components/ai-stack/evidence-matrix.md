# ai-stack Evidence Matrix

**Owner:** [ai-stack SAD](architecture.md) · [Mechanism catalog](mechanism-catalog.md)
**Last reconciled:** 2026-06-23

| Mechanism ID | Claim | Source | Test / gate | Proof state |
| --- | --- | --- | --- | --- |
| AI-M01 | Graph does not commit canon directly | `ai_stack/story_runtime/god_of_carnage/god_of_carnage_turn_seams.py` | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` | Implemented |
| AI-M08 | Role-aware logging canonicalizes parsed_decision | `backend/app/runtime/ai/ai_decision_logging.py` | `backend/tests/runtime/test_ai_decision_logging.py` | Implemented |
| AI-M09 | Non-responder proposals rejected when enforced | `ai_stack/langgraph/` | `backend/tests/runtime/test_responder_gating.py` | Implemented |
| AI-M12 | Capability selector runs locally | `ai_stack/capabilities/capability_selector.py` | `ai_stack/tests/test_capability_selector.py` | Partial |
| AI-M13 | Pulse dual-mode emits stream events | `ai_stack/story_runtime/director/` | `tests/gates/test_phase2_block_stream_gate.py` | Partial |
