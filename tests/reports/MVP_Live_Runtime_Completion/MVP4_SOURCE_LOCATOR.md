# MVP4 Source Locator Matrix

**MVP**: 04 — Observability, Diagnostics, Langfuse, and Narrative Gov
**Date**: 2026-04-26
**Status**: RESOLVED — no unresolved placeholders

---

## Source Locator Matrix

| Area | Expected Path | Actual Path | Symbol / Anchor | Status |
|---|---|---|---|---|
| MVP 04 guide | `docs/MVPs/MVP_Live_runtime_Completion/04_observability_diagnostics_langfuse_narrative_gov.md` | same | `## Mission`, `DiagnosticsEnvelope`, `NarrativeGovSummary` | found |
| Diagnostics contracts | `ai_stack/diagnostics_envelope.py` | `ai_stack/diagnostics_envelope.py` | `DiagnosticsEnvelope`, `TraceableDecision`, `LocalTraceExport`, `NarrativeGovSummary`, `build_diagnostics_envelope`, `build_narrative_gov_summary`, `redact_secrets` | found (NEW) |
| LDSS module | `ai_stack/live_dramatic_scene_simulator.py` | same | `run_ldss`, `SceneTurnEnvelopeV2` | found |
| World-engine story runtime | `world-engine/app/story_runtime/manager.py` | same | `_finalize_committed_turn` (adds diagnostics_envelope), `get_last_diagnostics_envelope`, `get_narrative_gov_summary` | found (MODIFIED) |
| World-engine API | `world-engine/app/api/http.py` | same | `GET /story/sessions/{session_id}/diagnostics-envelope`, `GET /story/runtime/narrative-gov-summary` | found (MODIFIED) |
| Existing diagnostics API | `world-engine/app/api/http.py` | same | `GET /story/sessions/{session_id}/diagnostics` | found (pre-existing) |
| Langfuse adapter | `backend/app/observability/langfuse_adapter.py` | same | `LangfuseAdapter`, `LangfuseConfig`, `start_trace`, `record_validation`, `redact_value` | found (pre-existing) |
| Trace context | `backend/app/observability/trace.py` | same | `ensure_trace_id`, `get_trace_id`, `set_trace_id` | found (pre-existing) |
| Observability backend routes | `backend/app/api/v1/observability_governance_routes.py` | same | `admin_observability_status`, `admin_observability_update` | found (pre-existing) |
| Observability service | `backend/app/services/observability_governance_service.py` | same | `get_observability_config`, `update_observability_config` | found (pre-existing) |
| Narrative Gov template | `administration-tool/templates/manage/narrative_governance/runtime.html` | same | `mvp4-narrative-gov-summary`, JS fetch of `/_proxy/api/story/runtime/narrative-gov-summary` | found (MODIFIED) |
| Narrative Gov route | `administration-tool/route_registration_manage_sections.py` | same | `manage_narrative_runtime` at `/manage/narrative/runtime` | found (pre-existing) |
| Proxy route | `administration-tool/route_registration_proxy.py` | same | `proxy_api` at `/_proxy/<path>` | found (pre-existing) |
| MVP4 gate tests | `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` | same | 26 test functions | found (NEW) |
| MVP4 integration tests | `world-engine/tests/test_mvp4_diagnostics_integration.py` | same | 8 test functions through execute_turn | found (NEW) |
| run-test.py | `run-test.py` | same | `--mvp4` flag | found (MODIFIED) |
| GitHub workflows | `.github/workflows/engine-tests.yml` | same | `engine-fast-tests` job covers world-engine/tests/ | found (pre-existing, covers MVP4) |
| Root pytest.ini | `pytest.ini` | same | `mvp4` marker | found (MODIFIED) |
| world-engine pytest.ini | `world-engine/pytest.ini` | same | `mvp4` marker | found (MODIFIED) |
| Reports | `tests/reports/MVP_Live_Runtime_Completion/` | same | `MVP4_SOURCE_LOCATOR.md`, `MVP4_OPERATIONAL_EVIDENCE.md` | found (NEW) |
| Handoff | `tests/reports/GOC_MVP4_HANDOFF.md` | same | handoff artifact | found (NEW) |
| ADR-008 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp4-008-diagnostics-degradation-semantics.md` | same | ADR-008 | found (NEW) |
| ADR-009 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp4-009-langfuse-traceable-decisions.md` | same | ADR-009 | found (NEW) |
| ADR-010 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp4-010-narrative-gov-operator-truth-surface.md` | same | ADR-010 | found (NEW) |

---

## Trace/Diagnostics Source Anchor Table

| Step | Required Meaning | Actual File | Actual Symbol | Evidence Test |
|---|---|---|---|---|
| 1 | trace/span creation for live turn | `ai_stack/diagnostics_envelope.py` | `build_local_trace_export()` | `test_mvp04_langfuse_trace_created_when_enabled` |
| 2 | TraceableDecision records created | `ai_stack/diagnostics_envelope.py` | `build_traceable_decisions()` | `test_mvp04_ai_human_actor_violation_is_traced_as_rejected` |
| 3 | LDSS diagnostics read from live turn | `world-engine/app/story_runtime/manager.py` | `_build_ldss_scene_envelope()` → `scene_turn_envelope["diagnostics"]` | `test_mvp04_response_packaging_uses_committed_state` |
| 4 | DiagnosticsEnvelope packaged into response | `world-engine/app/story_runtime/manager.py` | `_finalize_committed_turn` + `build_diagnostics_envelope()` | `test_mvp04_execute_turn_includes_diagnostics_envelope` |
| 5 | Local trace export written | `ai_stack/diagnostics_envelope.py` | `build_local_trace_export()` + file write | `test_mvp04_langfuse_trace_created_when_enabled` |
| 6 | Narrative Gov reads diagnostics source | `world-engine/app/story_runtime/manager.py` | `get_narrative_gov_summary()` | `test_mvp04_narrative_gov_summary_from_manager` |
| 7 | Narrative Gov template renders source-backed state | `administration-tool/templates/manage/narrative_governance/runtime.html` | JS fetch → `/_proxy/api/story/runtime/narrative-gov-summary` | `test_mvp04_narrative_gov_surface_returns_runtime_evidence` |

---

## MVP 04 Known Blockers

None.

## MVP 01/02/03 Dependencies

- All MVP1/2/3 source anchors remain valid
- `scene_turn_envelope` from MVP3 is consumed by MVP4 `build_diagnostics_envelope`
- Actor lane context from MVP2 is reflected in DiagnosticsEnvelope fields
