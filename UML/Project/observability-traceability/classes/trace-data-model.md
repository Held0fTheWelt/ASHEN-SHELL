# Observability - Data Model

**Viewpoint:** `class`
**Concern:** Turn trace, owned spans and explainable decisions

[PlantUML source](trace-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| TurnTrace | Identify one end-to-end player turn | Globally propagated trace id | [`world-engine/world_engine/observability/trace.py`](../../../../world-engine/world_engine/observability/trace.py) |
| SubsystemSpan | Record bounded operation and ownership | Parent relation and timing | [`ai_stack/langfuse/langfuse_evidence.py`](../../../../ai_stack/langfuse/langfuse_evidence.py) |
| DecisionEvidence | Explain validation, routing or commit outcome | Redacted inputs and explicit result | [`world-engine/world_engine/observability/audit_log.py`](../../../../world-engine/world_engine/observability/audit_log.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| TurnTrace | SubsystemSpan | contains | parented operation tree | [`world-engine/world_engine/observability/trace.py`](../../../../world-engine/world_engine/observability/trace.py) |
| SubsystemSpan | DecisionEvidence | records | explainable outcome | [`world-engine/world_engine/observability/audit_log.py`](../../../../world-engine/world_engine/observability/audit_log.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
