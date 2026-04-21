# V24 Package Validation

This file records the validation evidence created while assembling `world_of_shadows_mvp_v24_lean_finishable`.

## Validation scope

The goal of this validation is not to claim that the whole platform is production-ready.
The goal is to show that the lean v24 package is:

- intentionally curated,
- lighter than the broader v23 package,
- still anchored by the real runtime/service/governance surfaces,
- still backed by a working reference scaffold,
- still able to emit FY governance baselines,
- and easier to continue without carrying obvious ballast.

## Packaging result

The package keeps end-state-relevant surfaces such as:

- `backend/`
- `world-engine/`
- `frontend/`
- `administration-tool/`
- `writers-room/`
- `ai_stack/`
- `story_runtime_core/`
- `content/`
- `tools/`
- `mvp/`
- curated `docs/`
- `'fy'-suites/`

Examples of intentionally removed ballast include:

- `promo/`
- `outgoing/`
- `postman/`
- broad docs archive/history areas
- presentation-oriented or side-workflow material not needed for completion

## Executed checks

### 1. MVP reference scaffold tests

- command: `pytest mvp/reference_scaffold/tests -q`
- result: **37 passed**
- evidence: `validation/test_results_reference_scaffold.txt`

### 2. AI stack subset tests

- command: `pytest ai_stack/tests/test_capabilities.py ai_stack/tests/test_mcp_canonical_surface.py -q`
- result: **17 passed**
- evidence: `validation/test_results_ai_stack_subset.txt`

This subset remains a conservative importability/coherence proof rather than a claim that the full AI stack has been revalidated.

### 3. Contractify baseline

- contracts: **7**
- projections: **0**
- relations: **1**
- drift findings: **3**
- conflicts: **0**
- evidence: `validation/fy_reports/contractify_audit.json`

The lean package still produces a real contract baseline, even after ballast removal.

### 4. Docify baseline

- findings: **1123**
- files with findings: **201**
- parse errors: **2**
- evidence: `validation/fy_reports/docify_audit.json`

The docify run remains useful as backlog evidence. In this environment, the tool still exits with code `2` even when `--exit-zero` is supplied, so the package wrapper normalizes that specific exit for governance-cycle stability while keeping the findings output.

### 5. Despaghettify setup audit

- audit status: **PASS**
- JSON mirror matches Markdown canon: **True**
- evidence: `validation/fy_reports/despaghettify_setup_audit.json`

### 6. FY wrapper stability

- wrapper command: `python scripts/run_fy_governance_cycle.py`
- result: **passes in v24**
- evidence: `validation/fy_governance_cycle_stdout.txt`

The wrapper was hardened in v24 so that Docify's current non-zero findings exit does not break the full governance cycle.

## Bottom line

The v24 package is validated as a **lean but finishable** continuation bundle:

- lighter than v23,
- stripped of obvious ballast,
- still carrying the service/runtime/governance surfaces that matter at end-state,
- still proving the reference scaffold,
- still proving a conservative AI-stack subset,
- and still able to emit FY governance baselines.

It is therefore better suited for controlled completion than a broader archive-heavy bundle, while remaining more substantial than a minimal toy MVP.
