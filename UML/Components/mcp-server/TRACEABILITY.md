# MCP Server UML traceability

| View | Kind | Decisions | Source anchors |
| --- | --- | --- | --- |
| [MCP Server - Context](context/mcp-context.md) | `context` | D1 | `backend/app/api/v1/__init__.py`, `tools/mcp_server/README.md`, `tools/mcp_server/backend_client.py`, `tools/mcp_server/handlers/tools_registry_handlers_backend_session.py`, `tools/mcp_server/server.py`, `world-engine/app/api/http.py` |
| [MCP Server - Components](components/mcp-components.md) | `component` | D1, D2, D3 | `tools/mcp_server/backend_client.py`, `tools/mcp_server/handlers/__init__.py`, `tools/mcp_server/handlers/tools_registry_handlers_filesystem.py`, `tools/mcp_server/langfuse_tracing.py`, `tools/mcp_server/rate_limiter.py`, `tools/mcp_server/registry.py`, `tools/mcp_server/rpc_method_router.py`, `tools/mcp_server/server.py`, `tools/mcp_server/tools_registry.py` |
| [MCP Server - JSON-RPC Call](sequence/json-rpc-call-sequence.md) | `sequence` | D1, D3 | `tools/mcp_server/README.md`, `tools/mcp_server/handlers/__init__.py`, `tools/mcp_server/langfuse_tracing.py`, `tools/mcp_server/rate_limiter.py`, `tools/mcp_server/registry.py`, `tools/mcp_server/rpc_method_router.py`, `tools/mcp_server/server.py`, `tools/mcp_server/tools_registry.py` |
| [MCP Server - Governed Delegation](sequence/governed-delegation-sequence.md) | `sequence` | D2 | `backend/app/api/v1/__init__.py`, `tools/mcp_server/README.md`, `tools/mcp_server/backend_client.py`, `tools/mcp_server/handlers/__init__.py`, `tools/mcp_server/langfuse_tracing.py`, `tools/mcp_server/registry.py`, `tools/mcp_server/server.py`, `tools/mcp_server/tools_registry.py` |
| [MCP Server - Deployment](deployment/mcp-deployment.md) | `deployment` | D4 | `backend/Dockerfile`, `scripts/wos_mcp_stdio_launcher.py`, `tools/mcp_server/backend_client.py`, `tools/mcp_server/repo_dotenv.py` |

The table is a generated correspondence view. Source paths are validated before projection.
