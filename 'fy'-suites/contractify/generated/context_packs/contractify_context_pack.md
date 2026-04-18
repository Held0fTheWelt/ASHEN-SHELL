# Context Pack — contractify

Query: `openapi health`
Audience: `developer`
Evidence confidence: `high`

Found 8 indexed evidence hits for query "openapi health" across suites ['contractify']. Strongest source: generated/context_packs/contractify_context_pack.md#chunk-4. Use the top-ranked items first and treat lower-confidence hits as hints.

## Priorities

- Start with generated/context_packs/contractify_context_pack.md#chunk-4 because it currently has the strongest combined signal.
- Compare it with generated/context_packs/contractify_context_pack.json#chunk-1 before deciding on outward action.

## Most-Recent-Next-Steps

- Open generated/context_packs/contractify_context_pack.md#chunk-4 first.
- Use the top two hits to validate the next code or governance action.

## Uncertainty

- top_hits_close_together

## Artifact paths

- `adapter/tests/test_contractify_adapter.py#chunk-1`
- `docs/api/openapi.yaml#chunk-1`
- `generated/context_packs/contractify_context_pack.json#chunk-1`
- `generated/context_packs/contractify_context_pack.md#chunk-1`
- `generated/context_packs/contractify_context_pack.md#chunk-4`
- `state/LATEST_AUDIT_STATE.md#chunk-1`
- `tools/tests/test_conflicts.py#chunk-4`
- `tools/tests/test_drift_analysis.py#chunk-1`

## Cross-suite signals

- `usabilify`: Usabilify evaluated UI and UX surfaces, connected available UI contracts, and highlighted the next usability steps in plain language.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `testify`: Compared testify-c241f7057392 with testify-0d71644d3445. Focus first on changed artifacts, review-state changes, and any target or mode differences.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `templatify`: No summary available.
  - next: Validate the generated template previews before applying them to a target repo.
- `securify`: Securify found security follow-up work: no discoverable security documentation, secret-related ignore rules are missing. Start with the most direct exposure and the missing guidance surfaces.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `documentify`: Documentify generated the current documentation tracks and status pages.
  - next: Read the newly generated documentation and decide which tracks should be exported outward.
  - next: Open the generated output directory and review the new files in simple language first.

## generated/context_packs/contractify_context_pack.md#chunk-4

- suite: contractify
- scope: suite
- lexical: 1.0
- semantic: 0.4352
- hybrid: 0.7254
- recency: 0.5773
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: health, openapi

## generated/context_packs/contractify_context_pack.md#chunk-4  - suite: contractify - scope: suite - lexical: 1.0 - semantic: 0.4336 - hybrid: 0.7261 - recency: 0.5848 - suite_affinity: 0.0 - confidence: high - rationale: matched terms: health, openapi  ## generated/context_pack

## generated/context_packs/contractify_context_pack.json#chunk-1

- suite: contractify
- scope: suite
- lexical: 1.0
- semantic: 0.3749
- hybrid: 0.7097
- recency: 0.573
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: health, openapi

{   "pack_id": "2eb533d183824784819be6fdcbc79da8",   "query": "openapi health",   "suite_scope": [     "contractify"   ],   "audience": "developer",   "summary": "Found 8 indexed evidence hits for query \"openapi health\" across suites ['contractify']. Strongest source: generated

## adapter/tests/test_contractify_adapter.py#chunk-1

- suite: contractify
- scope: suite
- lexical: 1.0
- semantic: 0.0709
- hybrid: 0.6966
- recency: 0.9925
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: health, openapi; recently indexed evidence

from contractify.adapter.service import ContractifyAdapter from fy_platform.tests.fixtures_autark import create_target_repo   def test_contractify_adapter_full_cycle_and_consolidate(tmp_path, monkeypatch):     repo = create_target_repo(tmp_path)     monkeypatch.chdir(tmp_path)   

## docs/api/openapi.yaml#chunk-1

- suite: contractify
- scope: target
- lexical: 1.0
- semantic: 0.343
- hybrid: 0.6828
- recency: 0.2468
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: health, openapi; target-repo evidence

openapi: 3.0.0 info:   title: Toy API   version: 1.0.0 paths:   /health:     get:       tags: [system]       summary: Health       responses:         "200":           description: OK

## generated/context_packs/contractify_context_pack.md#chunk-1

- suite: contractify
- scope: suite
- lexical: 1.0
- semantic: 0.2309
- hybrid: 0.6738
- recency: 0.574
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: health, openapi

# Context Pack — contractify  Query: `openapi health` Audience: `developer` Evidence confidence: `high`  Found 8 indexed evidence hits for query "openapi health" across suites ['contractify']. Strongest source: generated/context_packs/contractify_context_pack.md#chunk-4. Use the 

## state/LATEST_AUDIT_STATE.md#chunk-1

- suite: contractify
- scope: suite
- lexical: 1.0
- semantic: 0.0891
- hybrid: 0.606
- recency: 0.3584
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: health, openapi

# Latest Contractify Audit State **Audit Timestamp:** 2026-04-17T14:47:48Z   **MVP Version:** v24   **Audit Status:** Complete, All Gates Passed  ---  ## Audit Metrics Summary  | Metric | Count | Status | |--------|-------|--------| | **Total Contracts** | 60 | ✓ At baseline (sta

## tools/tests/test_conflicts.py#chunk-4

- suite: contractify
- scope: suite
- lexical: 0.5
- semantic: 0.2582
- hybrid: 0.5104
- recency: 0.9388
- suite_affinity: 0.0
- confidence: medium
- rationale: matched terms: openapi; recently indexed evidence

def test_projection_fingerprint_mismatch_unit(tmp_path: Path) -> None:     # Shares ``tmp_path`` with the autouse hermetic repo; ``docs/api`` may already exist.     api_dir = tmp_path / "docs" / "api"     api_dir.mkdir(parents=True, exist_ok=True)     openapi = api_dir / "openapi

## tools/tests/test_drift_analysis.py#chunk-1

- suite: contractify
- scope: suite
- lexical: 0.5
- semantic: 0.208
- hybrid: 0.4983
- recency: 0.9421
- suite_affinity: 0.0
- confidence: medium
- rationale: matched terms: openapi; recently indexed evidence

import hashlib import json  import contractify.tools.repo_paths as repo_paths from contractify.tools.drift_analysis import drift_postman_openapi_manifest   def test_postman_openapi_hash_match_is_clean() -> None:     root = repo_paths.repo_root()     mf = root / "postman" / "postm
