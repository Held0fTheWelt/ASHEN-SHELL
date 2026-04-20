# Operational governance runtime (lean v24)

This document is the lean v24 operator-facing governance anchor for runtime-critical seams.

It is **not** a second truth boundary.
It operationalizes the current authoritative boundaries that are declared elsewhere:

- [ADR-0001: Runtime authority in world-engine](../governance/adr-0001-runtime-authority-in-world-engine.md)
- [ADR-0002: Backend session surface quarantine](../governance/adr-0002-backend-session-surface-quarantine.md)
- [Runtime authority and state flow](../technical/runtime/runtime-authority-and-state-flow.md)
- [MCP technical integration](../technical/integration/MCP.md)

## Core operator rules

1. **World-engine** remains the authoritative live runtime for story sessions.
2. **Backend** remains the governance, publishing, policy, and integration layer.
3. **AI output** is proposal material until validated and committed by runtime rules.
4. **MCP and admin/operator surfaces** may observe or trigger allowed flows, but they must not be misrepresented as authoritative player truth.

## Runtime-critical seams to treat carefully

- `backend/app/api/v1/session_routes.py`
- `backend/app/services/game_service.py`
- `backend/app/web/routes.py`
- `world-engine/app/story_runtime/manager.py`
- `ai_stack/mcp_canonical_surface.py`
- `ai_stack/langgraph_runtime.py`
- `story_runtime_core/input_interpreter.py`

## Validation and governance evidence

- Contract/discovery baseline: `validation/fy_reports/contractify_audit.json`
- Documentation/backlog baseline: `validation/fy_reports/docify_audit.json`
- Package validation: [`validation/V24_PACKAGE_VALIDATION.md`](../../validation/V24_PACKAGE_VALIDATION.md)
- Governance attachment repair: [`validation/V24_GOVERNANCE_ATTACHMENT_REPORT.md`](../../validation/V24_GOVERNANCE_ATTACHMENT_REPORT.md)

## Lean-scope note

The broader historical operations layer from the original repository is intentionally not restored in full here.
This page keeps the **runtime-governance anchor role** that contractify and future re-audits need.
