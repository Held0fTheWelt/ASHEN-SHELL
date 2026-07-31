"""Wave 8: TurnTrace gaps are reported as partial, never complete."""

from __future__ import annotations

from world_engine.observability.trace import TurnTrace


def test_trace_gap_is_reported_as_partial() -> None:
    trace = TurnTrace(trace_id="t-1", session_id="s-1", turn_id="turn-9", revision=3)
    trace.record_span("player_input")
    assert trace.completeness == "complete"

    trace.mark_expected_span_missing("model_call")
    assert trace.gaps == ["missing_span:model_call"]
    assert trace.completeness == "partial"

    # Recording further spans must not erase an open gap.
    trace.record_span("player_visible_projection")
    assert trace.completeness == "partial"


def test_turn_trace_propagates_identity_fields() -> None:
    trace = TurnTrace(trace_id="abc", session_id="sess", turn_id="42", revision=7)
    assert trace.trace_id == "abc"
    assert trace.session_id == "sess"
    assert trace.turn_id == "42"
    assert trace.revision == 7
    assert trace.redacted_fields == ()
