"""Tests for responder reconciliation in the validate-seam node.

The director-selected responder set is the authoritative scope for a scene.
When the model proposes a responder id or responder scope in its structured
output, the runtime must:

- accept the model's claim when it falls within the director's scope,
- drop any actor the model introduced that is not in scope, and
- record the outcome under ``responder_reconciliation`` on state.

The reconciliation dict is plain data; these tests exercise
``_reconcile_model_responders`` directly rather than spinning up the full
LangGraph pipeline.
"""

from __future__ import annotations

from ai_stack.langgraph_runtime_executor import _reconcile_model_responders


def _state(selected: list[dict]) -> dict:
    return {"selected_responder_set": selected}


def _generation_with_structured(structured: dict) -> dict:
    return {
        "success": True,
        "metadata": {"structured_output": structured},
    }


def test_model_responder_in_scope_is_accepted() -> None:
    state = _state(
        [
            {"actor_id": "annette_reille"},
            {"actor_id": "alain_reille"},
        ]
    )
    generation = _generation_with_structured(
        {
            "responder_id": "alain_reille",
            "responder_actor_ids": ["alain_reille"],
        }
    )
    out = _reconcile_model_responders(state, generation)
    assert out["outcome"] == "model_responder_accepted"
    assert out["effective_responder_id"] == "alain_reille"
    assert out["effective_responder_scope"] == ["alain_reille"]
    assert out["dropped_out_of_scope_actors"] == []
    assert out["dropped_out_of_scope_count"] == 0


def test_model_responder_out_of_scope_is_dropped_and_director_used() -> None:
    state = _state(
        [
            {"actor_id": "annette_reille"},
            {"actor_id": "alain_reille"},
        ]
    )
    generation = _generation_with_structured(
        {
            "responder_id": "ghost_character",
            "responder_actor_ids": ["ghost_character", "alain_reille"],
        }
    )
    out = _reconcile_model_responders(state, generation)
    assert out["outcome"] == "model_responder_out_of_scope_dropped"
    assert out["effective_responder_id"] == "annette_reille"
    assert out["effective_responder_scope"] == ["alain_reille"]
    assert out["dropped_out_of_scope_actors"] == ["ghost_character"]
    assert out["dropped_out_of_scope_count"] == 1


def test_model_proposes_no_responder_then_director_primary_used() -> None:
    state = _state([{"actor_id": "annette_reille"}])
    generation = _generation_with_structured({})
    out = _reconcile_model_responders(state, generation)
    assert out["outcome"] == "director_primary_responder_used"
    assert out["effective_responder_id"] == "annette_reille"


def test_model_responder_missing_from_director_scope_falls_back() -> None:
    # Director scope exists but the model's primary is not in it and its
    # scope list is empty — the director primary is used and the outcome
    # reflects that the model's responder was missing from scope.
    state = _state([{"actor_id": "annette_reille"}])
    generation = _generation_with_structured(
        {"responder_id": "outsider", "responder_actor_ids": []}
    )
    out = _reconcile_model_responders(state, generation)
    assert out["outcome"] == "model_responder_out_of_scope_dropped"
    assert out["effective_responder_id"] == "annette_reille"
    assert out["dropped_out_of_scope_actors"] == ["outsider"]


def test_no_director_scope_accepts_model_responder_as_effective() -> None:
    # When the director publishes no responder scope (for example in tests or
    # in modules that have not yet wired responder selection), the model's
    # proposed responder is accepted as the effective responder so the turn
    # still has a concrete actor to render — but no actor is dropped.
    state = _state([])
    generation = _generation_with_structured({"responder_id": "solo_actor"})
    out = _reconcile_model_responders(state, generation)
    assert out["outcome"] == "model_responder_accepted"
    assert out["effective_responder_id"] == "solo_actor"
    assert out["dropped_out_of_scope_count"] == 0


def test_empty_director_scope_and_empty_model_is_empty_reconciliation() -> None:
    out = _reconcile_model_responders(_state([]), {"metadata": {}})
    assert out["outcome"] == "no_director_scope_available"
    assert out["effective_responder_id"] is None
    assert out["effective_responder_scope"] == []
