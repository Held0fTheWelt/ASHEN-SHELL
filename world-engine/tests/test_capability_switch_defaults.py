"""Wave 4: capability switch surface on runtime config mixin."""
from __future__ import annotations

from app.story_runtime.manager.runtime_config import _RuntimeConfigMixin


class _Probe(_RuntimeConfigMixin):
    def __init__(self, settings: dict | None = None) -> None:
        self._governed_runtime_config = {
            "world_engine_settings": settings or {},
        }


def test_capability_switch_defaults_are_on() -> None:
    switches = _Probe()._capability_switches()
    assert switches == {
        "capability_state_deltas": True,
        "capability_mutation_policy": True,
        "capability_source_gate": True,
        "capability_failure_recovery": True,
        "capability_scene_legality": True,
    }


def test_capability_switch_can_be_disabled() -> None:
    switches = _Probe({"capability_source_gate": False})._capability_switches()
    assert switches["capability_source_gate"] is False
    assert switches["capability_state_deltas"] is True
