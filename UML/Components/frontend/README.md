# Frontend architecture models

Player-facing Flask shell and browser runtime for authentication, session launch, streaming narrative blocks and controls.

**Architecture authority:** Frontend owns presentation and transient browser interaction state; it never owns platform identity or live narrative truth.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Presentation boundary across player, backend and world-engine | `context` | [Frontend - System Context](context/frontend-context.md) | D1 |
| Canonical route, bootstrap, stream, rendering and input seams | `component` | [Frontend - Browser and Route Components](components/frontend-components.md) | D1, D2 |
| Ordered input submission and streamed block rendering | `sequence` | [Frontend - Player Turn](sequence/player-turn-sequence.md) | D1 |
| Launch, live and reconnect behavior without local truth drift | `state` | [Frontend - Shell Lifecycle](states/shell-lifecycle.md) | D2, D3 |
| Browser, frontend process and backend API boundary | `deployment` | [Frontend - Deployment](deployment/frontend-deployment.md) | D1 |

## Drift focus

The player shell is split across Python routes and many JavaScript modules while legacy pages remain. Models identify the canonical launch/stream path and browser-only state.

[Decision/view/source traceability](TRACEABILITY.md)
