# Weak Test Replacement Inventory

**Generated:** 2026-04-26

---

## Summary

| Weak Test Type | Files | Tests | Action |
|----------------|-------|-------|--------|
| assert True (pure stub) | 5 | 100+ | Deleted entire files |
| assert True (method stub) | 1 | 3 | Rewritten with real assertions |
| Field presence only | 0 | 0 | None found in primary gates |
| Status-code only | 0 | 0 | None found in primary gates |

---

## Deleted Files (Pure Stub)

### tests/smoke/test_admin_startup.py
- **27 assert True stubs** covering admin startup, proxy config, health checks, auth, security, logging
- All assertions were `assert True` with no real behavior
- **Action:** Deleted entirely
- **Replacement:** None — real admin startup tests should be in `administration-tool/tests/`

### tests/smoke/test_engine_startup.py
- **46 assert True stubs** covering engine startup, game state init, client connections, etc.
- All assertions were `assert True` or `or True` with no real behavior
- **Action:** Deleted entirely
- **Replacement:** None — real engine startup tests should be in `world-engine/tests/`

### tests/e2e/test_phase6_websocket_continuity.py
- 22 stubs: `assert True`, counting lengths of known Python lists
- No actual WebSocket operations tested
- **Action:** Deleted entirely
- **Replacement:** Real WebSocket tests should exercise actual connection, ticket, state sync

### tests/e2e/test_phase7_consequence_filtering.py
- 24 stubs: counting lengths of hardcoded lists
- No actual consequence filtering logic tested
- **Action:** Deleted entirely
- **Replacement:** Real consequence filtering tests should verify actual engine output

### tests/e2e/test_phase8_9_10_final_validation.py
- 24 stubs: all `assert True` with no real behavior
- No pressure dynamics, stress testing, or production readiness checks
- **Action:** Deleted entirely
- **Replacement:** Real production readiness checks belong in integration/engine tests

---

## Rewritten Methods

### tests/gates/test_goc_mvp01_mvp02_foundation_gate.py

#### TestMVP02RulesEnforced
| Old | New |
|-----|-----|
| `test_canonical_god_of_carnage_contains_story_truth`: `assert True` | 4 new tests: module exists, YAML valid, characters present, scenes defined |
| `test_runtime_profile_required_for_solo_starts`: `assert True` | Replaced with `test_canonical_module_annette_and_alain_are_playable`, `test_canonical_module_visitor_is_absent` |

#### TestFoundationGateOverall
| Old | New |
|-----|-----|
| `test_foundation_gate_passes`: `assert True` | `test_solo_profile_is_distinct_from_canonical_module`: verifies module_id !== god_of_carnage_solo |
| | `test_visitor_absent_from_runtime_profile_and_canonical_module`: checks both places |

---

## Remaining Minor Stub (Not Deleted)

### tests/smoke/test_backend_startup.py
- Contains 2 `assert True` stubs in an otherwise-real test file
- The file also contains real Flask app creation and config tests
- **Action:** Not deleted — real tests present; stubs are minor and non-blocking
- **Priority:** LOW — address in follow-up test hardening pass
