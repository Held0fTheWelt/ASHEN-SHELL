"""Phase 6B-5B / 6B-8 — narrator strict-mode parity contract (world-engine side).

Phase 6B-5B originally rewrote the test contract before the Phase 6B-5C
default-on flip. ADR-0068 now makes strict mode permanent:
``W5_AST_NARRATOR_STRICT_ENABLED=false/0/no/off`` is ignored.

These tests strengthen — rather than replace — the existing strict-migration
coverage in:

- ``world-engine/tests/test_story_runtime_w5_narrator_projection.py``
- ``world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py``
- ``ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py``

The Phase 6B-8 gate is semantic and end-to-end:

   - ``source_facts["transition_from_previous"]`` is removed from the
     top-level narrator contract.
   - ``source_facts._legacy_compat`` remains absent (ADR-0066).
   - The narrator prompt:

     - explicitly treats ``source_facts.w5_projection`` as the *sole*
       actor-situation authority;
     - explicitly tells the narrator *not* to consult
       ``source_facts.transition_from_previous``;
     - mentions every W5 summary (``who_summary``, ``where_summary``,
       ``what_summary``, ``how_summary``, ``why_summary``) by name;
     - keeps How first-class with manner/tone/intensity/pace/physicality/
       method/style attributes;
     - marks inferred Why as soft / never-spoken-as-fact;
     - uses ``where_summary.location_changed`` (not the legacy
       ``transition_from_previous.location_changed``) as the scene-shift
       steering signal — i.e. the hard-cut / directed-transition
       replacement signal lives on the W5 projection.

   - W5 ``where_summary`` semantically supplies ``current_location``,
     ``previous_location``, and ``location_changed``.
   - W5 ``what_summary`` carries observed action/interaction facts without
     absorbing How (no ``tone`` / ``intensity`` / ``manner`` leak into
     ``what_summary.facts``).
   - W5 ``how_summary`` is first-class with semantically meaningful values
     and a ``how_summary.facts.*`` ``truth_attribution`` per fact.
   - W5 ``why_summary`` carries inferred motive only, with
     ``truth_attribution`` marked ``inferred`` (never ``observed``).
   - Admin diagnostics expose
     ``w5.location_changed_source = w5_history_projection`` (W5-first) and do
     not expose narrator strict/parity compatibility metadata.

The tests below assert semantic content, not field-presence-only. They do not
weaken malformed-W5 fallback, and they do not mutate committed output.

How remains first-class. Inferred Why remains soft truth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from world_engine.story_runtime.manager import StoryRuntimeManager, StorySession


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
# Helpers - typed W5 snapshot + GoC-shaped narrator block
# ---------------------------------------------------------------------------


def _w5_fact(
    *,
    fact_id: str,
    actor_id: str,
    dimension: str,
    key: str,
    value: Any,
    source: str,
    truth: str,
    turn: int,
    visibility: str = "public",
    scope: tuple[str, ...] = (),
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
        "actor_knowledge_scope": list(scope),
        "status": "active",
        "superseded_by_fact_id": None,
        "contradicted_by_fact_id": None,
    }


def _w5_snapshot(
    *,
    turn: int,
    actor_id: str,
    location: str,
    current_action: str = "speaks",
    interaction_type: str = "confrontation",
    tone: str = "measured",
    intensity: str = "rising",
    motive: str = "defend_son",
) -> dict[str, Any]:
    return {
        "schema_version": "w5_snapshot.v1",
        "snapshot_id": f"w5s_6b5b_{turn}",
        "story_session_id": "sess_phase_6b5b_parity",
        "turn_number": turn,
        "actors": {
            actor_id: {
                "actor_id": actor_id,
                "actor_type": "human",
                "actor_role_in_scene": "aggressor",
                "involvement_type": "primary",
                "where": [
                    _w5_fact(
                        fact_id=f"w5f_w_{turn}",
                        actor_id=actor_id,
                        dimension="where",
                        key="scene_location",
                        value=location,
                        source="participant_state_move",
                        truth="observed",
                        turn=turn,
                    ),
                ],
                "what": [
                    _w5_fact(
                        fact_id=f"w5f_what_action_{turn}",
                        actor_id=actor_id,
                        dimension="what",
                        key="current_action",
                        value=current_action,
                        source="committed_action",
                        truth="observed",
                        turn=turn,
                    ),
                    _w5_fact(
                        fact_id=f"w5f_what_inter_{turn}",
                        actor_id=actor_id,
                        dimension="what",
                        key="interaction_type",
                        value=interaction_type,
                        source="committed_action",
                        truth="observed",
                        turn=turn,
                    ),
                ],
                "how": [
                    _w5_fact(
                        fact_id=f"w5f_how_tone_{turn}",
                        actor_id=actor_id,
                        dimension="how",
                        key="tone",
                        value=tone,
                        source="committed_action",
                        truth="observed",
                        turn=turn,
                    ),
                    _w5_fact(
                        fact_id=f"w5f_how_int_{turn}",
                        actor_id=actor_id,
                        dimension="how",
                        key="intensity",
                        value=intensity,
                        source="director_composition",
                        truth="director_assigned",
                        turn=turn,
                    ),
                ],
                "why": [
                    _w5_fact(
                        fact_id=f"w5f_why_motive_{turn}",
                        actor_id=actor_id,
                        dimension="why",
                        key="motive",
                        value=motive,
                        source="character_mind_record",
                        truth="inferred",
                        turn=turn,
                        visibility="private_to_actor",
                    ),
                ],
                "freshness_status": "fresh",
                "last_confirmed_turn": turn,
            }
        },
        "conflicts": [],
        "derived_from_event_ids": [f"ct_{turn:03d}"],
        "created_at": f"w5:turn:{turn}",
    }


def _make_session(
    *,
    actor_id: str = "veronique",
    previous_location: str = "foyer",
    current_location: str = "parlor",
) -> StorySession:
    previous = _w5_snapshot(
        turn=2,
        actor_id=actor_id,
        location=previous_location,
        current_action="enters",
        tone="quiet",
    )
    current = _w5_snapshot(
        turn=3,
        actor_id=actor_id,
        location=current_location,
        current_action="accuses",
        tone="sharp",
    )
    return StorySession(
        session_id="sess_phase_6b5b_parity",
        module_id="god_of_carnage",
        runtime_projection={"human_actor_id": actor_id},
        created_at=datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 22, 12, 0, 5, tzinfo=timezone.utc),
        turn_counter=3,
        current_scene_id="opening",
        w5_history=[previous, current],
        w5_latest_snapshot=current,
    )


def _source_narrator_block() -> dict[str, Any]:
    """A narrator block with ADR-0068 source_facts shape."""

    return {
        "id": "phase-6b5b-narrator-1",
        "block_type": "narrator",
        "speaker_label": "Narrator",
        "actor_id": None,
        "target_actor_id": None,
        "text": "...",
        "canonical_step_id": "opening_004_room_perception_winter_light",
        "canonical_mandatory_beat_id": "room_perception_winter_light",
        "source_facts": {
            "location": {"id": "parlor"},
        },
    }


def _strict_clean_block() -> dict[str, Any]:
    """A narrator block as emitted under strict-on + diagnostics flag OFF
    (Phase 6B-5E default): no ``_legacy_compat``, no ``transition_from_previous``."""

    return {
        "id": "phase-6b5e-narrator-1",
        "block_type": "narrator",
        "speaker_label": "Narrator",
        "actor_id": None,
        "target_actor_id": None,
        "text": "...",
        "canonical_step_id": "opening_004_room_perception_winter_light",
        "canonical_mandatory_beat_id": "room_perception_winter_light",
        "source_facts": {
            "location": {"id": "parlor"},
        },
    }


def _enrich(session: StorySession, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Invoke the W5 narrator-projection enrichment helper without booting
    the full StoryRuntimeManager."""

    class _Proxy:
        _w5_ast_narrator_projection_enabled = staticmethod(
            StoryRuntimeManager._w5_ast_narrator_projection_enabled
        )

    return StoryRuntimeManager._maybe_enrich_blocks_with_w5_narrator_projection(
        _Proxy(),  # type: ignore[arg-type]
        session=session,
        source_blocks=blocks,
    )


def _build_narrator_prompt(target_language: str = "de") -> str:
    return StoryRuntimeManager._narrator_path_output_prompt(
        source_blocks=[_source_narrator_block()],
        narrator_path={
            "source_input_mode": "semantic_frames_with_fallback_blocks",
            "path_id": "goc_opening_canonical_path",
            "canonical_step_ids": ["opening_004_room_perception_winter_light"],
            "narrative_source_frames": [],
        },
        source_language="en",
        target_language=target_language,
    )


class _AdminParityHarness:
    """Minimal harness exposing ``get_w5_langfuse_metadata`` without booting
    the full manager — same approach as the Phase 6B-3B F20 tests."""

    def __init__(self, session: StorySession) -> None:
        self._session = session

    def get_session(self, session_id: str) -> StorySession:
        assert session_id == self._session.session_id
        return self._session

    _latest_w5_validation_outcome = staticmethod(
        StoryRuntimeManager._latest_w5_validation_outcome
    )
    get_w5_langfuse_metadata = (  # type: ignore[assignment]
        StoryRuntimeManager.get_w5_langfuse_metadata
    )


# ---------------------------------------------------------------------------
# 1) W5 projection authoritative content (independent of strict flag)
# ---------------------------------------------------------------------------


class TestPhase6B5BW5ProjectionSemanticAuthority:
    """Phase 6B-5B parity gate — the W5 narrator projection that the
    strict-on prompt names as the actor-situation authority must carry
    *semantically meaningful* Who / Where / What / How / Why content with
    full source/truth attribution. These assertions hold under every value of
    the retired strict env var because ADR-0068 removed the posture switch."""

    @pytest.mark.parametrize("strict_value", [None, "false", "true"])
    def test_w5_where_summary_supplies_current_location_and_change(
        self, monkeypatch: pytest.MonkeyPatch, strict_value: str | None
    ) -> None:
        if strict_value is None:
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        else:
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", strict_value)
        session = _make_session(current_location="parlor", previous_location="foyer")
        enriched = _enrich(session, [_source_narrator_block()])
        proj = enriched[0]["source_facts"]["w5_projection"]
        where = proj["where_summary"]
        assert where["current_location"] == "parlor", (
            "W5 where_summary must supply the actor's current location as the "
            "strict-on actor-situation authority"
        )
        assert where["previous_location"] == "foyer"
        assert where["location_changed"] is True, (
            "W5 where_summary.location_changed must be the strict-on "
            "replacement for transition_from_previous.location_changed"
        )
        # The scene_location is preserved under facts so audit can trace the
        # underlying W5 fact, not just the promoted convenience field.
        assert where["facts"]["scene_location"] == "parlor"

    @pytest.mark.parametrize("strict_value", [None, "false", "true"])
    def test_w5_what_summary_is_action_observed_and_not_polluted_by_how(
        self, monkeypatch: pytest.MonkeyPatch, strict_value: str | None
    ) -> None:
        if strict_value is None:
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        else:
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", strict_value)
        session = _make_session()
        enriched = _enrich(session, [_source_narrator_block()])
        proj = enriched[0]["source_facts"]["w5_projection"]
        what_facts = proj["what_summary"]["facts"]
        assert what_facts["current_action"] == "accuses"
        assert what_facts["interaction_type"] == "confrontation"
        # ADR-0063 + ADR-0065: How is first-class, not folded into What.
        for how_key in ("tone", "intensity", "manner", "pace", "physicality", "method", "style"):
            assert how_key not in what_facts, (
                f"How attribute '{how_key}' must not appear in what_summary.facts; "
                "How is first-class per ADR-0063 / ADR-0065."
            )
        # truth_attribution preserved per fact (semantic, not field-presence).
        assert (
            proj["truth_attribution"]["what_summary.facts.current_action"]
            == "observed"
        )
        assert (
            proj["source_attribution"]["what_summary.facts.current_action"]
            == "committed_action"
        )

    @pytest.mark.parametrize("strict_value", [None, "false", "true"])
    def test_w5_how_summary_is_first_class_with_truth_attribution(
        self, monkeypatch: pytest.MonkeyPatch, strict_value: str | None
    ) -> None:
        if strict_value is None:
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        else:
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", strict_value)
        session = _make_session()
        enriched = _enrich(session, [_source_narrator_block()])
        proj = enriched[0]["source_facts"]["w5_projection"]
        how_facts = proj["how_summary"]["facts"]
        assert how_facts["tone"] == "sharp", "tone must be the strongest How fact"
        assert how_facts["intensity"] == "rising"
        # Per-fact truth_attribution carries the W5 truth level, which is
        # the semantic gate that prevents How from being narrated as observed
        # truth when it was director-assigned.
        assert (
            proj["truth_attribution"]["how_summary.facts.tone"] == "observed"
        )
        assert (
            proj["truth_attribution"]["how_summary.facts.intensity"]
            == "director_assigned"
        )

    @pytest.mark.parametrize("strict_value", [None, "false", "true"])
    def test_w5_why_summary_is_soft_inferred_truth(
        self, monkeypatch: pytest.MonkeyPatch, strict_value: str | None
    ) -> None:
        if strict_value is None:
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        else:
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", strict_value)
        session = _make_session()
        enriched = _enrich(session, [_source_narrator_block()])
        proj = enriched[0]["source_facts"]["w5_projection"]
        why_facts = proj["why_summary"]["facts"]
        assert why_facts["motive"] == "defend_son"
        # ADR-0063 + ADR-0065: inferred Why must remain soft truth — never
        # promoted to observed. The projection records this via
        # truth_attribution, and the strict-on prompt names it as such.
        assert (
            proj["truth_attribution"]["why_summary.facts.motive"] == "inferred"
        ), (
            "why_summary motive must be attributed as inferred; W5 must never "
            "present inferred Why as observed truth"
        )
        assert (
            proj["source_attribution"]["why_summary.facts.motive"]
            == "character_mind_record"
        )

    @pytest.mark.parametrize("strict_value", [None, "false", "true"])
    def test_w5_who_summary_identifies_actor(
        self, monkeypatch: pytest.MonkeyPatch, strict_value: str | None
    ) -> None:
        if strict_value is None:
            monkeypatch.delenv("W5_AST_NARRATOR_STRICT_ENABLED", raising=False)
        else:
            monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", strict_value)
        session = _make_session()
        enriched = _enrich(session, [_source_narrator_block()])
        proj = enriched[0]["source_facts"]["w5_projection"]
        who = proj["who_summary"]
        # Who summary identifies the actor and scope so the narrator does not
        # need to read transition_from_previous to know which actor is on
        # stage.
        assert who["actor_id"] == "veronique"
        assert who["actor_type"] == "human"
        assert who["actor_role_in_scene"] == "aggressor"
        assert who["involvement_type"] == "primary"
        assert proj["actor_id"] == "veronique"
        assert proj["target_consumer"] == "narrator"


# ---------------------------------------------------------------------------
# 2) source_facts shape under permanent strict-on
# ---------------------------------------------------------------------------


class TestPhase6B5BSourceFactsAuthorityShape:
    """ADR-0068 gate - W5 projection is the actor-situation surface and removed
    transition compatibility payloads are not recreated."""

    def test_enrichment_does_not_create_transition_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: env-var false does not recreate transition source_facts."""
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        session = _make_session()
        enriched = _enrich(session, [_source_narrator_block()])
        facts = enriched[0]["source_facts"]
        assert "transition_from_previous" not in facts
        assert "_legacy_compat" not in facts
        assert "w5_projection" in facts

    def test_strict_on_no_legacy_compat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase 6B-6B: strict-on never produces _legacy_compat in source_facts.
        W5 projection is the sole actor-situation authority (ADR-0066)."""

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        session = _make_session()
        enriched = _enrich(session, [_strict_clean_block()])
        facts = enriched[0]["source_facts"]
        assert "transition_from_previous" not in facts
        assert "_legacy_compat" not in facts, (
            "Phase 6B-6B: _legacy_compat breadcrumb path retired (ADR-0066)"
        )
        # W5 projection carries the location_changed signal.
        proj = facts["w5_projection"]
        assert proj["where_summary"]["location_changed"] is True
        assert proj["where_summary"]["current_location"] == "parlor"
        assert proj["where_summary"]["previous_location"] == "foyer"

    def test_strict_on_w5_projection_supplies_location_shift_signal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The location-shift signal comes from W5: where_summary.location_changed
        plus current/previous location."""

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        session = _make_session(previous_location="foyer", current_location="parlor")
        enriched = _enrich(session, [_strict_clean_block()])
        proj = enriched[0]["source_facts"]["w5_projection"]
        # The strict prompt expects all three signals from W5 alone.
        assert proj["where_summary"]["location_changed"] is True
        assert proj["where_summary"]["current_location"] == "parlor"
        assert proj["where_summary"]["previous_location"] == "foyer"
        # No top-level transition_from_previous and no _legacy_compat.
        assert "transition_from_previous" not in enriched[0]["source_facts"]
        assert "_legacy_compat" not in enriched[0]["source_facts"]


# ---------------------------------------------------------------------------
# 3) Narrator prompt contract under permanent strict-on
# ---------------------------------------------------------------------------


class TestPhase6B5BPromptContract:
    """Phase 6B-5B / Phase 6B-5D parity gate — the narrator output prompt must
    name source_facts.w5_projection as the actor-situation authority in all
    postures. ``transition_from_previous`` must not be promoted as narrator
    authority under any env-var value."""

    def test_prompt_does_not_promote_removed_fallback_guidance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: env-var false has no effect on prompt. Removed fallback
        instruction is absent under all postures. W5 projection is the authority.

        Note: source blocks no longer embed transition hard-cut payloads in
        source_facts. We check only the instruction portion before the data
        payload for the narrator-guidance phrases we removed."""
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        prompt = _build_narrator_prompt()
        instruction = prompt.split("Narrator synthesis input:")[0]
        assert "Use transition_from_previous only as a fallback" not in instruction
        assert "as a fallback when w5_projection is absent" not in instruction
        assert "hard authored scene break" not in instruction
        assert "directed_transition.kind" not in instruction
        assert "source_facts.w5_projection" in instruction
        for summary in (
            "where_summary",
            "what_summary",
            "how_summary",
            "why_summary",
        ):
            assert summary in instruction

    def test_strict_on_prompt_names_w5_projection_as_sole_authority(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        prompt = _build_narrator_prompt()
        # The strict-on prompt explicitly designates the W5 projection as
        # the actor-situation authority — not merely "preferred" or
        # "available". This is the semantic gate for Phase 6B-5C.
        assert "source_facts.w5_projection" in prompt
        assert "sole actor-situation authority" in prompt, (
            "Phase 6B-5B strict-on prompt must name w5_projection as the "
            "sole actor-situation authority"
        )

    def test_strict_on_prompt_forbids_consulting_legacy_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        prompt = _build_narrator_prompt()
        # The strict-on prompt explicitly tells the narrator not to consult
        # the legacy transition surface (Phase 6B-6B: _legacy_compat retired).
        assert "Do not consult source_facts.transition_from_previous" in prompt
        assert "that field is absent" in prompt
        # The unstrict-only fallback paragraph must be absent.
        assert "Use transition_from_previous only as a fallback" not in prompt
        assert "source_facts.transition_from_previous.location_changed" not in prompt
        assert (
            "source_facts.transition_from_previous.directed_transition" not in prompt
        )

    def test_strict_on_prompt_names_all_five_w5_summaries(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        prompt = _build_narrator_prompt()
        # Strict-on must explicitly enumerate all five W5 summaries so the
        # narrator does not need to infer the contract from absence.
        for summary in (
            "who_summary",
            "where_summary",
            "what_summary",
            "how_summary",
            "why_summary",
        ):
            assert summary in prompt, (
                f"strict-on prompt must explicitly name {summary} as the "
                f"actor-situation authority for that dimension"
            )

    def test_strict_on_prompt_uses_w5_location_changed_as_shift_signal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        prompt = _build_narrator_prompt()
        # The W5 where_summary.location_changed signal steers scene-shift
        # orientation.
        assert "where_summary.location_changed" in prompt

    def test_strict_on_prompt_keeps_how_first_class_with_attributes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        prompt = _build_narrator_prompt()
        assert "how_summary" in prompt
        assert "first-class" in prompt
        assert "never folded into what" in prompt or "not folded into what" in prompt
        # The strict-on prompt enumerates How attributes as steering signals.
        for attr in (
            "tone",
            "manner",
            "intensity",
            "pace",
            "physicality",
            "method",
            "style",
        ):
            assert attr in prompt, (
                f"strict-on prompt must keep '{attr}' first-class under "
                "how_summary"
            )

    def test_strict_on_prompt_marks_inferred_why_as_soft_truth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        prompt = _build_narrator_prompt()
        assert "why_summary" in prompt
        # Inferred Why must remain visibly soft / never-spoken-as-fact, even
        # under strict-on. ADR-0063 + ADR-0065.
        assert "inferred" in prompt.lower()
        assert (
            "never spoken as fact" in prompt
            or "never spoken as observed fact" in prompt
        )


# ---------------------------------------------------------------------------
# 4) Admin / diagnostics parity under permanent strict-on
# ---------------------------------------------------------------------------


class TestPhase6B5BAdminDiagnosticsParity:
    """Phase 6B-5B parity gate — ``get_w5_langfuse_metadata`` must report
    W5-first location-change semantics under all env-var postures without
    strict/parity compatibility metadata."""

    def test_env_var_false_still_uses_w5_history_and_reports_strict_on(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: env-var false no longer changes behavior."""
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")
        session = _make_session()
        harness = _AdminParityHarness(session)
        meta = harness.get_w5_langfuse_metadata(session.session_id)
        # W5 history projection always drives the signal.
        assert meta["w5.location_changed_this_turn"] is True
        assert meta["w5.location_changed_source"] == "w5_history_projection"
        assert "w5.narrator_strict_enabled" not in meta
        assert "w5.legacy_transition_parity" not in meta
        assert meta["w5.has_how"] is True
        assert meta["w5.has_inferred_why"] is True

    def test_strict_on_admin_metadata_has_no_compatibility_parity(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0068: strict/parity admin metadata is absent."""
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        session = _make_session()
        harness = _AdminParityHarness(session)
        meta = harness.get_w5_langfuse_metadata(session.session_id)
        assert meta["w5.location_changed_this_turn"] is True
        assert meta["w5.location_changed_source"] == "w5_history_projection"
        assert "w5.narrator_strict_enabled" not in meta
        assert "w5.legacy_transition_parity" not in meta
        assert "w5.narrator_legacy_compat_diagnostics_enabled" not in meta
        assert meta["w5.has_how"] is True
        assert meta["w5.has_inferred_why"] is True

    def test_strict_on_ignores_disagreeing_transition_from_previous_in_diagnostics(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ADR-0065 admin requirement: location-change evidence must be
        computed from W5 history/projection, NOT from a narrator block's
        ``transition_from_previous.location_changed`` claim. We seed a
        diagnostics entry whose stray legacy claim disagrees with W5 and
        verify the bridge follows W5 anyway."""

        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        same_previous = _w5_snapshot(turn=2, actor_id="veronique", location="foyer")
        same_current = _w5_snapshot(turn=3, actor_id="veronique", location="foyer")
        session = StorySession(
            session_id="sess_phase_6b5b_conflict",
            module_id="god_of_carnage",
            runtime_projection={"human_actor_id": "veronique"},
            created_at=datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2026, 5, 22, 12, 0, 5, tzinfo=timezone.utc),
            turn_counter=3,
            current_scene_id="opening",
            w5_history=[same_previous, same_current],
            w5_latest_snapshot=same_current,
        )
        # Stray legacy claim says location_changed=True; W5 says False.
        session.diagnostics.append(
            {
                "scene_blocks": [
                    {
                        "block_type": "narrator",
                        "source_facts": {
                            "transition_from_previous": {"location_changed": True}
                        },
                    }
                ]
            }
        )
        harness = _AdminParityHarness(session)
        meta = harness.get_w5_langfuse_metadata(session.session_id)
        # W5-first wins regardless of historical diagnostics payloads.
        assert meta["w5.location_changed_this_turn"] is False
        assert meta["w5.location_changed_source"] == "w5_history_projection"
        assert "w5.narrator_strict_enabled" not in meta
        assert "w5.legacy_transition_parity" not in meta


# ---------------------------------------------------------------------------
# 5) Safety: opt-out and malformed-W5 paths remain testable
# ---------------------------------------------------------------------------


class TestPhase6B5BSafetyFallbacksStillRequired:
    """ADR-0068 does not remove malformed-W5 or projection opt-out safety."""

    def test_explicit_projection_opt_out_leaves_source_facts_unenriched(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_PROJECTION_ENABLED", "0")
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        session = _make_session()
        blocks = [_source_narrator_block()]
        enriched = _enrich(session, blocks)
        # Projection enrichment is suppressed.
        assert enriched is blocks
        assert "w5_projection" not in enriched[0]["source_facts"]

    def test_malformed_w5_snapshot_falls_back_with_diagnostic(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "true")
        session = _make_session()
        session.w5_latest_snapshot = {
            "schema_version": "w5_snapshot.v1",
            "this_is": "garbage",
        }
        enriched = _enrich(session, [_source_narrator_block()])
        # Safety fallback: no projection added, diagnostic recorded.
        assert "w5_projection" not in enriched[0]["source_facts"]
        kinds = [d.get("diagnostic_kind") for d in session.diagnostics]
        assert "w5_narrator_projection_failed" in kinds
