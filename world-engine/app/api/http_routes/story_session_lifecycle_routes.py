from __future__ import annotations

from .common import *
from .models import *

@router.get("/story/sessions", dependencies=[Depends(_require_internal_api_key)])
def list_story_sessions(manager: StoryRuntimeManager = Depends(get_story_manager)) -> dict[str, Any]:
    items = manager.list_session_summaries()
    return {"items": items, "total": len(items)}


def _load_session_create_adapter() -> tuple[Any | None, Any | None]:
    try:
        from app.observability.langfuse_adapter import LangfuseAdapter

        adapter = LangfuseAdapter.get_instance()
        if hasattr(adapter, "refresh_backend_config"):
            adapter.refresh_backend_config(force=True)
        previous_active_span = adapter.get_active_span()
        adapter.set_active_span(None)
        logger.info(
            "[HTTP] Adapter loaded for session create: is_ready=%s is_enabled=%s",
            adapter.is_ready,
            adapter.is_enabled(),
        )
        return adapter, previous_active_span
    except Exception as exc:
        logger.error(
            "[HTTP] ERROR: Failed to load Langfuse adapter for session create: %s: %s",
            type(exc).__name__,
            exc,
            exc_info=True,
        )
        return None, None


def _session_create_langfuse_environment(
    *,
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


def _start_session_create_root_span(
    *,
    adapter: Any | None,
    payload: CreateStorySessionRequest,
    story_session_id: str,
    langfuse_trace_id: str | None,
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
) -> Any | None:
    if not (adapter and adapter.is_enabled()):
        return None
    input_payload = {"module_id": payload.module_id, "session_id": story_session_id}
    base_metadata = {
        "turn_kind": "session_loop",
        "session_loop_status": "runtime_engine_initializing",
        "session_id": story_session_id,
        "environment": lf_tracing_env,
        **trace_classification,
    }
    if langfuse_trace_id:
        return adapter.start_span_in_trace(
            trace_id=langfuse_trace_id,
            name="world-engine.session.create",
            input=input_payload,
            metadata={
                "stage": "world_engine_session_loop_create",
                **base_metadata,
            },
        )
    return adapter.start_trace(
        name="world-engine.session.create",
        session_id=story_session_id,
        input=input_payload,
        metadata={
            "module_id": payload.module_id,
            **base_metadata,
        },
    )


def _session_create_scope(
    *,
    adapter: Any | None,
    root_span: Any | None,
    payload: CreateStorySessionRequest,
    story_session_id: str,
) -> Any:
    if root_span and adapter and hasattr(adapter, "session_scope"):
        return adapter.session_scope(
            root_span=root_span,
            session_id=story_session_id,
            metadata={"module_id": payload.module_id, "turn_kind": "session_loop"},
            trace_name="world-engine.session.create",
            user_id=payload.user_id,
        )
    return nullcontext()


def _create_story_runtime_session(
    *,
    manager: StoryRuntimeManager,
    payload: CreateStorySessionRequest,
    trace_classification: dict[str, Any],
    trace_id: str | None,
    story_session_id: str,
):
    return manager.create_session(
        module_id=payload.module_id,
        runtime_projection=payload.runtime_projection,
        session_input_language=payload.session_input_language,
        session_output_language=payload.session_output_language,
        content_provenance={
            **(payload.content_provenance if isinstance(payload.content_provenance, dict) else {}),
            "trace_classification": trace_classification,
        },
        trace_id=trace_id if isinstance(trace_id, str) else None,
        session_id=story_session_id,
        skip_graph_opening_on_create=payload.skip_graph_opening_on_create,
    )


def _bind_story_session_to_runtime_run(request: Request, session: Any) -> None:
    provenance = session.content_provenance if isinstance(getattr(session, "content_provenance", None), dict) else {}
    run_id = str(provenance.get("run_id") or provenance.get("play_run_id") or "").strip()
    if not run_id:
        return
    runtime_manager = getattr(request.app.state, "manager", None)
    bind = getattr(runtime_manager, "bind_story_session", None)
    if not callable(bind):
        return
    try:
        bind(run_id, session.session_id)
    except Exception:
        logger.debug(
            "Could not bind story session %s to runtime run %s",
            getattr(session, "session_id", ""),
            run_id,
            exc_info=True,
        )


def _session_opening_turn(session: Any) -> dict[str, Any] | None:
    return next(
        (
            row
            for row in reversed(session.diagnostics)
            if isinstance(row, dict) and row.get("turn_kind") == "opening"
        ),
        None,
    )


def _runtime_world_summary(runtime_world: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": runtime_world.get("schema_version"),
        "status": runtime_world.get("status"),
        "mode": runtime_world.get("mode"),
        "current_room_id": runtime_world.get("current_room_id"),
        "room_count": len(runtime_world.get("rooms") if isinstance(runtime_world.get("rooms"), dict) else {}),
        "prop_count": len(runtime_world.get("props") if isinstance(runtime_world.get("props"), dict) else {}),
        "exit_count": len(runtime_world.get("exits") if isinstance(runtime_world.get("exits"), dict) else {}),
        "actor_count": len(runtime_world.get("actors") if isinstance(runtime_world.get("actors"), dict) else {}),
        "diagnostic_summary": runtime_world.get("diagnostic_summary"),
    }


def _session_loop_summary(session: Any, runtime_world_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "runtime_engine_initialized",
        "session_id": session.session_id,
        "module_id": session.module_id,
        "turn_counter": session.turn_counter,
        "current_scene_id": session.current_scene_id,
        "history_len": len(session.history),
        "diagnostics_len": len(session.diagnostics),
        "runtime_world": runtime_world_summary,
    }


def _update_session_create_root_span(
    *,
    root_span: Any | None,
    session: Any,
    session_loop: dict[str, Any],
    runtime_world_summary: dict[str, Any],
    opening_turn: dict[str, Any] | None,
    lf_tracing_env: str,
    trace_classification: dict[str, Any],
) -> None:
    if not root_span:
        return
    root_span.update(
        output={
            "session_id": session.session_id,
            "turn_counter": session.turn_counter,
            "success": True,
            "session_loop": session_loop,
            "path_summary": None,
        },
        metadata={
            "session_id": session.session_id,
            "turn_counter": session.turn_counter,
            "environment": lf_tracing_env,
            **trace_classification,
            "session_loop_status": "runtime_engine_initialized",
            "opening_turn_committed": isinstance(opening_turn, dict),
            "runtime_world": runtime_world_summary,
        },
        level="DEFAULT",
        status_message="runtime_engine_initialized",
    )


def _session_create_response(
    *,
    session: Any,
    opening_turn: dict[str, Any] | None,
    session_loop: dict[str, Any],
    manager: StoryRuntimeManager,
) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "module_id": session.module_id,
        "turn_counter": session.turn_counter,
        "current_scene_id": session.current_scene_id,
        "content_provenance": session.content_provenance,
        "opening_turn": opening_turn,
        "opening_generation_status": "ready_with_opening" if isinstance(opening_turn, dict) else "pending",
        "session_loop": session_loop,
        "runtime_config_status": manager.runtime_config_status(),
        "warnings": [
            "world_engine_authoritative_story_runtime",
            "session_loop_runtime_engine_initialized",
        ],
    }


def _update_session_create_error_span(
    *,
    root_span: Any | None,
    exc: Exception,
    error: str,
) -> None:
    if root_span:
        root_span.update(output={"error": str(exc)}, metadata={"error": error})


def _finalize_session_create_trace(
    *,
    adapter: Any | None,
    root_span: Any | None,
    previous_active_span: Any | None,
) -> None:
    if root_span:
        try:
            root_span.end()
        except Exception:
            logger.warning("Langfuse root span end failed during session create", exc_info=True)
    if adapter and adapter.is_enabled():
        _flush_langfuse_background(adapter, context="session-create")
        try:
            adapter.set_active_span(previous_active_span)
        except Exception:
            logger.warning("Langfuse active span restore failed during session create", exc_info=True)


@router.post("/story/sessions", dependencies=[Depends(_require_internal_api_key)])
def create_story_session(
    payload: CreateStorySessionRequest,
    request: Request,
    manager: StoryRuntimeManager = Depends(get_story_manager),
) -> dict[str, Any]:
    trace_id = getattr(request.state, "trace_id", None)
    langfuse_trace_id = getattr(request.state, "langfuse_trace_id", None)
    adapter = None
    root_span = None
    previous_active_span = None
    story_session_id = uuid4().hex

    try:
        trace_classification = _trace_classification_from_request(
            request,
            runtime_projection=payload.runtime_projection,
        )
        adapter, previous_active_span = _load_session_create_adapter()
        lf_tracing_env = _session_create_langfuse_environment(
            adapter=adapter,
            trace_classification=trace_classification,
        )
        root_span = _start_session_create_root_span(
            adapter=adapter,
            payload=payload,
            story_session_id=story_session_id,
            langfuse_trace_id=langfuse_trace_id,
            lf_tracing_env=lf_tracing_env,
            trace_classification=trace_classification,
        )
        if root_span and adapter:
            adapter.set_active_span(root_span)
        session_scope = _session_create_scope(
            adapter=adapter,
            root_span=root_span,
            payload=payload,
            story_session_id=story_session_id,
        )
        with session_scope:
            session = _create_story_runtime_session(
                manager=manager,
                payload=payload,
                trace_classification=trace_classification,
                trace_id=trace_id if isinstance(trace_id, str) else None,
                story_session_id=story_session_id,
            )
            _bind_story_session_to_runtime_run(request, session)
            runtime_world = session.runtime_world if isinstance(session.runtime_world, dict) else {}
            opening_turn = _session_opening_turn(session)
            runtime_world_summary = _runtime_world_summary(runtime_world)
            session_loop = _session_loop_summary(session, runtime_world_summary)
            _update_session_create_root_span(
                root_span=root_span,
                session=session,
                session_loop=session_loop,
                runtime_world_summary=runtime_world_summary,
                opening_turn=opening_turn,
                lf_tracing_env=lf_tracing_env,
                trace_classification=trace_classification,
            )
        return _session_create_response(
            session=session,
            opening_turn=opening_turn,
            session_loop=session_loop,
            manager=manager,
        )
    except LiveStoryGovernanceError as exc:
        _update_session_create_error_span(root_span=root_span, exc=exc, error="governance_error")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except StorySessionContractError as exc:
        _update_session_create_error_span(root_span=root_span, exc=exc, error="session_contract_error")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        _update_session_create_error_span(root_span=root_span, exc=exc, error="unknown_error")
        raise
    finally:
        _finalize_session_create_trace(
            adapter=adapter,
            root_span=root_span,
            previous_active_span=previous_active_span,
        )


@router.post("/story/sessions/{session_id}/opening", dependencies=[Depends(_require_internal_api_key)])
def generate_story_session_opening(
    session_id: str,
    request: Request,
    manager: StoryRuntimeManager = Depends(get_story_manager),
) -> dict[str, Any]:
    trace_id = getattr(request.state, "trace_id", None)
    try:
        turn = manager.execute_opening(
            session_id=session_id,
            trace_id=trace_id if isinstance(trace_id, str) else None,
        )
        return {
            "session_id": session_id,
            "turn": turn,
            "opening_generation_status": "ready_with_opening",
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Story session not found") from exc
