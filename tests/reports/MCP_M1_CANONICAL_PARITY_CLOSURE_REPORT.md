# MCP M1 — Canonical parity & governance closure report

## Scope

External MCP layer aligned to a **single canonical descriptor strand** (`ai_stack/mcp_canonical_surface.py`), with explicit tool classes, operating profiles, enriched capability mirror, compact operator truth, audit fields, and tests. No expansion of deferred session tools; no `CapabilityRegistry` shortcut from MCP.

## Named gates

| Gate | Criterion | Result |
|------|-----------|--------|
| **G-MCP-01** | MCP registry matches canonical descriptors; capability names aligned with `capability_catalog()` via `verify_catalog_names_alignment()`; strict translation documented (`docs/mcp/12_M1_canonical_parity.md`). | **PASS** |
| **G-MCP-02** | Governance keys present on every `tools/list` entry and on every `capability_records_for_mcp()` row; operator-visible. | **PASS** |
| **G-MCP-03** | `read_only` / `review_bound` / `write_capable` in registry; `review_safe` denies `wos.session.create`; audit stderr includes `tool_class`, `authority_source`, `operating_profile`. | **PASS** |
| **G-MCP-04** | `classify_mcp_no_eligible_discipline` distinguishes misconfigured, degraded, test_isolated, true no-eligible, healthy non-applicable; covered in tests. | **PASS** |
| **G-MCP-05** | `build_compact_mcp_operator_truth` / `wos.mcp.operator_truth` expose required compact keys including policy, selected_vs_executed note, evidence readiness, runtime authority preservation posture. | **PASS** |
| **G-MCP-06** | No MCP path to `CapabilityRegistry` or turn commit; stubs remain non-authoritative; session create only via backend client. | **PASS** |
| **G-MCP-07** | Validation commands below executed successfully; no regression in directly exercised related suite. | **PASS** |

## Validation commands (executed)

From repository root `WorldOfShadows` (POSIX):

```text
PYTHONPATH=. python -m pytest tools/mcp_server/tests -q --tb=short --no-cov
```

PowerShell (as executed in validation):

```text
cd <repo>
$env:PYTHONPATH = "."
python -m pytest tools/mcp_server/tests -q --tb=short --no-cov
```

**Result:** `56 passed`.

From repository root (ai_stack suite, includes `test_mcp_canonical_surface.py`; no external services):

```text
$env:PYTHONPATH = "."
python -m pytest ai_stack/tests -q --tb=short --no-cov
```

**Result:** `96 passed` (as of last verification).

From `backend/`:

```text
python -m pytest tests/runtime/test_mcp_enrichment.py -q --tb=short --no-cov
```

**Result:** `16 passed`.

## Limitations explicitly outside scope

- Full implementation of `wos.session.get` / `wos.session.state` / `wos.session.logs` / `wos.session.execute_turn` on MCP remains deferred; stubs are intentional.
- MCP operating profiles are **process-local** (env-driven); they do not replace or duplicate Area 2 model-routing operator truth in `app.runtime.area2_operator_truth`.
- No claim of exhaustive parity with every future capability until those capabilities are added to `capability_catalog()` and reflected in the catalog tool.

## 9+ vs 10/10

**9+ ready:** Single descriptor strand, enforced classes, profiles, catalog enrichment, operator truth, audit, and automated gate tests are in place; validation commands are green.

**Not 10/10:** Deferred session/turn tools are not implemented on MCP; MCP operator truth does not ingest live Area2 routing traces; broader backend/ai_stack suites were not re-run in full (only MCP suite + MCP enrichment tests as regression guard for this change).
