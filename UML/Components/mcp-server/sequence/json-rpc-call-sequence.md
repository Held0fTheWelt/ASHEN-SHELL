# MCP Server - JSON-RPC Call

**Viewpoint:** `sequence`
**Concern:** Protocol validation through bounded handler execution

[PlantUML source](json-rpc-call-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| MCP Client | Discover and invoke Better Tomorrow tools | JSON-RPC over stdio | [`tools/mcp_server/README.md`](../../../../tools/mcp_server/README.md) |
| MCP Server | Validate protocol and dispatch registered capabilities | MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| RPC Router | Decode methods and produce protocol errors | JSON-RPC request/response | [`tools/mcp_server/rpc_method_router.py`](../../../../tools/mcp_server/rpc_method_router.py) |
| Capability Registry | Publish stable tool, resource and prompt metadata | Unique names and schemas | [`tools/mcp_server/registry.py`](../../../../tools/mcp_server/registry.py) |
| Handler Families | Implement bounded capability groups | Validated arguments and structured result | [`tools/mcp_server/handlers/__init__.py`](../../../../tools/mcp_server/handlers/__init__.py) |
| Rate Limiter | Bound expensive or mutating calls | Per-operation policy | [`tools/mcp_server/rate_limiter.py`](../../../../tools/mcp_server/rate_limiter.py) |
| Langfuse Tracing | Correlate MCP calls without leaking credentials | Redacted trace events | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| MCP Client | MCP Server | invokes capability | valid MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| MCP Server | RPC Router | dispatches method | protocol envelope | [`tools/mcp_server/rpc_method_router.py`](../../../../tools/mcp_server/rpc_method_router.py) |
| RPC Router | Capability Registry | resolves capability | registered canonical name | [`tools/mcp_server/registry.py`](../../../../tools/mcp_server/registry.py) |
| Capability Registry | Handler Families | binds handler | schema-compatible callable | [`tools/mcp_server/tools_registry.py`](../../../../tools/mcp_server/tools_registry.py) |
| Handler Families | Rate Limiter | checks policy | budget before execution | [`tools/mcp_server/rate_limiter.py`](../../../../tools/mcp_server/rate_limiter.py) |
| Handler Families | Langfuse Tracing | emits call evidence | redacted trace | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
