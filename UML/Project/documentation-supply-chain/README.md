# Documentation Supply Chain architecture models

Authoring, validation, navigation and publication path for architecture and operational documentation.

**Architecture authority:** SADs, contracts, decisions and generated model companions have explicit roles; navigation and publication projections must not silently become competing truth.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Human author and authoritative documentation corpus | `context` | [Documentation Supply Chain - Context](context/documentation-context.md) | D1 |
| Source, generated models, validation and publication seams | `component` | [Documentation Supply Chain - Components](components/publication-components.md) | D1, D2 |
| Deterministic authoring-to-publication validation | `activity` | [Documentation Supply Chain - Publication Flow](activity/publication-flow.md) | D2 |
| Draft, validated, published and stale documentation | `state` | [Documentation Supply Chain - Lifecycle](states/document-lifecycle.md) | D3 |

## Drift focus

Documents and ADRs moved, archives retained links, and generated projections outlived source decisions. The chain models authorship, transformation and stale-reference detection.

[Decision/view/source traceability](TRACEABILITY.md)
