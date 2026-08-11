from __future__ import annotations

from types import SimpleNamespace

import pytest

from world_engine.story_runtime.manager.commit_side_effects import (
    apply_committed_turn_side_effects,
)


class _Manager:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def _refresh_callback_web_after_commit(self, **_: object) -> None:
        self.calls.append("callback")

    def _refresh_consequence_cascade_after_commit(self, **_: object) -> None:
        self.calls.append("cascade")

    def _emit_observability_path_for_event(self, **_: object) -> None:
        self.calls.append("observability")

    def _w5_shadow_extract_after_commit(self, **_: object) -> None:
        self.calls.append("w5")


@pytest.mark.parametrize(
    ("include_w5_shadow", "expected_calls"),
    [
        (False, ["callback", "cascade", "observability"]),
        (True, ["callback", "cascade", "observability", "w5"]),
    ],
)
def test_commit_side_effects_preserve_order_and_append_diagnostics_once(
    include_w5_shadow: bool,
    expected_calls: list[str],
) -> None:
    manager = _Manager()
    session = SimpleNamespace(diagnostics=[])
    event = {"canonical_turn_id": "turn-1"}

    apply_committed_turn_side_effects(
        manager,
        session=session,
        graph_state={},
        event=event,
        include_w5_shadow=include_w5_shadow,
    )

    assert manager.calls == expected_calls
    assert session.diagnostics == [event]
