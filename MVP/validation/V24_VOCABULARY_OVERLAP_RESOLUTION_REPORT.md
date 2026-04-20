# V24 normative-vocabulary overlap resolution report

## Scope

This pass clarifies **normative vocabulary ownership** for the remaining ADR overlap findings without changing runtime architecture or broadening product scope.

## Terms assigned explicit owners

- `runtime authority` -> `ADR-0001`
- `backend session surface` / `session surface` -> `ADR-0002`
- `canonical scene identity surface` -> `ADR-0003`

## Files changed

### Governance / docs
- `docs/ADR/README.md`
- `docs/ADR/adr-0002-backend-session-surface-quarantine.md`
- `docs/ADR/adr-0003-scene-identity-canonical-surface.md`
- `docs/dev/contracts/normative-contracts-index.md`
- `docs/governance/README.md`
- `docs/governance/adr-0001-runtime-authority-in-world-engine.md`
- `docs/governance/adr-0002-backend-session-surface-quarantine.md`
- `docs/governance/adr-0003-scene-identity-canonical-surface.md`
- `docs/governance/adr-template.md`

### Machine-readable governance input
- `validation/fy_inputs/contractify_vocabulary_ownership.json`

### Contractify behavior / validation
- `'fy'-suites/contractify/tools/discovery.py`
- `'fy'-suites/contractify/tools/conflicts.py`
- `'fy'-suites/contractify/tools/runtime_mvp_spine.py`
- `'fy'-suites/contractify/README.md`
- `scripts/validate_touched_governance_links.py`
- `validation/fy_reports/contractify_audit.json`
- `validation/V24_TOUCHED_GOVERNANCE_LINK_CHECK.md`
- `validation/V24_TOUCHED_GOVERNANCE_LINK_CHECK.json`

### Small supporting repairs used to keep the touched governance surface honest
- `ai_stack/goc_scene_identity.py`
- `ai_stack/goc_yaml_authority.py`
- `ai_stack/tests/test_goc_scene_identity.py`
- `tools/verify_goc_scene_identity_single_source.py`
- `backend/app/api/v1/world_engine_console_routes.py`
- `tests/smoke/test_repository_documented_paths_resolve.py`
- `docs/MVPs/MVP_VSL_And_GoC_Contracts/VERTICAL_SLICE_CONTRACT_GOC.md`
- `docs/MVPs/MVP_VSL_And_GoC_Contracts/CANONICAL_TURN_CONTRACT_GOC.md`
- `docs/MVPs/MVP_VSL_And_GoC_Contracts/GATE_SCORING_POLICY_GOC.md`

## Exact wording changes that matter

### ADR-0002
Changed the **Decision** section so it now states explicitly:
- ADR-0001 remains the **sole normative owner** of runtime authority.
- ADR-0002 does **not** define runtime authority.
- ADR-0002 only defines **backend session-surface quarantine**, **backend authority labeling**, and allowed backend use of non-authoritative session-shaped surfaces.

### ADR-0003
Changed the **Decision** section so it now states explicitly:
- ADR-0001 remains the **sole normative owner** of runtime authority.
- ADR-0003 does **not** define runtime authority.
- ADR-0003 only defines the **canonical scene identity surface** and **scene-identity continuity rules** for the GoC slice.

### Normative index
Added a new **Normative vocabulary ownership** section to `docs/dev/contracts/normative-contracts-index.md`.
That section records the owner term -> owner ADR mapping and lists downstream / dependent users.

## Wording narrowed

- In ADR-0002, broad runtime-authority phrasing was narrowed to **backend session-surface quarantine**, **backend authority labeling**, and **non-authoritative session-shaped surfaces** where that was the real subject.
- In ADR-0003, broad runtime-authority phrasing was narrowed to **canonical scene identity surface** and **scene-identity continuity rules**.
- Legitimate dependency references to runtime authority were preserved instead of erased.

## Machine-readable ownership input

Added and wired:
- `validation/fy_inputs/contractify_vocabulary_ownership.json`

This file is **not** an ignore list.
It records:
- the owner anchor for a governed vocabulary term,
- the allowed dependent mentions,
- and short notes explaining the dependency rule.

`contractify.tools.conflicts.detect_adr_vocabulary_overlap()` now consumes this ownership input and suppresses the overlap warning **only** when:
- the configured owner anchor is present among the hits, and
- every additional hit is an allowed dependent mention.

If another ADR or anchor starts using the same term outside the allowed dependent set, the overlap warning returns.

## Contract relation / governance alignment

- ADR-0002 refines ADR-0001: **PASS**
- ADR-0003 depends on ADR-0001: **PASS**
- Backend runtime classification operationalizes ADR-0002: **PASS**

## Focused validation rerun

### Before
- conflicts: **2**
- overlap conflicts:
  - `session surface`
  - `runtime authority`

### After
- conflicts: **0**
- overlap conflicts remaining: **0**
- manual unresolved areas still visible in the audit payload: **2**

The remaining unresolved areas are no longer the vocabulary-overlap ADR warnings.
They are separate, explicitly tracked manual review areas in `manual_unresolved_areas`.

### Touched governance/doc link validation
- status: **PASS**
- missing links: **0**

## Outcome

The two remaining **`normative_vocabulary_overlap`** conflicts disappeared.
They were resolved through explicit ownership, narrower dependent wording, normative-index visibility, and a real ownership input that Contractify now consumes honestly.
