# 06 Runtime Modes and Routing

## Execution mode semantics

### `mock_only`
Use only mock models/routes.
No real provider calls are allowed.
Best for safe local setup and deterministic smoke behavior.

### `ai_only`
Use only real providers/models.
No mock route may be used as standard fallback unless explicitly permitted for degraded emergency paths.

### `routed_llm_slm`
Use task routing across real models:
- cheaper structured tasks may prefer SLM
- complex narrative tasks may prefer LLM
- mock may remain disabled

### `hybrid_routed_with_mock_fallback`
Use real routes where available, but allow mock as explicit degraded fallback when configured.
This is the recommended practical mode for mixed local/cloud operation.

## Retrieval modes

### `disabled`
No retrieval augmentation.

### `sparse_only`
Sparse retrieval only.

### `hybrid_dense_sparse`
Use sparse + embeddings-based retrieval when configured and healthy.

## Validation modes

### `schema_only`
Fast deterministic validation.

### `schema_plus_semantic`
Schema plus semantic policy checks.

### `strict_rule_engine`
External or internal strict rule engine path.

## Routing resolution rules

For each task:
1. find enabled route by `task_kind` + `workflow_scope`
2. inspect runtime mode
3. resolve preferred model
4. verify provider availability and policy compatibility
5. if unavailable, evaluate fallback rules
6. if hybrid + mock fallback allowed, choose mock route
7. record route resolution in usage event metadata

## Required governed task kinds

At minimum:
- `narrative_live_generation`
- `narrative_preview_generation`
- `narrative_validation_semantic`
- `research_synthesis`
- `research_revision_drafting`
- `writers_room_revision_assist`
- `retrieval_embedding_generation`
- `retrieval_query_expansion`

## Runtime profile behavior

### `safe_local`
- mock or local-first
- lower cost risk
- conservative validation
- safe fallback emphasized

### `balanced`
- mixed provider use
- moderate costs
- normal fallback behavior

### `cost_aware`
- prefer cheaper providers/models where acceptable
- tighter budget warning behavior
- conservative LLM escalation

### `quality_first`
- prefer best configured quality path
- allow higher-cost routes if policy allows

## Routing blockers

A save/update must be blocked when:
- AI-only is selected but no valid real route exists for required tasks
- hybrid is selected but no mock fallback path exists where required
- route references disabled or missing models
- local-only provider selection conflicts with cloud-only preferred route

## Hidden-default elimination

The following current hidden/default behaviors should be replaced by governed routing:
- hardcoded default model registry choices
- ad hoc env-derived provider selection
- implicit mock bootstrap as the only safe route
- runtime main startup hardcoding of validator mode
