"""Phase 6B-8 (ADR-0068) - narrator strict-off rollback removed.

ADR-0067 deprecated ``W5_AST_NARRATOR_STRICT_ENABLED=false``. ADR-0068 removes
that rollback surface entirely:

- ``w5_ast_narrator_strict_enabled`` is no longer a public API.
- ``NarratorStrictOffDeprecationWarning`` is removed; no warning is emitted
  because there is no opt-out path left to deprecate.
- ``W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off`` does not change narrator
  source-facts behavior.
- ``source_facts.transition_from_previous`` and ``source_facts._legacy_compat``
  are absent from new narrator blocks.
- W5 projection remains the actor-situation authority in the manager-enriched
  narrator path; ``where_summary.location_changed`` is the location-shift
  signal, How is first-class, and inferred Why remains soft truth.
"""

from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path

import pytest


W5_FLAGS = (
    "W5_AST_DIRECTOR_PROJECTION_ENABLED",
    "W5_AST_NARRATOR_PROJECTION_ENABLED",
    "W5_AST_NPC_PROJECTION_ENABLED",
    "W5_AST_VALIDATION_ENABLED",
    "W5_AST_FRONTEND_PLAYER_VIEW_ENABLED",
    "W5_AST_NARRATOR_STRICT_ENABLED",
)


@pytest.fixture(autouse=True)
def _isolate_w5_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in W5_FLAGS:
        monkeypatch.delenv(name, raising=False)


class TestStrictOffPublicSurfaceRemoved:
    def test_warning_class_removed_from_diagnostics(self) -> None:
        import ai_stack.actor_tracking.diagnostics as diagnostics

        assert not hasattr(diagnostics, "NarratorStrictOffDeprecationWarning")
        assert "NarratorStrictOffDeprecationWarning" not in diagnostics.__all__

    def test_warning_class_removed_from_package(self) -> None:
        import ai_stack.actor_tracking as actor_tracking

        assert not hasattr(actor_tracking, "NarratorStrictOffDeprecationWarning")
        assert "NarratorStrictOffDeprecationWarning" not in actor_tracking.__all__

    def test_strict_resolver_removed_from_public_surfaces(self) -> None:
        import ai_stack.actor_tracking as actor_tracking
        import ai_stack.actor_tracking.diagnostics as diagnostics

        assert not hasattr(actor_tracking, "w5_ast_narrator_strict_enabled")
        assert not hasattr(diagnostics, "w5_ast_narrator_strict_enabled")
        assert "w5_ast_narrator_strict_enabled" not in actor_tracking.__all__
        assert "w5_ast_narrator_strict_enabled" not in diagnostics.__all__

    def test_projection_flag_states_no_longer_reports_strict_switch(self) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        states = w5_projection_flag_states()
        assert "narrator_strict" not in states
        assert states["narrator"] is True


class TestStrictEnvVarIsBehaviorallyInert:
    @pytest.mark.parametrize("value", ["false", "0", "no", "off", "", "true", "1"])
    def test_env_var_value_does_not_change_source_facts_shape(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
                session_output_language="de",
            )

        assert not [
            warning
            for warning in caught
            if warning.category.__name__ == "NarratorStrictOffDeprecationWarning"
        ]
        for block in opening["scene_blocks"]:
            facts = block["source_facts"]
            assert "transition_from_previous" not in facts
            assert "_legacy_compat" not in facts

    def test_unset_env_uses_same_source_facts_shape(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )

        for block in opening["scene_blocks"]:
            facts = block["source_facts"]
            assert "transition_from_previous" not in facts
            assert "_legacy_compat" not in facts


class TestADR0068PositiveRuntimeContracts:
    """ADR-0068 positive contracts: surfaces that MUST remain available.

    Phase 6B-8.1 verification: the narrator projection API remains the
    actor-situation authority and where_summary.location_changed is the
    location-shift signal. The actual source_facts.w5_projection enrichment
    for a live session is tested end-to-end by the world-engine parity tests
    (test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py); these tests
    verify the ai_stack-level contracts that underpin it.
    """

    def test_build_w5_projection_for_narrator_is_available(self) -> None:
        """source_facts.w5_projection is built by build_w5_projection_for_narrator.
        Verify the function is importable and returns a narrator-targeted projection.
        """
        from ai_stack.actor_tracking.projection import build_w5_projection_for_narrator

        minimal_snap = {
            "snapshot_id": "test",
            "story_session_id": "s1",
            "turn_number": 1,
            "created_at": "2026-01-01",
            "actors": {},
        }
        proj = build_w5_projection_for_narrator(minimal_snap)
        assert proj.target_consumer.value == "narrator", (
            "build_w5_projection_for_narrator must target the narrator consumer "
            "(ADR-0065 / ADR-0068)"
        )

    def test_where_summary_location_changed_available_in_projection(self) -> None:
        """where_summary.location_changed remains the sole location-shift signal
        after ADR-0068 removed source_facts.transition_from_previous.
        The detailed parity contract (True when locations differ) is pinned by
        test_w5_actor_tracking_projection.py::test_location_changed_true_when_snapshots_disagree_on_location.
        """
        from ai_stack.actor_tracking.projection import build_w5_projection_for_narrator

        minimal_snap = {
            "snapshot_id": "test",
            "story_session_id": "s1",
            "turn_number": 1,
            "created_at": "2026-01-01",
            "actors": {},
        }
        proj = build_w5_projection_for_narrator(minimal_snap)
        assert "location_changed" in proj.where_summary, (
            "where_summary.location_changed must remain available as the W5 "
            "location-shift signal (ADR-0068)"
        )


class TestInventoryClassifiesStrictOffTransitionAsRemoved:
    @staticmethod
    def _inventory_module():
        script_path = (
            Path(__file__).resolve().parents[2]
            / "scripts"
            / "inventory_w5_legacy_consumers.py"
        )
        spec = importlib.util.spec_from_file_location(
            "inventory_w5_legacy_consumers_6b8",
            script_path,
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["inventory_w5_legacy_consumers_6b8"] = module
        spec.loader.exec_module(module)
        return module

    def test_transition_from_previous_is_removed_by_adr_0068(self) -> None:
        module = self._inventory_module()

        classification = module.PHASE_6B4_CLASSIFICATION.get(
            "transition_from_previous",
            "",
        )
        assert "removed_by_adr_0068" in classification

    def test_historical_scanner_tracks_removed_surface(self) -> None:
        module = self._inventory_module()

        keys = {key for key, _ in module.LEGACY_SURFACES}
        assert "transition_from_previous" in keys
