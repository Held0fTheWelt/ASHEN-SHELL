# Observability and Traceability architecture models

Cross-system trace identity, spans, evidence projections, redaction and degradation semantics for a story turn.

**Architecture authority:** Each subsystem emits its own facts under one propagated trace identity; observability records execution but does not become business or narrative truth.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Operator evidence without displacement of domain truth | `context` | [Observability - Context](context/observability-context.md) | D1 |
| Backend, world, AI, MCP and operator projection span ownership | `component` | [Observability - Components](components/trace-components.md) | D1, D2 |
| Trace identity and evidence cross the canonical turn boundaries | `sequence` | [Observability - Turn Trace](sequence/turn-trace.md) | D1 |
| Turn trace, owned spans and explainable decisions | `class` | [Observability - Data Model](classes/trace-data-model.md) | D2 |
| Complete and partial telemetry both disclose their evidence quality | `state` | [Observability - Trace Lifecycle](states/trace-lifecycle.md) | D3 |

## Drift focus

Tracing exists in backend, world-engine, AI and MCP with different helpers and envelopes. Models expose propagation gaps, span ownership and places where diagnostics overstate runtime integration.

[Decision/view/source traceability](TRACEABILITY.md)
