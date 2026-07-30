# Observability - Context

**Viewpoint:** `context`
**Concern:** Operator evidence without displacement of domain truth

[PlantUML source](observability-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator | Diagnose a player turn across services | Authorized redacted view | [`administration-tool/templates/manage/diagnosis.html`](../../../../administration-tool/templates/manage/diagnosis.html) |
| Turn Observability | Correlate execution evidence without owning domain truth | Trace id and redaction policy | [`docs/architecture/project/observability-traceability/architecture.md`](../../../../docs/architecture/project/observability-traceability/architecture.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator | Turn Observability | inspects | authorized diagnostic query | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
