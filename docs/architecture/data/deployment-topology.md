# Deployment and trust topology

| Node | Process | Inbound trust boundary | Outbound dependencies | Durable state |
| --- | --- | --- | --- | --- |
| Browser | frontend assets/application | public browser session | backend HTTP, World Engine stream through governed launch | transient UI only |
| Frontend | Flask player/public app | browser auth/session | backend platform API | no live story truth |
| Administration Tool | separate admin frontend | privileged operator session | backend admin/control-plane API | no direct governed secret mutation |
| Backend | Flask API | frontend/admin/MCP authentication | World Engine HTTP, databases, governance stores | platform and control-plane truth |
| World Engine | FastAPI play service | signed backend/internal ticket | AI adapter, content projection, live stores, telemetry | live story authority |
| AI runtime | in-process or adapter-hosted | bounded proposal request | model providers, retrieval stores | proposal/evidence only |
| MCP Server | JSON-RPC adapter | local/authorized MCP client | backend and read-only evidence providers | no independent product truth |

## Trust rules

- Browser and admin requests never bypass backend authorization for governed mutations.
- Backend-to-World-Engine calls are signed and trace-correlated.
- AI providers receive bounded proposal context, not storage authority or raw secrets.
- Telemetry export is redacted and cannot block or change domain commit semantics.
- Local JSON stores are implementation mechanisms; production durability requires an explicit ADR
  before replacement and must preserve revision semantics.
