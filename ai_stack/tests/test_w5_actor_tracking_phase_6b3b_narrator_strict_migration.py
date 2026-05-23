"""Phase 6B-3B — narrator strict migration semantic tests (ai_stack side).

Pins the contract for the new opt-in narrator-strict flag
``W5_AST_NARRATOR_STRICT_ENABLED`` and the F8 source_facts migration in the
God-of-Carnage narrator path:

- Default-off (unset / empty / explicit ``0/false/no/off``) preserves the
  Phase 6B-3A behavior bit-for-bit: ``source_facts["transition_from_previous"]``
  remains first-class and ``_legacy_compat`` is absent.
- Explicit ``1/true/yes/on`` enables strict mode. ``transition_from_previous``
  is removed from the top-level ``source_facts`` contract and demoted to
  ``source_facts["_legacy_compat"]["transition_from_previous"]`` together with
  an ``authority`` marker and a ``notice`` string identifying the W5 narrator
  projection as authoritative.
- The strict flag does not alter the rest of the narrator path output:
  beat coverage, location resolution, mandatory beat coverage_cues, and
  ``hard_cut`` directed transitions remain intact.
- ``w5_ast_narrator_strict_enabled`` is reachable from the public
  ``ai_stack.actor_tracking`` package and from ``ai_stack.actor_tracking.diagnostics``.
- ``w5_projection_flag_states`` exposes the strict flag as ``narrator_strict``.

These tests do not weaken any existing W5 validation, Actor Lane, or
Canonical Path semantics. How remains first-class. Inferred Why remains soft
truth. No committed event is mutated by the strict flag.
"""

from __future__ import annotations

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
# W5_AST_NARRATOR_STRICT_ENABLED resolver — default-on opt-out (Phase 6B-5C)
# ---------------------------------------------------------------------------


class TestNarratorStrictFlagResolver:
    def test_resolver_default_on_when_env_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        assert w5_ast_narrator_strict_enabled() is True

    def test_resolver_default_on_when_env_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "")
        assert w5_ast_narrator_strict_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "FALSE", "Off"])
    def test_resolver_explicit_off_keeps_legacy_compatible_behavior(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        assert w5_ast_narrator_strict_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", "On"])
    def test_resolver_explicit_on_enables_strict_mode(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        assert w5_ast_narrator_strict_enabled() is True

    def test_resolver_independent_of_projection_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Toggling W5_AST_NARRATOR_PROJECTION_ENABLED does not affect strict."""

        from ai_stack.actor_tracking import w5_ast_narrator_strict_enabled

        for projection_value in ("0", "1", "false", "true", "off", "on"):
            monkeypatch.setenv("W5_AST_NARRATOR_PROJECTION_ENABLED", projection_value)
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
            assert w5_ast_narrator_strict_enabled() is True

    def test_strict_flag_exposed_via_projection_flag_states(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        assert w5_projection_flag_states()["narrator_strict"] is True
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        assert w5_projection_flag_states()["narrator_strict"] is False


# ---------------------------------------------------------------------------
# F8 — narrator path source_facts contract under strict flag
# ---------------------------------------------------------------------------


class TestF8NarratorPathSourceFactsContract:
    """Pins the ``source_facts.transition_from_previous`` migration in
    ``ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py``."""

    def test_strict_off_explicit_off_keeps_transition_from_previous_first_class(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        blocks = opening["scene_blocks"]
        assert blocks, "expected narrator opening blocks"
        first = blocks[0]
        assert "transition_from_previous" in first["source_facts"], (
            "Phase 6B-3B strict-OFF (explicit opt-out) must preserve legacy "
            "first-class transition_from_previous in source_facts."
        )
        assert first["source_facts"]["transition_from_previous"]["kind"] == "opening_start"
        # Legacy compatibility breadcrumb is absent in unstrict mode.
        assert "_legacy_compat" not in first["source_facts"]

    def test_strict_off_explicit_false_keeps_transition_from_previous_first_class(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        for block in opening["scene_blocks"]:
            assert "transition_from_previous" in block["source_facts"]
            assert "_legacy_compat" not in block["source_facts"]

    def test_strict_on_default_removes_transition_and_legacy_compat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase 6B-6B: strict-on never produces transition_from_previous at top
        level or _legacy_compat. W5 projection is the sole authority (ADR-0066)."""
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        for block in opening["scene_blocks"]:
            facts = block["source_facts"]
            assert "transition_from_previous" not in facts, (
                "strict-on must remove transition_from_previous from top-level source_facts."
            )
            assert "_legacy_compat" not in facts, (
                "Phase 6B-6B: _legacy_compat breadcrumb path retired (ADR-0066)."
            )

    def test_strict_on_preserves_canonical_step_and_beat_coverage(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Strict mode is a source-of-truth migration, not a content rewrite.

        The same canonical step IDs and mandatory-beat coverage that the
        unstrict opening produces must be present under strict mode.
        """
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        unstrict = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        strict = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )

        assert strict["canonical_step_ids"] == unstrict["canonical_step_ids"]
        assert [block["id"] for block in strict["scene_blocks"]] == [
            block["id"] for block in unstrict["scene_blocks"]
        ]
        assert [block["canonical_mandatory_beat_id"] for block in strict["scene_blocks"]] == [
            block["canonical_mandatory_beat_id"] for block in unstrict["scene_blocks"]
        ]
        # Mandatory-beat coverage_cues survive strict mode (How and Why hooks
        # in source_facts.mandatory_beat are untouched).
        for strict_block, unstrict_block in zip(strict["scene_blocks"], unstrict["scene_blocks"]):
            assert (
                strict_block["source_facts"]["mandatory_beat"]
                == unstrict_block["source_facts"]["mandatory_beat"]
            )


# ---------------------------------------------------------------------------
# Phase 6B-3B does not weaken existing W5 contracts
# ---------------------------------------------------------------------------


class TestPhase6B3BNonRegression:
    def test_strict_flag_does_not_remove_projection_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        monkeypatch.delenv("W5_AST_NARRATOR_PROJECTION_ENABLED", raising=False)
        states = w5_projection_flag_states()
        # Phase 6B-1 default-on Narrator projection flag is independent.
        assert states["narrator"] is True
        assert states["narrator_strict"] is True

    def test_strict_flag_does_not_alter_director_or_npc_projection_flags(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        monkeypatch.delenv("W5_AST_DIRECTOR_PROJECTION_ENABLED", raising=False)
        monkeypatch.delenv("W5_AST_NPC_PROJECTION_ENABLED", raising=False)
        states = w5_projection_flag_states()
        assert states["director"] is True
        assert states["npc"] is True
