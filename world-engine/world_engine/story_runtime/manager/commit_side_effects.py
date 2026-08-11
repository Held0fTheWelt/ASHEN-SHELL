"""Central compatibility seam for committed-turn side effects.

The caller currently invokes this seam before durable session persistence so
derived callback, cascade, observability, and W5 fields are included in the
session payload. AR-V012 tracks the required transaction/order repair; this
module only removes duplicated orchestration and makes that reorder local.
"""

from __future__ import annotations

from typing import Any


def apply_committed_turn_side_effects(
    manager: Any,
    *,
    session: Any,
    graph_state: dict[str, Any],
    event: dict[str, Any],
    include_w5_shadow: bool,
) -> None:
    """Apply the current ordered compatibility hook sequence exactly once."""

    manager._refresh_callback_web_after_commit(
        session=session,
        event=event,
        graph_state=graph_state,
    )
    manager._refresh_consequence_cascade_after_commit(
        session=session,
        event=event,
        graph_state=graph_state,
    )
    manager._emit_observability_path_for_event(
        session=session,
        graph_state=graph_state,
        event=event,
    )
    session.diagnostics.append(event)
    if include_w5_shadow:
        manager._w5_shadow_extract_after_commit(
            session=session,
            graph_state=graph_state,
            event=event,
        )


__all__ = ["apply_committed_turn_side_effects"]
