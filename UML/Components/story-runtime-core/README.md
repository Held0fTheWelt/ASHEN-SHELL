# Story Runtime Core architecture models

Dependency-light shared contracts for semantic player input, committed truth, consequence propagation, branching and delivery adapters.

**Architecture authority:** The package owns portable domain contracts and pure algorithms; it does not own a live session, transport or persistence.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Portable contracts versus live and proposal authorities | `context` | [Story Runtime Core - Authority Context](context/story-runtime-core-context.md) | D1 |
| Pure model, intent, truth, consequence, branching and delivery seams | `component` | [Story Runtime Core - Components](components/domain-components.md) | D1, D2 |
| Host data crosses portable algorithms and returns without authority transfer | `sequence` | [Story Runtime Core - Host Adapter Flow](sequence/host-adapter-flow.md) | D1, D3 |
| Intent, committed truth and calculated outcomes | `class` | [Story Runtime Core - Contract Data Model](classes/contract-data-model.md) | D2 |
| Validation and host adaptation of uncommitted shared values | `state` | [Story Runtime Core - Value Lifecycle](states/value-lifecycle.md) | D3 |

## Drift focus

Shared code risks becoming a second runtime. Models separate pure contracts from world-engine ownership and reveal adapters that have accumulated product-specific behavior.

[Decision/view/source traceability](TRACEABILITY.md)
