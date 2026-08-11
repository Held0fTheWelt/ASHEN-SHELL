# Architecture Governance - Runtime Policy Change

**Viewpoint:** `sequence`
**Concern:** Accepted policy becomes audited runtime configuration and gate evidence

[PlantUML source](runtime-policy-change.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Maintainer | Propose, review and accept architecture decisions | Evidence-backed review | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Governance System | Control decision lifecycle and runtime policy changes | Recorded decision and audit evidence | [`docs/architecture/project/governance/architecture.md`](../../../../docs/architecture/project/governance/architecture.md) |
| SAD Decision Sections | Explain decisions in architecture context | Traceable rationale and consequences | [`docs/architecture/project/ecosystem-topology/architecture.md`](../../../../docs/architecture/project/ecosystem-topology/architecture.md) |
| Runtime Governance Services | Validate and apply operational policy | Authorized audited mutation | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Governance Evidence | Record actor, before/after and outcome | Immutable audit event | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| Policy Gates | Block invalid authority and decision drift | Executable CI checks | [`tests/gates/test_adr_live_runtime_commit_semantics_gate.py`](../../../../tests/gates/test_adr_live_runtime_commit_semantics_gate.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Maintainer | Governance System | proposes and reviews | evidence-backed change | catalog contract |
| Governance System | SAD Decision Sections | records accepted contextual decision | active ADR and affected SAD are updated together | [`docs/architecture/decisions/README.md`](../../../../docs/architecture/decisions/README.md) |
| SAD Decision Sections | Runtime Governance Services | constrains implementation | accepted policy semantics | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Runtime Governance Services | Governance Evidence | records mutation outcome | actor and before/after evidence | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| Governance Evidence | Policy Gates | supports verification | machine-checkable evidence | [`tests/gates/test_adr_live_runtime_commit_semantics_gate.py`](../../../../tests/gates/test_adr_live_runtime_commit_semantics_gate.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
