# Admin / player / MCP surfaces

**Owning SAD:** [administration-tool](../components/administration-tool/architecture.md), [mcp-server](../components/mcp-server/architecture.md), [security-governance](../project/security-governance/architecture.md).

- Player UI (`frontend/`) uses backend APIs only for auth and play bootstrap.
- Admin UI (`administration-tool/`) uses backend governance routes only.
- MCP (`tools/mcp_server/`) exposes operator/diagnostic tools; no live commit authority.

Evidence: [ADR-0050](../../archive/adr-retired-2026/adr-0050-security-governance-browser-mutation-boundaries.md), [ADR-0052](../../archive/adr-retired-2026/adr-0052-security-governance-admin-control-plane.md).
