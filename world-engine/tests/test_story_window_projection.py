from __future__ import annotations

from app.story_runtime.manager import StorySession, _story_window_entries_for_session


def test_story_window_projection_uses_committed_opening_and_player_turn() -> None:
    session = StorySession(
        session_id="story-1",
        module_id="god_of_carnage",
        runtime_projection={"start_scene_id": "scene_1"},
        current_scene_id="scene_1",
    )
    session.diagnostics = [
        {
            "turn_number": 0,
            "turn_kind": "opening",
            "raw_input": "internal opening prompt hidden from players",
            "visible_output_bundle": {"gm_narration": ["The room is already tense."]},
            "narrative_commit": {"committed_consequences": ["opening_committed"]},
            "committed_turn_authority": {
                "authority_record_version": "committed_turn_authority.v1",
                "committed_scene_id": "scene_1",
                "validation_status": "approved",
                "commit_applied": True,
            },
            "runtime_governance_surface": {"governed_runtime_active": True},
        },
        {
            "turn_number": 1,
            "turn_kind": "player",
            "raw_input": "I say that is enough.",
            "visible_output_bundle": {
                "gm_narration": ["The answer lands hard."],
                "spoken_lines": ["Annette: Enough?"],
                "render_support": {
                    "projection_version": "director_surface_hints.v1",
                    "player_visible": False,
                    "director_surface_hints": [{"hint_type": "phase_context", "text": "Debate is open."}],
                },
            },
            "narrative_commit": {"committed_consequences": ["tension_escalates"]},
            "committed_turn_authority": {
                "authority_record_version": "committed_turn_authority.v1",
                "committed_scene_id": "scene_1",
                "validation_status": "approved",
                "commit_applied": True,
            },
            "selected_scene_function": "escalate_conflict",
            "visibility_class_markers": ["truth_aligned"],
        },
    ]

    entries = _story_window_entries_for_session(session)

    assert [entry["role"] for entry in entries] == ["runtime", "player", "runtime"]
    assert entries[0]["kind"] == "opening"
    assert entries[0]["text"] == "The room is already tense."
    assert "internal opening prompt" not in entries[0]["text"]
    assert entries[1]["text"] == "I say that is enough."
    assert entries[2]["text"] == "The answer lands hard."
    assert entries[2]["spoken_lines"] == ["Annette: Enough?"]
    assert entries[2]["committed_consequences"] == ["tension_escalates"]
    assert entries[2]["render_support"]["player_visible"] is False
    assert entries[2]["authority_summary"]["validation_status"] == "approved"
    assert entries[2]["authority_summary"]["selected_scene_function"] == "escalate_conflict"
    assert entries[2]["authority_summary"]["visibility_class_markers"] == ["truth_aligned"]
