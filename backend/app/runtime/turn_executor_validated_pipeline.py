"""Validated turn pipeline (validation → deltas → apply → narrative commit) — DS-054.

DS-007 Task 3: Decision gates extracted to pipeline_decision_guards module.
Reduced from 155 to ~100 LOC via guard extraction and cleanup.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from app.content.module_models import ContentModule
from app.runtime.event_log import RuntimeEventLog
from app.runtime.narrative_commit import resolve_narrative_commit
from app.runtime.runtime_models import (
    GuardOutcome,
    MockDecision,
    NarrativeCommitRecord,
    SessionState,
)
from app.runtime.scene_legality import SceneTransitionLegality
from app.runtime.turn_execution_types import TurnExecutionResult
from app.runtime.turn_executor_decision_delta import (
    _compute_guard_outcome,
    apply_deltas,
    construct_deltas,
)
from app.runtime.validators import validate_decision


def run_validated_turn_pipeline(
    session: SessionState,
    current_turn: int,
    mock_decision: MockDecision,
    module: ContentModule,
    event_log: RuntimeEventLog,
    started_at: datetime,
    prior_scene_id: str | None,
) -> TurnExecutionResult:
    """Execute validation through completion for a successful source-gate path.

    Args:
        session: Current session state.
        current_turn: Turn number being executed.
        mock_decision: Decision proposal from AI.
        module: Content module context.
        event_log: Event logger for turn execution.
        started_at: Turn start timestamp.
        prior_scene_id: Scene ID before execution.

    Returns:
        TurnExecutionResult with complete execution data and narrative commit.
    """
    # Stage 1: Validate decision
    validation_outcome = validate_decision(mock_decision, session, module)

    event_log.log(
        "decision_validated",
        f"Decision validated: {validation_outcome.status} "
        f"({len(validation_outcome.accepted_delta_indices)} accepted, "
        f"{len(validation_outcome.rejected_delta_indices)} rejected)",
        payload={
            "status": validation_outcome.status,
            "is_valid": validation_outcome.is_valid,
            "accepted_delta_count": len(validation_outcome.accepted_delta_indices),
            "rejected_delta_count": len(validation_outcome.rejected_delta_indices),
            "errors": validation_outcome.errors,
        },
    )

    # Stage 2: Construct deltas from validated decision
    accepted_deltas, rejected_deltas = construct_deltas(
        mock_decision, session, validation_outcome, current_turn
    )

    event_log.log(
        "deltas_generated",
        f"Deltas: {len(accepted_deltas)} accepted, {len(rejected_deltas)} rejected",
        payload={
            "accepted_count": len(accepted_deltas),
            "rejected_count": len(rejected_deltas),
            "accepted_deltas": [
                {
                    "id": d.id,
                    "delta_type": d.delta_type,
                    "target_path": d.target_path,
                    "target_entity": d.target_entity,
                    "previous_value": d.previous_value,
                    "next_value": d.next_value,
                    "source": d.source,
                }
                for d in accepted_deltas
            ],
            "rejected_delta_ids": [d.id for d in rejected_deltas],
        },
    )

    # Stage 3: Apply deltas to canonical state
    updated_state = apply_deltas(session.canonical_state, accepted_deltas)

    event_log.log(
        "deltas_applied",
        f"{len(accepted_deltas)} delta(s) applied to canonical state",
        payload={
            "applied_count": len(accepted_deltas),
            "delta_ids": [d.id for d in accepted_deltas],
        },
    )

    # Stage 4: Resolve narrative commit from post-delta state
    guard_outcome_value = _compute_guard_outcome(accepted_deltas, rejected_deltas, "success")
    narrative_commit = resolve_narrative_commit(
        turn_number=current_turn,
        prior_scene_id=prior_scene_id or session.current_scene_id,
        post_delta_canonical_state=updated_state,
        session_template=session,
        decision=mock_decision,
        module=module,
        guard_outcome=guard_outcome_value,
        accepted_deltas=accepted_deltas,
        rejected_deltas=rejected_deltas,
    )

    updated_scene_id = narrative_commit.committed_scene_id
    updated_ending_id = narrative_commit.committed_ending_id

    # Stage 5: Log narrative outcomes and check scene transitions
    _log_narrative_outcomes(
        event_log,
        narrative_commit,
        session,
        mock_decision,
        updated_state,
        prior_scene_id,
        module,
    )

    # Stage 6: Complete execution
    completed_at = datetime.now(timezone.utc)
    duration_ms = (completed_at - started_at).total_seconds() * 1000

    event_log.log(
        "turn_completed",
        f"Turn {current_turn} completed: {len(accepted_deltas)} accepted, {len(rejected_deltas)} rejected",
        payload={
            "turn_number": current_turn,
            "accepted_delta_count": len(accepted_deltas),
            "rejected_delta_count": len(rejected_deltas),
            "guard_outcome": guard_outcome_value.value,
            "detected_triggers": mock_decision.detected_triggers,
            "duration_ms": duration_ms,
        },
    )

    return TurnExecutionResult(
        turn_number=current_turn,
        session_id=session.session_id,
        execution_status="success",
        decision=mock_decision,
        validation_outcome=validation_outcome,
        validation_errors=validation_outcome.errors,
        accepted_deltas=accepted_deltas,
        rejected_deltas=rejected_deltas,
        updated_canonical_state=updated_state,
        updated_scene_id=updated_scene_id,
        updated_ending_id=updated_ending_id,
        guard_outcome=guard_outcome_value,
        narrative_commit=narrative_commit,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        events=event_log.flush(),
    )


def _log_narrative_outcomes(
    event_log: RuntimeEventLog,
    narrative_commit: NarrativeCommitRecord,
    session: SessionState,
    mock_decision: MockDecision,
    updated_state: dict,
    prior_scene_id: str | None,
    module: ContentModule,
) -> None:
    """Log narrative commit outcomes (endings, scene transitions, blocks).

    Extracted narrative outcome logging to reduce main function complexity.
    """
    if narrative_commit.situation_status == "ending_reached":
        event_log.log(
            "ending_triggered",
            f"Ending triggered: {narrative_commit.committed_ending_id}",
            payload={"ending_id": narrative_commit.committed_ending_id},
        )
    elif narrative_commit.situation_status == "transitioned":
        event_log.log(
            "scene_changed",
            f"Scene transitioned to {narrative_commit.committed_scene_id}",
            payload={
                "from_scene": prior_scene_id,
                "to_scene": narrative_commit.committed_scene_id,
            },
        )
    elif mock_decision.proposed_scene_id:
        post_delta_session = session.model_copy(deep=True)
        post_delta_session.canonical_state = deepcopy(updated_state)
        post_delta_session.current_scene_id = prior_scene_id or session.current_scene_id
        td = SceneTransitionLegality.check_transition_legal(
            prior_scene_id or session.current_scene_id,
            mock_decision.proposed_scene_id,
            module,
            session=post_delta_session,
            detected_triggers=mock_decision.detected_triggers,
        )
        if not td.allowed:
            event_log.log(
                "scene_transition_blocked",
                f"Scene transition to {mock_decision.proposed_scene_id} blocked: {td.reason}",
                payload={
                    "from_scene": prior_scene_id,
                    "proposed_scene": mock_decision.proposed_scene_id,
                    "reason": td.reason,
                },
            )
