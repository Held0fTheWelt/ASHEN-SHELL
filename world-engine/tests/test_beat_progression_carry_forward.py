"""Tests for the committed dramatic-continuity structure (``BeatProgression``).

``BeatProgression`` is computed at commit time from the committed scene id,
the planner-truth snapshot, and the prior committed beat. Two consecutive
commits must share a single beat identity when scene and scene function are
stable (continuity carries forward) and must advance with a truthful
``advancement_reason`` when scene or function changes.
"""

from __future__ import annotations

from app.story_runtime.commit_models import (
    BeatProgression,
    resolve_narrative_commit,
)


def _projection() -> dict:
    return {
        "scenes": [{"scene_id": "s1"}, {"scene_id": "s2"}],
        "start_scene_id": "s1",
        "transition_hints": [{"from": "s1", "to": "s2"}],
    }


def test_initial_turn_creates_initial_beat() -> None:
    rec = resolve_narrative_commit(
        turn_number=1,
        prior_scene_id="s1",
        player_input="hello",
        interpreted_input={"kind": "free_narration"},
        generation=None,
        runtime_projection=_projection(),
        graph_state={
            "selected_scene_function": "establish_pressure",
            "pacing_mode": "measured",
        },
    )
    bp = rec.beat_progression
    assert isinstance(bp, BeatProgression)
    assert bp.beat_id == "s1:establish_pressure"
    assert bp.beat_slot == 0
    assert bp.advanced is True
    assert bp.advancement_reason == "initial_beat"
    assert bp.pacing_carry_forward == "measured"
    assert bp.continuity_carry_forward_reason is None


def test_continuity_carry_forward_increments_slot() -> None:
    prior = BeatProgression(
        beat_id="s1:establish_pressure",
        beat_slot=0,
        pressure_state="tension_escalation",
        pacing_carry_forward="measured",
        responder_focus_carry_forward=["annette"],
        advanced=True,
        advancement_reason="initial_beat",
        continuity_carry_forward_reason=None,
        prior_beat_id=None,
    )
    rec = resolve_narrative_commit(
        turn_number=2,
        prior_scene_id="s1",
        player_input="press harder",
        interpreted_input={"kind": "free_narration"},
        generation=None,
        runtime_projection=_projection(),
        graph_state={
            "selected_scene_function": "establish_pressure",
            "pacing_mode": "measured",
            "continuity_impacts": [{"class": "tension_escalation"}],
        },
        prior_beat_progression=prior,
    )
    bp = rec.beat_progression
    assert bp is not None
    assert bp.beat_id == "s1:establish_pressure"
    assert bp.beat_slot == 1
    assert bp.advanced is False
    assert bp.advancement_reason == "continuity_carry_forward"
    # Dominant continuity class is preserved as the carry-forward reason.
    assert bp.continuity_carry_forward_reason == "tension_escalation"
    assert bp.prior_beat_id == "s1:establish_pressure"
    assert bp.pressure_state == "tension_escalation"


def test_scene_transition_advances_beat_with_truthful_reason() -> None:
    prior = BeatProgression(
        beat_id="s1:establish_pressure",
        beat_slot=3,
        pressure_state="tension_escalation",
        pacing_carry_forward="measured",
        responder_focus_carry_forward=["annette"],
        advanced=False,
        advancement_reason="continuity_carry_forward",
        continuity_carry_forward_reason="tension_escalation",
        prior_beat_id="s1:establish_pressure",
    )
    rec = resolve_narrative_commit(
        turn_number=4,
        prior_scene_id="s1",
        player_input="s2",
        interpreted_input={
            "kind": "explicit_command",
            "command_name": "move",
            "command_args": ["s2"],
        },
        generation=None,
        runtime_projection=_projection(),
        graph_state={
            "selected_scene_function": "establish_pressure",
            "pacing_mode": "measured",
        },
        prior_beat_progression=prior,
    )
    bp = rec.beat_progression
    assert bp is not None
    assert bp.beat_id == "s2:establish_pressure"
    assert bp.beat_slot == 0
    assert bp.advanced is True
    assert bp.advancement_reason == "scene_transition"
    assert bp.prior_beat_id == "s1:establish_pressure"


def test_function_shift_advances_beat() -> None:
    prior = BeatProgression(
        beat_id="s1:establish_pressure",
        beat_slot=1,
        pressure_state=None,
        pacing_carry_forward=None,
        responder_focus_carry_forward=[],
        advanced=True,
        advancement_reason="initial_beat",
        continuity_carry_forward_reason=None,
        prior_beat_id=None,
    )
    rec = resolve_narrative_commit(
        turn_number=3,
        prior_scene_id="s1",
        player_input="regroup",
        interpreted_input={"kind": "free_narration"},
        generation=None,
        runtime_projection=_projection(),
        graph_state={
            "selected_scene_function": "repair_attempt",
        },
        prior_beat_progression=prior,
    )
    bp = rec.beat_progression
    assert bp is not None
    assert bp.beat_id == "s1:repair_attempt"
    assert bp.advanced is True
    assert bp.advancement_reason == "function_shift"
    assert bp.prior_beat_id == "s1:establish_pressure"


def test_blocked_turn_does_not_advance_beat() -> None:
    prior = BeatProgression(
        beat_id="s1:establish_pressure",
        beat_slot=2,
        pressure_state="tension_escalation",
        pacing_carry_forward="measured",
        responder_focus_carry_forward=[],
        advanced=False,
        advancement_reason="continuity_carry_forward",
        continuity_carry_forward_reason="tension_escalation",
        prior_beat_id="s1:establish_pressure",
    )
    # Propose s2 in a projection with no transition hints → blocked via
    # transition_hints_missing.
    projection_no_hints = {
        "scenes": [{"scene_id": "s1"}, {"scene_id": "s2"}],
        "start_scene_id": "s1",
    }
    rec = resolve_narrative_commit(
        turn_number=5,
        prior_scene_id="s1",
        player_input="go to s2",
        interpreted_input={"kind": "free_narration"},
        generation={
            "success": True,
            "metadata": {"structured_output": {"proposed_scene_id": "s2"}},
        },
        runtime_projection=projection_no_hints,
        graph_state={"selected_scene_function": "establish_pressure"},
        prior_beat_progression=prior,
    )
    # Commit must be blocked
    assert rec.situation_status == "blocked"
    bp = rec.beat_progression
    assert bp is not None
    assert bp.beat_id == prior.beat_id
    assert bp.beat_slot == prior.beat_slot
    assert bp.advanced is False
    assert bp.advancement_reason == "blocked_turn_no_advance"


def test_prior_beat_read_back_from_session_history() -> None:
    """Manager-level proof: _prior_beat_from_session rehydrates the committed
    beat from a prior history entry, so the next turn's commit can carry it
    forward. Without this, beat continuity would stay ephemeral per turn."""
    from app.story_runtime.manager import _prior_beat_from_session
    from app.story_runtime.manager import StorySession

    s = StorySession(
        session_id="sess-beat-test",
        module_id="god_of_carnage",
        runtime_projection={"scenes": [], "start_scene_id": "s1"},
    )
    # Simulate a prior committed turn by appending a history entry shaped like
    # _finalize_committed_turn writes.
    prior_commit_payload = {
        "turn_number": 1,
        "committed_scene_id": "s1",
        "situation_status": "continue",
        "authoritative_reason": "no scene change",
        "commit_reason_code": "no_scene_proposal",
        "beat_progression": {
            "beat_id": "s1:establish_pressure",
            "beat_slot": 2,
            "pressure_state": "tension_escalation",
            "pacing_carry_forward": "measured",
            "responder_focus_carry_forward": ["annette"],
            "advanced": False,
            "advancement_reason": "continuity_carry_forward",
            "continuity_carry_forward_reason": "tension_escalation",
            "prior_beat_id": "s1:establish_pressure",
        },
    }
    s.history.append(
        {
            "turn_number": 1,
            "turn_kind": "player",
            "trace_id": "",
            "turn_outcome": "ok",
            "narrative_commit": prior_commit_payload,
            "committed_turn_authority": {},
            "committed_state_after": {"current_scene_id": "s1", "turn_counter": 1},
        }
    )

    beat = _prior_beat_from_session(s)
    assert beat is not None
    assert beat.beat_id == "s1:establish_pressure"
    assert beat.beat_slot == 2
    assert beat.pressure_state == "tension_escalation"

    # Next turn's commit, using this rehydrated beat, must carry forward to
    # slot 3 because scene + function are unchanged.
    next_rec = resolve_narrative_commit(
        turn_number=2,
        prior_scene_id="s1",
        player_input="press",
        interpreted_input={"kind": "free_narration"},
        generation=None,
        runtime_projection={"scenes": [{"scene_id": "s1"}], "start_scene_id": "s1"},
        graph_state={
            "selected_scene_function": "establish_pressure",
            "continuity_impacts": [{"class": "tension_escalation"}],
        },
        prior_beat_progression=beat,
    )
    nb = next_rec.beat_progression
    assert nb is not None
    assert nb.beat_id == "s1:establish_pressure"
    assert nb.beat_slot == 3
    assert nb.advanced is False


def test_dominant_pressure_order_respected() -> None:
    """Dominant continuity class follows drama-weighted precedence, not first-emitted."""
    rec = resolve_narrative_commit(
        turn_number=1,
        prior_scene_id="s1",
        player_input="hi",
        interpreted_input={"kind": "free_narration"},
        generation=None,
        runtime_projection=_projection(),
        graph_state={
            "selected_scene_function": "establish_pressure",
            "continuity_impacts": [
                {"class": "repair_attempt"},
                {"class": "tension_escalation"},
                {"class": "alliance_shift"},
            ],
        },
    )
    bp = rec.beat_progression
    assert bp is not None
    # tension_escalation must win over repair_attempt/alliance_shift even though
    # it appeared second in the list.
    assert bp.pressure_state == "tension_escalation"
