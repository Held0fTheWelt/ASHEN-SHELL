"""
Thematic sections for package_output (DS-037) — dramatic review and
planner projection.
"""

from __future__ import annotations

from typing import Any

from ai_stack.goc_frozen_vocab import GOC_MODULE_ID
from ai_stack.langgraph_runtime_package_output_dramatic_review import build_dramatic_review_section
from ai_stack.langgraph_runtime_state import RuntimeTurnState


def append_goc_validation_reject_failure_marker(
    *,
    module_id: str,
    validation: dict[str, Any],
    failure_markers: list[Any],
) -> None:
    """Describe what ``append_goc_validation_reject_failure_marker`` does
    in one line (verb-led summary for this function).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        module_id: ``module_id`` (str); meaning follows the type and call sites.
        validation: ``validation`` (dict[str, Any]); meaning follows the type and call sites.
        failure_markers: ``failure_markers`` (list[Any]); meaning follows the type and call sites.
    """
    if module_id != GOC_MODULE_ID or validation.get("status") != "rejected":
        return
    if any(isinstance(m, dict) and m.get("failure_class") == "validation_reject" for m in failure_markers):
        return
    failure_markers.append(
        {
            "failure_class": "validation_reject",
            "closure_impacting": False,
            "note": "goc_validation_rejected_truth_safe_visible",
            "validation_reason": validation.get("reason"),
        }
    )


def compute_experiment_preview_for_package_output(
    *,
    state: RuntimeTurnState,
    module_id: str,
    validation: dict[str, Any],
    committed: dict[str, Any],
    failure_markers: list[Any],
) -> bool:
    """Describe what ``compute_experiment_preview_for_package_output`` does
    in one line (verb-led summary for this function).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (RuntimeTurnState); meaning follows the type and call sites.
        module_id: ``module_id`` (str); meaning follows the type and call sites.
        validation: ``validation`` (dict[str, Any]); meaning follows the type and call sites.
        committed: ``committed`` (dict[str, Any]); meaning follows the type and call sites.
        failure_markers: ``failure_markers`` (list[Any]); meaning follows the type and call sites.
    
    Returns:
        bool:
            Returns a value of type ``bool``; see the function body for structure, error paths, and sentinels.
    """
    experiment_preview = True
    if state.get("force_experiment_preview"):
        experiment_preview = True
    elif module_id != GOC_MODULE_ID:
        experiment_preview = True
    elif validation.get("status") == "waived":
        experiment_preview = True
    elif validation.get("status") != "approved":
        experiment_preview = True
    elif not state.get("goc_slice_active"):
        experiment_preview = True
    else:
        experiment_preview = False

    if module_id == GOC_MODULE_ID and validation.get("status") == "approved" and not committed.get("commit_applied"):
        pass

    for fm in failure_markers:
        fc = fm.get("failure_class") if isinstance(fm, dict) else None
        if fc in ("scope_breach", "graph_error"):
            experiment_preview = True

    return experiment_preview


def build_planner_state_projection(state: RuntimeTurnState) -> dict[str, Any]:
    """Describe what ``build_planner_state_projection`` does in one line
    (verb-led summary for this function).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (RuntimeTurnState); meaning follows the type and call sites.
    
    Returns:
        dict[str, Any]:
            Returns a value of type ``dict[str, Any]``; see the function body for structure, error paths, and sentinels.
    """
    return {
        "semantic_move_record": state.get("semantic_move_record"),
        "social_state_record": state.get("social_state_record"),
        "character_mind_records": state.get("character_mind_records"),
        "scene_plan_record": state.get("scene_plan_record"),
        "note": "Derived projection of RuntimeTurnState planner fields — not a second truth surface.",
    }
