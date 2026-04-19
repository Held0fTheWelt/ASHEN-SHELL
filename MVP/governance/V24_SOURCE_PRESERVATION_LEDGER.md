# V24 source-preservation and carry-forward ledger

This ledger records which original-repository source layers were intentionally excluded from the curated v24 package, which v24 files now replace their practical governance role, and which areas remain intentionally out of scope.

It exists to stop future cycles from confusing **intentionally excluded** with **accidentally missing**.

## Carry-forward rules

- Do **not** re-expand full historical trees just because a legacy link once existed.
- Prefer a **lean v24-resident replacement anchor**, redirect, or tombstone note where governance value remains.
- Keep historical material out of scope unless it materially improves runtime-readiness implementation governance.

## Layer mapping

| Original repository layer | v24 treatment | v24 replacement / carry-forward anchor | Notes |
|---|---|---|---|
| `docs/dev/contracts/normative-contracts-index.md` | Restored in lean form | `docs/dev/contracts/normative-contracts-index.md` | Reinstated because contractify and runtime-governance navigation depend on it |
| broader `docs/dev/**` tree | Not fully restored | `docs/dev/README.md` plus lean redirect pages under `docs/dev/architecture/`, `docs/dev/tooling/`, `docs/dev/testing/` | Only governance-critical stable paths were recreated |
| `docs/governance/adr-0002-*.md` | Restored in lean form | `docs/governance/adr-0002-backend-session-surface-quarantine.md` | Needed for backend ↔ world-engine authority seam governance |
| `docs/governance/adr-0003-*.md` | Restored in adapted lean form | `docs/governance/adr-0003-scene-identity-canonical-surface.md` | Re-bound to the scene-identity surfaces that actually exist in v24 |
| `docs/operations/OPERATIONAL_GOVERNANCE_RUNTIME.md` | Restored in lean form | `docs/operations/OPERATIONAL_GOVERNANCE_RUNTIME.md` | Needed as an operator/governance contract anchor |
| `docs/api/openapi.yaml` | Restored as machine anchor | `docs/api/openapi.yaml` | Reintroduced because OpenAPI remains contractify-relevant |
| `docs/audit/**` | Not restored in full | `docs/audit/README.md`, `validation/`, `governance/FY_BASELINE_SUMMARY.md` | Historical audit narratives remain out of scope |
| `docs/archive/**` | Not restored in full | `docs/archive/README.md` and selected lean tombstones | Only stable redirect/tombstone targets were added where active v24 docs still referenced them |
| `docs/archive/documentation-consolidation-2026/**` | Not restored in full | lean tombstones in the same subfolder | Preserved only as explicit carry-forward notes for active links |
| `audits/**` at repo root | Intentionally excluded | this ledger + `validation/V24_GOVERNANCE_ATTACHMENT_REPORT.md` | Future re-audits should use current v24 governance outputs, not assume hidden audit trees |
| presentation-only docs (`docs/presentations/**`, promo/export material) | Intentionally excluded | `docs/presentations/README.md` and `docs/presentations/executive-summary-world-of-shadows.md` tombstones | No broad presentation archive restored |
| broad operational/admin/archive side-surfaces | Intentionally excluded | current active docs under `docs/admin/`, `docs/technical/`, `docs/operations/` | Out of scope unless a future cycle proves governance necessity |

## Intentionally out of scope after this repair

The following remain intentionally **not restored**:

- full historical archive narratives,
- broad audit baseline trees,
- presentation decks and promo/export packages,
- full legacy developer-doc coverage beyond stable redirect targets,
- and any runtime-feature implementation that is unrelated to governance attachment.

## Re-audit note

A missing historical file should only be treated as a defect when **both** of these are true:

1. it still has a material governance role for the current v24 package, and
2. no v24 replacement anchor, redirect, or tombstone note exists.

Otherwise treat it as **intentionally excluded by curation**.
