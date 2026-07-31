# Backend — System Context

**Viewpoint:** `context`
**Concern:** Platform ownership, operator delegation and live-runtime authority

[PlantUML source](c4-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Authenticate, browse community and start or continue play | Browser/API session | [`docs/architecture/components/backend/architecture.md`](../../../../docs/architecture/components/backend/architecture.md) |
| Operator | Manage content, providers, policies and diagnostics | Privileged authenticated request | [`docs/architecture/project/security-governance/architecture.md`](../../../../docs/architecture/project/security-governance/architecture.md) |
| Administration Tool | Present operator intent | Backend proxy only | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Backend | Own platform data and governed control-plane operations | Flask /api/v1 | [`backend/app/factory_app.py`](../../../../backend/app/factory_app.py) |
| World Engine | Own live story sessions and commits | Internal story HTTP API plus signed ticket | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Backend | uses platform API | authenticated HTTP | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Operator | Administration Tool | operates | browser control plane | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Administration Tool | Backend | delegates mutations | privileged backend API | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
| Backend | World Engine | proxies live play | signed internal story request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
