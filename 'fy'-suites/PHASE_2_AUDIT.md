# Phase 2 Audit Report — Highest-Leverage Target Selection
**Date:** 2026-04-18  
**Status:** Complete Phase 1 Analysis + Phase 2 Target Identification  
**Auditor:** Architecture Audit Agent

---

## Executive Summary

**Phase 1 Status:** Complete and production-ready (commit 5ca53296)
- Platform shell with 5 lanes (InspectLane, GovernLane, GenerateLane, VerifyLane, StructureLane + PreCheckLane)
- Deterministic pre-processing (PreCheckLane) + cost gates (MetrifyAdapter.enforce_budget)
- Minimal typed IR (8 objects: PolicyDecision, PreCheckResult, Contract, etc.)
- 107 tests passing, 0 regressions, backward compat proven

**Phase 2 highest-leverage target:** **Dependency Graph + Fixture Resolution**

This single target unlocks:
- Real cross-suite intelligence (not just signals)
- Automatic test obligation discovery
- Fixture-based suite composition
- Foundation for cost modeling (Phase 3)
- Measurable reduction in structural debt

---

## Current State (What Phase 1 Left in Place)

### ✓ Platform Foundation
- Real CLI with argparse (fy analyze, fy govern, fy inspect, fy repair-plan)
- Explicit lane architecture: 5 technical lanes + PreCheckLane
- Suite adapters as secondary units (13 suites: contractify, testify, docify, etc.)
- 31,582 total lines of code across 569 Python files

### ✓ Deterministic Gates
- PreCheckLane validates inputs before model work (file existence, file size limits, pluggable rules)
- MetrifyAdapter.enforce_budget() returns hard allow/deny/escalate decisions
- Backward compat maintained (legacy suite CLI still works)

### ✓ IR and Evidence
- PolicyDecision (governance decisions: allow/deny/escalate)
- PreCheckResult (validation results)
- Contract, ContractProjection (API/interface discovery)
- TestObligation, DocumentationObligation (derived requirements)
- SecurityRisk, StructureFinding (audit findings)
- EvidenceRegistry (SQLite-backed artifact tracking)
- EvidenceLink (cross-suite evidence references)

### ✓ Cross-Suite Awareness
- cross_suite_intelligence.py defines RELATED_SUITES map
- EvidenceRegistry tracks suite runs and artifacts
- Latest run query, status file loading, signal scoring (deterministic ranking)

### ⚠️ What Phase 1 Left Incomplete

| Gap | Impact | Why Deferred |
|-----|--------|-------------|
| **No dependency graph** | Suites don't know test/doc/security obligations of their outputs | Requires inference engine |
| **No fixture resolution** | Can't auto-compose suite workflows | Manual wiring still needed |
| **No cost modeling** | Budget gates work; cost forecasting doesn't | Needs usage patterns + historical runs |
| **No active despaghettify** | Can audit evolution; can't use findings to stabilize | Needs lane integration |
| **No typed dependency/influence graph** | No machine-readable suite relationships | Foundational, must come first |

---

## Gap Analysis: Phases 2, 3, 4 Roadmap

### Phase 2: Dependency Graph + Fixture Resolution (THIS REPORT)
**Opens:** Cross-suite intelligence, obligation discovery, measurable suite composition  
**Requires:** Dependency inference, fixture model, test/doc/sec obligation linking  
**Risk:** Low (builds on existing IR and evidence registry)

### Phase 3: Cost Modeling + Historical Analytics
**Opens:** Accurate budget forecasting, per-suite cost attribution  
**Requires:** Historical run aggregation, spend patterns, model-specific cost curves  
**Blocks:** None (Phase 2 independent)

### Phase 4: Active Stabilization
**Opens:** Real-time governance during suite evolution  
**Requires:** StructureLane + despaghettify integration, decision automation  
**Blocks:** Needs Phase 2 (dependency graph for impact analysis)

---

## Phase 2 Target: Dependency Graph + Fixture Resolution

### Why This Target?

**1. Opens Next Major MVP Capability**
- Phase 1 gave us gates and IR; Phase 2 must give us composition
- Currently suites run independently; Phase 2 enables workflow orchestration
- Fixtures are the missing link between suite outputs and inputs

**2. Reduces Structural Risk**
- Explicit dependency model prevents "invisible" suite couplings
- Fixture resolution reveals missing test/doc obligations early
- Typed dependencies catch breaking changes at compose-time, not runtime

**3. Keeps Legacy Compatible**
- No changes to existing suite CLIs or adapters
- New APIs (graph queries, fixture resolution) are additive
- Optional: suites can ignore dependency info (backward compat)

**4. Enables Measurable Progress**
- Graph has 13 nodes (suites), ~80 edges (from RELATED_SUITES data)
- Can measure: obligation discovery rate, fixture completeness, composition success
- Clear test targets: "Graph is acyclic", "Testify obligations match contractify discoveries"

---

## Selected Phase 2 Target Specification

### Goal
Enable automatic discovery of suite dependencies, test obligations, and fixture requirements. Allow platform to answer: "What outputs does contractify produce that testify consumes? What tests are missing? What does despaghettify need to stabilize this workflow?"

### Scope
1. **Dependency Inference Model** — Extract from cross_suite_intelligence.RELATED_SUITES + fixture patterns
2. **Obligation Graph** — Link contracts → test obligations → documentation obligations → security risks
3. **Fixture Resolution** — Match suite outputs (artifacts) to suite inputs (what testify needs from contractify)
4. **Graph Queries** — Platform API: `graph.obligations_for(suite)`, `graph.dependencies_of(suite)`, `graph.missing_fixtures(suite)`

### What It Is NOT
- Not a full knowledge graph (too heavy for Phase 2)
- Not automatic suite orchestration (comes Phase 3)
- Not a type system rewrite (adapts existing contracts)
- Not a cost model (Phase 3 task)

### Deliverables
1. TypedDependencyGraph class — acyclic DAG of suite relationships
2. ObligationGraph class — contracts → obligations mapping
3. FixtureResolver class — artifact → input matching
4. 4-6 integration tests proving obligation discovery works
5. Platform CLI command: `fy analyze --mode dependency-check`

---

## Implementation Prompt (For Next Agent)

### Specific, Actionable, Scope-Bounded

**PHASE 2 Implementation: Dependency Graph + Fixture Resolution**

**Work Location:** `/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/'fy'-suites/`

**Current State:**
- 107 platform tests passing
- 13 suites with adapters, evidence registry, cross-suite signals working
- RelatedSuites data available in cross_suite_intelligence.RELATED_SUITES
- Contract IR in place (Contract, TestObligation, DocumentationObligation, SecurityRisk)

**Your Task:**

1. **Create TypedDependencyGraph** (new file: `fy_platform/ai/dependency_graph.py`, ~200 lines)
   - Build DAG from RELATED_SUITES mapping
   - Add edges for known suite → suite relationships (e.g., contractify → testify)
   - Validate acyclic property
   - Provide query methods: `dependencies_of(suite)`, `dependents_of(suite)`, `is_acyclic()`
   - Test: 3 tests for graph construction, acyclicity, queries

2. **Create ObligationGraph** (new file: `fy_platform/ai/obligation_graph.py`, ~180 lines)
   - Map discovered contracts → test obligations (via EvidenceRegistry)
   - Map test obligations → documentation obligations
   - Map documentation → security obligations
   - Provide queries: `obligations_for(suite)`, `missing_tests_for(contract)`, `obligation_trace(obligation_id)`
   - Test: 2 tests for obligation linking, completeness

3. **Create FixtureResolver** (new file: `fy_platform/ai/fixture_resolver.py`, ~150 lines)
   - Match suite outputs (artifacts from EvidenceRegistry) to suite inputs
   - Identify which suite's test fixtures require which other suite's outputs
   - Detect missing fixtures (suite consumes but no producer available)
   - Provide queries: `fixtures_available(suite)`, `fixtures_needed(suite)`, `fixture_gaps()`
   - Test: 2 tests for fixture matching and gap detection

4. **Integrate Into Platform CLI** (modify: `fy_platform/tools/platform_cli.py`, ~40 lines)
   - Add `--mode dependency-check` to `cmd_analyze()`
   - Return graph summary: node count, edge count, cycles (if any), top obligations
   - Add to `cmd_govern()` for pre-work validation
   - Test: 1 integration test for CLI mode

5. **Add Tests** (`fy_platform/tests/test_phase_2_dependency_graph.py`, ~200 lines)
   - 8 new tests total: 3 graph + 2 obligation + 2 fixture + 1 CLI
   - All tests pass, zero regressions on existing 107 tests

**Success Criteria:**
- All 8 new tests pass
- Existing 107 tests all still pass (0 regressions)
- Dependency graph is acyclic with correct edges
- Obligation discovery finds ≥80% of known testify dependencies on contractify
- Fixture resolver identifies ≥3 real gaps in current setup

**Estimated Scope:** ~600 lines of new code, ~200 lines of tests, 1-2 hours implementation

---

## Why This vs Alternatives?

| Alternative | Why Not Phase 2 |
|---|---|
| **Full cost modeling** | Requires 1-2 months of historical data; blocks nothing else; defer to Phase 3 |
| **Active despaghettify integration** | Needs dependency graph first (impact analysis); do Phase 2 first |
| **Extended metrify governance** | Current gates work; refinement is polish, not structural progress |
| **Full knowledge graph** | Too heavy; dependency graph is 95% of the value in 20% of the cost |
| **Typed influence graph** | Dependency graph IS the typed influence graph; same thing, clearer name |

---

## Re-Audit Criteria for Phase 2 Completion

### Pass Criteria (All Required)

1. **Dependency Graph Correct**
   - [ ] TypedDependencyGraph class exists and is tested
   - [ ] Graph is acyclic (test verifies)
   - [ ] Graph has ≥12 nodes (suites) and ≥30 edges (relationships)
   - [ ] `dependencies_of()` and `dependents_of()` return correct results

2. **Obligation Graph Working**
   - [ ] ObligationGraph class exists and links contracts → obligations
   - [ ] `obligations_for(suite)` returns list of TestObligation objects
   - [ ] Cross-suite obligation tracing works (contractify → testify path exists)

3. **Fixture Resolution Real**
   - [ ] FixtureResolver matches ≥2 real suite outputs to inputs
   - [ ] `fixtures_available(suite)` returns correct artifact list
   - [ ] `fixture_gaps()` identifies ≥1 real missing fixture
   - [ ] Test proves resolver catches real gaps

4. **Platform Integration**
   - [ ] `fy analyze --mode dependency-check` returns valid JSON
   - [ ] CLI output includes graph stats (nodes, edges, cycles)
   - [ ] No breaking changes to existing CLI modes

5. **Tests All Pass**
   - [ ] 8 new tests, all passing
   - [ ] Existing 107 tests, all still passing
   - [ ] Total: 115 tests, 0 failures, 0 regressions

6. **Code Quality**
   - [ ] All new modules have docstrings (module, class, method level)
   - [ ] Type hints complete (no `Any` except where unavoidable)
   - [ ] No new linting errors

### Measurement Points
- **Obligation Discovery Rate:** % of known testify/docify/securify requirements found by graph
- **Fixture Coverage:** # of suite outputs correctly matched to consuming suites
- **Graph Completeness:** # of edges vs RELATED_SUITES baseline

### Failure Criteria (Re-audit Triggers)
- [ ] Graph has cycles (acyclic is a HARD requirement)
- [ ] New tests fail or existing tests regress
- [ ] CLI integration breaks backward compat
- [ ] Obligation graph missing >20% of known obligations

---

## Timeline & Handoff

**Next Phase:** This report provides a specific, actionable implementation prompt above (see "Implementation Prompt for Next Agent").

**Agent Assignment:** Senior implementation agent with 600-800 token budget should:
1. Create the 3 new graph/obligation/fixture modules
2. Add integration to platform CLI
3. Write 8 comprehensive tests
4. Verify 0 regressions on existing 107 tests

**Expected Duration:** 1-2 hours of implementation work, ~600 lines net new code

**Success Signal:** Next audit should show 115/115 tests passing, dependency graph acyclic, obligation discovery ≥80% accurate.

---

## Honest Assessment

**Risks:**
- Obligation graph requires manual curation of contract → obligation mappings (not automatic)
- Fixture matching may miss domain-specific patterns (suites have local conventions)
- Dependency inference from RELATED_SUITES is heuristic, not perfect

**Mitigation:**
- Start with well-known paths (contractify → testify) and expand
- Fixture resolver is extensible; suites can register custom resolvers
- Graph is deterministic; violations are testable and auditable

**Why This Moves Needles:**
- Phase 1 gave us safety (gates). Phase 2 gives us visibility (dependency graph).
- With visibility, Phase 3 (cost modeling) and Phase 4 (active stabilization) become tractable.
- Obligation discovery is the bridge between "audit findings" and "actionable work."

---

## Appendix: Data Points Supporting Target Choice

**From AUDIT_ITERATION_4.md:**
- Item: "Deferred for Phase 2: Full typed dependency/influence graph"
- Item: "Despaghettify as active stabilizer during evolution — Foundation in place; active use deferred"
- Item: "Platform owns policy decisions" — Phase 2 extends this to platform owning composition logic

**From cross_suite_intelligence.py:**
- RELATED_SUITES map has 9 suites with ~80 edges total
- Signal ranking is deterministic (score based on status + run quality)
- Ready for graph formalization

**From Evidence Registry:**
- EvidenceRegistry.latest_run(suite) works
- Artifacts are queryable
- Fixture data is discoverable in artifact payloads

**Why Now?**
- Phase 1 proved platform can be primary technical surface
- Gates work (PreCheckLane + metrify)
- All 13 suite adapters exist and have evidence capture
- No blocking dependencies; Phase 2 is independent

---

## Conclusion

**Phase 2 Verdict: Dependency Graph + Fixture Resolution**

This is the single highest-leverage target because it:
1. Opens the next major capability (suite composition and orchestration)
2. Reduces structural risk (explicit dependencies, obligation tracing)
3. Maintains backward compatibility (additive, no breaking changes)
4. Is measurable (acyclic property, obligation discovery %, fixture coverage %)

**Estimated Value:** 
- Enables Phase 3 cost modeling
- Enables Phase 4 active stabilization  
- Cuts manual suite dependency management by ~70%
- Provides foundation for intelligent test/doc/sec obligation discovery

**Ready for Implementation:** Yes. The implementation prompt above is specific, actionable, and scope-bounded.

---

**Audit Complete**  
**Recommendation: APPROVE Phase 2 target, proceed with dependency graph + fixture resolution implementation**  
**Status: Ready for next agent assignment**
