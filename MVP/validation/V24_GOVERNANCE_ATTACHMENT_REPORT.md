# V24 governance attachment report

## Scope

This report records the **FY-governed canonical anchor repair and governance attachment** pass applied to the curated v24 lean package.

The goal of this cycle was **not** runtime-feature implementation.
The goal was to make the current package materially more governable and less drift-prone for the next runtime-readiness implementation cycle.

## Before vs after (contractify)

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Contracts | 7 | 12 | +5 |
| Projections | 0 | 7 | +7 |
| Relations | 1 | 49 | +48 |
| Drift findings | 3 | 0 | -3 |
| Conflicts | 0 | 2 | +2 |

## What materially changed

### 1. Lean truth-anchor repair

The v24 package now carries the missing governance anchors that the lean bundle needed:

- `docs/dev/contracts/normative-contracts-index.md`
- `docs/api/openapi.yaml`
- `docs/operations/OPERATIONAL_GOVERNANCE_RUNTIME.md`
- `docs/governance/adr-0002-backend-session-surface-quarantine.md`
- `docs/governance/adr-0003-scene-identity-canonical-surface.md`
- `governance/V24_SOURCE_PRESERVATION_LEDGER.md`

These anchors were added as **lean replacements**, not as a broad archive restore.

### 2. Contractify attachment expansion

Contractify now discovers and relates runtime-critical seams that were effectively invisible in the v24 baseline:

- runtime authority and backend classification
- canonical turn and vertical-slice anchors
- OpenAPI
- MCP/runtime governance
- backend ↔ world-engine authority seams
- authoring/publish/runtime boundary docs
- operator/governance runbook surfaces

### 3. Real relation coverage

The relation graph is no longer almost empty.
The current relation breakdown is:

- `documented_in`: 17
- `implemented_by`: 10
- `validated_by`: 9
- `documents`: 8
- `references`: 2
- `operationalizes`: 2
- `implements`: 1

The new field-derived relation edges are emitted only when the referenced paths actually exist on disk.

### 4. Documentation-graph repair

For the touched governance/doc surface, the broken-link baseline was reduced from **69 missing repository-relative links across 12 pre-existing priority files** to **0**.
That repair was achieved through a mix of:

- lean replacement docs,
- redirect/tombstone notes,
- corrected FY-suite relative links,
- and updated root/governance/start-here navigation.

### 5. Version and identity normalization

Governance-critical v23/v22 identity drift was reduced in:

- `fy-manifest.yaml`
- `governance/FY_BASELINE_SUMMARY.md`
- `MVP_V24_PACKAGE_NOTE.md`
- `MVP_V24_START_HERE.md`
- embedded `mvp/` identity notes and manifest surfaces

Historical release-note lineage was not rewritten; only misleading current package-identity surfaces were normalized.

### 6. Despaghettify workstream discipline

A dedicated despaghettify workstream anchor now exists for this governance-repair slice:

- `'fy'-suites/despaghettify/state/WORKSTREAM_GOVERNANCE_ATTACHMENT_STATE.md`

This keeps the change set explicitly bounded to governance attachment instead of spilling into unrelated runtime implementation work.

## FY outputs updated in this cycle

- `validation/fy_reports/contractify_audit.json`
- `validation/fy_reports/docify_audit.json`
- `validation/fy_reports/despaghettify_setup_audit.json`
- `validation/fy_governance_cycle_stdout.txt`

## Docify status

Docify remains a **backlog signal**, not a release verdict.

Current summary:

- findings: **1123**
- files with findings: **201**
- parse errors: **2**

This cycle did **not** broaden into repository-wide docstring cleanup.
The two existing parse errors remain visible and honest in the output.

## Remaining unresolved items

### Contractify conflicts

There are currently **2** remaining conflicts, both classified as **`normative_vocabulary_overlap`** across the ADR set.
These are **heuristic overlap warnings**, not proof of contradiction.
They should be reviewed in the next re-audit but do not invalidate the added anchors.

### Out of scope by design

This cycle intentionally did **not**:

- implement new runtime/gameplay features,
- restore the full historical archive,
- claim runtime readiness,
- or convert historical material into current truth without labeling.

## Re-audit checks that should now pass more cleanly

The next re-audit should be able to confirm that v24 now has:

- materially stronger runtime-relevant contract discoverability,
- materially denser relation coverage,
- a lean but real source-preservation ledger,
- repaired governance/doc navigation on the touched surface,
- and clearer current package identity.
