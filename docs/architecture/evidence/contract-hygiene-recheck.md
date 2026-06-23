# Contract hygiene recheck — 2026-06-23

**Phase:** ADR-retirement plan Phase −1 (contract placement)

## Actions

| Item | Result |
| --- | --- |
| Removed 8 root stubs under `docs/architecture/` | `session_runtime_contract`, `ai_story_contract`, `god_of_carnage_*`, `observability_traceability_contract`, `runtime_profile_vs_content_contract`, `mvp_definition`, `current_service_boundaries` |
| Canonical contracts | Unchanged under `docs/architecture/contracts/` (+ `contracts/runtime/`) |
| Inbound link fixes | content-authority, mvp-live-runtime-completion, ecosystem-topology, `boundaries/content-vs-runtime-profile.md` |
| Smoke tests | `tests/smoke/test_docs_truth.py` now assert SAD/boundary/MVP paths |
| Audit script | `scripts/contract_placement_audit.py` |

## Root whitelist

Only these markdown files remain at `docs/architecture/` top level:

- `README.md`
- `START-HERE.md`
- `QUALITY-STANDARD.md`
- `DOC-HEALTH.md`

## Verification

```bash
python scripts/contract_placement_audit.py --check
python -m pytest tests/gates/test_architecture_documentation_gate.py -q
python tests/run_tests.py tests/smoke/test_docs_truth.py::TestActiveDocsRequiredContracts -q
```

## Deferred

- `contracts/runtime/` subfolder split (`platform/` + `aspects/`) — not done (minimal hygiene path)
- `docs/technical/architecture/*` redirect stubs — retained; point at SADs
