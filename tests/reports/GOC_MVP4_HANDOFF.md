# MVP4 Handoff — Observability, Diagnostics, Langfuse, and Narrative Gov

**From**: MVP 4 — Observability, Diagnostics, Langfuse, and Narrative Gov
**To**: MVP 5 — Interactive Text-Adventure Frontend
**Date**: 2026-04-26

---

## Runtime Diagnostics Contract

Every `execute_turn` response for God of Carnage solo sessions includes:

```json
{
  "diagnostics_envelope": {
    "contract": "diagnostics_envelope.v1",
    "trace_id": "<trace_id from request>",
    "story_session_id": "<uuid>",
    "turn_number": 1,
    "content_module_id": "god_of_carnage",
    "runtime_profile_id": "god_of_carnage_solo",
    "human_actor_id": "annette",
    "npc_actor_ids": ["alain", "veronique", "michel"],
    "ai_allowed_actor_ids": ["alain", "michel", "veronique"],
    "ai_forbidden_actor_ids": ["annette"],
    "actor_lane_validation_status": "approved",
    "dramatic_validation_status": "approved",
    "commit_applied": true,
    "response_packaged_from_committed_state": true,
    "quality_class": "canonical",
    "langfuse_status": "disabled",
    "traceable_decisions": [...],
    "live_dramatic_scene_simulator": {"status": "evidenced_live_path", ...},
    "npc_agency": {"primary_responder_id": "veronique", ...},
    "frontend_render_contract": {"scene_block_count": 3, "legacy_blob_used": false},
    "quality": {"outcome": "ok", "quality_class": "canonical", ...}
  }
}
```

## Trace Correlation Contract

- `trace_id` from HTTP request header `X-Trace-Id` appears in `diagnostics_envelope.trace_id`
- `TraceableDecision` records each decision: `responder_plan`, `actor_lane_validation`, `dramatic_validation`, `engine_commit`
- Each decision has `decision_id`, `status` (`accepted`/`rejected`), `trace_span_name`, `input_refs`, `rejected_reasons`

## Langfuse Enabled/Disabled Behavior

- **Disabled** (default in test and dev): `langfuse_status = "disabled"`, `langfuse_trace_id = ""`
- **Enabled with credentials**: `langfuse_status = "traced"`, `langfuse_trace_id = "<lf-trace-id>"`
- Local trace exports written to `tests/reports/langfuse/` during test runs (not static fixtures)
- Langfuse adapter: `backend/app/observability/langfuse_adapter.py`

## Narrative Gov Evidence Contract

`GET /api/story/runtime/narrative-gov-summary` returns:

```json
{
  "contract": "narrative_gov_summary.v1",
  "content_module_health": {"status": "canonical_loaded", ...},
  "runtime_profile_health": {"status": "profile_only", "story_truth_present": false},
  "ldss_health": {"status": "evidenced_live_path", "last_trace_id": "...", ...},
  "actor_lane_health": {"human_actor_id": "annette", "visitor_present": false, ...},
  "frontend_render_contract_health": {"scene_block_count": 3, "legacy_blob_used": false},
  "degradation_health": {"quality_class": "canonical", "degradation_signals": []}
}
```

The administration-tool `runtime.html` page fetches this via `/_proxy/api/story/runtime/narrative-gov-summary` and renders health panels in the browser.

## Actor-Lane Diagnostic Fields

- `human_actor_id` — always in `ai_forbidden_actor_ids`
- `npc_actor_ids` — always in `ai_allowed_actor_ids`
- `visitor` — never appears anywhere
- `actor_lane_validation_status` — `approved` or `rejected`
- If `rejected`, `TraceableDecision` for `actor_lane_validation` has `status=rejected` and `rejected_reasons`

## Dramatic Validation Diagnostic Fields

- `dramatic_validation_status` — `approved` or `rejected`
- `dramatic_validation_reason` — reason string when rejected

## Commit/Response Packaging Evidence

- `commit_applied` — `true` when engine committed the turn
- `response_packaged_from_committed_state` — always `true` (enforced, not AI proposal)
- `live_dramatic_scene_simulator.status` — `evidenced_live_path` (not `not_invoked`)

## Secret Redaction Rules

- Any field with key containing `secret`, `key`, `token`, `password`, `credential`, `auth`, `api_key`, `private`, `passphrase`, `access_token` is redacted to `"[REDACTED]"`
- Langfuse secret_key is never exposed in diagnostics
- Player input is hashed (`player_input_hash`), never logged plaintext

## Visitor Exclusion Proof

- `visitor` never appears in `npc_actor_ids`, `ai_allowed_actor_ids`, `ai_forbidden_actor_ids`, or `actor_lane_health`
- `actor_lane_health.visitor_present` is always `false`
- Gate test `test_mvp04_diagnostics_exclude_visitor` verifies this

## Test Evidence Paths

| Evidence | Path |
|---|---|
| Diagnostics contracts | `ai_stack/diagnostics_envelope.py` |
| Manager integration | `world-engine/app/story_runtime/manager.py` |
| API endpoints | `world-engine/app/api/http.py` |
| Gate tests (26) | `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` |
| Integration tests (8) | `world-engine/tests/test_mvp4_diagnostics_integration.py` |
| Local trace exports | `tests/reports/langfuse/` |
| Source locator | `tests/reports/MVP_Live_Runtime_Completion/MVP4_SOURCE_LOCATOR.md` |
| Operational evidence | `tests/reports/MVP_Live_Runtime_Completion/MVP4_OPERATIONAL_EVIDENCE.md` |

## Known Limitations

1. **Langfuse real trace**: In test environment, Langfuse is disabled; local export proves the contract. Real Langfuse traces require credentials in `LANGFUSE_*` env vars.
2. **Narrative Gov UI**: The `runtime.html` JS panel fetches from play-service. In standalone admin-tool without play-service, it shows "unavailable." Full UI testing requires docker-compose.
3. **ADR-006 Evidence-Gated Architecture**: Pre-existing ADRs cover this; no new ADR needed.

## Safe Assumptions for MVP 5

- `diagnostics_envelope` is always in `execute_turn` result for GoC solo sessions
- `diagnostics_envelope.frontend_render_contract.scene_block_count` > 0 for valid turns
- `diagnostics_envelope.frontend_render_contract.legacy_blob_used` is `false`
- `scene_turn_envelope.visible_scene_output.blocks` is typed and non-empty
- The Narrative Gov API is available at `/api/story/runtime/narrative-gov-summary`
