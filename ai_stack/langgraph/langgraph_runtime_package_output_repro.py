"""Repro metadata and graph-path summary for package_output (DS-037)."""

from __future__ import annotations

from typing import Any

from ai_stack.story_runtime.turn.god_of_carnage_turn_seams import repro_metadata_complete
from ai_stack.langgraph.langgraph_runtime_state import RuntimeTurnState
from ai_stack.langgraph.langgraph_runtime_tracking import _dist_version
from ai_stack.contracts.runtime_turn_contracts import (
    ADAPTER_INVOCATION_AUTHORITATIVE_ACTION_RESOLUTION,
    ADAPTER_INVOCATION_DEGRADED_NO_FALLBACK,
    ADAPTER_INVOCATION_LANGCHAIN_PRIMARY,
    ADAPTER_INVOCATION_META_CONTROL,
    EXECUTION_HEALTH_DEGRADED_GENERATION,
    EXECUTION_HEALTH_GRAPH_ERROR,
    EXECUTION_HEALTH_HEALTHY,
    EXECUTION_HEALTH_MODEL_FALLBACK,
)
from ai_stack.version import AI_STACK_SEMANTIC_VERSION


def _base_repro_metadata(
    state: RuntimeTurnState,
    *,
    graph_name: str,
    graph_version: str,
) -> dict[str, Any]:
    routing = state.get("routing") or {}
    retrieval = state.get("retrieval") or {}
    generation = state.get("generation") or {}
    host_versions = dict(state.get("host_versions") or {})
    return {
        "ai_stack_semantic_version": AI_STACK_SEMANTIC_VERSION,
        "runtime_turn_graph_version": graph_version,
        "graph_name": graph_name,
        "trace_id": state.get("trace_id") or "",
        "story_runtime_core_version": _dist_version("story_runtime_core"),
        "routing_policy": "story_runtime_core.RoutingPolicy",
        "routing_policy_version": "registry_default_v1",
        "planned_route": {
            "selected_model": routing.get("selected_model"),
            "selected_provider": routing.get("selected_provider"),
            "route_reason": routing.get("route_reason"),
            "fallback_chain": routing.get("fallback_chain"),
        },
        "selected_model": routing.get("selected_model"),
        "selected_provider": routing.get("selected_provider"),
        "route_reason": routing.get("route_reason") or routing.get("reason"),
        "fallback_chain": routing.get("fallback_chain"),
        "actual_invocation": {
            "attempted": generation.get("attempted"),
            "success": generation.get("success"),
            "fallback_used": generation.get("fallback_used"),
        },
        "model_attempted": generation.get("attempted"),
        "model_success": generation.get("success"),
        "model_fallback_used": generation.get("fallback_used"),
        "retrieval_domain": retrieval.get("domain"),
        "retrieval_profile": retrieval.get("profile"),
        "retrieval_status": retrieval.get("status"),
        "retrieval_hit_count": retrieval.get("hit_count"),
        "module_id": state.get("module_id"),
        "session_id": state.get("session_id"),
        "host_versions": host_versions,
    }


def _apply_action_resolution_repro_fields(
    repro_metadata: dict[str, Any],
    state: RuntimeTurnState,
) -> None:
    routing = state.get("routing") or {}
    short_path = bool(routing.get("action_resolution_short_path"))
    nodes_executed = list(state.get("nodes_executed") or [])
    generation_required = routing.get("generation_required")
    if generation_required is None:
        generation_required = bool("invoke_model" in nodes_executed or "fallback_model" in nodes_executed)
    repro_metadata["action_resolution_short_path"] = short_path
    repro_metadata["synthetic_short_path"] = short_path
    repro_metadata["generation_required"] = bool(generation_required)
    if bool(routing.get("meta_control_path")):
        repro_metadata["meta_control_path"] = True
    if not short_path:
        return
    reason = str(routing.get("action_resolution_short_path_reason") or "authoritative_action_resolution")
    repro_metadata["action_resolution_short_path_reason"] = reason
    repro_metadata["authoritative_action_resolution_reason"] = reason
    repro_metadata["execution_tier"] = str(state.get("execution_tier") or "live")
    repro_metadata["fallback_used"] = False
    repro_metadata["mock_used"] = False
    repro_metadata["ldss_fallback"] = False


def _execution_health_for_state(
    state: RuntimeTurnState,
    *,
    fallback_taken: bool,
) -> str:
    generation = state.get("generation") or {}
    graph_errors = list(state.get("graph_errors", []))
    if graph_errors:
        return EXECUTION_HEALTH_GRAPH_ERROR
    if fallback_taken:
        return EXECUTION_HEALTH_MODEL_FALLBACK
    if generation.get("success") is False:
        return EXECUTION_HEALTH_DEGRADED_GENERATION
    return EXECUTION_HEALTH_HEALTHY


def _graph_path_summary_for_invocation(
    *,
    fallback_taken: bool,
    adapter_mode: Any,
) -> str:
    if fallback_taken and adapter_mode == ADAPTER_INVOCATION_LANGCHAIN_PRIMARY:
        return "used_fallback_model_node_langchain_adapter"
    if fallback_taken:
        return "used_fallback_model_node_raw_adapter"
    if adapter_mode == ADAPTER_INVOCATION_LANGCHAIN_PRIMARY:
        return "primary_invoke_langchain_only"
    if adapter_mode == ADAPTER_INVOCATION_AUTHORITATIVE_ACTION_RESOLUTION:
        return "authoritative_action_resolution_deterministic"
    if adapter_mode == ADAPTER_INVOCATION_META_CONTROL:
        return "meta_control_deterministic"
    if adapter_mode == ADAPTER_INVOCATION_DEGRADED_NO_FALLBACK:
        return "degraded_adapter_or_fallback_missing"
    return "primary_path_unknown_adapter_mode"


def build_repro_metadata_and_health(
    state: RuntimeTurnState,
    *,
    graph_name: str,
    graph_version: str,
    fallback_taken: bool,
) -> tuple[dict[str, Any], str, bool]:
    """Return repro_metadata (incl. graph_path_summary, repro_complete),
    execution_health, repro_ok.
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (RuntimeTurnState); meaning follows the type and call sites.
        graph_name: ``graph_name`` (str); meaning follows the type and call sites.
        graph_version: ``graph_version`` (str); meaning follows the type and call sites.
        fallback_taken: ``fallback_taken`` (bool); meaning follows the type and call sites.
    
    Returns:
        tuple[dict[str, Any], str, bool]:
            Returns a value of type ``tuple[dict[str, Any], str, bool]``; see the function body for structure, error paths, and sentinels.
    """
    generation = state.get("generation") or {}
    # P1-5: Separate planned route from actual invocation for clarity
    repro_metadata = _base_repro_metadata(state, graph_name=graph_name, graph_version=graph_version)
    _apply_action_resolution_repro_fields(repro_metadata, state)
    execution_health = _execution_health_for_state(state, fallback_taken=fallback_taken)
    gen_meta = generation.get("metadata") if isinstance(generation.get("metadata"), dict) else {}
    adapter_mode = gen_meta.get("adapter_invocation_mode")
    repro_metadata["adapter_invocation_mode"] = adapter_mode
    repro_metadata["graph_path_summary"] = _graph_path_summary_for_invocation(
        fallback_taken=fallback_taken,
        adapter_mode=adapter_mode,
    )
    repro_ok = repro_metadata_complete(repro_metadata)
    repro_metadata["repro_complete"] = repro_ok

    return repro_metadata, execution_health, repro_ok
