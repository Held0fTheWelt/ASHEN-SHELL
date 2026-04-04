# LLM / SLM role stratification (Task 2A)

## Scope (what exists today)

Task 2A adds a **canonical, model-aware routing core** in the backend runtime:

- **Contracts**: `backend/app/runtime/model_routing_contracts.py` — bounded enums, `AdapterModelSpec`, `RoutingRequest`, `RoutingDecision`.
- **Registry**: `backend/app/runtime/adapter_registry.py` — legacy `register_adapter` / `get_adapter` unchanged; `register_adapter_model` stores both the adapter instance and its spec; `clear_registry()` clears both stores.
- **Policy**: `backend/app/runtime/model_routing.py` — explicit `TASK_ROUTING_MODE` role matrix, deterministic `route_model()`, inspectable `RouteReasonCode`, `decision_factors`, `fallback_chain`, and `escalation_applied` / `degradation_applied` flags.

This layer chooses an **adapter name** (and echoes provider/model from the spec). It does **not** call providers and is **not** wired into `turn_dispatcher`, `ai_turn_executor`, writers-room, or improvement flows in Task 2A.

## Not the same as `role_contract.py`

`backend/app/runtime/role_contract.py` defines **interpreter / director / responder** sections inside **one** structured adapter output. That is an **intra-call** shape contract.

Task 2A routing is **cross-model** stratification: which registered adapter (LLM-class vs SLM-class, tier, cost/latency metadata) should handle a **routing request** described by workflow phase and task kind. Keep the two concepts separate.

## Role matrix (encoded in code)

`TASK_ROUTING_MODE` maps each `TaskKind` to:

- **SLM-first**: `classification`, `trigger_signal_extraction`, `repetition_consistency_check`, `ranking`, `cheap_preflight`
- **LLM-first**: `scene_direction`, `conflict_synthesis`, `narrative_formulation`, `social_narrative_tradeoff`, `revision_synthesis`
- **Escalation-sensitive**: `ambiguity_resolution`, `continuity_judgment`, `high_stakes_narrative_tradeoff` — with optional `EscalationHint` values to prefer LLM-class adapters when both classes are eligible.

## Deferred work (Tasks 2B / 2C)

- Dispatching turns via `session.adapter_name` remains the legacy path until explicitly integrated.
- No change to guard/commit semantics or authoritative narrative commit behavior as part of Task 2A.

## Honest limits

- **Tier and alignment scores** are deterministic heuristics until production telemetry informs tuning.
- **Registry consistency**: `register_adapter(name, ...)` does not update or remove an existing spec for the same name; mixed use of legacy and spec registration for one name can leave stale metadata — prefer `register_adapter_model` when specs are in play.