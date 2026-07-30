# AI Stack — Proposal Pipeline Components

**Viewpoint:** `component`
**Concern:** Internal responsibilities and contracts on the canonical proposal path

[PlantUML source](c4-component.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| LangGraph Runtime Executor | Coordinate the proposal pipeline | Prepared state in; proposal package out | [`ai_stack/langgraph/runtime_executor/public.py`](../../../../ai_stack/langgraph/runtime_executor/public.py) |
| Semantic Input Translation | Translate player text into bounded intent evidence | Semantic input record without invented state | [`ai_stack/langgraph/runtime_executor/semantic_input_translation.py`](../../../../ai_stack/langgraph/runtime_executor/semantic_input_translation.py) |
| RAG Context Fabric | Assemble governed continuity and knowledge context | Bounded context pack with provenance | [`ai_stack/rag/rag_context_pack_build.py`](../../../../ai_stack/rag/rag_context_pack_build.py) |
| Director | Select dramatic direction and capability plan | Scene plan and ordered actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |
| Capability Registry | Select allowed runtime capabilities | Evidence-gated capability plan | [`ai_stack/capabilities/capability_selector.py`](../../../../ai_stack/capabilities/capability_selector.py) |
| Narrator | Realize visible narrative blocks | Proposal-only block stream | [`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`](../../../../ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py) |
| Proposal Validator | Evaluate seams, capabilities and retry feedback | Accepted proposal or actionable rejection | [`ai_stack/langgraph/validation/builder.py`](../../../../ai_stack/langgraph/validation/builder.py) |
| Runtime Aspect Ledger | Project aspect evidence and decision metadata | Typed, non-authoritative evidence records | [`ai_stack/story_runtime/runtime_aspect_ledger/records.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/records.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| LangGraph Runtime Executor | Semantic Input Translation | interprets input | semantic intent envelope | [`ai_stack/langgraph/runtime_executor/executor_input_interpretation_semantics.py`](../../../../ai_stack/langgraph/runtime_executor/executor_input_interpretation_semantics.py) |
| Semantic Input Translation | RAG Context Fabric | queries grounded context | bounded retrieval query | [`ai_stack/langgraph/runtime_executor/executor_model_context_retrieval.py`](../../../../ai_stack/langgraph/runtime_executor/executor_model_context_retrieval.py) |
| RAG Context Fabric | Director | provides context pack | citations and continuity facts | [`ai_stack/langgraph/runtime_executor/executor_director_selection_context.py`](../../../../ai_stack/langgraph/runtime_executor/executor_director_selection_context.py) |
| Director | Capability Registry | requests capability plan | evidence-gated selection | [`ai_stack/langgraph/runtime_executor/executor_realization_capabilities.py`](../../../../ai_stack/langgraph/runtime_executor/executor_realization_capabilities.py) |
| Director | Narrator | requests realization | scene plan and actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |
| Narrator | Proposal Validator | submits proposal | visible blocks plus proposed delta | [`ai_stack/langgraph/runtime_executor/executor_validation_commit.py`](../../../../ai_stack/langgraph/runtime_executor/executor_validation_commit.py) |
| Proposal Validator | Runtime Aspect Ledger | records validation evidence | typed aspect status | [`ai_stack/langgraph/validation/result.py`](../../../../ai_stack/langgraph/validation/result.py) |
| Runtime Aspect Ledger | LangGraph Runtime Executor | returns evidence projection | proposal package metadata | [`ai_stack/story_runtime/runtime_aspect_ledger/runtime_intelligence_projection/builder.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/runtime_intelligence_projection/builder.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
