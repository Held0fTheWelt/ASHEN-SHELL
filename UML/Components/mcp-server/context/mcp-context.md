# MCP Server - Context

**Viewpoint:** `context`
**Concern:** Protocol adapter boundary against domain authorities

[PlantUML source](mcp-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| MCP Client | Discover and invoke Better Tomorrow tools | JSON-RPC over stdio | [`tools/mcp_server/README.md`](../../../../tools/mcp_server/README.md) |
| MCP Server | Validate protocol and dispatch registered capabilities | MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| Backend | Authorize and execute platform mutations | Authenticated backend API | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| World Engine | Expose safe session inspection and commands | Runtime API | [`world-engine/app/api/http.py`](../../../../world-engine/app/api/http.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| MCP Client | MCP Server | invokes capability | valid MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| MCP Server | Backend | delegates mutation | backend authority and audit | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| MCP Server | World Engine | inspects session | safe runtime surface | [`tools/mcp_server/handlers/tools_registry_handlers_backend_session.py`](../../../../tools/mcp_server/handlers/tools_registry_handlers_backend_session.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
