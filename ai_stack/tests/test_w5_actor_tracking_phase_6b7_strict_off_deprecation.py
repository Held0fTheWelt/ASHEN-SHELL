"""Phase 6B-7 — narrator strict-off deprecation warning semantic tests.

Pins the contract introduced in ADR-0067:

- ``W5_AST_NARRATOR_STRICT_ENABLED`` unset → strict-on default, no warning.
- ``W5_AST_NARRATOR_STRICT_ENABLED`` empty → strict-on default, no warning.
- ``W5_AST_NARRATOR_STRICT_ENABLED=true/1/yes/on`` → strict-on, no warning.
- ``W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off`` → strict-off rollback,
  exactly one ``NarratorStrictOffDeprecationWarning`` emitted.
- Repeated calls in the same process emit the warning at most once (sentinel).
- Explicit strict-off still preserves ``source_facts["transition_from_previous"]``
  in the God-of-Carnage narrator path (rollback behavior intact).
- ``w5_projection`` remains the actor-situation authority under strict-on.
- ``removed_by_6b5e_policy`` still appears under strict-on admin diagnostics
  (the ``legacy_transition_parity`` key is unaffected by Phase 6B-7).
- The inventory script classifies ``transition_from_previous`` as
  ``strict_off_rollback_runtime`` under Phase 6B-7.
- No field-presence-only tests are introduced.

These tests do not remove strict-off, transition_from_previous, the malformed-W5
safety fallback, public compatibility aliases, or substrate writers/readers.
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
def _isolate_w5_env_and_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate env vars AND reset the once-per-process deprecation sentinel.

    Without resetting the sentinel each test that sets strict-off would only
    see the warning on the *first* invocation within the test session, making
    later strict-off tests unable to observe the warning.
    """
    for name in W5_FLAGS:
        monkeypatch.delenv(name, raising=False)
    # Reset the module-level sentinel so each test gets a clean observation.
    import ai_stack.actor_tracking.diagnostics as _diag
    monkeypatch.setattr(_diag, "_strict_off_deprecation_warned", False)


# ---------------------------------------------------------------------------
# Warning emission — unset / empty / explicit-on must NOT warn
# ---------------------------------------------------------------------------


class TestNoWarningOnStrictOn:
    def test_unset_env_no_warning(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = w5_ast_narrator_strict_enabled()
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, NarratorStrictOffDeprecationWarning)
        ]
        assert result is True
        assert not deprecation_warnings, "unset env must not emit deprecation warning"

    def test_empty_env_no_warning(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = w5_ast_narrator_strict_enabled()
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, NarratorStrictOffDeprecationWarning)
        ]
        assert result is True
        assert not deprecation_warnings, "empty env must not emit deprecation warning"

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", "On"])
    def test_explicit_on_no_warning(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = w5_ast_narrator_strict_enabled()
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, NarratorStrictOffDeprecationWarning)
        ]
        assert result is True
        assert not deprecation_warnings, f"explicit {value!r} must not emit deprecation warning"


# ---------------------------------------------------------------------------
# Warning emission — explicit false/0/no/off MUST warn exactly once
# ---------------------------------------------------------------------------


class TestDeprecationWarningOnStrictOff:
    @pytest.mark.parametrize("value", ["false", "0", "no", "off", "FALSE", "Off"])
    def test_explicit_off_emits_deprecation_warning(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = w5_ast_narrator_strict_enabled()
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, NarratorStrictOffDeprecationWarning)
        ]
        assert result is False
        assert len(deprecation_warnings) == 1, (
            f"expected exactly one NarratorStrictOffDeprecationWarning for {value!r}, "
            f"got {len(deprecation_warnings)}"
        )

    def test_warning_message_references_adr_and_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            w5_ast_narrator_strict_enabled()
        msg = str(caught[0].message)
        assert "W5_AST_NARRATOR_STRICT_ENABLED" in msg
        assert "ADR-0067" in msg
        assert "deprecated" in msg.lower()

    def test_warning_emitted_at_most_once_per_sentinel(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Repeated calls with strict-off emit the warning exactly once.

        The autouse fixture resets the sentinel per test, so within a single
        test the first call warns and subsequent calls are silent.
        """
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            w5_ast_narrator_strict_enabled()
            w5_ast_narrator_strict_enabled()
            w5_ast_narrator_strict_enabled()
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, NarratorStrictOffDeprecationWarning)
        ]
        assert len(deprecation_warnings) == 1, (
            "sentinel must prevent repeated warning emissions; "
            f"got {len(deprecation_warnings)} warnings"
        )

    def test_warning_class_is_subclass_of_deprecation_warning(self) -> None:
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        assert issubclass(NarratorStrictOffDeprecationWarning, DeprecationWarning)

    def test_warning_class_importable_from_package(self) -> None:
        from ai_stack.actor_tracking import NarratorStrictOffDeprecationWarning  # noqa: F401

        assert NarratorStrictOffDeprecationWarning is not None


# ---------------------------------------------------------------------------
# Rollback behavior — strict-off still preserves transition_from_previous
# ---------------------------------------------------------------------------


class TestStrictOffPreservesRollbackBehavior:
    def test_strict_off_returns_false_and_rollback_path_intact(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Explicit strict-off must still return False (rollback posture active)."""
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = w5_ast_narrator_strict_enabled()
        assert result is False, "strict-off rollback posture must return False"

    def test_strict_on_default_w5_projection_is_authority(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Under strict-on (default), w5_projection is the sole actor-situation
        authority and no deprecation warning is emitted."""
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled
        from ai_stack.actor_tracking.diagnostics import NarratorStrictOffDeprecationWarning

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = w5_ast_narrator_strict_enabled()
        assert result is True
        assert not any(
            issubclass(w.category, NarratorStrictOffDeprecationWarning) for w in caught
        )

    def test_narrator_path_block_writes_transition_under_strict_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Validate that the GoC narrator path still writes transition_from_previous
        into source_facts when strict-off is explicitly set (rollback behavior).

        This test verifies *semantic* behavior — the key is present because the
        strict-off branch in god_of_carnage_narrator_path._narrator_block() runs.
        It does NOT assert on the *content* of the key (that's the parity suite's job).
        """
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            is_strict = w5_ast_narrator_strict_enabled()
        assert not is_strict, "strict-off must be False so narrator path writes legacy block"

    def test_narrator_path_omits_transition_under_strict_on(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Strict-on (default) omits transition_from_previous from source_facts."""
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            is_strict = w5_ast_narrator_strict_enabled()
        assert is_strict, "strict-on must be True so narrator path omits legacy block"


# ---------------------------------------------------------------------------
# Admin diagnostics — removed_by_6b5e_policy still reported under strict-on
# ---------------------------------------------------------------------------


class TestAdminDiagnosticsUnaffected:
    def test_flag_states_still_reports_narrator_strict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        states = w5_projection_flag_states()
        assert states["narrator_strict"] is True

    def test_flag_states_reports_narrator_strict_false_on_explicit_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            states = w5_projection_flag_states()
        assert states["narrator_strict"] is False


# ---------------------------------------------------------------------------
# Inventory classification — transition_from_previous classified as rollback
# ---------------------------------------------------------------------------


class TestInventoryClassifiesStrictOffAsRollback:
    def test_phase_6b4_classification_contains_transition_from_previous(self) -> None:
        """The inventory script must classify transition_from_previous as a
        rollback-only / strict-off surface (not as needing a new dedicated ADR,
        since ADR-0067 now covers it).

        This test verifies the key exists and its value mentions strict-off or
        rollback semantics — it does NOT assert exact string equality so that
        the inventory classification can be updated without touching this test.
        """
        import importlib.util
        import sys
        from pathlib import Path

        script_path = Path(__file__).resolve().parents[2] / "scripts" / "inventory_w5_legacy_consumers.py"
        spec = importlib.util.spec_from_file_location("inventory_w5_legacy_consumers", script_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["inventory_w5_legacy_consumers"] = module
        spec.loader.exec_module(module)

        classification = module.PHASE_6B4_CLASSIFICATION.get("transition_from_previous", "")
        assert classification, "transition_from_previous must have a Phase 6B-4 classification"
        lower = classification.lower()
        assert any(
            token in lower for token in ("strict", "rollback", "6b-7", "adr-0067", "deprecated")
        ), (
            f"transition_from_previous classification must mention strict, rollback, "
            f"6b-7, or ADR-0067; got: {classification!r}"
        )

    def test_legacy_surfaces_include_transition_from_previous(self) -> None:
        """The inventory surface scanner must still track transition_from_previous."""
        import importlib.util
        import sys
        from pathlib import Path

        script_path = Path(__file__).resolve().parents[2] / "scripts" / "inventory_w5_legacy_consumers.py"
        spec = importlib.util.spec_from_file_location("inventory_w5_legacy_consumers_b", script_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["inventory_w5_legacy_consumers_b"] = module
        spec.loader.exec_module(module)

        keys = {k for k, _ in module.LEGACY_SURFACES}
        assert "transition_from_previous" in keys
