"""
MVP4 Contract 3: Frontend Playability E2E Integration Tests

End-to-end verification that can_execute correctly reflects story state
through the full backend→world-engine→backend flow.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.mvp4
def test_mvp4_can_execute_false_on_empty_session():
    """E2E: Backend bundle with empty story window has can_execute=False."""
    from backend.app.api.v1.game_routes import _player_session_bundle

    # Simulate empty story window from world-engine (session just created, opening failed)
    state = {
        "story_window": {
            "contract": "authoritative_story_window_v1",
            "source": "world_engine_story_runtime",
            "entries": [],  # Empty: no opening yet
            "entry_count": 0,
            "latest_entry": None,
        },
        "turn_counter": 0,
        "current_scene_id": "scene_1",
    }

    bundle = _player_session_bundle(
        run_id="test_run",
        template_id="god_of_carnage",
        module_id="god_of_carnage",
        runtime_session_id="test_session",
        state=state,
        created=None,
    )

    # Verify can_execute matches empty state
    assert bundle.get("can_execute") is False, \
        "can_execute should be False for empty story window"


@pytest.mark.mvp4
def test_mvp4_can_execute_true_on_session_with_opening():
    """E2E: Backend bundle with opening has can_execute=True."""
    from backend.app.api.v1.game_routes import _player_session_bundle

    # Simulate story window with opening from world-engine
    state = {
        "story_window": {
            "contract": "authoritative_story_window_v1",
            "source": "world_engine_story_runtime",
            "entries": [
                {
                    "turn_number": 0,
                    "kind": "opening",
                    "role": "runtime",
                    "text": "The room is tense. Veronique sits across from Michel.",
                }
            ],
            "entry_count": 1,
            "latest_entry": {
                "turn_number": 0,
                "kind": "opening",
                "role": "runtime",
                "text": "The room is tense. Veronique sits across from Michel.",
            },
        },
        "turn_counter": 0,
        "current_scene_id": "scene_1",
    }

    bundle = _player_session_bundle(
        run_id="test_run",
        template_id="god_of_carnage",
        module_id="god_of_carnage",
        runtime_session_id="test_session",
        state=state,
        created=None,
    )

    # Verify can_execute reflects entry_count > 0
    assert bundle.get("can_execute") is True, \
        "can_execute should be True when opening exists"


@pytest.mark.mvp4
def test_mvp4_can_execute_consistency_with_story_entries():
    """E2E: can_execute should be consistent with story_entries presence."""
    from backend.app.api.v1.game_routes import _player_session_bundle

    # Test various entry counts
    test_cases = [
        (0, False, "empty session"),
        (1, True, "opening only"),
        (2, True, "opening + player turn"),
        (5, True, "multiple turns"),
    ]

    for entry_count, expected_can_execute, description in test_cases:
        entries = [
            {
                "turn_number": i,
                "kind": "opening" if i == 0 else "runtime",
                "role": "runtime",
                "text": f"Entry {i}",
            }
            for i in range(entry_count)
        ]

        state = {
            "story_window": {
                "contract": "authoritative_story_window_v1",
                "source": "world_engine_story_runtime",
                "entries": entries,
                "entry_count": entry_count,
                "latest_entry": entries[-1] if entries else None,
            },
            "last_committed_turn": None,
        }

        bundle = _player_session_bundle(
            run_id="test_run",
            template_id="god_of_carnage",
            module_id="god_of_carnage",
            runtime_session_id="test_session",
            state=state,
            created=None,
        )

        actual_can_execute = bundle.get("can_execute")
        assert actual_can_execute == expected_can_execute, \
            f"Entry count {entry_count} ({description}): " \
            f"expected can_execute={expected_can_execute}, got {actual_can_execute}"


@pytest.mark.mvp4
def test_mvp4_can_execute_reflects_story_window_state():
    """E2E: Backend response reflects actual story_window state from world-engine."""
    from backend.app.api.v1.game_routes import _player_session_bundle

    # Simulate world-engine returning opening + first player turn
    state = {
        "story_window": {
            "contract": "authoritative_story_window_v1",
            "source": "world_engine_story_runtime",
            "entries": [
                {
                    "turn_number": 0,
                    "kind": "opening",
                    "role": "runtime",
                    "text": "The room crackles with tension.",
                },
                {
                    "turn_number": 1,
                    "kind": "player",
                    "role": "player",
                    "text": "I break the uncomfortable silence.",
                },
                {
                    "turn_number": 1,
                    "kind": "runtime",
                    "role": "runtime",
                    "text": "Michel's eyes narrow.",
                },
            ],
            "entry_count": 3,
            "latest_entry": {
                "turn_number": 1,
                "kind": "runtime",
                "role": "runtime",
                "text": "Michel's eyes narrow.",
            },
        },
        "last_committed_turn": {
            "turn_number": 1,
            "visible_output_bundle": {
                "gm_narration": ["Michel's eyes narrow."],
                "spoken_lines": [],
                "action_lines": [],
            },
        },
    }

    bundle = _player_session_bundle(
        run_id="test_run",
        template_id="god_of_carnage",
        module_id="god_of_carnage",
        runtime_session_id="test_session",
        state=state,
        created=None,
    )

    # Verify contract compliance
    assert bundle.get("runtime_session_ready") is True
    assert bundle.get("can_execute") is True  # 3 entries > 0
    assert bundle.get("story_window", {}).get("entry_count") == 3
    assert len(bundle.get("story_entries", [])) == 3
    assert bundle.get("story_entries") == state["story_window"]["entries"]
