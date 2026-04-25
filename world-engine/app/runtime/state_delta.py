"""MVP2 StateDeltaBoundary — protected path enforcement at the commit seam.

Rejects any state delta that targets canonical story truth, runtime identity
fields (selected_player_role, human_actor_id, actor_lanes), or unknown paths
when reject_unknown_paths=True.

Error codes:
  protected_state_mutation_rejected — delta targets a protected path
  state_delta_boundary_violation    — delta targets an unknown non-allowed path
"""

from __future__ import annotations

from typing import Any

from app.runtime.models import StateDeltaBoundary, StateDeltaValidationResult


def _path_is_protected(path: str, protected_paths: list[str]) -> str | None:
    """Return the matched protected root if path is protected, else None."""
    for root in protected_paths:
        if path == root or path.startswith(root + ".") or path.startswith(root + "["):
            return root
    return None


def _path_is_allowed(path: str, allowed_paths: list[str]) -> bool:
    for root in allowed_paths:
        if path == root or path.startswith(root + ".") or path.startswith(root + "["):
            return True
    return False


def validate_state_delta(
    candidate_delta: dict[str, Any],
    boundary: StateDeltaBoundary | None = None,
) -> StateDeltaValidationResult:
    """Validate a single candidate state delta against the boundary.

    A delta is a dict with at minimum a 'path' key and an 'operation' key.

    Protected paths are always rejected regardless of allow list.
    Unknown paths are rejected when boundary.reject_unknown_paths is True.
    """
    if boundary is None:
        boundary = StateDeltaBoundary()

    path = str(candidate_delta.get("path") or "").strip()
    operation = str(candidate_delta.get("operation") or "").strip()

    if not path:
        return StateDeltaValidationResult(
            status="rejected",
            error_code="state_delta_boundary_violation",
            path=path,
            operation=operation,
            message="Delta path is required.",
        )

    protected_root = _path_is_protected(path, boundary.protected_paths)
    if protected_root is not None:
        return StateDeltaValidationResult(
            status="rejected",
            error_code="protected_state_mutation_rejected",
            path=path,
            operation=operation,
            message=(
                f"Path {path!r} is under protected root {protected_root!r} "
                f"and cannot be mutated by runtime delta."
            ),
        )

    if boundary.reject_unknown_paths and not _path_is_allowed(path, boundary.allowed_runtime_paths):
        return StateDeltaValidationResult(
            status="rejected",
            error_code="state_delta_boundary_violation",
            path=path,
            operation=operation,
            message=(
                f"Path {path!r} is not in the allowed runtime paths. "
                f"Allowed: {boundary.allowed_runtime_paths!r}"
            ),
        )

    return StateDeltaValidationResult(status="approved", path=path, operation=operation)


def validate_state_deltas(
    candidate_deltas: list[dict[str, Any]],
    boundary: StateDeltaBoundary | None = None,
) -> list[StateDeltaValidationResult]:
    """Validate a list of candidate deltas. Returns one result per delta.

    First rejection in the list indicates a blocked commit.
    """
    return [validate_state_delta(d, boundary) for d in candidate_deltas]


def first_rejection(
    results: list[StateDeltaValidationResult],
) -> StateDeltaValidationResult | None:
    """Return the first rejected result, or None if all approved."""
    for r in results:
        if r.status == "rejected":
            return r
    return None


def build_default_goc_boundary() -> StateDeltaBoundary:
    """Return the default StateDeltaBoundary for God of Carnage solo runtime."""
    return StateDeltaBoundary()
