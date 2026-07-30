# MCP Server - Governed Delegation

**Viewpoint:** `sequence`
**Concern:** Mutation requests remain under backend authority

[PlantUML source](governed-delegation-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| MCP Client | Discover and invoke Better Tomorrow tools | JSON-RPC over stdio | [`tools/mcp_server/README.md`](../../../../tools/mcp_server/README.md) |
| MCP Server | Validate protocol and dispatch registered capabilities | MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| Capability Registry | Publish stable tool, resource and prompt metadata | Unique names and schemas | [`tools/mcp_server/registry.py`](../../../../tools/mcp_server/registry.py) |
| Handler Families | Implement bounded capability groups | Validated arguments and structured result | [`tools/mcp_server/handlers/__init__.py`](../../../../tools/mcp_server/handlers/__init__.py) |
| Backend Client | Delegate governed session and platform operations | Authenticated HTTP with normalized errors | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| Backend | Authorize and execute platform mutations | Authenticated backend API | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| Langfuse Tracing | Correlate MCP calls without leaking credentials | Redacted trace events | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| MCP Client | MCP Server | invokes capability | valid MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| Capability Registry | Handler Families | binds handler | schema-compatible callable | [`tools/mcp_server/tools_registry.py`](../../../../tools/mcp_server/tools_registry.py) |
| Handler Families | Backend Client | delegates remote operation | normalized backend request | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| MCP Server | Backend | delegates mutation | backend authority and audit | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| Handler Families | Langfuse Tracing | emits call evidence | redacted trace | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
