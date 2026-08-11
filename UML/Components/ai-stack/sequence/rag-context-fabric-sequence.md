# AI Stack — RAG Context Fabric

**Viewpoint:** `sequence`
**Concern:** How a runtime query becomes a bounded provenance-preserving context pack

[PlantUML source](rag-context-fabric-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| LangGraph Runtime Executor | Coordinate the proposal pipeline | Prepared state in; proposal package out | [`ai_stack/langgraph/runtime_executor/public.py`](../../../../ai_stack/langgraph/runtime_executor/public.py) |
| Semantic Input Translation | Normalize player text to the module-declared internal language and preserve provenance | Neutral semantic input; English alias only for English compatibility envelopes | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| SemanticInputRecord | Carry raw input, neutral internal normalization and language provenance | normalized_internal_text is primary; compatibility alias is language-gated | [`ai_stack/contracts/action_resolution_contracts.py`](../../../../ai_stack/contracts/action_resolution_contracts.py) |
| RAG Context Fabric | Assemble governed continuity and knowledge context | Bounded context pack with provenance | [`ai_stack/rag/rag_context_pack_build.py`](../../../../ai_stack/rag/rag_context_pack_build.py) |
| RetrievalContextBundle | Carry bounded retrieval results | Provenance-preserving ranked context | [`ai_stack/rag/retrieval_context_bundles.py`](../../../../ai_stack/rag/retrieval_context_bundles.py) |
| Director | Select dramatic direction and capability plan | Scene plan and ordered actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| LangGraph Runtime Executor | Semantic Input Translation | interprets input | semantic intent envelope | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| Semantic Input Translation | SemanticInputRecord | emits neutral input record | module-declared internal language and source provenance | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| SemanticInputRecord | RAG Context Fabric | keys grounded retrieval | neutral internal query with raw-input provenance | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| RAG Context Fabric | RetrievalContextBundle | builds | ranked and budgeted context | [`ai_stack/rag/rag_context_pack_assembler.py`](../../../../ai_stack/rag/rag_context_pack_assembler.py) |
| RetrievalContextBundle | Director | supplies bounded context | ranked citations and continuity facts | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
