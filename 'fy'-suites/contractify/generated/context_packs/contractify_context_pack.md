# Context Pack — contractify

Query: `openapi health`

Found 8 indexed evidence hits for query "openapi health". Strongest source: generated/context_packs/contractify_context_pack.md#chunk-1.

## generated/context_packs/contractify_context_pack.md#chunk-1

- lexical: 1.0
- semantic: 0.4714
- hybrid: 0.7886

# Context Pack — contractify  Query: `openapi health`  Found 8 indexed evidence hits for query "openapi health". Strongest source: generated/context_packs/contractify_context_pack.md#chunk-1.  ## generated/context_packs/contractify_context_pack.md#chunk-1  - lexical: 1.0 - semant

## generated/context_packs/contractify_context_pack.json#chunk-1

- lexical: 1.0
- semantic: 0.3811
- hybrid: 0.7524

{   "pack_id": "623c4bd75c594c26ac82b3d5a5fb01b2",   "query": "openapi health",   "suite_scope": [     "contractify"   ],   "audience": "developer",   "summary": "Found 8 indexed evidence hits for query \"openapi health\". Strongest source: generated/context_packs/contractify_con

## docs/api/openapi.yaml#chunk-1

- lexical: 1.0
- semantic: 0.343
- hybrid: 0.7372

openapi: 3.0.0 info:   title: Toy API   version: 1.0.0 paths:   /health:     get:       tags: [system]       summary: Health       responses:         "200":           description: OK

## generated/context_packs/contractify_context_pack.md#chunk-2

- lexical: 1.0
- semantic: 0.2643
- hybrid: 0.7057

openapi: 3.0.0 info:   title: Toy API   version: 1.0.0 paths:   /health:     get:       tags: [system]       summary: Health       responses:         "200":           description: OK  ## generated/context_packs/contractify_context_pack.md#chunk-2  - lexical: 1.0 - semantic: 0.308

## state/LATEST_AUDIT_STATE.md#chunk-5

- lexical: 1.0
- semantic: 0.2102
- hybrid: 0.6841

#### Signal Analysis - **Contract Graph Stability:** 60 contracts, 310 relations, 25 projections—all at baseline. No silent regressions. - **Confidence Stability:** 100% >= 0.85 confidence maintained. No erosion of contract strength. - **New Signals:** +1 drift finding (OpenAPI s

## reports/contractify_audit_report_latest.md#chunk-6

- lexical: 1.0
- semantic: 0.1577
- hybrid: 0.6631

**Conclusion:** MVP remains coherent with committed contracts. Contractify enforcement is working—gates are catching the OpenAPI drift and vocabulary overlaps. No dangerous gaps detected. The +3 conflicts and +1 drift signal indicate normal evolution friction, not structural brea

## state/LATEST_AUDIT_STATE.md#chunk-6

- lexical: 1.0
- semantic: 0.1572
- hybrid: 0.6629

**Contractify enforcement is working.** Evidence: - New conflicts flagged (+3): Gates caught Postman fingerprint stale issue and ADR vocabulary overlaps - Drift detection active (+1): Gates flagged OpenAPI spec modification - Zero silent regressions: Contract graph unchanged, sam

## state/LATEST_AUDIT_STATE.md#chunk-1

- lexical: 1.0
- semantic: 0.0891
- hybrid: 0.6356

# Latest Contractify Audit State **Audit Timestamp:** 2026-04-17T14:47:48Z   **MVP Version:** v24   **Audit Status:** Complete, All Gates Passed  ---  ## Audit Metrics Summary  | Metric | Count | Status | |--------|-------|--------| | **Total Contracts** | 60 | ✓ At baseline (sta
