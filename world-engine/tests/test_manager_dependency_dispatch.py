from __future__ import annotations

from unittest.mock import Mock

import world_engine.story_runtime.manager as manager_package
from world_engine.story_runtime.manager import _deps


def test_dependency_dispatch_uses_the_active_manager_namespace(monkeypatch) -> None:
    replacement = Mock()
    monkeypatch.setattr(manager_package, "log_story_turn_event", replacement)

    _deps.log_story_turn_event(trace_id="trace-1")

    replacement.assert_called_once_with(trace_id="trace-1")
