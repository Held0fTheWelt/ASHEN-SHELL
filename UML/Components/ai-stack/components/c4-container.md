# AI Stack — Runtime Containers

**Viewpoint:** `container`
**Concern:** Major execution, retrieval, planning, validation and evidence seams

[PlantUML source](c4-container.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| LangGraph Runtime Executor | Coordinate the proposal pipeline | Prepared state in; proposal package out | [`ai_stack/langgraph/runtime_executor/public.py`](../../../../ai_stack/langgraph/runtime_executor/public.py) |
| Semantic Input Translation | Normalize player text to the module-declared internal language and preserve provenance | Neutral semantic input; English alias only for English compatibility envelopes | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| RAG Context Fabric | Assemble governed continuity and knowledge context | Bounded context pack with provenance | [`ai_stack/rag/rag_context_pack_build.py`](../../../../ai_stack/rag/rag_context_pack_build.py) |
| Director | Select dramatic direction and capability plan | Scene plan and ordered actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |
| Narrator | Realize visible narrative blocks | Proposal-only block stream | [`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`](../../../../ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py) |
| Proposal Validator | Evaluate seams, capabilities and retry feedback | Accepted proposal or actionable rejection | [`ai_stack/langgraph/validation/builder.py`](../../../../ai_stack/langgraph/validation/builder.py) |
| Runtime Aspect Ledger | Project aspect evidence and decision metadata | Typed, non-authoritative evidence records | [`ai_stack/story_runtime/runtime_aspect_ledger/records.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/records.py) |
| Quality Lab | Score traces and narrative output | Evaluation evidence, never runtime authority | [`ai_stack/quality_lab/evaluation_pipeline.py`](../../../../ai_stack/quality_lab/evaluation_pipeline.py) |
| Research Lane | Explore and draft bounded canon improvements | Draft-only findings; cannot publish canon | [`ai_stack/research/canon_improvement_engine.py`](../../../../ai_stack/research/canon_improvement_engine.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Semantic Input Translation | RAG Context Fabric | queries grounded context | bounded retrieval query | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| RAG Context Fabric | Director | provides context pack | citations and continuity facts | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| Director | Narrator | requests realization | scene plan and actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |
| Narrator | Proposal Validator | submits proposal | visible blocks plus proposed delta | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| Proposal Validator | Runtime Aspect Ledger | records validation evidence | typed aspect status | [`ai_stack/langgraph/validation/result.py`](../../../../ai_stack/langgraph/validation/result.py) |
| Runtime Aspect Ledger | LangGraph Runtime Executor | returns evidence projection | proposal package metadata | [`ai_stack/story_runtime/runtime_aspect_ledger/runtime_intelligence_projection/builder.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/runtime_intelligence_projection/builder.py) |
| Quality Lab | Runtime Aspect Ledger | reads trace aspects | evaluation-only projection | [`ai_stack/quality_lab/trace_interpreter.py`](../../../../ai_stack/quality_lab/trace_interpreter.py) |
| Research Lane | Quality Lab | uses evaluation evidence | draft improvement finding | [`ai_stack/research/research_validation.py`](../../../../ai_stack/research/research_validation.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
