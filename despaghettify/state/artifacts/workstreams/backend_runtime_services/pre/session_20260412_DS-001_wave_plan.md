# DS-001: Import SCC Reduction — Wave Plan

**Date:** 2026-04-12  
**DS-ID:** DS-001  
**Workstream:** backend_runtime_services  
**Baseline Metrics:**
- C1 files in cycles: 35/325 (10.77%)
- C1 trigger: YES (anteil_pct > bar)
- Policy fires: YES

## Sub-waves

| Sub-wave | Goal | Primary files / symbols | Gate |
|----------|------|---------|------|
| 1 | Identify and document SCC structure in `backend/app` | `backend/app` import graph analysis; cycles report | `python despaghettify/tools/import_cycle_share.py` and analysis; verify 35 files found |
| 2 | Extract cycle-breaking DTO module at runtime/services boundary | New: `app.runtime.internal_contracts` (shared DTO types); refactor key exports in `__init__.py` | `pytest backend/tests/runtime/ backend/tests/test_service_layer.py -q` (no regression) |
| 3 | Promote cycle-boundary facades in key affected packages | New: `app.api.v1.dto_layer` (thin re-export layer); thin imports in routes | `pytest backend/tests/test_*_routes.py -q` (route tests); `python despaghettify/tools/ds005_runtime_import_check.py` exit 0 |
| 4 | Verify SCC reduction and close DS-001 | Re-run check with metrics; verify C1 files ≤ 25 (target 20%+); update state docs | `python -m despaghettify.tools check --with-metrics` exit 0; `pytest backend/tests/ -q` green subset |

**Notes:**
- Wave 1 is analysis-only (no code changes); required to scope waves 2–4
- Waves 2–3 may be combined if single DTO extraction resolves multiple cycles
- Target: reduce C1 from 10.77% → <8% (below current high-severity bar)
- Each wave must satisfy completion gate before proceeding to next
