"""Session memory policy helpers.

Controls how session memory is retained, summarized, and exposed to later runtime turns.
"""
from __future__ import annotations

from .._deps import *

def story_session_from_payload(data: dict[str, Any]) -> StorySession:
    fv = data.get("format_version", 1)
    if fv != 1:
        raise ValueError(f"Unsupported story session snapshot format_version: {fv!r}")

    raw_trace = data.get("last_thread_update_trace")
    trace: ThreadUpdateTrace | None = None
    if isinstance(raw_trace, dict):
        trace = ThreadUpdateTrace.model_validate(raw_trace)

    threads_raw = data.get("narrative_threads") or {}
    threads = StoryNarrativeThreadSet.model_validate(threads_raw)

    created_at = _parse_iso_datetime(str(data["created_at"]))
    updated_at = _parse_iso_datetime(str(data["updated_at"]))

    provenance = data.get("content_provenance")
    if not isinstance(provenance, dict):
        provenance = {}

    return StorySession(
        session_id=str(data["session_id"]),
        module_id=str(data["module_id"]),
        runtime_projection=dict(data["runtime_projection"]),
        created_at=created_at,
        updated_at=updated_at,
        turn_counter=int(data.get("turn_counter", 0)),
        current_scene_id=str(data.get("current_scene_id") or ""),
        session_input_language=str(data.get("session_input_language") or data.get("session_output_language") or DEFAULT_SESSION_LANGUAGE),
        session_output_language=str(data.get("session_output_language") or DEFAULT_SESSION_LANGUAGE),
        history=list(data.get("history") or []),
        diagnostics=list(data.get("diagnostics") or []),
        narrative_threads=threads,
        last_thread_update_trace=trace,
        prior_continuity_impacts=list(data.get("prior_continuity_impacts") or []),
        hierarchical_memory=dict(data.get("hierarchical_memory") or {}),
        environment_state=dict(data.get("environment_state") or {}),
        runtime_world=dict(data.get("runtime_world") or {}),
        content_provenance=provenance,
        canonical_step_id=(str(data["canonical_step_id"]) if data.get("canonical_step_id") else None),
        # ADR-0063: legacy payloads without W5 fields default to [] / None.
        w5_history=[
            dict(snap) for snap in (data.get("w5_history") or []) if isinstance(snap, dict)
        ],
        w5_latest_snapshot=(
            dict(data["w5_latest_snapshot"])
            if isinstance(data.get("w5_latest_snapshot"), dict)
            else None
        ),
    )

def _load_module_memory_policy(
    *,
    module_id: str,
    runtime_profile_id: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        runtime_policy = load_module_runtime_policy(
            module_id=module_id,
            runtime_profile_id=runtime_profile_id,
        ).to_dict()
    except Exception:
        return {}, {}
    memory_policy = (
        runtime_policy.get("memory_policy")
        if isinstance(runtime_policy.get("memory_policy"), dict)
        else {}
    )
    return runtime_policy, memory_policy

def _load_module_callback_web_policy(
    *,
    module_id: str,
    runtime_profile_id: str | None,
) -> dict[str, Any]:
    try:
        runtime_policy = load_module_runtime_policy(
            module_id=module_id,
            runtime_profile_id=runtime_profile_id,
        ).to_dict()
    except Exception:
        return normalize_callback_web_policy(None)
    return callback_web_policy_from_module_runtime(runtime_policy)

def _load_module_consequence_cascade_policy(
    *,
    module_id: str,
    runtime_profile_id: str | None,
) -> dict[str, Any]:
    try:
        runtime_policy = load_module_runtime_policy(
            module_id=module_id,
            runtime_profile_id=runtime_profile_id,
        ).to_dict()
    except Exception:
        return normalize_consequence_cascade_policy(None)
    return consequence_cascade_policy_from_module_runtime(runtime_policy)


def _session_memory_runtime_profile_id(session: StorySession) -> str | None:
    """Resolve the runtime profile used by session memory policies."""
    projection = session.runtime_projection if isinstance(session.runtime_projection, dict) else None
    return _runtime_profile_id_from_projection(projection)


def _prior_hierarchical_memory_snapshot(
    *,
    session: StorySession,
    runtime_profile_id: str | None,
) -> dict[str, Any]:
    """Return the persisted memory snapshot or a policy-compatible empty one."""
    if isinstance(session.hierarchical_memory, dict):
        return session.hierarchical_memory
    return empty_hierarchical_memory_snapshot(
        module_id=session.module_id,
        runtime_profile_id=runtime_profile_id,
    )


def _committed_turn_for_memory_write(
    *,
    session: StorySession,
    committed_turn: dict[str, Any],
    runtime_profile_id: str | None,
    allow_write: bool,
) -> dict[str, Any]:
    """Add module/runtime identity required by the memory write contract."""
    memory_turn = dict(committed_turn)
    memory_turn.setdefault("module_id", session.module_id)
    memory_turn.setdefault("runtime_profile_id", runtime_profile_id)
    if not allow_write:
        memory_turn["recoverable_outcome"] = True
    return memory_turn


def _apply_hierarchical_memory_write_result(
    *,
    session: StorySession,
    prior_snapshot: dict[str, Any],
    write_result: dict[str, Any],
    memory_policy: dict[str, Any],
    runtime_profile_id: str | None,
    allow_write: bool,
) -> dict[str, Any]:
    """Persist an accepted write result or normalize the previous snapshot."""
    if allow_write and write_result.get("write_allowed") and not write_result.get("uncommitted_write_detected"):
        snapshot_after = merge_hierarchical_memory_snapshot(
            prior_snapshot=prior_snapshot,
            write_result=write_result,
            memory_policy=memory_policy,
            module_id=session.module_id,
            runtime_profile_id=runtime_profile_id,
        )
    else:
        snapshot_after = normalize_hierarchical_memory_snapshot(
            prior_snapshot,
            module_id=session.module_id,
            runtime_profile_id=runtime_profile_id,
        )
    session.hierarchical_memory = snapshot_after
    return snapshot_after


def _hierarchical_memory_runtime_surface(
    *,
    write_result: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Expose the memory write and bounded context on the committed event."""
    return {
        "contract": "hierarchical_memory_runtime_surface.v1",
        "write_result": write_result,
        "context": context,
    }


def _selected_memory_tiers(write_result: dict[str, Any]) -> list[str]:
    """Return selected tier ids as non-empty strings."""
    return [
        str(item).strip()
        for item in (write_result.get("selected_tiers") or [])
        if str(item).strip()
    ]


def _written_memory_items(write_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Return concrete memory items accepted by the writer."""
    return [
        item
        for item in (write_result.get("written_items") or [])
        if isinstance(item, dict)
    ]


def _written_memory_tiers(written_items: list[dict[str, Any]]) -> list[str]:
    """Return written tier ids once, preserving write order."""
    tiers_written: list[str] = []
    for item in written_items:
        tier_id = str(item.get("tier") or "").strip()
        if tier_id and tier_id not in tiers_written:
            tiers_written.append(tier_id)
    return tiers_written


def _hierarchical_memory_ledger(
    *,
    session: StorySession,
    event: dict[str, Any],
    graph_state: dict[str, Any],
    runtime_profile_id: str | None,
) -> dict[str, Any]:
    """Load or initialize the runtime aspect ledger used by the memory aspect."""
    ledger = event.get("turn_aspect_ledger")
    if not isinstance(ledger, dict):
        ledger = graph_state.get("turn_aspect_ledger")
    return ensure_runtime_aspect_ledger(
        ledger if isinstance(ledger, dict) else None,
        session_id=session.session_id,
        module_id=session.module_id,
        turn_number=event.get("turn_number"),
        turn_kind=str(event.get("turn_kind") or "player"),
        raw_player_input=event.get("raw_input"),
        trace_id=event.get("trace_id"),
        runtime_profile_id=runtime_profile_id,
    )


def _hierarchical_memory_aspect_record(
    *,
    write_result: dict[str, Any],
    memory_policy: dict[str, Any],
    context: dict[str, Any],
    snapshot_after: dict[str, Any],
    selected_tiers: list[str],
    written_items: list[dict[str, Any]],
    tiers_written: list[str],
    allow_write: bool,
) -> Any:
    """Create the ledger record that explains the memory write decision."""
    failure_reason = write_result.get("failure_reason")
    policy_present = bool(write_result.get("policy_present"))
    return make_aspect_record(
        applicable=policy_present,
        status=str(write_result.get("status") or "not_applicable"),
        expected={
            "policy_present": policy_present,
            "policy_enabled": bool(write_result.get("policy_enabled")),
            "committed_turn_required": True,
            "allow_uncommitted_writes": bool(memory_policy.get("allow_uncommitted_writes")),
            "context_projection_bounded": True,
        },
        selected={
            "selected_tiers": selected_tiers,
            "source_canonical_turn_id": write_result.get("source_canonical_turn_id"),
        },
        actual={
            "write_allowed": bool(write_result.get("write_allowed")),
            "written_item_count": len(written_items),
            "tiers_written": tiers_written,
            "memory_present": bool(context.get("memory_present")),
            "context_item_count": int(context.get("item_count") or 0),
            "context_bounded": bool(context.get("bounded")),
            "uncommitted_write_detected": bool(write_result.get("uncommitted_write_detected")),
            "snapshot_item_count": int(snapshot_after.get("item_count") or 0),
        },
        reasons=[str(failure_reason)] if failure_reason else [],
        source="commit" if allow_write else "commit_guard",
        failure_class="hard_contract_failure" if write_result.get("uncommitted_write_detected") else None,
        failure_reason=str(failure_reason) if failure_reason else None,
        missing_field="canonical_turn_id" if failure_reason == "canonical_turn_id_missing" else None,
    )


def _record_hierarchical_memory_aspect(
    *,
    session: StorySession,
    graph_state: dict[str, Any],
    event: dict[str, Any],
    committed_turn: dict[str, Any],
    allow_write: bool,
) -> dict[str, Any]:
    """Record policy-driven memory evidence and optionally update session memory."""
    runtime_profile_id = _session_memory_runtime_profile_id(session)
    runtime_policy, memory_policy = _load_module_memory_policy(
        module_id=session.module_id,
        runtime_profile_id=runtime_profile_id,
    )
    prior_snapshot = _prior_hierarchical_memory_snapshot(
        session=session,
        runtime_profile_id=runtime_profile_id,
    )
    memory_turn = _committed_turn_for_memory_write(
        session=session,
        committed_turn=committed_turn,
        runtime_profile_id=runtime_profile_id,
        allow_write=allow_write,
    )
    write_result = build_hierarchical_memory_write(
        memory_policy=memory_policy,
        committed_turn=memory_turn,
        runtime_policy=runtime_policy,
    )
    snapshot_after = _apply_hierarchical_memory_write_result(
        session=session,
        prior_snapshot=prior_snapshot,
        write_result=write_result,
        memory_policy=memory_policy,
        runtime_profile_id=runtime_profile_id,
        allow_write=allow_write,
    )
    context = project_hierarchical_memory_context(
        snapshot=snapshot_after,
        memory_policy=memory_policy,
    )
    memory_surface = _hierarchical_memory_runtime_surface(
        write_result=write_result,
        context=context,
    )
    event["hierarchical_memory"] = memory_surface
    graph_state["hierarchical_memory_context"] = context
    selected_tiers = _selected_memory_tiers(write_result)
    written_items = _written_memory_items(write_result)
    tiers_written = _written_memory_tiers(written_items)
    ledger = _hierarchical_memory_ledger(
        session=session,
        event=event,
        graph_state=graph_state,
        runtime_profile_id=runtime_profile_id,
    )
    ledger = set_aspect_record(
        ledger,
        ASPECT_HIERARCHICAL_MEMORY,
        _hierarchical_memory_aspect_record(
            write_result=write_result,
            memory_policy=memory_policy,
            context=context,
            snapshot_after=snapshot_after,
            selected_tiers=selected_tiers,
            written_items=written_items,
            tiers_written=tiers_written,
            allow_write=allow_write,
        ),
    )
    event["turn_aspect_ledger"] = ledger
    graph_state["turn_aspect_ledger"] = ledger
    return memory_surface

__all__ = [
    name
    for name in globals()
    if not name.startswith("__") and name != "annotations"
]
