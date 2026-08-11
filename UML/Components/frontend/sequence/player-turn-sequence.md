# Frontend - Player Turn

**Viewpoint:** `sequence`
**Concern:** Ordered input submission and streamed block rendering

[PlantUML source](player-turn-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Launch and interact with a story session | Authenticated browser interaction | [`frontend/templates/session_shell.html`](../../../../frontend/templates/session_shell.html) |
| Play Controls | Capture player intent and accessibility controls | Semantic input command | [`frontend/static/play_controls.js`](../../../../frontend/static/play_controls.js) |
| Play Routes | Launch session and proxy play requests | No local narrative decisions | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Backend API Client | Apply authentication and transport policy | Bounded HTTP client | [`frontend/app/api_client.py`](../../../../frontend/app/api_client.py) |
| Runtime Bootstrap | Hydrate browser shell from launch payload | Validated bootstrap JSON | [`frontend/static/play_runtime_bootstrap.js`](../../../../frontend/static/play_runtime_bootstrap.js) |
| Narrative Stream | Receive ordered live events | Reconnect-aware WebSocket stream | [`frontend/static/play_narrative_stream.js`](../../../../frontend/static/play_narrative_stream.js) |
| Block Renderer | Render typed narrative blocks safely | Escaped block display model | [`frontend/static/play_block_renderer.js`](../../../../frontend/static/play_block_renderer.js) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Play Controls | enters semantic intent | one explicit player command | [`frontend/static/play_controls.js`](../../../../frontend/static/play_controls.js) |
| Play Controls | Play Routes | submits semantic input | one command per turn | [`frontend/static/play_controls.js`](../../../../frontend/static/play_controls.js) |
| Play Routes | Backend API Client | launches session | validated launch payload | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Backend API Client | Runtime Bootstrap | returns accepted session binding | session id, ticket and initial cursor | [`frontend/static/play_runtime_bootstrap.js`](../../../../frontend/static/play_runtime_bootstrap.js) |
| Runtime Bootstrap | Narrative Stream | opens event channel | session ticket and cursor | [`frontend/static/play_runtime_bootstrap.js`](../../../../frontend/static/play_runtime_bootstrap.js) |
| Narrative Stream | Block Renderer | delivers typed block | monotonic event order | [`frontend/static/play_narrative_stream.js`](../../../../frontend/static/play_narrative_stream.js) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
