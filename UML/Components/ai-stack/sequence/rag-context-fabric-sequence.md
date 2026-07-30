# AI Stack — RAG Context Fabric

**Viewpoint:** `sequence`
**Concern:** How a runtime query becomes a bounded provenance-preserving context pack

[PlantUML source](rag-context-fabric-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| LangGraph Runtime Executor | Coordinate the proposal pipeline | Prepared state in; proposal package out | [`ai_stack/langgraph/runtime_executor/public.py`](../../../../ai_stack/langgraph/runtime_executor/public.py) |
| Semantic Input Translation | Translate player text into bounded intent evidence | Semantic input record without invented state | [`ai_stack/langgraph/runtime_executor/semantic_input_translation.py`](../../../../ai_stack/langgraph/runtime_executor/semantic_input_translation.py) |
| RAG Context Fabric | Assemble governed continuity and knowledge context | Bounded context pack with provenance | [`ai_stack/rag/rag_context_pack_build.py`](../../../../ai_stack/rag/rag_context_pack_build.py) |
| RetrievalContextBundle | Carry bounded retrieval results | Provenance-preserving ranked context | [`ai_stack/rag/retrieval_context_bundles.py`](../../../../ai_stack/rag/retrieval_context_bundles.py) |
| Director | Select dramatic direction and capability plan | Scene plan and ordered actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| LangGraph Runtime Executor | Semantic Input Translation | interprets input | semantic intent envelope | [`ai_stack/langgraph/runtime_executor/executor_input_interpretation_semantics.py`](../../../../ai_stack/langgraph/runtime_executor/executor_input_interpretation_semantics.py) |
| Semantic Input Translation | RAG Context Fabric | queries grounded context | bounded retrieval query | [`ai_stack/langgraph/runtime_executor/executor_model_context_retrieval.py`](../../../../ai_stack/langgraph/runtime_executor/executor_model_context_retrieval.py) |
| RAG Context Fabric | RetrievalContextBundle | builds | ranked and budgeted context | [`ai_stack/rag/rag_context_pack_assembler.py`](../../../../ai_stack/rag/rag_context_pack_assembler.py) |
| RAG Context Fabric | Director | provides context pack | citations and continuity facts | [`ai_stack/langgraph/runtime_executor/executor_director_selection_context.py`](../../../../ai_stack/langgraph/runtime_executor/executor_director_selection_context.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
