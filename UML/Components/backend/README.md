# Backend architecture models

Flask platform and control plane for identity, community, content governance, persistence and the proxy boundary to world-engine.

**Architecture authority:** Backend owns platform data and governed operator state; world-engine owns live narrative state.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Platform ownership, operator delegation and live-runtime authority | `context` | [Backend — System Context](components/c4-context.md) | D1, D2, D4 |
| API, service, persistence, compatibility and observability boundaries | `container` | [Backend — Runtime Containers](components/c4-container.md) | D1, D2 |
| Identity, play proxy, content and governance collaborations | `component` | [Backend — Core Components](components/c4-component.md) | D1, D4 |
| How backend creates trace/ticket context and delegates the live turn | `sequence` | [Backend — Player Turn Proxy](sequence/play-proxy-sequence.md) | D1 |
| Authorization, validation, persistence and audit of operator changes | `sequence` | [Backend — Governed Admin Mutation](sequence/governed-admin-mutation-sequence.md) | D4 |
| Separation of platform truth, narrative governance read models and schema evolution | `class` | [Backend — Persistence Ownership Model](classes/backend-persistence-model.md) | D1, D2 |
| Backend process, persistence, shared governance store and world-engine boundary | `deployment` | [Backend — Deployment](deployment/backend-deployment.md) | D2, D4 |

## Drift focus

Backend is the largest tracked area and changed heavily in services, API and runtime. Models distinguish durable platform ownership, proxy-only play paths and quarantined compatibility runtime.

[Decision/view/source traceability](TRACEABILITY.md)
