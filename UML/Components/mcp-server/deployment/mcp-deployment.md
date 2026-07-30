# MCP Server - Deployment

**Viewpoint:** `deployment`
**Concern:** Local stdio process, scoped repository and backend boundary

[PlantUML source](mcp-deployment.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Local Stdio Process | Host MCP protocol adapter | One client transport | [`scripts/wos_mcp_stdio_launcher.py`](../../../../scripts/wos_mcp_stdio_launcher.py) |
| Repository Workspace | Provide scoped read/write targets | Configured root containment | [`tools/mcp_server/repo_dotenv.py`](../../../../tools/mcp_server/repo_dotenv.py) |
| Backend Process | Execute governed remote actions | HTTP | [`backend/Dockerfile`](../../../../backend/Dockerfile) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Local Stdio Process | Repository Workspace | scoped filesystem access | configured root | [`tools/mcp_server/repo_dotenv.py`](../../../../tools/mcp_server/repo_dotenv.py) |
| Local Stdio Process | Backend Process | HTTP | governed delegation | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
