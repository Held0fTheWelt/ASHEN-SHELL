"""Phase 6B-5B / 6B-8 — narrator strict-mode parity contract (ai_stack side).

Phase 6B-5B originally rewrote the parity contract before the Phase 6B-5C
default-on flip. ADR-0068 now makes strict mode permanent: explicit
``W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off`` is ignored.

These tests strengthen the existing ai_stack strict-migration coverage in:

- ``ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py``
- ``ai_stack/tests/test_god_of_carnage_narrator_path.py``

so permanent strict-on behavior is gated by *semantic* assertions, not
field-presence-only assertions. The world-engine-side end-to-end parity
contract lives in
``world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py``.

Scope of this file:

1. ``ai_stack.actor_tracking.w5_ast_narrator_strict_enabled`` is removed from
   the public surface.
2. ``ai_stack.actor_tracking.w5_projection_flag_states`` no longer reports a
   narrator strict switch.
3. ``ai_stack.story_runtime.narrator.god_of_carnage_narrator_path``:
   - ``source_facts["transition_from_previous"]`` is absent under every
     env value.
   - ``_legacy_compat`` remains absent (ADR-0066).
   - W5 projection is the sole actor-situation authority.
   - Canonical step ids, mandatory-beat coverage cues, and source_refs
     are unchanged by the strict flag — strict mode is a source-of-truth
     migration, not a content rewrite.
4. ``build_w5_projection_for_narrator`` carries Who / Where / What / How
   / Why summaries with semantically meaningful values and
   ``source_attribution`` / ``truth_attribution`` per fact path. The
   strict-on prompt names this projection as the actor-situation
   authority, so its semantic content is a Phase 6B-5B gate.

These tests do not weaken malformed-W5 fallback and do not mutate committed
events. How remains first-class. Inferred Why remains soft truth.
"""

from __future__ import annotations

from typing import Any

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
# 1) Strict resolver posture matrix — only forbidden package is forbidden
# ---------------------------------------------------------------------------


class TestPhase6B5BStrictResolverPosture:
    """Phase 6B-8 gate - the strict resolver surface is gone. The W5 module is
    imported only from ``ai_stack.actor_tracking``; the retired
    ``ai_stack.actor_situation`` / ``ai_stack.w5_actor_situation`` packages
    must not be importable."""

    def test_strict_resolver_removed_from_public_surface(self) -> None:
        import ai_stack.actor_tracking as actor_tracking
        import ai_stack.actor_tracking.diagnostics as diagnostics

        assert not hasattr(actor_tracking, "w5_ast_narrator_strict_enabled")
        assert not hasattr(diagnostics, "w5_ast_narrator_strict_enabled")
        assert "w5_ast_narrator_strict_enabled" not in actor_tracking.__all__
        assert "w5_ast_narrator_strict_enabled" not in diagnostics.__all__

    def test_retired_packages_are_not_importable(self) -> None:
        # Phase 6B-4 + ADR-0065 require these packages to remain absent.
        import importlib

        for retired in ("ai_stack.actor_situation", "ai_stack.w5_actor_situation"):
            with pytest.raises(ModuleNotFoundError):
                importlib.import_module(retired)

    @pytest.mark.parametrize(
        "value",
        ["", "  ", "garbage", "0", "false", "no", "off", "1", "true", "yes", "on"],
    )
    def test_env_values_do_not_recreate_strict_switch(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        """ADR-0068: the env var no longer has a behavior-changing resolver."""
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
        states = w5_projection_flag_states()
        assert "narrator_strict" not in states
        assert states["narrator"] is True

    # Phase 6B-6B: diagnostics flag retired — assert it is absent from flag_states

    def test_flag_states_no_legacy_compat_diagnostics_key(self) -> None:
        """Phase 6B-6B: w5_projection_flag_states must NOT include the retired
        narrator_legacy_compat_diagnostics key (ADR-0066)."""
        from ai_stack.actor_tracking import w5_projection_flag_states

        states = w5_projection_flag_states()
        assert "narrator_legacy_compat_diagnostics" not in states

    def test_legacy_compat_diagnostics_not_importable(self) -> None:
        """Phase 6B-6B: the retired symbol must not be importable from the
        package public API (ADR-0066)."""
        import ai_stack.actor_tracking as pkg

        assert not hasattr(pkg, "w5_ast_narrator_legacy_compat_diagnostics_enabled")


# ---------------------------------------------------------------------------
# 2) GoC narrator path — permanent strict-on source_facts shape
# ---------------------------------------------------------------------------


class TestPhase6B5BGoCNarratorPathSourceFactsShape:
    """Phase 6B-5B parity gate — the strict flag flips the *authority surface*
    inside ``source_facts``, but content references (canonical step ids,
    mandatory-beat coverage_cues, source_refs) remain identical. This
    reflects ADR-0065's "source-of-truth migration, not content rewrite"
    constraint."""

    def test_transition_from_previous_absent_under_any_env_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: transition_from_previous is never emitted regardless of env."""
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        for value in ("false", "0", "off", "true", "1"):
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", value)
            opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
                session_output_language="de",
            )
            blocks = opening["scene_blocks"]
            assert blocks
            for block in blocks:
                assert "transition_from_previous" not in block["source_facts"], (
                    f"ADR-0068: transition_from_previous must be absent for env value {value!r}"
                )
                assert "_legacy_compat" not in block["source_facts"]

    def test_strict_on_has_no_legacy_compat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase 6B-6B: strict-on must never include _legacy_compat or
        transition_from_previous. W5 projection is the sole authority (ADR-0066)."""
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        blocks = opening["scene_blocks"]
        assert blocks
        for block in blocks:
            facts = block["source_facts"]
            assert "transition_from_previous" not in facts, (
                "strict-on must not expose transition_from_previous at top level"
            )
            assert "_legacy_compat" not in facts, (
                "Phase 6B-6B: _legacy_compat breadcrumb path retired (ADR-0066)"
            )

    def test_strict_on_canonical_content_unchanged(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase 6B-6B: canonical beat ids present under strict-on even without
        legacy compat. W5 where_summary is the location-change authority."""
        from ai_stack.story_runtime.narrator import god_of_carnage_narrator_path

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        opening = god_of_carnage_narrator_path.build_goc_narrator_path_opening(
            session_output_language="de",
        )
        blocks = opening["scene_blocks"]
        for block in blocks:
            assert "_legacy_compat" not in block["source_facts"]
            assert "transition_from_previous" not in block["source_facts"]
        hard_cut_beats = [block["canonical_mandatory_beat_id"] for block in blocks]
        assert "room_perception_winter_light" in hard_cut_beats, (
            "Canonical beat content must be preserved after _legacy_compat removal"
        )

    def test_canonical_content_stable_across_env_values(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: canonical content is identical regardless of env var value.
        The strict-off rollback path no longer exists; all runs produce the same
        canonical step ids, block ids, source_refs, and mandatory_beat content."""

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
        assert with_false["source_refs"] == baseline["source_refs"]
        assert [block["id"] for block in with_false["scene_blocks"]] == [
            block["id"] for block in baseline["scene_blocks"]
        ]
        for a, b in zip(baseline["scene_blocks"], with_false["scene_blocks"]):
            assert a["canonical_mandatory_beat_id"] == b["canonical_mandatory_beat_id"]
            assert a["source_refs"] == b["source_refs"]
            assert a["source_facts"]["mandatory_beat"] == b["source_facts"]["mandatory_beat"]
            assert a["source_facts"]["module_context"] == b["source_facts"]["module_context"]
            assert a["text"] == b["text"]


# ---------------------------------------------------------------------------
# 3) W5 narrator projection — semantic five-summary authority content
# ---------------------------------------------------------------------------


def _projection_input_snapshot(
    *,
    turn: int,
    actor_id: str,
    location: str,
    current_action: str,
    tone: str,
    intensity: str = "rising",
    motive: str = "defend_son",
) -> dict[str, Any]:
    def _fact(
        fact_id: str,
        dimension: str,
        key: str,
        value: Any,
        source: str,
        truth: str,
        visibility: str = "public",
    ) -> dict[str, Any]:
        return {
            "schema_version": "w5_fact.v1",
            "fact_id": fact_id,
            "actor_id": actor_id,
            "dimension": dimension,
            "key": key,
            "value": value,
            "source": source,
            "source_event_id": f"ct_{turn:03d}",
            "truth_level": truth,
            "confidence": 1.0,
            "valid_from_turn": turn,
            "valid_until_turn": None,
            "last_confirmed_turn": turn,
            "visibility": visibility,
            "actor_knowledge_scope": [],
            "status": "active",
            "superseded_by_fact_id": None,
            "contradicted_by_fact_id": None,
        }

    return {
        "schema_version": "w5_snapshot.v1",
        "snapshot_id": f"w5s_6b5b_ai_{turn}",
        "story_session_id": "sess_phase_6b5b_ai_parity",
        "turn_number": turn,
        "actors": {
            actor_id: {
                "actor_id": actor_id,
                "actor_type": "human",
                "actor_role_in_scene": "aggressor",
                "involvement_type": "primary",
                "where": [
                    _fact(
                        f"w5f_w_{turn}",
                        "where",
                        "scene_location",
                        location,
                        "participant_state_move",
                        "observed",
                    )
                ],
                "what": [
                    _fact(
                        f"w5f_wact_{turn}",
                        "what",
                        "current_action",
                        current_action,
                        "committed_action",
                        "observed",
                    ),
                    _fact(
                        f"w5f_winter_{turn}",
                        "what",
                        "interaction_type",
                        "confrontation",
                        "committed_action",
                        "observed",
                    ),
                ],
                "how": [
                    _fact(
                        f"w5f_htone_{turn}",
                        "how",
                        "tone",
                        tone,
                        "committed_action",
                        "observed",
                    ),
                    _fact(
                        f"w5f_hint_{turn}",
                        "how",
                        "intensity",
                        intensity,
                        "director_composition",
                        "director_assigned",
                    ),
                ],
                "why": [
                    _fact(
                        f"w5f_wmot_{turn}",
                        "why",
                        "motive",
                        motive,
                        "character_mind_record",
                        "inferred",
                        visibility="private_to_actor",
                    )
                ],
                "freshness_status": "fresh",
                "last_confirmed_turn": turn,
            }
        },
        "conflicts": [],
        "derived_from_event_ids": [f"ct_{turn:03d}"],
        "created_at": f"w5:turn:{turn}",
    }


class TestPhase6B5BNarratorProjectionSemanticContent:
    """Phase 6B-5B parity gate — ``build_w5_projection_for_narrator`` must
    carry semantically meaningful Who / Where / What / How / Why content
    and full ``source_attribution`` / ``truth_attribution``. The strict-on
    prompt names this projection as the actor-situation authority, so its
    semantic content is a Phase 6B-5C readiness gate."""

    def _build(self) -> Any:
        from ai_stack.actor_tracking import build_w5_projection_for_narrator

        previous = _projection_input_snapshot(
            turn=2,
            actor_id="veronique",
            location="foyer",
            current_action="enters",
            tone="quiet",
        )
        current = _projection_input_snapshot(
            turn=3,
            actor_id="veronique",
            location="parlor",
            current_action="accuses",
            tone="sharp",
        )
        return build_w5_projection_for_narrator(
            current,
            actor_id="veronique",
            previous_snapshot=previous,
        ).to_dict()

    def test_who_summary_identifies_actor_and_role(self) -> None:
        proj = self._build()
        who = proj["who_summary"]
        assert who["actor_id"] == "veronique"
        assert who["actor_type"] == "human"
        assert who["actor_role_in_scene"] == "aggressor"
        assert who["involvement_type"] == "primary"

    def test_where_summary_supplies_current_previous_and_change(self) -> None:
        proj = self._build()
        where = proj["where_summary"]
        assert where["current_location"] == "parlor"
        assert where["previous_location"] == "foyer"
        assert where["location_changed"] is True
        assert where["facts"]["scene_location"] == "parlor"
        # The strict prompt's hard-cut replacement signal is derived from
        # these fields; the structural attribution must be present so admin
        # diagnostics can correlate.
        assert (
            proj["source_attribution"]["where_summary.location_changed"]
            == "derived_from_where_facts"
        )
        assert (
            proj["truth_attribution"]["where_summary.location_changed"]
            == "observed"
        )

    def test_what_summary_is_observed_action_not_polluted_by_how(self) -> None:
        proj = self._build()
        what_facts = proj["what_summary"]["facts"]
        assert what_facts["current_action"] == "accuses"
        assert what_facts["interaction_type"] == "confrontation"
        for how_key in ("tone", "intensity", "manner", "pace", "physicality"):
            assert how_key not in what_facts, (
                f"How attribute '{how_key}' must not appear under "
                "what_summary.facts; ADR-0063 / ADR-0065 keep How first-class"
            )

    def test_how_summary_is_first_class_with_per_fact_truth(self) -> None:
        proj = self._build()
        how_facts = proj["how_summary"]["facts"]
        assert how_facts["tone"] == "sharp"
        assert how_facts["intensity"] == "rising"
        # The per-fact truth attribution lets the narrator distinguish
        # director-assigned How from committed-action How.
        assert (
            proj["truth_attribution"]["how_summary.facts.tone"] == "observed"
        )
        assert (
            proj["truth_attribution"]["how_summary.facts.intensity"]
            == "director_assigned"
        )
        assert (
            proj["source_attribution"]["how_summary.facts.tone"]
            == "committed_action"
        )

    def test_why_summary_is_soft_inferred_truth(self) -> None:
        proj = self._build()
        why_facts = proj["why_summary"]["facts"]
        assert why_facts["motive"] == "defend_son"
        # ADR-0063 + ADR-0065: never observed.
        assert (
            proj["truth_attribution"]["why_summary.facts.motive"] == "inferred"
        )
        assert (
            proj["source_attribution"]["why_summary.facts.motive"]
            == "character_mind_record"
        )

    def test_observed_why_is_rejected_by_model(self) -> None:
        """Negative test: the dataclass forbids constructing OBSERVED Why
        facts. ADR-0063 + ADR-0065 invariant: inferred Why may never be
        promoted to observed truth without a separate engine-owned commit
        path."""

        from ai_stack.actor_tracking.models import (
            W5Dimension,
            W5Fact,
            W5FactStatus,
            W5Source,
            W5TruthLevel,
            W5VisibilityScope,
        )

        with pytest.raises(Exception):
            W5Fact(
                schema_version="w5_fact.v1",
                fact_id="bad",
                actor_id="veronique",
                dimension=W5Dimension.WHY,
                key="motive",
                value="defend_son",
                source=W5Source.COMMITTED_ACTION,
                source_event_id="ct_999",
                truth_level=W5TruthLevel.OBSERVED,
                confidence=1.0,
                valid_from_turn=3,
                valid_until_turn=None,
                last_confirmed_turn=3,
                visibility=W5VisibilityScope.PUBLIC,
                actor_knowledge_scope=(),
                status=W5FactStatus.ACTIVE,
                superseded_by_fact_id=None,
                contradicted_by_fact_id=None,
            )


# ---------------------------------------------------------------------------
# 4) Phase 6B-5B does not regress earlier gates
# ---------------------------------------------------------------------------


class TestPhase6B5BNonRegression:
    """Phase 6B-5B must not weaken Phase 6B-3B or Phase 6B-1 contracts."""

    def test_removed_strict_switch_is_independent_of_projection_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        # Projection flag toggled; the strict switch remains absent.
        for projection_value in ("0", "1", "false", "true", "off", "on"):
            monkeypatch.setenv("W5_AST_NARRATOR_PROJECTION_ENABLED", projection_value)
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
            assert "narrator_strict" not in w5_projection_flag_states()

    def test_strict_on_does_not_disable_other_w5_projections(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from ai_stack.actor_tracking import w5_projection_flag_states

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        states = w5_projection_flag_states()
        # Default-on Phase 6B-1 flags remain on under strict mode.
        assert states["narrator"] is True
        assert states["director"] is True
        assert states["npc"] is True
        assert "narrator_strict" not in states
