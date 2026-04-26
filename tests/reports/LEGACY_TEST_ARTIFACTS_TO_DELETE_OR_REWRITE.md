# Legacy Test Artifacts — To Delete or Rewrite

**Generated:** 2026-04-26

---

## Deleted Test Files

| File | Reason | Stub Count | Action |
|------|--------|-----------|--------|
| tests/smoke/test_admin_startup.py | All `assert True` stubs — zero behavioral proof | 27 | DELETED |
| tests/smoke/test_engine_startup.py | All `assert True` stubs — zero behavioral proof | 46 | DELETED |
| tests/e2e/test_phase6_websocket_continuity.py | Stubs counting known list lengths — not real behavior | 22 | DELETED |
| tests/e2e/test_phase7_consequence_filtering.py | Stubs counting known list lengths — not real behavior | 24 | DELETED |
| tests/e2e/test_phase8_9_10_final_validation.py | All `assert True` stubs — zero behavioral proof | 24 | DELETED |

---

## Rewritten Test Methods

| File | Method | Old Pattern | New Behavior |
|------|--------|-------------|--------------|
| tests/gates/test_goc_mvp01_mvp02_foundation_gate.py | test_canonical_god_of_carnage_contains_story_truth | assert True | Validates canonical module YAML exists and loads |
| tests/gates/test_goc_mvp01_mvp02_foundation_gate.py | test_runtime_profile_required_for_solo_starts | assert True | Validates module_id in canonical module YAML |
| tests/gates/test_goc_mvp01_mvp02_foundation_gate.py | test_foundation_gate_passes | assert True | Validates runtime profile is distinct from canonical module |

---

## Tests Retained (Currently Valid)

| File | Classification | Notes |
|------|---------------|-------|
| tests/smoke/test_goc_module_structure_smoke.py | current_valid | Real YAML validation of GoC module structure |
| tests/smoke/test_smoke_contracts.py | current_valid | Contract doc existence checks |
| tests/smoke/test_repository_documented_paths_resolve.py | current_valid | Path resolution |
| tests/gates/test_goc_mvp01_mvp02_foundation_gate.py | current_valid (rewritten) | Foundation gate |
| tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py | current_valid | LDSS gate |
| tests/gates/test_goc_mvp04_observability_diagnostics_gate.py | current_valid | Observability gate |
| tests/e2e/test_gameplay_seam_repairs.py | current_valid | Real HTTP client tests |
| tests/e2e/test_phase4_surface_separation.py | current_valid | Real function call tests |
| tests/e2e/test_phase5_reconnect_reentry.py | current_valid | Real function call tests |

---

## Remaining Minor Issues (Tracked)

| File | Issue | Priority |
|------|-------|----------|
| tests/smoke/test_backend_startup.py | 2 minor `assert True` stubs in otherwise-real test file | LOW |
| tests/gates/test_goc_mvp01_mvp02_foundation_gate.py | test_no_datetime_utcnow_deprecation runs subprocess — fragile | LOW |

---

## Patterns Not Found Requiring Cleanup

After searching:
- `pytest.mark.skip` — not found in primary test paths
- `pytest.mark.xfail` — not found in primary test paths (xfail_policy.md documents policy)
- `or True` — not found in primary gate tests
- `visitor` as valid live actor in tests — not found; only in negative tests (visitor must not exist)
- `god_of_carnage_solo` as canonical content in tests — not found; only as runtime profile reference
