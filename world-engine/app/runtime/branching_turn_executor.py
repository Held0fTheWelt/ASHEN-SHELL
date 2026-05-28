"""
Branching-aware turn execution.

Extends turn executor to handle decision points and branch path tracking.
Implements four seams: proposal, validation, commit, render.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

from story_runtime_core.branching import (
    DecisionPointRegistry, PathStateManager, ConsequenceFilter
)


class TurnSeam(Enum):
    """Turn execution seams where branching can intervene."""
    PROPOSAL = "proposal"  # What's being proposed (including decision points)
    VALIDATION = "validation"  # Validation rules (including decision option validation)
    COMMIT = "commit"  # Committing state (including path recording)
    RENDER = "render"  # Rendering output (including consequence filtering)


@dataclass
class BranchingTurnResult:
    """Turn result with branching information."""
    success: bool
    new_turn_number: int
    state_delta: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    executed_at: Optional[datetime] = None

    # Branching-specific fields
    decision_point_id: Optional[str] = None  # If this turn had a decision point
    chosen_option_id: Optional[str] = None  # Option chosen
    consequence_tags: List[str] = field(default_factory=list)  # Tags applied
    path_signature: Optional[str] = None  # Unique signature of player's current path


class BranchingTurnExecutor:
    """Execute turns with branching awareness."""

    def __init__(self, session_manager, decision_registry: DecisionPointRegistry,
                 path_manager: PathStateManager, consequence_filter: ConsequenceFilter):
        """
        Initialize branching-aware turn executor.

        Args:
            session_manager: SessionManager for state access
            decision_registry: DecisionPointRegistry for decision definitions
            path_manager: PathStateManager for tracking player paths
            consequence_filter: ConsequenceFilter for path-based fact filtering
        """
        self.session_manager = session_manager
        self.decision_registry = decision_registry
        self.path_manager = path_manager
        self.consequence_filter = consequence_filter

    def _get_or_create_path(self, *, session_id: str, session):
        path = self.path_manager.get_path(session_id)
        if path:
            return path
        return self.path_manager.create_path(session_id, session.scenario_id)

    def _resolve_decision_choice(
        self,
        *,
        session,
        current_turn: int,
        action: Dict[str, Any],
    ) -> tuple[Any | None, str | None, Any | None, str | None]:
        decision_point = self.decision_registry.get_for_turn(
            session.scenario_id,
            current_turn,
        )
        decision_option_id = action.get("decision_option_id")
        if decision_point is None and decision_option_id:
            decision_point = self.decision_registry.get_for_option(
                session.scenario_id,
                str(decision_option_id),
            )
        if not decision_point:
            return None, decision_option_id, None, None
        if not decision_option_id:
            return (
                decision_point,
                None,
                None,
                f"Decision point {decision_point.id} requires decision_option_id",
            )
        chosen_option = decision_point.get_option(decision_option_id)
        if not chosen_option:
            return (
                decision_point,
                decision_option_id,
                None,
                f"Invalid option {decision_option_id} for decision {decision_point.id}",
            )
        return decision_point, decision_option_id, chosen_option, None

    def _validation_error(
        self,
        *,
        action: Dict[str, Any],
        decision_point,
        chosen_option,
        decision_option_id: str | None,
        session,
        player_id: str,
    ) -> str | None:
        if not self._is_valid_action(action):
            return "Invalid action format"
        if decision_point and chosen_option:
            if not self._is_valid_decision_choice(chosen_option, session, player_id):
                return f"Cannot choose {decision_option_id} in current state"
        return None

    def _record_branch_decision(
        self,
        *,
        session_id: str,
        current_turn: int,
        decision_point,
        decision_option_id: str | None,
        chosen_option,
    ) -> List[str]:
        if not decision_point or not chosen_option:
            return []
        consequence_tags = chosen_option.consequence_tags
        self.path_manager.record_decision(
            session_id=session_id,
            turn=current_turn,
            decision_id=decision_point.id,
            option_id=decision_option_id,
            consequence_tags=consequence_tags,
        )
        return consequence_tags

    @staticmethod
    def _append_turn_history(
        *,
        session,
        current_turn: int,
        player_id: str,
        action: Dict[str, Any],
        state_delta: Dict[str, Any],
        decision_point,
        decision_option_id: str | None,
        consequence_tags: List[str],
    ) -> None:
        session.history.append({
            "turn": current_turn,
            "player_id": player_id,
            "action": action,
            "delta": state_delta,
            "decision_point_id": decision_point.id if decision_point else None,
            "chosen_option_id": decision_option_id,
            "consequence_tags": consequence_tags,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _path_signature(self, session_id: str) -> str | None:
        current_path = self.path_manager.get_path(session_id)
        return current_path.get_path_signature() if current_path else None

    def execute_turn(
        self,
        session_id: str,
        player_id: str,
        action: Dict[str, Any]
    ) -> BranchingTurnResult:
        """
        Execute a turn with branching awareness.

        Four seams:
        1. PROPOSAL - Detect if this turn has a decision point
        2. VALIDATION - Validate action (including decision option validation)
        3. COMMIT - Record decision and path state
        4. RENDER - Filter output based on path

        Args:
            session_id: Session to execute in
            player_id: Player executing action
            action: Action to execute (may include decision_option_id if decision point)

        Returns:
            BranchingTurnResult with result and branching info
        """
        # Get authoritative session
        session = self.session_manager.get_session(session_id)
        if not session:
            return BranchingTurnResult(
                success=False,
                new_turn_number=-1,
                error_message=f"Session {session_id} not found"
            )

        self._get_or_create_path(session_id=session_id, session=session)

        current_turn = session.turn_number

        decision_point, decision_option_id, chosen_option, decision_error = (
            self._resolve_decision_choice(
                session=session,
                current_turn=current_turn,
                action=action,
            )
        )
        if decision_error:
            return BranchingTurnResult(
                success=False,
                new_turn_number=current_turn,
                error_message=decision_error,
            )

        validation_error = self._validation_error(
            action=action,
            decision_point=decision_point,
            chosen_option=chosen_option,
            decision_option_id=decision_option_id,
            session=session,
            player_id=player_id,
        )
        if validation_error:
            return BranchingTurnResult(
                success=False,
                new_turn_number=current_turn,
                error_message=validation_error,
            )

        state_delta = self._execute_action(session, player_id, action)
        consequence_tags = self._record_branch_decision(
            session_id=session_id,
            current_turn=current_turn,
            decision_point=decision_point,
            decision_option_id=decision_option_id,
            chosen_option=chosen_option,
        )
        session.turn_number += 1
        self._append_turn_history(
            session=session,
            current_turn=current_turn,
            player_id=player_id,
            action=action,
            state_delta=state_delta,
            decision_point=decision_point,
            decision_option_id=decision_option_id,
            consequence_tags=consequence_tags,
        )
        filtered_delta = self._filter_output(state_delta, session_id)

        return BranchingTurnResult(
            success=True,
            new_turn_number=session.turn_number,
            state_delta=filtered_delta,
            executed_at=datetime.now(timezone.utc),
            decision_point_id=decision_point.id if decision_point else None,
            chosen_option_id=decision_option_id,
            consequence_tags=consequence_tags,
            path_signature=self._path_signature(session_id),
        )

    def _is_valid_action(self, action: Dict[str, Any]) -> bool:
        """Validate action format."""
        return isinstance(action, dict) and "type" in action

    def _is_valid_decision_choice(self, chosen_option, session, player_id) -> bool:
        """
        Validate that a decision choice is valid in current state.

        Could check things like:
        - Has player met prerequisites for this choice?
        - Is player's character in valid state for this choice?
        - Are there any locks/constraints?
        """
        # Simplified: all valid for now
        # Real implementation could check session state, player status, etc.
        return True

    def _execute_action(
        self,
        session,
        player_id: str,
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute action game logic.

        Returns state delta (what changed).
        """
        # Simplified: just return action as delta for now
        # Real implementation would have game logic here
        return {
            "action_executed": action["type"],
            "turn_number": session.turn_number
        }

    def _filter_output(self, state_delta: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Filter output based on player's branch path.

        Uses consequence filter to hide/show facts based on path.
        """
        path = self.path_manager.get_path(session_id)
        if not path:
            return state_delta

        # Apply consequence filtering to state delta
        return self.consequence_filter.filter_turn_output(state_delta, path.active_consequence_tags)


class BranchingTurnExecutorFactory:
    """Factory for creating branching-aware turn executors."""

    @staticmethod
    def create_for_session(session_manager, scenario_id: str) -> BranchingTurnExecutor:
        """
        Create a branching turn executor for a scenario.

        Args:
            session_manager: SessionManager instance
            scenario_id: Scenario ID (used to load decision points)

        Returns:
            BranchingTurnExecutor ready to use
        """
        # In a real implementation, these would be loaded from config/files
        decision_registry = DecisionPointRegistry()
        path_manager = PathStateManager()
        consequence_filter = ConsequenceFilter()

        return BranchingTurnExecutor(
            session_manager=session_manager,
            decision_registry=decision_registry,
            path_manager=path_manager,
            consequence_filter=consequence_filter
        )
