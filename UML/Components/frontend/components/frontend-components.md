# Frontend - Browser and Route Components

**Viewpoint:** `component`
**Concern:** Canonical route, bootstrap, stream, rendering and input seams

[PlantUML source](frontend-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Page Routes | Serve account, community and shell pages | Server-rendered Flask routes | [`frontend/app/routes.py`](../../../../frontend/app/routes.py) |
| Play Routes | Launch session and proxy play requests | No local narrative decisions | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Backend API Client | Apply authentication and transport policy | Bounded HTTP client | [`frontend/app/api_client.py`](../../../../frontend/app/api_client.py) |
| Runtime Bootstrap | Hydrate browser shell from launch payload | Validated bootstrap JSON | [`frontend/static/play_runtime_bootstrap.js`](../../../../frontend/static/play_runtime_bootstrap.js) |
| Narrative Stream | Receive ordered live events | Reconnect-aware WebSocket stream | [`frontend/static/play_narrative_stream.js`](../../../../frontend/static/play_narrative_stream.js) |
| Block Renderer | Render typed narrative blocks safely | Escaped block display model | [`frontend/static/play_block_renderer.js`](../../../../frontend/static/play_block_renderer.js) |
| Play Controls | Capture player intent and accessibility controls | Semantic input command | [`frontend/static/play_controls.js`](../../../../frontend/static/play_controls.js) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Page Routes | Backend API Client | loads platform data | HTTP response mapping | [`frontend/app/routes.py`](../../../../frontend/app/routes.py) |
| Play Routes | Backend API Client | launches session | validated launch payload | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Runtime Bootstrap | Narrative Stream | opens event channel | session ticket and cursor | [`frontend/static/play_runtime_bootstrap.js`](../../../../frontend/static/play_runtime_bootstrap.js) |
| Narrative Stream | Block Renderer | delivers typed block | monotonic event order | [`frontend/static/play_narrative_stream.js`](../../../../frontend/static/play_narrative_stream.js) |
| Play Controls | Play Routes | submits semantic input | one command per turn | [`frontend/static/play_controls.js`](../../../../frontend/static/play_controls.js) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
