from __future__ import annotations

from copy import deepcopy

from world_engine.story_runtime.manager.commit_evidence_projection import (
    build_commit_evidence_projection,
)


def test_commit_evidence_projection_preserves_source_and_is_pure() -> None:
    graph_state = {
        "routing": {
            "selected_provider": "openai",
            "selected_model": "model-a",
            "fallback_reason": "primary_timeout",
        },
        "nodes_executed": ["route_model", "fallback_model"],
        "self_correction": {"attempt_count": 2},
        "retrieval": {
            "status": "ok",
            "hit_count": 3,
            "documents_used": ["scene", "memory"],
            "retrieval_route": "hybrid",
            "profile": "runtime",
            "domain": "story",
            "top_hit_score": 0.9,
            "corpus_fingerprint": "corpus-1",
            "index_version": "v2",
        },
    }
    generation = {
        "metadata": {"adapter": "openai", "adapter_invocation_mode": "primary"},
        "structured_output": {"narrative": "candidate"},
        "parser_error": None,
    }
    validation_outcome = {
        "status": "accepted",
        "reason": "valid",
        "dramatic_quality_gate": "passed",
        "actor_lane_validation": {"status": "passed", "reason": "owned actor"},
    }
    original = deepcopy((graph_state, generation, validation_outcome))

    projection = build_commit_evidence_projection(
        graph_state=graph_state,
        generation=generation,
        validation_outcome=validation_outcome,
        model_ok=False,
        errors=["provider degraded"],
        committed=True,
    )

    assert (graph_state, generation, validation_outcome) == original
    assert projection["llm_invocation_details"]["fallback_stage_reached"] == "graph_fallback_executed"
    assert projection["validation_details"]["actor_lane_validation_status"] == "passed"
    assert projection["commit_details"] == {
        "committed": True,
        "degraded": True,
        "degradation_reason": "provider degraded",
    }
    assert projection["retrieval_details"]["corpus_fingerprint"] == "corpus-1"


def test_commit_evidence_projection_handles_missing_optional_evidence() -> None:
    projection = build_commit_evidence_projection(
        graph_state={"routing": "invalid", "nodes_executed": "invalid"},
        generation={},
        validation_outcome={},
        model_ok=True,
        errors=[],
        committed=False,
    )

    assert projection["llm_invocation_details"]["fallback_stage_reached"] == "primary_only"
    assert projection["commit_details"]["degraded"] is False
    assert projection["retrieval_details"] is None
