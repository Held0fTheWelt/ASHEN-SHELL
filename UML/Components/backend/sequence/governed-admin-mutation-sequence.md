# Backend — Governed Admin Mutation

**Viewpoint:** `sequence`
**Concern:** Authorization, validation, persistence and audit of operator changes

[PlantUML source](governed-admin-mutation-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator | Manage content, providers, policies and diagnostics | Privileged authenticated request | [`docs/architecture/project/security-governance/architecture.md`](../../../../docs/architecture/project/security-governance/architecture.md) |
| Governance Services | Validate provider, route, security and runtime settings | Audit-producing admin mutation boundary | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Persistence Models | Represent backend and narrative-governance durable truth | SQLAlchemy models and Alembic schema | [`backend/app/models/__init__.py`](../../../../backend/app/models/__init__.py) |
| Observability | Record platform traces, metrics and diagnostic evidence | Trace correlation with redaction | [`backend/app/observability/__init__.py`](../../../../backend/app/observability/__init__.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator | Governance Services | requests change | authenticated intent | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
| Governance Services | Persistence Models | persists settings and audit | validated governance transaction | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Governance Services | Observability | records decision | auditable outcome | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
