# Architecture Governance - Components

**Viewpoint:** `component`
**Concern:** Decision registry, SAD, runtime policy, evidence and gate chain

[PlantUML source](governance-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Decision Registry | Index accepted and retired decisions | Stable identifiers and status | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| SAD Decision Sections | Explain decisions in architecture context | Traceable rationale and consequences | [`docs/architecture/project/ecosystem-topology/architecture.md`](../../../../docs/architecture/project/ecosystem-topology/architecture.md) |
| Runtime Governance Services | Validate and apply operational policy | Authorized audited mutation | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Governance Evidence | Record actor, before/after and outcome | Immutable audit event | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| Policy Gates | Block invalid authority and decision drift | Executable CI checks | [`tests/gates/test_adr_live_runtime_commit_semantics_gate.py`](../../../../tests/gates/test_adr_live_runtime_commit_semantics_gate.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Decision Registry | SAD Decision Sections | indexes contextual decision | stable decision id | [`docs/architecture/project/ADR_ABSORPTION_MATRIX.md`](../../../../docs/architecture/project/ADR_ABSORPTION_MATRIX.md) |
| SAD Decision Sections | Runtime Governance Services | constrains implementation | accepted policy semantics | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Runtime Governance Services | Governance Evidence | records mutation outcome | actor and before/after evidence | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| Governance Evidence | Policy Gates | supports verification | machine-checkable evidence | [`tests/gates/test_adr_live_runtime_commit_semantics_gate.py`](../../../../tests/gates/test_adr_live_runtime_commit_semantics_gate.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
