# Workstream: repo_governance_rollout

## Closed — DS-028 Quality Lab MCP handler split (session 20260523)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | Quality Lab MCP registry construction now returns stable top-level handler functions instead of owning nested handler bodies. | `tools_registry_handlers_quality_lab.py`; `build_quality_lab_mcp_handlers` | Post: `artifacts/workstreams/repo_governance_rollout/post/session_20260523_DS-028_quality_lab_mcp_comparison.*` |
| w02 | Review, trace, MCP exchange, pattern, investigation, repair-wave, judge-set, and content-revision handlers are readable named functions with unchanged public MCP response contracts. | `wos_quality_lab_review_judgments`, `wos_quality_lab_review_trace`, `wos_quality_lab_review_mcp_exchange`, `wos_quality_lab_find_patterns`, `wos_quality_lab_suggest_investigation`, `wos_quality_lab_plan_repair_wave`, `wos_quality_lab_refine_judge_set`, `wos_quality_lab_plan_content_revision` | Same post comparison as w01. |

**Gates (final):**

- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q tools/mcp_server/tests/test_quality_lab_tools.py ai_stack/tests/test_quality_lab_judgment_interpreter.py ai_stack/tests/test_quality_lab_mcp_exchange_interpreter.py ai_stack/tests/test_quality_lab_pattern_and_planning.py ai_stack/tests/test_quality_lab_trace_interpreter.py --tb=short` — 85 passed.
- `python -m py_compile tools/mcp_server/handlers/tools_registry_handlers_quality_lab.py` — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-23T14:33:12Z`.

**Structural delta:** `build_quality_lab_mcp_handlers` no longer appears in the formal top-12 longest ranking.

## Closed — DS-016 tooling/proxy cleanup (session 20260523)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | The large Langfuse runtime-aspect matrix test now uses a reusable fixture and grouped semantic assertion helpers. | `tools/mcp_server/tests/test_langfuse_verify_tools.py`, `tools/mcp_server/tests/langfuse_verify_runtime_aspect_fixture.py`; `test_summarize_runtime_aspect_matrix_reads_ledger_from_path_summary` | Post comparison: `artifacts/workstreams/repo_governance_rollout/post/session_20260523_DS-016_tooling_proxy_comparison.*` |
| w02 | Administration-tool proxy status/policy constants, header filtering, target construction, logging, and response/error mapping live in a focused policy helper module. | `administration-tool/route_registration_proxy.py`, `administration-tool/route_registration_proxy_policy.py`; `proxy_api` | Post comparison: `artifacts/workstreams/repo_governance_rollout/post/session_20260523_DS-016_tooling_proxy_comparison.*` |

**Plan mirror:** `artifacts/workstreams/repo_governance_rollout/pre/session_20260523_DS-016_wave_plan.json`

**Current metrics report:** `../reports/latest_check_with_metrics.json` generated `2026-05-23T09:10:16Z`.

## Gates

- `python -m py_compile tools/mcp_server/tests/test_langfuse_verify_tools.py tools/mcp_server/tests/langfuse_verify_runtime_aspect_fixture.py administration-tool/route_registration_proxy.py administration-tool/route_registration_proxy_policy.py` — passed.
- `PYTHONPATH=. pytest -q tools/mcp_server/tests/test_langfuse_verify_tools.py --tb=short` — 41 passed.
- `PYTHONPATH=administration-tool:. pytest -q administration-tool/tests/test_proxy.py administration-tool/tests/test_proxy_contract.py administration-tool/tests/test_proxy_error_mapping.py --tb=short` — 127 passed.
- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` — passed.
- `git diff --check` for touched DS-016 files — passed with CRLF normalization warnings only.

## Structural delta

- `test_summarize_runtime_aspect_matrix_reads_ledger_from_path_summary`: 558 AST lines → 15.
- Largest new Langfuse fixture assertion helper: 31 AST lines.
- `proxy_api`: 74 AST lines → 53.
- Current full scan: 10653 functions; L50 793; L100 186; D6 16.
- DS-016 Langfuse fixture hotspot no longer appears in the formal top-12 longest ranking.

## Closed — DS-006 (session 20260520)

Scan-scope hygiene for despaghettify metrics. The wave aligns `fy-manifest.yaml` with the product-code roots required by `spaghetti-check-task.md`, then refreshes `latest_check_with_metrics.json` and the implementation input scan section.

**Wave plan:** `artifacts/workstreams/repo_governance_rollout/pre/session_20260520_DS-006_wave_plan.json`

**Pre artefacts:**

- `artifacts/workstreams/repo_governance_rollout/pre/session_20260520_DS-006_w01_scope_snapshot.md`
- `artifacts/workstreams/repo_governance_rollout/pre/session_20260520_DS-006_w01_scope_snapshot.json`

**Post artefacts:**

- `artifacts/workstreams/repo_governance_rollout/post/session_20260520_DS-006_w01_scope_comparison.md`
- `artifacts/workstreams/repo_governance_rollout/post/session_20260520_DS-006_w01_scope_comparison.json`

**Gates (final):**

- `PYTHONPATH="'fy'-suites" DESPAG_SKIP_ARCHIVE_SYNC=1 python -m despaghettify.tools.hub_cli check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` — pass
- `PYTHONPATH="'fy'-suites" python "'fy'-suites/despaghettify/tools/spaghetti_ast_scan.py"` — pass
