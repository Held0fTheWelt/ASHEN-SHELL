# Language Gateway Sprint — Status Report
**Datum:** 2026-05-29
**Ausgeführt von:** Claude Code

## Test-Ergebnisse

### backend
- Passed: 4538
- Failed: 3
- Skipped: 2
- Errors: 0
- Command: `python tests/run_tests.py --suite backend`
- JUnit: `tests/reports/pytest_backend_20260529_004306.xml`

#### backend — vollständige Fehlermeldungen
##### FAILURE: `tests.test_adr0041_readiness_consumer_single_mutation_site::test_adr0041_readiness_consumer_only_wired_in_player_session_bundle`
Message:
```text
AssertionError: ADR-0041 final readiness consumer must remain only in game_routes.py; unexpected references in: ['app/api/v1/game/imports_and_dependencies.py', 'app/api/v1/game/player_session_bundle_visible_output.py']
assert not ['app/api/v1/game/imports_and_dependencies.py', 'app/api/v1/game/player_session_bundle_visible_output.py']
```
Details:
```text
tests/test_adr0041_readiness_consumer_single_mutation_site.py:24: in test_adr0041_readiness_consumer_only_wired_in_player_session_bundle
    assert not offenders, (
E   AssertionError: ADR-0041 final readiness consumer must remain only in game_routes.py; unexpected references in: ['app/api/v1/game/imports_and_dependencies.py', 'app/api/v1/game/player_session_bundle_visible_output.py']
E   assert not ['app/api/v1/game/imports_and_dependencies.py', 'app/api/v1/game/player_session_bundle_visible_output.py']
```

##### FAILURE: `tests.test_ai_engineer_suite_service_structure::test_ai_engineer_suite_facade_imports_named_modules`
Message:
```text
AssertionError: assert {'orchestration_status.py', 'runtime_settings.py', 'settings_validation.py', 'repository_paths.py', 'runtime_dashboard.py', 'rag_operations.py'} == {'orchestration_status.py', 'runtime_settings.py', 'settings_validation.py', 'orchestration_status_snapshot.py', 'repository_paths.py', 'runtime_dashboard.py', 'rag_operations.py'}
  
  Extra items in the right set:
  'orchestration_status_snapshot.py'
  
  Full diff:
    {
        'orchestration_status.py',
  -     'orchestration_status_snapshot.py',
        'rag_operations.py',
        'repository_paths.py',
        'runtime_dashboard.py',
        'runtime_settings.py',
        'settings_validation.py',
    }
```
Details:
```text
tests/test_ai_engineer_suite_service_structure.py:34: in test_ai_engineer_suite_facade_imports_named_modules
    assert _facade_imported_modules() == implementation_files
E   AssertionError: assert {'orchestration_status.py', 'runtime_settings.py', 'settings_validation.py', 'repository_paths.py', 'runtime_dashboard.py', 'rag_operations.py'} == {'orchestration_status.py', 'runtime_settings.py', 'settings_validation.py', 'orchestration_status_snapshot.py', 'repository_paths.py', 'runtime_dashboard.py', 'rag_operations.py'}
E     
E     Extra items in the right set:
E     'orchestration_status_snapshot.py'
E     
E     Full diff:
E       {
E           'orchestration_status.py',
E     -     'orchestration_status_snapshot.py',
E           'rag_operations.py',
E           'repository_paths.py',
E           'runtime_dashboard.py',
E           'runtime_settings.py',
E           'settings_validation.py',
E       }
```

##### FAILURE: `tests.test_w5_player_shell_payload::test_live_ws_room_helper_is_w5_first_and_does_not_render_private_why`
Message:
```text
FileNotFoundError: [Errno 2] No such file or directory: 'frontend/static/play_live_ws.js'
```
Details:
```text
tests/test_w5_player_shell_payload.py:132: in test_live_ws_room_helper_is_w5_first_and_does_not_render_private_why
    source = Path("frontend/static/play_live_ws.js").read_text(encoding="utf-8")
/usr/lib/python3.10/pathlib.py:1134: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
/usr/lib/python3.10/pathlib.py:1119: in open
    return self._accessor.open(self, mode, buffering, encoding, errors,
E   FileNotFoundError: [Errno 2] No such file or directory: 'frontend/static/play_live_ws.js'
```

### engine
- Passed: 1548
- Failed: 68
- Skipped: 0
- Errors: 0
- Command: `python tests/run_tests.py --suite engine`
- JUnit: `tests/reports/pytest_engine_20260529_082720.xml`
- Coverage-Gate: FAILED — required 90%, total 84.83%

#### engine — vollständige Fehlermeldungen
##### FAILURE: `tests.test_mvp3_complete_integration.TestPhase345Integration::test_complete_flow_ldss_to_streaming_endpoint`
Message:
```text
AssertionError: Should emit narrator blocks
assert 0 > 0
 +  where 0 = len([])
```
Details:
```text
tests/test_mvp3_complete_integration.py:90: in test_complete_flow_ldss_to_streaming_endpoint
    assert len(narrator_blocks) > 0, "Should emit narrator blocks"
E   AssertionError: Should emit narrator blocks
E   assert 0 > 0
E    +  where 0 = len([])
```

##### FAILURE: `tests.test_mvp3_complete_integration.TestMVP3IntegrationGate::test_mvp3_ldss_to_endpoint_to_frontend_flow`
Message:
```text
AssertionError: assert 'narrator_block' in ['trace_scaffold_emitted', 'ruhepunkt_reached', 'trace_scaffold_summary', 'streaming_complete']
```
Details:
```text
tests/test_mvp3_complete_integration.py:327: in test_mvp3_ldss_to_endpoint_to_frontend_flow
    assert "narrator_block" in event_kinds
E   AssertionError: assert 'narrator_block' in ['trace_scaffold_emitted', 'ruhepunkt_reached', 'trace_scaffold_summary', 'streaming_complete']
```

##### FAILURE: `tests.test_story_runtime_api::test_story_session_lifecycle_and_nl_interpretation`
Message:
```text
AssertionError: assert 'speech' == 'mixed'
  
  - mixed
  + speech
```
Details:
```text
tests/test_story_runtime_api.py:180: in test_story_session_lifecycle_and_nl_interpretation
    assert turn_payload["interpreted_input"]["kind"] == "mixed"
E   AssertionError: assert 'speech' == 'mixed'
E     
E     - mixed
E     + speech
```

##### FAILURE: `tests.test_story_runtime_api::test_story_turns_cover_primary_free_input_paths`
Message:
```text
AssertionError: assert 'ambiguous' == 'speech'
  
  - speech
  + ambiguous
```
Details:
```text
tests/test_story_runtime_api.py:261: in test_story_turns_cover_primary_free_input_paths
    assert turn["interpreted_input"]["kind"] == expected_kind
E   AssertionError: assert 'ambiguous' == 'speech'
E     
E     - speech
E     + ambiguous
```

##### FAILURE: `tests.test_story_runtime_api::test_p0_action_resolution_evidence_opening_vs_schalte_fernseher`
Message:
```text
AssertionError: assert 'rejected_recoverable' in {'committed', 'committed_degraded'}
 +  where 'rejected_recoverable' = <built-in method get of dict object at 0x7d476c12e240>('turn_status')
 +    where <built-in method get of dict object at 0x7d476c12e240> = {'action_consequence_diagnostics': {'action_consequence_contract_pass': 1.0, 'local_context_transition_present': 1.0, 'narrator_consequence_present': 1.0, 'new_location_established': 1.0, ...}, 'callback_web': {'branch_tree_ids': [], 'callback_kind_counts': {}, 'callback_web_id': 'callback_web_0647ee0bb0911312', 'continuity_classes': [], ...}, 'callback_web_feedback': {'callback_web_id': 'callback_web_0647ee0bb0911312', 'continuity_classes': [], 'edge_count': 0, 'edges': [], ...}, 'callback_web_validation': {'contract_pass': True, 'edge_count': 0, 'failure_codes': [], 'observation_count': 1, ...}, ...}.get
```
Details:
```text
tests/test_story_runtime_api.py:320: in test_p0_action_resolution_evidence_opening_vs_schalte_fernseher
    assert turn.get("turn_status") in {"committed", "committed_degraded"}
E   AssertionError: assert 'rejected_recoverable' in {'committed', 'committed_degraded'}
E    +  where 'rejected_recoverable' = <built-in method get of dict object at 0x7d476c12e240>('turn_status')
E    +    where <built-in method get of dict object at 0x7d476c12e240> = {'action_consequence_diagnostics': {'action_consequence_contract_pass': 1.0, 'local_context_transition_present': 1.0, 'narrator_consequence_present': 1.0, 'new_location_established': 1.0, ...}, 'callback_web': {'branch_tree_ids': [], 'callback_kind_counts': {}, 'callback_web_id': 'callback_web_0647ee0bb0911312', 'continuity_classes': [], ...}, 'callback_web_feedback': {'callback_web_id': 'callback_web_0647ee0bb0911312', 'continuity_classes': [], 'edge_count': 0, 'edges': [], ...}, 'callback_web_validation': {'contract_pass': True, 'edge_count': 0, 'failure_codes': [], 'observation_count': 1, ...}, ...}.get
```

##### FAILURE: `tests.test_trace_middleware::test_story_session_create_sets_langfuse_parent_for_opening_turn`
Message:
```text
AssertionError: assert False is True
 +  where False = <built-in method get of dict object at 0x7d474f296680>('generation_fallback_used')
 +    where <built-in method get of dict object at 0x7d474f296680> = {'action_commit_policy': None, 'action_consequence_diagnostics': {'action_consequence_contract_pass': 1.0, 'local_context_transition_present': 1.0, 'narrator_consequence_present': 1.0, 'new_location_established': 1.0, ...}, 'action_resolution_branch': None, 'action_resolution_short_path': False, ...}.get
```
Details:
```text
tests/test_trace_middleware.py:693: in test_story_session_create_sets_langfuse_parent_for_opening_turn
    assert path_summary.get("generation_fallback_used") is True
E   AssertionError: assert False is True
E    +  where False = <built-in method get of dict object at 0x7d474f296680>('generation_fallback_used')
E    +    where <built-in method get of dict object at 0x7d474f296680> = {'action_commit_policy': None, 'action_consequence_diagnostics': {'action_consequence_contract_pass': 1.0, 'local_context_transition_present': 1.0, 'narrator_consequence_present': 1.0, 'new_location_established': 1.0, ...}, 'action_resolution_branch': None, 'action_resolution_short_path': False, ...}.get
```

##### FAILURE: `tests.test_websocket::test_invalid_command_produces_command_rejected_message`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket.py:120: in test_invalid_command_produces_command_rejected_message
    with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:416: in _portal_factory
    yield self.portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket::test_natural_input_message_executes_runtime_turn`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket.py:148: in test_natural_input_message_executes_runtime_turn
    with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:416: in _portal_factory
    yield self.portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket::test_ambiguous_natural_input_continues_with_runtime_event`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket.py:177: in test_ambiguous_natural_input_continues_with_runtime_event
    with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:416: in _portal_factory
    yield self.portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket::test_explicit_command_text_still_works_as_special_case`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket.py:206: in test_explicit_command_text_still_works_as_special_case
    with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:416: in _portal_factory
    yield self.portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket::test_websocket_disconnect_marks_participant_as_offline`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket.py:237: in test_websocket_disconnect_marks_participant_as_offline
    with client.websocket_connect(f"/ws?ticket={ticket}") as websocket:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:416: in _portal_factory
    yield self.portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket_security::test_websocket_rate_limits_commands`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket_security.py:160: in test_websocket_rate_limits_commands
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket_security::test_websocket_enforces_command_authorization`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket_security.py:241: in test_websocket_enforces_command_authorization
    with client.websocket_connect(f"/ws?ticket={guest_ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket_security::test_websocket_prevents_message_injection`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket_security.py:272: in test_websocket_prevents_message_injection
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket_security::test_websocket_graceful_disconnect_on_error`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket_security.py:316: in test_websocket_graceful_disconnect_on_error
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_websocket_security::test_websocket_timeout_inactive_connections`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_websocket_security.py:355: in test_websocket_timeout_inactive_connections
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/sessions.py:85: in __call__
    await self.app(scope, receive, send_wrapper)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/base.py:103: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_run_a_messages_do_not_reach_run_b`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:73: in test_run_a_messages_do_not_reach_run_b
    with client.websocket_connect(f"/ws?ticket={ticket_a}") as ws_a:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_foreign_participant_cannot_claim_seat`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:112: in test_foreign_participant_cannot_claim_seat
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_participant_sees_only_their_perspective`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:158: in test_participant_sees_only_their_perspective
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_transcript_isolated_by_run`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:205: in test_transcript_isolated_by_run
    with client.websocket_connect(f"/ws?ticket={ticket_a}") as ws_a:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_no_permission_bypass_via_crafted_messages`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:239: in test_no_permission_bypass_via_crafted_messages
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_participant_cannot_impersonate_npc`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:279: in test_participant_cannot_impersonate_npc
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_multiple_runs_isolated_state`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:321: in test_multiple_runs_isolated_state
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_commands_only_affect_own_participant`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:375: in test_commands_only_affect_own_participant
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_invalid_run_id_in_message_rejected`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:410: in test_invalid_run_id_in_message_rejected
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_isolation.TestWebSocketIsolation::test_private_state_not_leaked_to_other_participants`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_isolation.py:447: in test_private_state_not_leaked_to_other_participants
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_disconnect_and_reconnect_with_same_ticket`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:62: in test_disconnect_and_reconnect_with_same_ticket
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws1:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_reconnect_preserves_ready_state`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:95: in test_reconnect_preserves_ready_state
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_foreign_participant_rejoin_fails`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:172: in test_foreign_participant_rejoin_fails
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_wrong_character_rejoin_fails`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:229: in test_wrong_character_rejoin_fails
    with client.websocket_connect(f"/ws?ticket={valid_ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_seat_ownership_preserved_across_rejoin`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:266: in test_seat_ownership_preserved_across_rejoin
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_state_consistency_across_rejoin`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:300: in test_state_consistency_across_rejoin
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_normal_disconnect_reconnect`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:340: in test_normal_disconnect_reconnect
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_concurrent_rejoin_attempts`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:369: in test_concurrent_rejoin_attempts
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_rejoin_after_guest_joins`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:408: in test_rejoin_after_guest_joins
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_participant_marked_disconnected_on_graceful_close`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:457: in test_participant_marked_disconnected_on_graceful_close
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_rejoin.TestWebSocketRejoin::test_reconnect_with_wrong_run_id_fails`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_rejoin.py:506: in test_reconnect_with_wrong_run_id_fails
    with client.websocket_connect(f"/ws?ticket={ticket_for_run1}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_say_command_via_websocket`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:70: in test_say_command_via_websocket
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_emote_command_via_websocket`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:98: in test_emote_command_via_websocket
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_move_command_via_websocket`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:122: in test_move_command_via_websocket
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_invalid_command_rejected_with_message`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:157: in test_invalid_command_rejected_with_message
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_say_command_empty_text_rejected`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:185: in test_say_command_empty_text_rejected
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_emote_command_empty_text_rejected`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:211: in test_emote_command_empty_text_rejected
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_move_to_unreachable_room_rejected`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:236: in test_move_to_unreachable_room_rejected
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_inspect_command_via_websocket`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:262: in test_inspect_command_via_websocket
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_set_ready_command_in_group_lobby`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:289: in test_set_ready_command_in_group_lobby
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_start_run_blocked_for_non_host`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:319: in test_start_run_blocked_for_non_host
    with client.websocket_connect(f"/ws?ticket={guest_ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestRuntimeCommandsOverWebSocket::test_multiple_commands_in_sequence`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:346: in test_multiple_commands_in_sequence
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_participant_only_sees_own_account_id_in_snapshot`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:388: in test_participant_only_sees_own_account_id_in_snapshot
    with client.websocket_connect(f"/ws?ticket={alice_ticket}") as alice_ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_no_cross_run_state_leakage`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:422: in test_no_cross_run_state_leakage
    with client.websocket_connect(f"/ws?ticket={ticket_a}") as ws_a:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_visible_occupants_filters_invisible_participants`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:465: in test_visible_occupants_filters_invisible_participants
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_lobby_seat_shows_connected_status`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:492: in test_lobby_seat_shows_connected_status
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_transcript_privacy_in_snapshot`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:521: in test_transcript_privacy_in_snapshot
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_snapshot_contains_run_metadata`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:550: in test_snapshot_contains_run_metadata
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_runtime_commands_and_isolation.TestStateAndBroadcastIsolation::test_available_actions_reflect_current_state`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_runtime_commands_and_isolation.py:580: in test_available_actions_reflect_current_state
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_initial_state_is_lobby`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:59: in test_initial_state_is_lobby
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_ready_action_in_lobby`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:80: in test_ready_action_in_lobby
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_ready_becomes_true_then_false`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:106: in test_ready_becomes_true_then_false
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_duplicate_ready_is_idempotent`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:136: in test_duplicate_ready_is_idempotent
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_start_run_requires_all_ready`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:174: in test_start_run_requires_all_ready
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_start_run_succeeds_when_all_ready`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:218: in test_start_run_succeeds_when_all_ready
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_ready_unavailable_after_run_starts`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:265: in test_ready_unavailable_after_run_starts
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_invalid_action_rejected`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:309: in test_invalid_action_rejected
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_move_blocked_in_lobby`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:336: in test_move_blocked_in_lobby
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_only_host_can_start_run`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:369: in test_only_host_can_start_run
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_state_transitions_are_deterministic`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:426: in test_state_transitions_are_deterministic
    result1 = run_sequence(client, ticket)
tests/test_ws_state_transitions.py:397: in run_sequence
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_multiple_participants_state_synchronization`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:454: in test_multiple_participants_state_synchronization
    with client.websocket_connect(f"/ws?ticket={host_ticket}") as host_ws, \
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

##### FAILURE: `tests.test_ws_state_transitions.TestWebSocketStateTransitions::test_start_run_blocked_in_solo`
Message:
```text
ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```
Details:
```text
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:114: in __enter__
    message = self.receive()
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:177: in receive
    return self.portal.call(self._send_rx.receive)
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:334: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:117: in receive
    return self.receive_nowait()
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/streams/memory.py:99: in receive_nowait
    raise ClosedResourceError
E   anyio.ClosedResourceError

During handling of the above exception, another exception occurred:
tests/test_ws_state_transitions.py:496: in test_start_run_blocked_in_solo
    with client.websocket_connect(f"/ws?ticket={ticket}") as ws:
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:108: in __enter__
    with contextlib.ExitStack() as stack:
/usr/lib/python3.10/contextlib.py:576: in __exit__
    raise exc_details[1]
/usr/lib/python3.10/contextlib.py:153: in __exit__
    self.gen.throw(typ, value, traceback)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:419: in _portal_factory
    yield portal
/usr/lib/python3.10/contextlib.py:561: in __exit__
    if cb(*exc_details):
/usr/lib/python3.10/contextlib.py:449: in _exit_wrapper
    callback(*args, **kwds)
/usr/lib/python3.10/concurrent/futures/_base.py:451: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
/home/heldofthewelt/.local/lib/python3.10/site-packages/anyio/from_thread.py:259: in _call_func
    retval = await retval_or_awaitable
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/testclient.py:137: in _run
    await self.app(self.scope, receive_rx.receive, send_tx.send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/applications.py:1160: in __call__
    await super().__call__(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/applications.py:107: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/errors.py:151: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/routing.py:364: in handle
    await self.app(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:156: in app
    await wrap_app_handling_exceptions(app, session)(scope, receive, send)
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
/home/heldofthewelt/.local/lib/python3.10/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:153: in app
    await func(session)
/home/heldofthewelt/.local/lib/python3.10/site-packages/fastapi/routing.py:760: in app
    await dependant.call(**solved_result.values)
app/api/ws.py:42: in runtime_socket
    await manager.connect(run_id, participant_id, websocket)
app/runtime/manager.py:551: in connect
    await self.broadcast_snapshot(run_id)
app/runtime/manager.py:762: in broadcast_snapshot
    w5_player_view, w5_player_view_diagnostics = self._build_ws_w5_player_view(
app/runtime/manager.py:98: in _build_ws_w5_player_view
    from app.story_runtime.manager.actor_tracking.ws_runtime_snapshot_w5_view import (
app/story_runtime/manager/actor_tracking/ws_runtime_snapshot_w5_view.py:7: in <module>
    from .session_state_w5_view import build_w5_player_view_for_session
E   ImportError: cannot import name 'build_w5_player_view_for_session' from 'app.story_runtime.manager.actor_tracking.session_state_w5_view' (/mnt/d/WorldOfShadows/world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py)
```

## Acceptance Criteria

### task_language_gateway_foundation — PASS
| Kriterium | Status | Fundstelle |
|---|---|---|
| `TaskKind.translation` unter SLM-first | ✓ | `backend/app/runtime/model_routing_contracts.py:29-31` |
| `"translation"` in `TASK_TYPES` | ✓ | `ai_stack/story_runtime/semantic_planner/god_of_carnage_roadmap_semantic_surface.py:47-52` |
| `task_type="translation"` im Adapter-Call | ✓ | `ai_stack/langgraph/runtime_executor/executor_translation_adapter.py:6-9` |
| English Fast-Path `status="skipped_same_language"` | ✓ | `ai_stack/langgraph/runtime_executor/executor_translation_adapter.py:77-83` |
| Schlanker Prompt ohne Catalog-Embed | ✓ | `ai_stack/langgraph/runtime_executor/executor_translation_adapter.py:93-99`; `rg "content_catalog|SEMANTIC CATALOG"` findet keinen Prompt-Embed |
| `timeout_seconds=30.0` | ✓ | `ai_stack/langgraph/runtime_executor/executor_translation_adapter.py:110-113` |

### task_runtime_route_bootstrap — PASS
| Kriterium | Status | Fundstelle |
|---|---|---|
| `classification`, `narrative_formulation`, `translation` in `_REQUIRED_TASK_KINDS` | ✓ | `backend/app/services/governance/governance_runtime/01_imports_and_defaults.py:48-52` |
| `TaskKind.translation: TaskRoutingMode.slm_first` | ✓ | `backend/app/runtime/model_routing.py:32-34` |
| `cost_aware` Preset mit `controlled_values` | ✓ | `backend/app/services/ai_stack/ai_engineer_suite/common.py:243-265` |

### task_output_language_gateway — PASS
| Kriterium | Status | Fundstelle |
|---|---|---|
| `executor_output_translation.py` existiert mit `SOURCE_LINES` | ✓ | `ai_stack/langgraph/runtime_executor/executor_output_translation.py:1-7` |
| `executor_output_translation` in `commit_render` Boundary | ✓ | `ai_stack/langgraph/runtime_executor/semantic_boundaries.py:147-155` |
| `graph.add_node("translate_output", ...)` | ✓ | `ai_stack/langgraph/runtime_executor/executor_graph_build.py:74-76` |
| Edge `render_visible → translate_output → package_output` | ✓ | `ai_stack/langgraph/runtime_executor/executor_graph_build.py:121-123` |

## Legacy-Inventur

| Fund | Typ | Datei:Zeile | Aktion |
|---|---|---|---|
| `OUTPUT LANGUAGE:` Prompt-Zeile in Narrator-Code | CLEAN | `ai_stack/langgraph/runtime_executor/executor_goc_canonical_content.py` — kein Treffer | Keine |
| `OUTPUT LANGUAGE` / `Never default to English` in Core-Prompts | CLEAN | `prompts/ai_stack/core_prompts.json`; Typography-Regel bei `:183` ohne Legacy-Prefix | Keine |
| `_semantic_translation_prompt` | DEAD_CODE | `ai_stack/langgraph/runtime_executor/semantic_input_translation.py:98`; keine Source-Aufrufer außerhalb `semantic_input_translation*.py` | Dokumentieren; Entfernung in Folge-Task prüfen |
| `_compact_semantic_catalog` | DEAD_CODE | `ai_stack/langgraph/runtime_executor/semantic_input_translation.py:53`; nur von `_semantic_translation_prompt` genutzt | Dokumentieren; Entfernung in Folge-Task prüfen |
| README ohne `executor_output_translation` | README_DRIFT | `ai_stack/langgraph/runtime_executor/README.md` — kein Treffer | Korrigieren in Folge-Task |

Hinweis: Der wörtliche `grep -rn "_semantic_translation_prompt" ai_stack/langgraph/runtime_executor/ | grep -v "semantic_input_translation"` meldet nur binäre `__pycache__`-Treffer. Die Source-Prüfung mit `rg --glob "*.py"` findet keine externen Aufrufer.

## Offene Punkte

- Backend-Suite ist rot: 3 Failures, 0 Errors. Betroffen sind ADR-0041 Readiness-Consumer-Single-Mutation, AI-Engineer-Suite-Facade-Importstruktur und ein fehlender Frontend-Static-Pfad `frontend/static/play_live_ws.js`.
- Engine-Suite ist rot: 68 Failures, 0 Errors. Schwerpunkt: MVP3 Streaming/Integration, Story-Runtime-API, Trace-Middleware und WebSocket Runtime/Security/Isolation/Rejoin/State-Transitions. Zusätzlich verfehlt die Suite das Coverage-Gate: 84.83% statt required 90%.
- `semantic_input_translation.py` enthält dokumentierten toten Legacy-Code: `_semantic_translation_prompt` und `_compact_semantic_catalog`.
- `ai_stack/langgraph/runtime_executor/README.md` dokumentiert `executor_output_translation` noch nicht.

## Gesamtstatus

SPRINT_BLOCKED

Begründung: Alle geprüften Language-Gateway-Acceptance-Criteria der drei Sprint-Tasks sind erfüllt und die Legacy-Prompt-Workarounds sind sauber zurückgebaut. Der Sprint kann trotzdem nicht als complete gemeldet werden, weil die geforderten Full-Suites nicht grün sind (`backend`: 3 Failures; `engine`: 68 Failures plus Coverage-Gate-Fehler) und zwei Folgepunkte aus der Legacy-Inventur offen bleiben.
