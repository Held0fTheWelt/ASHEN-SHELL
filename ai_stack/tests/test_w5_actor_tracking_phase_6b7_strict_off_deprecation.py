"""Phase 6B-8 (ADR-0068) — narrator strict mode is permanent.

ADR-0067 deprecated W5_AST_NARRATOR_STRICT_ENABLED=false. ADR-0068 removed the
strict-off rollback path entirely. This file was previously the Phase 6B-7
deprecation-warning contract; it has been rewritten for Phase 6B-8 to pin the
permanent-strict-on contract:

- ``w5_ast_narrator_strict_enabled()`` is unconditionally True regardless of the
  env-var value; the env-var no longer changes narrator behavior.
- ``NarratorStrictOffDeprecationWarning`` exists as a tombstone (import compat)
  but is never emitted.
- No deprecation warning is emitted for any env value.
- ``source_facts["transition_from_previous"]`` is absent from narrator blocks
  under all postures.
- ``_legacy_compat`` remains absent (ADR-0066).
- ``w5_projection`` remains the actor-situation authority.
- ``where_summary.location_changed`` remains the location-shift signal.
- How remains first-class. Inferred Why remains soft truth.
- Inventory classifies ``transition_from_previous`` as removed_by_adr_0068.

These tests do not weaken ADR-0033, ADR-0061, ADR-0063, ADR-0065, ADR-0066,
ADR-0067, W5 validation, Actor Lane, Commit/Readiness, the Canonical Path,
public compatibility aliases, or substrate writers/readers.
"""

from __future__ import annotations

import importlib
import warnings

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


# ---------------------------------------------------------------------------
# Tombstone import compatibility — NarratorStrictOffDeprecationWarning exists
# ---------------------------------------------------------------------------


class TestNarratorStrictOffTombstone:
    def test_warning_class_still_importable_from_diagnostics(self) -> None:
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning
        assert NarratorStrictOffDeprecationWarning is not None

    def test_warning_class_still_importable_from_package(self) -> None:
        from ai_stack.actor_tracking import NarratorStrictOffDeprecationWarning
        assert NarratorStrictOffDeprecationWarning is not None

    def test_warning_class_is_subclass_of_deprecation_warning(self) -> None:
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning
        assert issubclass(NarratorStrictOffDeprecationWarning, DeprecationWarning)


# ---------------------------------------------------------------------------
# Unconditional strict-on — env var no longer changes behavior
# ---------------------------------------------------------------------------


class TestUnconditionalStrictOn:
    def test_unset_env_returns_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        assert w5_ast_narrator_strict_enabled() is True

    def test_empty_env_returns_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "")
        assert w5_ast_narrator_strict_enabled() is True

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", "On"])
    def test_explicit_on_returns_true(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        assert w5_ast_narrator_strict_enabled() is True

    @pytest.mark.parametrize("value", ["false", "0", "no", "off", "FALSE", "Off"])
    def test_explicit_off_still_returns_true_after_adr_0068(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        """ADR-0068: explicit false/0/no/off no longer changes narrator behavior."""
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        assert w5_ast_narrator_strict_enabled() is True

    def test_flag_states_narrator_strict_always_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states
        for value in ("false", "0", "no", "off", "", "true", "1"):
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
            assert w5_projection_flag_states()["narrator_strict"] is True

    def test_flag_states_narrator_strict_true_when_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states
        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        assert w5_projection_flag_states()["narrator_strict"] is True


# ---------------------------------------------------------------------------
# No deprecation warning — tombstone class is never emitted
# ---------------------------------------------------------------------------


class TestNoDeprecationWarningEmitted:
    @pytest.mark.parametrize("value", ["false", "0", "no", "off", "FALSE", "Off", "", "true", "1"])
    def test_no_warning_for_any_env_value(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            w5_ast_narrator_strict_enabled()
        assert not any(
            issubclass(w.category, NarratorStrictOffDeprecationWarning) for w in caught
        ), f"tombstone warning class must never be emitted; got warnings for value {value!r}"

    def test_no_warning_when_env_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            w5_ast_narrator_strict_enabled()
        assert not any(
            issubclass(w.category, NarratorStrictOffDeprecationWarning) for w in caught
        )


# ---------------------------------------------------------------------------
# source_facts — transition_from_previous absent under all postures
# ---------------------------------------------------------------------------


class TestTransitionFromPreviousAbsent:
    @pytest.mark.parametrize("value", ["false", "0", "no", "off", "true", "1"])
    def test_narrator_path_blocks_never_have_transition_from_previous(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        for block in opening["scene_blocks"]:
            assert "transition_from_previous" not in block["source_facts"], (
                f"ADR-0068: transition_from_previous must be absent under any "
                f"W5_AST_NARRATOR_STRICT_ENABLED={value!r}"
            )

    def test_narrator_path_blocks_never_have_legacy_compat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        for block in opening["scene_blocks"]:
            assert "_legacy_compat" not in block["source_facts"], (
                "Phase 6B-6B / ADR-0066: _legacy_compat breadcrumb must remain absent"
            )


# ---------------------------------------------------------------------------
# w5_projection authority — where_summary.location_changed is the signal
# ---------------------------------------------------------------------------


class TestW5ProjectionAuthority:
    def test_strict_on_returns_true_w5_projection_is_authority(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        assert w5_ast_narrator_strict_enabled() is True


# ---------------------------------------------------------------------------
# Inventory classification — transition_from_previous is removed_by_adr_0068
# ---------------------------------------------------------------------------


class TestInventoryClassifiesTransitionAsRemoved:
    def test_phase_6b4_classification_marks_transition_removed(self) -> None:
        import importlib.util
        import sys
        from pathlib import Path

        script_path = Path(__file__).resolve().parents[2] / "scripts" / "inventory_w5_legacy_consumers.py"
        spec = importlib.util.spec_from_file_location("inventory_w5_legacy_consumers_6b8", script_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["inventory_w5_legacy_consumers_6b8"] = module
        spec.loader.exec_module(module)

        classification = module.PHASE_6B4_CLASSIFICATION.get("transition_from_previous", "")
        assert classification, "transition_from_previous must have a Phase 6B-4 classification"
        lower = classification.lower()
        assert any(
            token in lower
            for token in ("removed", "adr_0068", "adr-0068", "6b-8", "6b8")
        ), (
            f"transition_from_previous classification must mention removal or ADR-0068; "
            f"got: {classification!r}"
        )

    def test_legacy_surfaces_still_tracks_transition_from_previous(self) -> None:
        import importlib.util
        import sys
        from pathlib import Path

        script_path = Path(__file__).resolve().parents[2] / "scripts" / "inventory_w5_legacy_consumers.py"
        spec = importlib.util.spec_from_file_location("inventory_w5_legacy_consumers_6b8b", script_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["inventory_w5_legacy_consumers_6b8b"] = module
        spec.loader.exec_module(module)

        keys = {k for k, _ in module.LEGACY_SURFACES}
        assert "transition_from_previous" in keys, (
            "scanner still tracks transition_from_previous to detect "
            "doc/test-historical references after removal"
        )
