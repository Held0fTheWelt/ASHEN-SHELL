# Frontend - Shell Lifecycle

**Viewpoint:** `state`
**Concern:** Launch, live and reconnect behavior without local truth drift

[PlantUML source](shell-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Idle | Await session selection | No live binding | [`frontend/static/play_session_start.js`](../../../../frontend/static/play_session_start.js) |
| Launching | Obtain session and ticket | Single pending launch | [`frontend/static/play_session_start.js`](../../../../frontend/static/play_session_start.js) |
| Live | Accept input and render stream | Bound session id | [`frontend/static/play_shell.js`](../../../../frontend/static/play_shell.js) |
| Reconnecting | Restore event stream without duplicate rendering | Resume cursor | [`frontend/static/play_live_ws.js`](../../../../frontend/static/play_live_ws.js) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Idle | page ready | shell initialized | catalog contract |
| Idle | Launching | experience selected | launch request | [`frontend/static/play_session_start.js`](../../../../frontend/static/play_session_start.js) |
| Launching | Live | bootstrap accepted | session and stream bound | [`frontend/static/play_runtime_bootstrap.js`](../../../../frontend/static/play_runtime_bootstrap.js) |
| Live | Reconnecting | stream lost | retain last cursor | [`frontend/static/play_live_ws.js`](../../../../frontend/static/play_live_ws.js) |
| Reconnecting | Live | resume succeeds | no duplicate blocks | [`frontend/static/play_live_ws.js`](../../../../frontend/static/play_live_ws.js) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
