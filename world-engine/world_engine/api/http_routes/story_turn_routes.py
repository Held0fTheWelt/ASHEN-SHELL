from __future__ import annotations

from .common import *
from .models import *


def _turn_input_fingerprint(player_line: str) -> dict[str, Any]:
    return {
        "player_input_length": len(player_line),
        "player_input_sha256": hashlib.sha256(player_line.encode("utf-8")).hexdigest(),
    }


def _load_turn_langfuse_adapter() -> tuple[Any | None, Any | None]:
    try:
        from world_engine.observability.langfuse_adapter import LangfuseAdapter

        adapter = LangfuseAdapter.get_instance()
        if hasattr(adapter, "refresh_backend_config"):
            adapter.refresh_backend_config(force=True)
        previous_active_span = adapter.get_active_span()
        adapter.set_active_span(None)
        logger.info(
            "[HTTP] Adapter loaded: is_ready=%s, is_enabled=%s",
            adapter.is_ready,
            adapter.is_enabled(),
        )
        return adapter, previous_active_span
    except Exception as exc:
        logger.error(
            "[HTTP] ERROR: Failed to load Langfuse adapter: %s: %s",
            type(exc).__name__,
            exc,
            exc_info=True,
        )
        return None, None


def _turn_langfuse_environment(
    adapter: Any | None,
    trace_classification: dict[str, Any],
) -> str:
    default_lf = os.getenv("LANGFUSE_ENVIRONMENT", "development")
    if adapter and adapter.is_enabled():
        default_lf = str(adapter.config.environment or default_lf)
    return resolve_langfuse_environment(
        trace_classification.get("trace_origin"),
        trace_classification.get("execution_tier"),
        default=default_lf,
    )


def _start_backend_trace_span(
    *,
    adapter: Any,
    langfuse_trace_id: str,
    session_id: str,
    fingerprint: dict[str, Any],
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
) -> Any | None:
    logger.info("[HTTP] Received Langfuse trace_id from Backend: %s", langfuse_trace_id)
    try:
        root_span = adapter.start_span_in_trace(
            trace_id=langfuse_trace_id,
            name="world-engine.turn.execute",
            input={"session_id": session_id, **fingerprint},
            metadata={
                "stage": "world_engine_turn_execution",
                "session_id": session_id,
                "environment": lf_tracing_env,
                **fingerprint,
                **trace_classification,
            },
        )
        logger.info("[HTTP] Created world-engine span in Langfuse trace %s", langfuse_trace_id)
        adapter.set_active_span(root_span)
        return root_span
    except Exception as exc:
        logger.error(
            "[HTTP] Failed to create span under existing Langfuse trace: %s",
            exc,
            exc_info=True,
        )
        return None


def _start_direct_trace_span(
    *,
    adapter: Any,
    session_id: str,
    fingerprint: dict[str, Any],
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
) -> tuple[str | None, Any | None]:
    logger.info("[HTTP] No Langfuse trace_id from Backend - creating new root span")
    root_span = adapter.start_trace(
        name="world-engine.turn.execute",
        session_id=session_id,
        input={"session_id": session_id, **fingerprint},
        metadata={
            "turn_number": 0,
            "session_id": session_id,
            "environment": lf_tracing_env,
            **fingerprint,
            **trace_classification,
        },
    )
    if not root_span:
        logger.warning("[HTTP] Failed to create root span for session %s", session_id)
        return None, None
    logger.info("[HTTP] Root span created, setting as active context")
    adapter.set_active_span(root_span)
    trace_id = getattr(root_span, "trace_id", None)
    if trace_id:
        logger.info("[HTTP] Langfuse trace_id: %s", trace_id)
    return trace_id if isinstance(trace_id, str) else None, root_span


def _start_turn_root_span(
    *,
    adapter: Any | None,
    session_id: str,
    fingerprint: dict[str, Any],
    trace_id: Any,
    langfuse_trace_id: Any,
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
) -> tuple[Any, Any | None]:
    if not adapter or not adapter.is_enabled():
        return trace_id, None
    if langfuse_trace_id:
        root_span = _start_backend_trace_span(
            adapter=adapter,
            langfuse_trace_id=str(langfuse_trace_id),
            session_id=session_id,
            fingerprint=fingerprint,
            lf_tracing_env=lf_tracing_env,
            trace_classification=trace_classification,
        )
        return trace_id, root_span
    resolved_trace_id, root_span = _start_direct_trace_span(
        adapter=adapter,
        session_id=session_id,
        fingerprint=fingerprint,
        lf_tracing_env=lf_tracing_env,
        trace_classification=trace_classification,
    )
    return resolved_trace_id or trace_id, root_span


def _update_turn_root_span(
    *,
    root_span: Any | None,
    turn: dict[str, Any],
    session_id: str,
    player_line: str,
    fingerprint: dict[str, Any],
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
    w5_trace_metadata: dict[str, Any],
) -> int:
    turn_number = int(turn.get("turn_number", 0) or 0)
    if not root_span:
        return turn_number
    cost_summary = (
        turn.get("diagnostics_envelope", {}).get("cost_summary")
        if isinstance(turn.get("diagnostics_envelope"), dict)
        else None
    )
    path_summary = (
        turn.get("observability_path_summary")
        if isinstance(turn.get("observability_path_summary"), dict)
        else None
    )
    level, status_message = _langfuse_root_status(path_summary)
    logger.info("[HTTP] Updating root span with turn_number=%s", turn_number)
    p0_evidence = (
        path_summary.get("p0_action_resolution_evidence")
        if isinstance(path_summary, dict)
        else None
    )
    root_span.update(
        output={
            "turn_number": turn_number,
            "session_id": session_id,
            "success": bool(turn.get("ok", True)),
            "turn_status": turn.get("turn_status"),
            "turn_reason": turn.get("reason"),
            "path_summary": path_summary,
            "raw_player_input": str(turn.get("raw_input") or player_line or "").strip(),
            **fingerprint,
        },
        metadata={
            "turn_number": turn_number,
            "environment": lf_tracing_env,
            **trace_classification,
            "cost_summary": cost_summary,
            "path_quality": path_summary.get("quality_class") if path_summary else None,
            "path_degradation": path_summary.get("degradation_summary") if path_summary else None,
            "path_selected_model": path_summary.get("selected_model") if path_summary else None,
            "path_adapter": path_summary.get("adapter") if path_summary else None,
            "path_fallback_used": path_summary.get("generation_fallback_used") if path_summary else None,
            "p0_action_resolution_evidence": p0_evidence,
            **fingerprint,
            **w5_trace_metadata,
        },
        level=level,
        status_message=status_message,
    )
    logger.info("[HTTP] Root span updated")
    return turn_number


def _backfill_turn_trace_metadata(
    *,
    adapter: Any | None,
    root_span: Any | None,
    langfuse_trace_id: Any,
    turn: dict[str, Any],
    session_id: str,
    turn_number: int,
    lf_tracing_env: str,
) -> None:
    if not adapter or not adapter.is_enabled():
        return
    if not hasattr(adapter, "backfill_trace_metadata_after_commit"):
        return
    turn_trace_ref = getattr(root_span, "trace_id", None) or langfuse_trace_id
    backfill_diag = adapter.backfill_trace_metadata_after_commit(
        trace_id=turn_trace_ref,
        canonical_turn_id=turn.get("canonical_turn_id"),
        story_session_id=session_id,
        turn_number=turn_number,
        environment=lf_tracing_env,
    )
    logger.info("[HTTP] Langfuse trace metadata backfill (turn): %s", backfill_diag)


def _execute_turn_in_trace_scope(
    *,
    manager: StoryRuntimeManager,
    session_id: str,
    player_line: str,
    trace_id: Any,
    adapter: Any | None,
    root_span: Any | None,
    langfuse_trace_id: Any,
    fingerprint: dict[str, Any],
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
) -> dict[str, Any]:
    session_scope = (
        adapter.session_scope(
            root_span=root_span,
            session_id=session_id,
            metadata={"stage": "world_engine_turn_execution"},
            trace_name="world-engine.turn.execute",
        )
        if root_span and adapter and hasattr(adapter, "session_scope")
        else nullcontext()
    )
    with session_scope:
        turn = manager.execute_turn(
            session_id=session_id,
            player_input=player_line,
            trace_id=trace_id if isinstance(trace_id, str) else None,
        )
        try:
            w5_trace_metadata = manager.get_w5_langfuse_metadata(session_id)
        except Exception:
            w5_trace_metadata = {}
        turn_number = _update_turn_root_span(
            root_span=root_span,
            turn=turn if isinstance(turn, dict) else {},
            session_id=session_id,
            player_line=player_line,
            fingerprint=fingerprint,
            lf_tracing_env=lf_tracing_env,
            trace_classification=trace_classification,
            w5_trace_metadata=w5_trace_metadata,
        )
        _backfill_turn_trace_metadata(
            adapter=adapter,
            root_span=root_span,
            langfuse_trace_id=langfuse_trace_id,
            turn=turn if isinstance(turn, dict) else {},
            session_id=session_id,
            turn_number=turn_number,
            lf_tracing_env=lf_tracing_env,
        )
        return turn


def _mark_turn_span_error(root_span: Any | None, exc: Exception, error: str) -> None:
    if root_span:
        root_span.update(output={"error": str(exc)}, metadata={"error": error})


def _close_turn_root_span(
    *,
    adapter: Any | None,
    root_span: Any | None,
    previous_active_span: Any | None,
) -> None:
    if root_span:
        logger.info("[HTTP] Ending root span")
        try:
            root_span.end()
            logger.info("[HTTP] Root span ended")
        except Exception:
            logger.warning("[HTTP] Langfuse root span end failed during story turn", exc_info=True)
    if adapter and adapter.is_enabled():
        logger.info("[HTTP] Scheduling Langfuse adapter flush")
        _flush_langfuse_background(adapter, context="story-turn")
        try:
            adapter.set_active_span(previous_active_span)
        except Exception:
            logger.warning("[HTTP] Langfuse active span restore failed during story turn", exc_info=True)
    else:
        logger.info("[HTTP] Adapter not enabled or not initialized, skipping flush")


@router.post("/story/sessions/{session_id}/turns", dependencies=[Depends(_require_internal_api_key)])
def execute_story_turn(
    session_id: str,
    payload: ExecuteStoryTurnRequest,
    request: Request,
    manager: StoryRuntimeManager = Depends(get_story_manager),
) -> dict[str, Any]:
    player_line = str(payload.player_input).strip()
    fingerprint = _turn_input_fingerprint(player_line)
    trace_id = getattr(request.state, "trace_id", None)
    langfuse_trace_id = getattr(request.state, "langfuse_trace_id", None)
    trace_classification = _trace_classification_from_request(request)
    adapter, previous_active_span = _load_turn_langfuse_adapter()
    lf_tracing_env = _turn_langfuse_environment(adapter, trace_classification)
    trace_id, root_span = _start_turn_root_span(
        adapter=adapter,
        session_id=session_id,
        fingerprint=fingerprint,
        trace_id=trace_id,
        langfuse_trace_id=langfuse_trace_id,
        lf_tracing_env=lf_tracing_env,
        trace_classification=trace_classification,
    )

    try:
        return {
            "session_id": session_id,
            "turn": _execute_turn_in_trace_scope(
                manager=manager,
                session_id=session_id,
                player_line=player_line,
                trace_id=trace_id,
                adapter=adapter,
                root_span=root_span,
                langfuse_trace_id=langfuse_trace_id,
                fingerprint=fingerprint,
                lf_tracing_env=lf_tracing_env,
                trace_classification=trace_classification,
            ),
        }

    except KeyError as exc:
        _mark_turn_span_error(root_span, exc, "session_not_found")
        raise HTTPException(status_code=404, detail="Story session not found") from exc

    except LiveStoryGovernanceError as exc:
        _mark_turn_span_error(root_span, exc, "governance_error")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    except RuntimeError as exc:
        msg = str(exc)
        _mark_turn_span_error(root_span, exc, "runtime_error")
        if msg.startswith("Hard narrative boundary:"):
            detail = msg.split(":", 1)[1].strip() or "hard_boundary_failure"
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail) from exc
        raise

    except Exception as exc:
        _mark_turn_span_error(root_span, exc, "unknown_error")
        raise

    finally:
        _close_turn_root_span(
            adapter=adapter,
            root_span=root_span,
            previous_active_span=previous_active_span,
        )
