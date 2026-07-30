# Backend — Persistence Ownership Model

**Viewpoint:** `class`
**Concern:** Separation of platform truth, narrative governance read models and schema evolution

[PlantUML source](backend-persistence-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Platform Models | Persist identity, community and site state | Backend database ownership | [`backend/app/models/backend/user.py`](../../../../backend/app/models/backend/user.py) |
| Narrative Governance Models | Persist packages, revisions, evaluations and runtime read models | Governance truth, not live session authority | [`backend/app/models/world_engine/narrative_contracts.py`](../../../../backend/app/models/world_engine/narrative_contracts.py) |
| Alembic Schema | Version backend persistence | Forward migration sequence | [`backend/migrations/env.py`](../../../../backend/migrations/env.py) |
| Persistence Models | Represent backend and narrative-governance durable truth | SQLAlchemy models and Alembic schema | [`backend/app/models/__init__.py`](../../../../backend/app/models/__init__.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Persistence Models | Platform Models | contains | platform ownership | [`backend/app/models/backend/__init__.py`](../../../../backend/app/models/backend/__init__.py) |
| Persistence Models | Narrative Governance Models | contains | governance read model ownership | [`backend/app/models/world_engine/__init__.py`](../../../../backend/app/models/world_engine/__init__.py) |
| Alembic Schema | Persistence Models | versions | Alembic migration history | [`backend/migrations/env.py`](../../../../backend/migrations/env.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
