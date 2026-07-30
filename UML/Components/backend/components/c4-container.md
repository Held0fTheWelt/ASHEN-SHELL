# Backend — Runtime Containers

**Viewpoint:** `container`
**Concern:** API, service, persistence, compatibility and observability boundaries

[PlantUML source](c4-container.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| API v1 | Expose platform, play-proxy and admin HTTP contracts | Blueprint routes with auth and rate limits | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| Domain Services | Implement platform and governance use cases | Transaction-scoped service operations | [`backend/app/services/__init__.py`](../../../../backend/app/services/__init__.py) |
| Persistence Models | Represent backend and narrative-governance durable truth | SQLAlchemy models and Alembic schema | [`backend/app/models/__init__.py`](../../../../backend/app/models/__init__.py) |
| Transitional Runtime | Retain explicitly non-authoritative compatibility functions | Quarantined; never player truth authority | [`backend/app/runtime/__init__.py`](../../../../backend/app/runtime/__init__.py) |
| Observability | Record platform traces, metrics and diagnostic evidence | Trace correlation with redaction | [`backend/app/observability/__init__.py`](../../../../backend/app/observability/__init__.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| API v1 | Domain Services | invokes use cases | validated request DTOs | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| Domain Services | Persistence Models | reads/writes durable truth | transaction boundary | [`backend/app/extensions.py`](../../../../backend/app/extensions.py) |
| API v1 | Transitional Runtime | uses explicit compatibility paths | quarantined non-authoritative behavior | [`backend/app/runtime/__init__.py`](../../../../backend/app/runtime/__init__.py) |
| Domain Services | Observability | emits evidence | redacted trace correlation | [`backend/app/observability/trace.py`](../../../../backend/app/observability/trace.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
