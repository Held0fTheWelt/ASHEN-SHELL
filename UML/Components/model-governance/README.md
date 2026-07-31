# Model Governance architecture models

Backend-hosted model routing and in-process governance session contracts without live turn commit authority.

**Architecture authority:** Owns adapter routing and governance session shape only; world-engine owns live narrative commits.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Routing package versus live world-engine authority | `context` | [Model Governance - Authority Context](context/authority-context.md) | D1 |
| Routing, registry, contracts and governance session seams | `component` | [Model Governance - Components](components/routing-components.md) | D1 |
| Adapter selection without live commit | `sequence` | [Model Governance - Routing Sequence](sequence/routing-sequence.md) | D1 |
| Governance session models and routing decisions | `class` | [Model Governance - Data Model](classes/routing-data-model.md) | D1 |
| Configure, route and persist governance snapshots only | `state` | [Model Governance - Routing Lifecycle](states/routing-lifecycle.md) | D1 |

## Drift focus

Former backend/app/runtime surfaces moved here or were retired. Models keep routing separate from live session authority.

[Decision/view/source traceability](TRACEABILITY.md)
