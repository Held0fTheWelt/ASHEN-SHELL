# MCP Server architecture models

Local MCP protocol adapter exposing explicit filesystem, backend-session, governance, evaluation, research and observability tools.

**Architecture authority:** The MCP server owns protocol validation and tool routing only; domain mutations remain with backend or world-engine authorities.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Protocol adapter boundary against domain authorities | `context` | [MCP Server - Context](context/mcp-context.md) | D1 |
| Routing, registry, handler, safety and observability seams | `component` | [MCP Server - Components](components/mcp-components.md) | D1, D2, D3 |
| Protocol validation through bounded handler execution | `sequence` | [MCP Server - JSON-RPC Call](sequence/json-rpc-call-sequence.md) | D1, D3 |
| Mutation requests remain under backend authority | `sequence` | [MCP Server - Governed Delegation](sequence/governed-delegation-sequence.md) | D2 |
| Local stdio process, scoped repository and backend boundary | `deployment` | [MCP Server - Deployment](deployment/mcp-deployment.md) | D4 |

## Drift focus

A formerly broad tools module has split into registries, routers and handler families. Models make aliases, deferred tools, filesystem scope and mutation delegation explicit.

[Decision/view/source traceability](TRACEABILITY.md)
