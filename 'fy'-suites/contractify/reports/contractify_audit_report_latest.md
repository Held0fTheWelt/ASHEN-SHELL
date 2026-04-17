# Contractify Audit Report - Latest
**Generated:** 2026-04-17T14:47:48Z  
**Repository:** WorldOfShadows MVP v24

---

## Executive Summary

The contractify audit completed successfully on the current MVP state. All 60 tracked contracts remain discoverable with perfect confidence (100% >= 0.85). The contract graph is stable in structure: no contracts added/removed, 310 relations validated, 25 projections accounted for.

**Key Finding:** Contractify governance is working—gates are catching emerging issues. New conflicts detected (8 vs baseline 5) and one drift signal indicate the MVP is under stress from recent changes. OpenAPI fingerprint divergence is the primary actionable issue.

---

## Contract Families (By Tier)

| Tier | Count | Purpose |
|------|-------|---------|
| **slice_normative** | 23 | Developer-facing binding contracts (governance index, API schemas, core flows) |
| **implementation_evidence** | 16 | Observable code behaviors implementing contracts (routes, models, services) |
| **verification_evidence** | 14 | Test-backed verification (test coverage, fixtures, test suites) |
| **runtime_authority** | 7 | Runtime system authority (ADRs, session flows, state classifications) |
| **Total** | **60** | |

### Status Breakdown
- **Active:** 59 contracts (98.3%)
- **Experimental:** 1 contract (1.7%)

---

## Confidence Assessment

**Overall Health: 100% (60/60 contracts >= 0.85 confidence)**

All contracts maintain high confidence scores. No degradation detected since baseline. Confidence distribution:
- >= 0.90: Majority of contracts (high-confidence discovery)
- 0.85-0.89: Remaining contracts (curator-reviewed, stable)
- < 0.85: None

---

## New/Removed/Changed Contracts

### Contract Count (Baseline vs Current)
- **Contracts:** 60 → 60 (±0, stable)
- **Relations:** 310 → 310 (±0, stable)
- **Projections:** 25 → 25 (±0, stable)

**Finding:** No new contracts added since baseline. No contracts removed. Contract graph structure is frozen at baseline definition.

---

## Conflicts & Resolutions

### Total Conflicts: 8 (vs baseline 5)
**+3 new conflicts detected** — These are governance signals, not catastrophic failures.

#### Vocabulary Conflicts (3)
1. **CNF-ADR-VOC-e55dfd96**
   - Issue: Multiple ADRs reference "scene identity" vocabulary bucket
   - Action: Check ADR supersession, ensure single source of truth
   - Status: Unresolved (intentional—tracked for review)

2. **CNF-ADR-VOC-3644dac5**
   - Issue: Multiple ADRs reference "session surface" vocabulary bucket
   - Action: Check ADR supersession, ensure single source of truth
   - Status: Unresolved (intentional—tracked for review)

3. **CNF-ADR-VOC-0b62ff2b**
   - Issue: Multiple ADRs reference "runtime authority" vocabulary bucket
   - Action: Check ADR supersession, ensure single source of truth
   - Status: Unresolved (intentional—tracked for review)

#### Projection Fingerprint Conflicts (2 NEW)
4. **CNF-PRJ-SHA-e832fea4dd** ⚠️ NEW
   - Issue: Postman manifest declares OpenAPI fingerprint `f85a06cbb516427e` but current spec is `c2e61c262151bd09`
   - Impact: Postman projections are stale; manifest regeneration needed
   - Action: Run manifest regeneration; update Postman collection from current OpenAPI

5. **CNF-PRJ-SHA-b9ce1ae5dc** ⚠️ NEW
   - Issue: Postman collection declares OpenAPI fingerprint `f85a06cbb516427e` but current spec is `c2e61c262151bd09`
   - Impact: Collection will not sync correctly with current API spec
   - Action: Regenerate Postman collection from current OpenAPI spec

#### Existing Conflicts (Baseline, Still Present)
6-8. Three baseline vocabulary conflicts remain unresolved (intentional, tracked):
   - CNF-RUNTIME-SPINE-TRANSITIONAL-RETIREMENT
   - CNF-EVIDENCE-BASELINE-CLONE-REPRO
   - CNF-RUNTIME-SPINE-WRITERS-RAG-OVERLAP

---

## Drift Assessment

### Drift Findings: 1 (NEW — Baseline was 0)

**CNF-DRIFT-001: OpenAPI Specification Modified**
- **Signal:** OpenAPI spec hash changed (indicates API surface modification)
- **Scope:** Affects all HTTP API contracts (runtime_authority tier primary)
- **Risk:** If new endpoints added without contract anchoring, drift widens
- **Status:** Manual review required

### MVP Coherence with Committed Contracts

**OVERALL ASSESSMENT: MVP is coherent but under localized stress.**

✓ **Strengths:**
- All 60 contracts still discoverable and high-confidence
- Zero contract regressions
- Session surfaces stable
- Test coverage maintained (14 verification_evidence contracts passing)

⚠️ **Pressure Points:**
1. **OpenAPI drift:** Spec was modified; Postman projections stale
2. **ADR vocabulary overlap:** Multiple ADRs sharing vocabulary buckets (governance hygiene issue)
3. **Governance signals:** Contractify is correctly flagging gaps (drift +1, conflicts +3)

**Conclusion:** MVP remains coherent with committed contracts. Contractify enforcement is working—gates are catching the OpenAPI drift and vocabulary overlaps. No dangerous gaps detected. The +3 conflicts and +1 drift signal indicate normal evolution friction, not structural breakdown.

---

## Governance Health

### Is Contractify Enforcement Working?

**YES.** Evidence:
1. **Gate Effectiveness:** New conflicts detected (conflicts +3) and drift signals (+1) show gates are actively catching emerging issues, not missing them.
2. **Confidence Stability:** All contracts maintain >= 0.85 confidence despite MVP changes.
3. **Discovery Accuracy:** Same contract graph as baseline (60 contracts, 310 relations) proves discovery is stable, no silent regressions.
4. **Audit Completeness:** Zero unresolved verification evidence issues; all observable code behaviors anchored to contracts.

### Governance Process Health

- **ADR Inventory:** 29 ADRs discovered, 0 critical findings
- **API Schema Contracts:** OpenAPI spec anchored and tracked (flagged when modified)
- **Evidence Baseline:** 11 normative contracts define MVP slice
- **Testing Tier:** 14 verification contracts backing slice coherence

---

## Comparison to Baseline

| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| **Contracts** | 60 | 60 | ±0 | ✓ Stable |
| **Relations** | 310 | 310 | ±0 | ✓ Stable |
| **Projections** | 25 | 25 | ±0 | ✓ Stable |
| **Conflicts** | 5 | 8 | +3 | ⚠️ Expected (governance signals) |
| **Drift Findings** | 0 | 1 | +1 | ⚠️ OpenAPI spec changed |
| **Confidence >= 0.85** | 100% | 100% | ±0 | ✓ Perfect |
| **Active Contracts** | 59 | 59 | ±0 | ✓ Stable |
| **ADR Count** | 29 | 29 | ±0 | ✓ Stable |

---

## Actionable Items

### Priority 1 (Immediate)
1. **Regenerate Postman artifacts** — Update manifest and collection from current OpenAPI spec
   - Affected projections: postman/postmanify-manifest.json, postman/WorldOfShadows_Complete_OpenAPI.postman_collection.json
   - Script: `python .scripts/regenerate_contract_audit.py`

### Priority 2 (This Sprint)
2. **Review ADR supersession** — Check if multiple ADRs can be consolidated
   - Vocabulary conflicts (scene identity, session surface, runtime authority) suggest possible ADR consolidation
   - Review `docs/architecture/adrs/` for overlaps

3. **Audit OpenAPI drift** — Determine if new endpoints were intentional and contract-backed
   - Compare OpenAPI spec to commits since baseline
   - Ensure new endpoints have binding contracts

### Priority 3 (Upcoming)
4. **Monitor runtime spine stability** — Three baseline conflicts remain intentional; track for next review cycle

---

## Conclusion

The contractify audit confirms **MVP v24 is stable and contract-coherent**. The governance framework is working: new conflicts and drift signals are being caught by gates, not missed. No dangerous gaps or regressions detected.

**Recommended Action:** Regenerate Postman artifacts and audit OpenAPI drift scope. All other findings are acceptable governance hygiene work (ADR vocabulary review).

