"""Unit tests for narrative governance service guards and workflows."""

from __future__ import annotations

import pytest

from app.extensions import db
from app.models import NarrativeRevisionCandidate, NarrativeRevisionConflict
from app.models.narrative_contracts import DraftPatchBundle
from app.services.narrative_governance_service import (
    NarrativeGovernanceError,
    apply_revision_bundle_to_draft,
    detect_conflicts_for_module,
    transition_revision,
)


def _seed_revision(revision_id: str, review_status: str, target_ref: str) -> NarrativeRevisionCandidate:
    return NarrativeRevisionCandidate(
        revision_id=revision_id,
        module_id="god_of_carnage",
        source_finding_id=None,
        target_kind="actor_mind",
        target_ref=target_ref,
        operation="replace_clause",
        structured_delta_json={"path": target_ref, "value": "patched"},
        expected_effects_json=["stability"],
        risk_flags_json=[],
        review_status=review_status,
        requires_review=True,
        mutation_allowed=False,
        created_by="system",
    )


def test_detect_conflicts_creates_target_overlap_rows(app):
    with app.app_context():
        db.session.add(_seed_revision("rev_a", "pending", "actor_minds.veronique"))
        db.session.add(_seed_revision("rev_b", "in_review", "actor_minds.veronique"))
        db.session.commit()

        conflicts = detect_conflicts_for_module("god_of_carnage")
        assert len(conflicts) == 1
        assert conflicts[0]["target_ref"] == "actor_minds.veronique"
        stored = NarrativeRevisionConflict.query.filter_by(module_id="god_of_carnage").all()
        assert len(stored) == 1


def test_transition_revision_blocks_invalid_edges(app):
    with app.app_context():
        db.session.add(_seed_revision("rev_invalid", "pending", "actor_minds.alain"))
        db.session.commit()
        with pytest.raises(NarrativeGovernanceError) as exc:
            transition_revision(
                revision_id="rev_invalid",
                to_status="promoted",
                actor_id="operator",
                actor_role="operator",
                notes=None,
            )
        assert exc.value.code == "invalid_revision_transition"


def test_apply_to_draft_requires_approved_and_no_conflicts(app):
    with app.app_context():
        db.session.add(_seed_revision("rev_apply", "approved", "actor_minds.michel"))
        db.session.commit()
        bundle = DraftPatchBundle(
            patch_bundle_id="patch_bundle_1",
            module_id="god_of_carnage",
            draft_workspace_id="draft_goc_001",
            revision_ids=["rev_apply"],
            target_refs=["actor_minds.michel"],
            patch_operations=[{"operation": "replace_clause"}],
            created_at="2026-04-13T00:00:00Z",
        )
        result = apply_revision_bundle_to_draft(bundle=bundle, requested_by="system")
        assert result["applied"] is True


def test_apply_to_draft_blocks_unresolved_conflicts(app):
    with app.app_context():
        db.session.add(_seed_revision("rev_conflict", "approved", "actor_minds.annette"))
        db.session.add(
            NarrativeRevisionConflict(
                conflict_id="conf_pending_1",
                module_id="god_of_carnage",
                candidate_ids_json=["rev_conflict"],
                conflict_type="target_overlap",
                target_kind="actor_mind",
                target_ref="actor_minds.annette",
                resolution_status="pending",
            )
        )
        db.session.commit()
        bundle = DraftPatchBundle(
            patch_bundle_id="patch_bundle_2",
            module_id="god_of_carnage",
            draft_workspace_id="draft_goc_001",
            revision_ids=["rev_conflict"],
            target_refs=["actor_minds.annette"],
            patch_operations=[{"operation": "replace_clause"}],
            created_at="2026-04-13T00:00:00Z",
        )
        with pytest.raises(NarrativeGovernanceError) as exc:
            apply_revision_bundle_to_draft(bundle=bundle, requested_by="system")
        assert exc.value.code == "revision_conflicts_unresolved"
