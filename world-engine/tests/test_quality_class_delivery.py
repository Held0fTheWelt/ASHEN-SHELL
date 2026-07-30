"""Wave 0: quality_class must survive delivery without collapsing to a lone boolean."""
from __future__ import annotations

from app.story_runtime.manager.story_window_entry_parts import build_story_window_runtime_entry


class _Session:
    session_id = "qc-session"


def test_degraded_and_failed_are_distinguishable_at_delivery() -> None:
    base_kwargs = dict(
        session=_Session(),
        turn_number=1,
        turn_kind="player",
        visible_lines=["The room still holds its breath."],
        spoken_lines=[],
        action_lines=[],
        consequence_lines=[],
        story_dramatic_context={},
        authority_summary={"validation_status": "approved"},
        degradation_summary="primary_retry_exhausted",
        actor_turn_summary={},
        actor_survival_telemetry={},
        vitality_summary={},
        passivity_diagnosis={},
        runtime_governance_surface={},
        scene_blocks=[],
        render_support=None,
    )
    degraded = build_story_window_runtime_entry(
        **base_kwargs,
        quality_class="degraded",
        degradation_signals=["self_correction_exhausted"],
    )
    failed = build_story_window_runtime_entry(
        **base_kwargs,
        quality_class="failed",
        degradation_signals=["hard_budget_exceeded"],
    )
    ok = build_story_window_runtime_entry(
        **base_kwargs,
        quality_class="ok",
        degradation_signals=[],
    )

    assert degraded["quality_class"] == "degraded"
    assert failed["quality_class"] == "failed"
    assert ok["quality_class"] == "ok"
    assert degraded["degradation_signals"] == ["self_correction_exhausted"]
    assert failed["degradation_signals"] == ["hard_budget_exceeded"]
    # Boolean remains as derived compatibility field, not the sole quality signal.
    assert degraded["degraded"] is True
    assert failed["degraded"] is True
    assert ok["degraded"] is False


def test_characterization_story_window_runtime_entry_field_list() -> None:
    """Characterization: delivered runtime entry exposes quality fields today."""
    entry = build_story_window_runtime_entry(
        session=_Session(),
        turn_number=0,
        turn_kind="opening",
        visible_lines=["Opening."],
        spoken_lines=[],
        action_lines=[],
        consequence_lines=[],
        story_dramatic_context={},
        authority_summary={},
        quality_class="ok",
        degradation_signals=[],
        degradation_summary=None,
        actor_turn_summary={},
        actor_survival_telemetry={},
        vitality_summary={},
        passivity_diagnosis={},
        runtime_governance_surface={},
        scene_blocks=[],
        render_support=None,
    )
    for field in ("quality_class", "degradation_signals", "degraded", "degraded_reasons"):
        assert field in entry
