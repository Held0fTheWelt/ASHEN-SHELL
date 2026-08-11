"""Pure projection of committed-turn observability evidence."""

from __future__ import annotations

from typing import Any


def build_commit_evidence_projection(
    *,
    graph_state: dict[str, Any],
    generation: dict[str, Any],
    validation_outcome: dict[str, Any],
    model_ok: bool,
    errors: list[Any],
    committed: bool,
) -> dict[str, Any]:
    """Derive log-ready evidence without mutating graph or session state."""

    routing = graph_state.get("routing")
    routing = routing if isinstance(routing, dict) else {}
    generation_metadata = generation.get("metadata")
    generation_metadata = generation_metadata if isinstance(generation_metadata, dict) else {}
    self_correction = graph_state.get("self_correction")
    self_correction = self_correction if isinstance(self_correction, dict) else {}
    nodes_executed = graph_state.get("nodes_executed")
    nodes_executed = nodes_executed if isinstance(nodes_executed, list) else []

    llm_invocation = {
        "selected_provider": routing.get("selected_provider"),
        "selected_model": routing.get("selected_model"),
        "adapter_used": generation_metadata.get("adapter"),
        "adapter_invocation_mode": generation_metadata.get("adapter_invocation_mode"),
        "fallback_stage_reached": routing.get("fallback_stage_reached")
        or (
            "graph_fallback_executed"
            if "fallback_model" in nodes_executed
            else "primary_only"
        ),
        "fallback_reason": routing.get("fallback_reason"),
        "retry_attempt_count": self_correction.get("attempt_count"),
        "parser_error": generation.get("parser_error"),
        "structured_output_present": generation.get("structured_output") is not None,
        "model_success": model_ok,
    }

    validation = {
        "status": validation_outcome.get("status"),
        "reason": validation_outcome.get("reason"),
        "dramatic_quality_gate": validation_outcome.get("dramatic_quality_gate"),
    }
    actor_lane_validation = validation_outcome.get("actor_lane_validation")
    if isinstance(actor_lane_validation, dict) and actor_lane_validation:
        validation["actor_lane_validation_status"] = actor_lane_validation.get("status")
        validation["actor_lane_validation_reason"] = actor_lane_validation.get("reason")

    retrieval_status = graph_state.get("retrieval")
    retrieval_status = retrieval_status if isinstance(retrieval_status, dict) else {}
    retrieval = (
        {
            "status": retrieval_status.get("status"),
            "hit_count": retrieval_status.get("hit_count"),
            "documents_used": retrieval_status.get("documents_used"),
            "retrieval_route": retrieval_status.get("retrieval_route"),
            "profile": retrieval_status.get("profile"),
            "domain": retrieval_status.get("domain"),
            "top_hit_score": retrieval_status.get("top_hit_score"),
            "corpus_fingerprint": retrieval_status.get("corpus_fingerprint"),
            "index_version": retrieval_status.get("index_version"),
        }
        if retrieval_status
        else None
    )

    return {
        "llm_invocation_details": llm_invocation,
        "validation_details": validation,
        "commit_details": {
            "committed": bool(committed),
            "degraded": not model_ok or bool(errors),
            "degradation_reason": str(errors[0]) if errors else None,
        },
        "retrieval_details": retrieval,
    }


__all__ = ["build_commit_evidence_projection"]
