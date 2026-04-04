# AI Stack Milestone 11 — Closure Report

**Date:** 2026-04-04  
**Milestone:** M11 — Observability, Governance, and Release Hardening  
**Commit title (required):** `M11: harden observability governance and release readiness`

## Summary

Milestone 11 hardens the unified AI stack for **diagnosis**, **human review**, and **release discipline**. The canonical story execution path now carries a single trace identifier from the backend through World-Engine into LangGraph reproducibility metadata, with structured audits on both sides of the bridge and governance APIs backed by real runtime data.

## Final observability statement

**End-to-end trace continuity is real** for `POST /api/v1/sessions/<id>/turns` and related internal story calls: `X-WoS-Trace-Id` is forwarded to World-Engine, echoed on responses, embedded in turn payloads (`trace_id`), and recorded under `graph_diagnostics.repro_metadata`. Writers-Room and improvement workflows expose `trace_id` in HTTP JSON and emit `workflow.run` audit records.

**Partial:** Standalone MCP tools that call the backend without propagating a caller trace may still generate independent ids; this does not break the canonical path but is not yet unified.

## Final governance statement

Human reviewers can use:

- **`GET /api/v1/admin/ai-stack/session-evidence/<session_id>`** for a consolidated bundle (backend session truth, World-Engine state/diagnostics when reachable, last-turn `repro_metadata`, improvement package count).
- **`GET /api/v1/admin/ai-stack/improvement-packages`** for recommendation packages.
- **Administration-tool** page `/manage/ai-stack/governance` (and alias `/manage/ai-stack-governance`) to drive those APIs through the existing proxy with JWT.
- Existing **`/sessions/.../capability-audit`** with `trace_id` and explicit `bridge_error` when World-Engine cannot be reached.

Surfaces are tied to **real stores and live fetches**, not static placeholders.

## Final reproducibility / versioning statement

`wos_ai_stack.version` defines **`AI_STACK_SEMANTIC_VERSION`** and **`RUNTIME_TURN_GRAPH_VERSION`** (`m11_v1`). Each packaged turn includes **`repro_metadata`** with graph name/version, routing and retrieval summaries, model outcome flags, module/session ids, trace id, optional `story_runtime_core_version`, and **`host_versions.world_engine_app_version`**.

## Final operational failure-visibility statement

- Backend session turns return **502** with `failure_class: world_engine_unreachable` when the play/story bridge fails, and emit **`world_engine.bridge`** audit rows.
- Capability audit and evidence APIs surface **`bridge_error` / `bridge_errors`** instead of empty success.
- World-Engine logs **`story.runtime.failure`** when graph execution throws before exit; graph-level issues continue to appear under **`graph_diagnostics.errors`**.

## Final release-readiness statement

`docs/reports/AI_STACK_RELEASE_READINESS_CHECKLIST.md` lists executable checks (trace, audit, governance APIs, privacy, tests, God of Carnage proof, rollback). The stack is **more release-worthy** than pre-M11 but **not** unconditionally production-grade until environment-specific aggregation, retention, MCP trace unification, and full CI sweep are satisfied.

## Known remaining gaps after M11

- MCP operator trace alignment with backend-originated ids.
- Optional redaction tier for `raw_input` in diagnostics exports.
- Single-command CI from repo root without package path pitfalls (`PYTHONPATH` / separate jobs).

## Recommended post-M11 priorities

1. Wire MCP tools to accept/propagate `X-WoS-Trace-Id` when invoked from authenticated contexts.
2. Add integration test job that runs backend + world-engine scoped suites in CI with documented env vars.
3. Define production log shipping for `wos.audit` and `wos.world_engine.audit` JSON lines.

## References

- Architecture: `docs/architecture/observability_and_governance_in_world_of_shadows.md`
- Gate: `docs/reports/ai_stack_gates/M11_GATE_REVIEW.md`
- Readiness: `docs/reports/AI_STACK_RELEASE_READINESS_CHECKLIST.md`
