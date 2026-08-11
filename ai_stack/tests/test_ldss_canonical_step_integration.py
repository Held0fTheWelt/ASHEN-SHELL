"""Phase 5 integration test: canonical step renders through LDSS envelope."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_stack.story_runtime.canonical_path.canonical_path_resolver import clear_resolver_cache, load_canonical_path
from ai_stack.live_dramatic_scene_simulator import (
    build_ldss_input_from_session,
    build_scene_turn_envelope_v2,
    run_ldss,
)


@pytest.fixture(autouse=True)
def _reset_resolver_cache():
    clear_resolver_cache()
    yield
    clear_resolver_cache()


def _goc_module_root() -> Path:
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    return repo_root / "content" / "modules" / "god_of_carnage"


def test_run_ldss_emits_evidenced_live_path_for_canonical_step_005():
    canonical = load_canonical_path(_goc_module_root())
    ldss_input = build_ldss_input_from_session(
        session_id="test-canon-integration",
        module_id="god_of_carnage",
        turn_number=2,
        selected_player_role="annette",
        human_actor_id="annette",
        npc_actor_ids=["alain", "veronique", "michel"],
        player_input="",
        canonical_step_id="opening_005_statement_reading",
        canonical_path=canonical,
    )

    ldss_output = run_ldss(ldss_input)

    assert ldss_output.status == "approved"
    assert ldss_output.visible_actor_response_present is True
    assert ldss_output.scene_block_count > 1
    assert ldss_output.npc_agency_plan is not None
    assert ldss_output.npc_agency_plan.primary_responder_id == "veronique"


def test_envelope_diagnostics_record_canonical_path_output():
    canonical = load_canonical_path(_goc_module_root())
    ldss_input = build_ldss_input_from_session(
        session_id="test-canon-envelope",
        module_id="god_of_carnage",
        turn_number=0,
        selected_player_role="annette",
        human_actor_id="annette",
        npc_actor_ids=["alain", "veronique", "michel"],
        player_input="",
        canonical_step_id=canonical.first_step_id(),
        canonical_path=canonical,
    )
    ldss_output = run_ldss(ldss_input)
    envelope = build_scene_turn_envelope_v2(
        ldss_input=ldss_input,
        ldss_output=ldss_output,
        story_session_id="test-canon-envelope",
        turn_number=0,
    )
    payload = envelope.to_dict()
    diag = payload["diagnostics"]["live_dramatic_scene_simulator"]

    assert diag["invoked"] is True
    assert diag["error_present"] is False
    assert diag["scene_block_count"] >= 1


def test_canonical_step_branch_skipped_when_input_lacks_canonical_fields():
    ldss_input = build_ldss_input_from_session(
        session_id="test-no-canon",
        module_id="god_of_carnage",
        turn_number=0,
        selected_player_role="annette",
        human_actor_id="annette",
        npc_actor_ids=["alain", "veronique", "michel"],
        player_input="hello",
        canonical_step_id=None,
        canonical_path=None,
    )
    ldss_output = run_ldss(ldss_input)
    # No canonical fields → previous degraded-notice fallback path is preserved.
    assert ldss_output.status == "degraded_error"
    assert ldss_output.error_code == "ldss_no_live_visible_generation"


def test_bounded_emergence_uses_validated_runtime_bundle_instead_of_canonical_renderer():
    canonical = load_canonical_path(_goc_module_root())
    ldss_input = build_ldss_input_from_session(
        session_id="test-bounded-emergence",
        module_id="god_of_carnage",
        turn_number=3,
        selected_player_role="annette",
        human_actor_id="annette",
        npc_actor_ids=["alain", "veronique", "michel"],
        player_input="I put the glass down and wait.",
        canonical_step_id="opening_005_statement_reading",
        canonical_path=canonical,
        narrative_mode="bounded_emergence",
        canonical_path_role="reference_arc",
        visible_output_bundle={
            "gm_narration": ["The glass settles on the table; nobody returns to the statement."],
            "spoken_lines": [{"speaker_id": "michel", "text": "Michel says, 'So we wait.'"}],
            "action_lines": [],
        },
    )

    ldss_output = run_ldss(ldss_input)

    assert ldss_output.status == "approved"
    assert ldss_output.phase_cost["model"] == "ldss_validated_runtime_bundle"
    texts = [block.text for block in ldss_output.visible_scene_output.blocks]
    assert any("nobody returns to the statement" in text for text in texts)
    assert not any("armed" in text.lower() for text in texts)
