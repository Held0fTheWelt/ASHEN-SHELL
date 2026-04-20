# V24 normative-vocabulary ownership implementation report

## What changed

- Added a canonical `docs/ADR/` home for the touched ADR set while retaining `docs/governance/` only as compatibility redirects.
- Clarified ADR-0002 and ADR-0003 so neither reads like a competing owner of runtime authority.
- Added an explicit normative-vocabulary ownership section to the normative contracts index.
- Added a machine-readable ownership file at `validation/fy_inputs/contractify_vocabulary_ownership.json`.
- Taught Contractify conflict detection to consume that ownership file for ADR overlap review.
- Taught generic ADR discovery to prefer `docs/ADR/` and fall back to legacy `docs/governance/`.
- Updated the runtime/MVP spine attachment logic so ADR anchors and supporting documentation prefer `docs/ADR/`.
- Added relation meaning that makes the dependency chain more explicit:
  - ADR-0002 -> `refines` -> ADR-0001
  - ADR-0003 -> `depends_on` -> ADR-0001
- Re-ran focused governance validation and regenerated `validation/fy_reports/contractify_audit.json`.

## What did not change

- No runtime/gameplay feature logic was added.
- No runtime authority was moved away from world-engine.
- No new architecture concepts were introduced.
- No broad ADR rewrite was attempted.
- No blanket ignore/suppression list was added.
- No second normative index was created.

## What was intentionally not attempted

- Full repository-wide migration of every old `docs/governance/` link.
- Full archival cleanup or broad history rewriting.
- New semantic conflict classes beyond the bounded ownership input needed for the two existing overlap warnings.
- Broader Contractify redesign outside the touched ADR / conflict / index path.

## Whether Contractify behavior changed materially

Yes, but in a narrow and honest way.

Material changes:
1. ADR discovery now prefers `docs/ADR/` when present.
2. ADR overlap detection now consults explicit ownership metadata instead of treating every repeated term as an unresolved co-definition.
3. Runtime/MVP spine ADR anchors now resolve against the canonical ADR home first.
4. Curated manual unresolved areas remain visible in the audit payload, but are no longer duplicated into the generic conflict list.

These changes are governance-specific and do not alter runtime/product behavior.

## Focused validation evidence

- Contractify audit: regenerated at `validation/fy_reports/contractify_audit.json`
- Touched governance/doc link check: `validation/V24_TOUCHED_GOVERNANCE_LINK_CHECK.md` -> PASS
- Focused tests: `21 passed`

## Before vs after (audit)

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Contracts | 12 | 40 | +28 |
| Projections | 7 | 10 | +3 |
| Relations | 49 | 276 | +227 |
| Drift findings | 0 | 0 | +0 |
| Conflicts | 2 | 0 | -2 |

## Next re-audit should verify

- ADR-0001 still reads as the single owner of runtime authority.
- ADR-0002 and ADR-0003 still read as dependent/narrow contracts instead of competing owners.
- `validation/fy_inputs/contractify_vocabulary_ownership.json` remains synchronized with the ADR text and the normative index ownership table.
- No future cycle silently reintroduces duplicate linked owner rows in the normative index.
- Legacy `docs/governance/` remains only redirect-level until a broader migration removes it safely.
