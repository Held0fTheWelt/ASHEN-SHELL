# Documentation Truth Policy

**Status:** Active — 2026-04-26

---

## Principle

Active documentation must describe current intended architecture. Stale, archived, or historical
documents must not appear in active implementation guidance paths.

---

## Active Documentation Paths

The following paths are authoritative active documentation:

| Path | Content |
|------|---------|
| `docs/architecture/` | Current service boundaries and contracts |
| `docs/testing/` | Test suite contracts and policies |
| `docs/ADR/` | Architecture decision records |
| `docs/admin/` | Operational runbooks |
| `docs/MVPs/` | Current MVP specifications |

---

## Prohibited Content in Active Docs

Active documentation in the above paths must NOT:

| Forbidden Content | Reason |
|------------------|--------|
| Describe `visitor` as a valid live actor | visitor is globally prohibited |
| Describe `god_of_carnage_solo` as canonical content | it is a runtime profile only |
| Reference built-in/demo content as production proof | fallback is not production truth |
| Describe backend-rendered player pages as canonical UI | backend does not render player UI |
| Cite stale phase reports as gate proof | reports are historical, not current evidence |
| Describe fallback/degraded output as success | degraded output must be diagnosed |
| Imply AI output is committed truth | AI proposals require engine validation |
| Reference old monolithic architecture as current | service boundaries are now separate |

---

## Archive Policy

Documents that are no longer active contracts must be moved to `docs/archive/`.

Archive paths:
- `docs/archive/architecture-legacy/` — obsolete architecture docs
- `docs/archive/session-reports-2026/` — historical session and implementation reports
- `docs/archive/documentation-consolidation-2026/` — superseded consolidation docs

Archived documents must have a `README.md` that clearly marks them as historical.

---

## Report vs Proof Distinction

A test report (markdown PASS report, source locator report, closure report) is NOT proof.
Proof requires running, current, source-backed tests that exercise real behavior.

Stale reports in `tests/reports/` are historical records only.
They must not be cited as active gate evidence.

---

## Enforcement

The `root_smoke` suite includes `test_smoke_contracts.py` which validates that required
active architecture documents exist and are non-empty.

Additional docs truth tests should be added to `tests/smoke/` to verify that active docs
do not contain prohibited legacy content.
