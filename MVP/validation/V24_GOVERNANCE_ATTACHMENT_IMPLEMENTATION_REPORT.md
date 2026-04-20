# V24 governance attachment implementation report

## What was changed

- Added a lean `docs/dev/` replacement layer for governance-stable developer paths.
- Restored a v24-resident normative contracts index.
- Restored OpenAPI as a machine anchor under `docs/api/openapi.yaml`.
- Restored or adapted runtime-critical ADRs 0002 and 0003.
- Added a lean operational runtime-governance anchor.
- Added a source-preservation / carry-forward ledger.
- Normalized v24 package identity in governance-critical files.
- Repaired critical FY/root/governance/start-here link targets through a combination of redirects, tombstones, and targeted edits.
- Added a despaghettify workstream state file for governance attachment.
- Extended contractify so explicit `implemented_by`, `validated_by`, and `documented_in` fields now emit bounded relation edges when the referenced files really exist.
- Re-ran the FY governance cycle and generated updated outputs.

## What was not changed

- No gameplay/runtime feature implementation was added.
- No world-engine authority was moved or diluted.
- No broad archive/history tree was restored.
- No attempt was made to close the repository-wide docify backlog.
- No claim of runtime readiness was made.

## What original-repository material was intentionally not restored

- the full `docs/archive/**` tree
- the full `docs/audit/**` tree
- broad `audits/**` history
- presentation-only or promo/export material
- the full historical `docs/dev/**` tree beyond stable lean replacement paths

## What new or repaired v24 anchors now replace removed materials

- `docs/dev/contracts/normative-contracts-index.md`
- `docs/dev/README.md`
- lean redirects under `docs/dev/architecture/`, `docs/dev/tooling/`, and `docs/dev/testing/`
- `docs/operations/OPERATIONAL_GOVERNANCE_RUNTIME.md`
- `docs/governance/adr-0002-backend-session-surface-quarantine.md`
- `docs/governance/adr-0003-scene-identity-canonical-surface.md`
- `governance/V24_SOURCE_PRESERVATION_LEDGER.md`
- lean tombstones under `docs/archive/`, `docs/audit/`, and `docs/presentations/`

## Which FY outputs changed

- `validation/fy_reports/contractify_audit.json`
- `validation/fy_reports/docify_audit.json`
- `validation/fy_reports/despaghettify_setup_audit.json`
- `validation/fy_governance_cycle_stdout.txt`

## What remains unresolved

- Contractify still reports two heuristic ADR vocabulary-overlap conflicts.
- The broad repository docify backlog remains large.
- Historical archive/audit content remains intentionally out of scope unless a future re-audit proves a specific governance need.

## What the next re-audit must verify

- that the added ADR/runtime/OpenAPI/normative-index anchors are still the right lean replacements
- that the new relation density is being used honestly and has not drifted into fabricated edges
- that the touched governance/doc surface remains link-clean
- that no future cycle silently reintroduces v22/v23 identity drift in current package notes
- that runtime-focused implementation work now attaches to these repaired anchors instead of falling back to removed or stale paths
