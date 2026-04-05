# LLM / SLM role stratification (Tasks 2A / 2B)

## Scope (what exists today)

Task 2A adds a **canonical, model-aware routing core** in the backend runtime:

- **Contracts**: `backend/app/runtime/model_routing_contracts.py` — bounded enums, `AdapterModelSpec`, `RoutingRequest`, `RoutingDecision`.
- **Registry**: `backend/app/runtime/adapter_registry.py` — legacy `register_adapter` / `get_adapter` unchanged; `register_adapter_model` stores both the adapter instance and its spec; `clear_registry()` clears both stores.
- **Policy**: `backend/app/runtime/model_routing.py` — explicit `TASK_ROUTING_MODE` role matrix, deterministic `route_model()`, inspectable `RouteReasonCode`, `decision_factors`, `fallback_chain`, and `escalation_applied` / `degradation_applied` flags.

This layer chooses an **adapter name** (and echoes provider/model from the spec). It does **not** call providers itself.

### Task 2B — where routing is wired

- **Canonical runtime AI path** (`execute_turn_with_ai` in `backend/app/runtime/ai_turn_executor.py`): builds a minimal `RoutingRequest` from session/context, calls `route_model(...)` **once** before adapter execution, resolves the executable adapter by name, and falls back to the caller-supplied adapter when no eligible spec-backed adapter exists (e.g. `no_eligible_adapter`). Guard legality, commit semantics, and reject behavior are unchanged. A compact **`model_routing_trace`** is attached to `AIDecisionLog` (full `RoutingRequest` / `RoutingDecision` JSON plus legacy fields). **Task 2C-2** adds a nested **`routing_evidence`** object with a stable cross-surface summary (`requested_workflow_phase`, `requested_task_kind`, selected vs executed adapter, `route_reason_code`, `fallback_chain`, flags, `no_eligible_spec_selection`, runtime-only `passed_adapter_name` / `fallback_to_passed_adapter`). This is observability for operators, not a telemetry product.
- **Writers Room** (`backend/app/services/writers_room_service.py`): model choice no longer uses `story_runtime_core.RoutingPolicy`. Specs are built via `backend/app/services/writers_room_model_routing.py` and **two honest routing stages** call `route_model`: **Stage A** (preflight / cheap task kinds) as an optional bounded model call when a routed adapter resolves; **Stage B** (synthesis / generation). `model_generation.task_2a_routing` exposes `preflight` / `synthesis` traces; each stage includes **`routing_evidence`** in the same normalized shape as runtime (bounded-call / skip fields filled where applicable; synthesis uses the provider that actually produced content when known).
- **Improvement** (`backend/app/api/v1/improvement_routes.py` + `backend/app/services/improvement_task2a_routing.py`): after the deterministic recommendation package is built, **two** `route_model` stages (preflight + synthesis, same spec source as Writers Room) attach **`task_2a_routing`** and **`model_assisted_interpretation`** to the persisted recommendation package. Sandbox metrics and threshold-based recommendation labels remain the truth-bearing base; `deterministic_recommendation_base` is set before transcript suffixes. Bounded model calls are optional; traces stay honest when no adapter resolves (`no_eligible_adapter_or_missing_provider_adapter`). Each stage carries **`routing_evidence`** aligned with the shared helper in `backend/app/runtime/model_routing_evidence.py`.

Shared helper: **`backend/app/runtime/model_routing_evidence.py`** — `build_routing_evidence`, `attach_stage_routing_evidence` (Writers Room / Improvement stages).

## Not the same as `role_contract.py`

`backend/app/runtime/role_contract.py` defines **interpreter / director / responder** sections inside **one** structured adapter output. That is an **intra-call** shape contract.

Task 2A routing is **cross-model** stratification: which registered adapter (LLM-class vs SLM-class, tier, cost/latency metadata) should handle a **routing request** described by workflow phase and task kind. Keep the two concepts separate.

## Role matrix (encoded in code)

`TASK_ROUTING_MODE` maps each `TaskKind` to:

- **SLM-first**: `classification`, `trigger_signal_extraction`, `repetition_consistency_check`, `ranking`, `cheap_preflight`
- **LLM-first**: `scene_direction`, `conflict_synthesis`, `narrative_formulation`, `social_narrative_tradeoff`, `revision_synthesis`
- **Escalation-sensitive**: `ambiguity_resolution`, `continuity_judgment`, `high_stakes_narrative_tradeoff` — with optional `EscalationHint` values to prefer LLM-class adapters when both classes are eligible.

## Task 2C status (honest scope)

- **2C-1**: Improvement HTTP path uses Task-2A routing as **bounded enrichment** around the deterministic evaluation core (no model override of governance or threshold semantics).
- **2C-2**: **Normalized `routing_evidence`** is shared across Runtime (`model_routing_trace`), Writers Room (`task_2a_routing` stages), and Improvement (`task_2a_routing` stages). This does **not** add new dashboards, product-wide telemetry, or deeper `RouteReasonCode` semantics than `route_model` actually emits.
- **Still not claimed**: multi-stage narrative pipelines in runtime (still **route once, execute one adapter** per turn), or “full stack” observability beyond these JSON surfaces.

## Honest limits

- **Tier and alignment scores** are deterministic heuristics until production telemetry informs tuning.
- **`RouteReasonCode`**: the contract enumerates rich reason codes; **not every code is actively produced as the primary policy output** in all paths — do not overclaim finer-grained routing narratives than the current `route_model` implementation returns.
- **Registry consistency**: `register_adapter(name, ...)` does not update or remove an existing spec for the same name; mixed use of legacy and spec registration for one name can leave stale metadata — prefer `register_adapter_model` when specs are in play.
- **Environments without `register_adapter_model`**: routing often yields `no_eligible_adapter`; runtime integration **must** keep the honest fallback to the already supplied executable adapter.