# AI Stack — Runtime Proposal Data Model

**Viewpoint:** `class`
**Concern:** Data contracts carried between retrieval, planning, realization and validation

[PlantUML source](runtime-proposal-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Semantic Input Translation | Normalize player text to the module-declared internal language and preserve provenance | Neutral semantic input; English alias only for English compatibility envelopes | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| SemanticInputRecord | Carry raw input, neutral internal normalization and language provenance | normalized_internal_text is primary; compatibility alias is language-gated | [`ai_stack/contracts/action_resolution_contracts.py`](../../../../ai_stack/contracts/action_resolution_contracts.py) |
| RAG Context Fabric | Assemble governed continuity and knowledge context | Bounded context pack with provenance | [`ai_stack/rag/rag_context_pack_build.py`](../../../../ai_stack/rag/rag_context_pack_build.py) |
| Director | Select dramatic direction and capability plan | Scene plan and ordered actor directives | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |
| Narrator | Realize visible narrative blocks | Proposal-only block stream | [`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`](../../../../ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py) |
| Proposal Validator | Evaluate seams, capabilities and retry feedback | Accepted proposal or actionable rejection | [`ai_stack/langgraph/validation/builder.py`](../../../../ai_stack/langgraph/validation/builder.py) |
| Runtime Aspect Ledger | Project aspect evidence and decision metadata | Typed, non-authoritative evidence records | [`ai_stack/story_runtime/runtime_aspect_ledger/records.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/records.py) |
| RetrievalContextBundle | Carry bounded retrieval results | Provenance-preserving ranked context | [`ai_stack/rag/retrieval_context_bundles.py`](../../../../ai_stack/rag/retrieval_context_bundles.py) |
| SemanticScenePlan | Carry intended scene target, beats and directives | Immutable proposal structure | [`ai_stack/story_runtime/semantic_planner/semantic_scene_plan/__init__.py`](../../../../ai_stack/story_runtime/semantic_planner/semantic_scene_plan/__init__.py) |
| NarrativeMoveProposal | Expose the advisory dramatic move and its relation to the reference arc | Non-authoritative proposal; World Engine remains the state writer | [`ai_stack/story_runtime/semantic_planner/semantic_scene_plan/narrative_move.py`](../../../../ai_stack/story_runtime/semantic_planner/semantic_scene_plan/narrative_move.py) |
| Runtime Proposal | Carry visible blocks and state-delta proposal | Must pass world-engine validation before commit | [`ai_stack/langgraph/langgraph_runtime_package_output.py`](../../../../ai_stack/langgraph/langgraph_runtime_package_output.py) |
| RuntimeAspectRecord | Carry one grounded runtime aspect | Typed source, status and evidence | [`ai_stack/story_runtime/runtime_aspect_ledger/records.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/records.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Semantic Input Translation | SemanticInputRecord | emits neutral input record | module-declared internal language and source provenance | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| SemanticInputRecord | RAG Context Fabric | keys grounded retrieval | neutral internal query with raw-input provenance | [`ai_stack/langgraph/langgraph_runtime_executor_impl.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor_impl.py) |
| RAG Context Fabric | RetrievalContextBundle | builds | ranked and budgeted context | [`ai_stack/rag/rag_context_pack_assembler.py`](../../../../ai_stack/rag/rag_context_pack_assembler.py) |
| Director | SemanticScenePlan | creates | bounded semantic scene plan | [`ai_stack/story_runtime/semantic_planner/semantic_scene_planner.py`](../../../../ai_stack/story_runtime/semantic_planner/semantic_scene_planner.py) |
| SemanticScenePlan | NarrativeMoveProposal | projects advisory move | configured off-path or reference-rejoin relation | [`ai_stack/story_runtime/semantic_planner/semantic_scene_plan/narrative_move.py`](../../../../ai_stack/story_runtime/semantic_planner/semantic_scene_plan/narrative_move.py) |
| SemanticScenePlan | Narrator | guides | realization constraints | [`ai_stack/story_runtime/director/director_realization_composer.py`](../../../../ai_stack/story_runtime/director/director_realization_composer.py) |
| Proposal Validator | Runtime Proposal | annotates | validation result and retry feedback | [`ai_stack/langgraph/validation/result.py`](../../../../ai_stack/langgraph/validation/result.py) |
| Runtime Aspect Ledger | RuntimeAspectRecord | aggregates | one record per supported aspect | [`ai_stack/story_runtime/runtime_aspect_ledger/records.py`](../../../../ai_stack/story_runtime/runtime_aspect_ledger/records.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
