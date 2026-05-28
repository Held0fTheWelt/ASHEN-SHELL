"""Phase 6B-3B / 6B-8 — narrator strict migration semantic tests (ai_stack side).

Pins the F8 source_facts contract after ADR-0068 made narrator strict mode
permanent:

- ``W5_AST_NARRATOR_STRICT_ENABLED`` is retained only as an inert compatibility
  env-var name; false/0/no/off no longer changes behavior.
- ``transition_from_previous`` is absent from new narrator source_facts under
  every env value, and ``_legacy_compat`` remains absent.
- The permanent strict path does not alter the rest of the narrator path output:
  beat coverage, location resolution, mandatory beat coverage_cues, and
  canonical hard-cut beat identity remain intact.
- ``w5_ast_narrator_strict_enabled`` is no longer a public API.
- ``w5_projection_flag_states`` no longer exposes a narrator strict switch.

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
# W5_AST_NARRATOR_STRICT_ENABLED resolver removed (ADR-0068)
# ---------------------------------------------------------------------------


class TestNarratorStrictFlagResolverRemoved:
    def test_resolver_removed_from_package(self) -> None:
        import ai_stack.actor_tracking as actor_tracking

        assert not hasattr(actor_tracking, "w5_ast_narrator_strict_enabled")
        assert "w5_ast_narrator_strict_enabled" not in actor_tracking.__all__

    def test_resolver_removed_from_diagnostics(self) -> None:
        import ai_stack.actor_tracking.diagnostics as diagnostics

        assert not hasattr(diagnostics, "w5_ast_narrator_strict_enabled")
        assert "w5_ast_narrator_strict_enabled" not in diagnostics.__all__

    def test_strict_switch_not_reported_by_projection_flag_states(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        states = w5_projection_flag_states()
        assert "narrator_strict" not in states
        assert states["narrator"] is True


# ---------------------------------------------------------------------------
# F8 — narrator path source_facts contract under strict flag
# ---------------------------------------------------------------------------


class TestF8NarratorPathSourceFactsContract:
    """Pins the ``source_facts.transition_from_previous`` migration in
    ``ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py``."""

    def test_transition_from_previous_absent_under_explicit_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: transition_from_previous is absent even when env is 'false'."""
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        blocks = opening["scene_blocks"]
        assert blocks, "expected narrator opening blocks"
        for block in blocks:
            assert "transition_from_previous" not in block["source_facts"], (
                "ADR-0068: transition_from_previous must be absent regardless of env value"
            )
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

    def test_canonical_content_identical_regardless_of_env_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: canonical content is identical regardless of env var value.
        All runs produce the same step ids, block ids, beat ids, and mandatory_beat content.
        """
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        baseline = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        with_false = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )

        assert with_false["canonical_step_ids"] == baseline["canonical_step_ids"]
        assert [block["id"] for block in with_false["scene_blocks"]] == [
            block["id"] for block in baseline["scene_blocks"]
        ]
        assert [block["canonical_mandatory_beat_id"] for block in with_false["scene_blocks"]] == [
            block["canonical_mandatory_beat_id"] for block in baseline["scene_blocks"]
        ]
        for a, b in zip(baseline["scene_blocks"], with_false["scene_blocks"]):
            assert a["source_facts"]["mandatory_beat"] == b["source_facts"]["mandatory_beat"]


# ---------------------------------------------------------------------------
# Phase 6B-3B does not weaken existing W5 contracts
# ---------------------------------------------------------------------------


class TestPhase6B3BNonRegression:
    def test_removed_strict_switch_does_not_remove_projection_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        monkeypatch.delenv("W5_AST_NARRATOR_PROJECTION_ENABLED", raising=False)
        states = w5_projection_flag_states()
        # Phase 6B-1 default-on Narrator projection flag is independent.
        assert states["narrator"] is True
        assert "narrator_strict" not in states

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
