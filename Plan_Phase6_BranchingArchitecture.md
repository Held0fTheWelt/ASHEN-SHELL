# Phase 6: Branching Architecture Implementation

**Phase 6 Date Range:** 2026-06-09 to 2026-07-20 (6 weeks)  
**Status:** READY FOR PLANNING  
**Dependency:** Phase 5 complete with validation reports (2026-06-06)

---

## What Phase 6 Proves

| Question | Target | Success Criteria |
|---|---|---|
| **Do player choices matter?** | Branching outcomes must diverge by 60%+ | Different paths reference different facts, reach different endings |
| **Is branching replayable?** | Same scenario/approach must be deterministic | Two runs with same inputs produce identical results |
| **Does replay feel different?** | Player detects variation across replays | 70%+ replayability likelihood (Phase 5 Scenario E data) |
| **Can branch complexity scale?** | 3 decision points → 8 outcomes. Can we handle 5 points (32 outcomes)? | System remains coherent with 5 decision points |

---

## Phase 6 Architecture (4 Workstreams)

### Workstream A: Branching Decision System Design

**Goal:** Formalize decision points, outcome paths, consequence tracking

**Scope:**
- Decision point definition (when does choice happen? what are options?)
- Path state tracking (which decision path am I on?)
- Outcome divergence measurement (how different is Path A vs Path B?)
- Consequence binding (which facts belong to which path?)

**Ownership:** Architecture + World-engine team

**Key Files:**
- `world-engine/branching/decision_point.py` (NEW)
- `world-engine/branching/path_state.py` (NEW)
- `world-engine/branching/outcome_divergence.py` (NEW)
- `story_runtime_core/consequence_binding.py` (UPDATE)

**Deliverables:**
- Branching system specification (doc)
- Decision point registry schema (JSON)
- Path state contract (TypeScript/Python)
- Outcome divergence metrics (formulas)

**Success Criteria:**
- ✓ 5+ decision points supported per session
- ✓ 32+ outcome combinations trackable
- ✓ Consequence binding unambiguous (no fact appears on multiple paths unless intentional)
- ✓ Divergence measurement accurate (correlates with evaluator perception)

**Timeline:** Weeks 1-2 (design + prototype)

---

### Workstream B: Branching Runtime Integration

**Goal:** Integrate branching system into turn execution, ensure authority maintained

**Scope:**
- Turn execution seam updates (where does branching decision happen?)
- State persistence across turns (remember current path)
- Consequence filtering (only show consequences from current path)
- Fallback behavior (what if branch logic fails?)

**Ownership:** World-engine team

**Key Files:**
- `world-engine/app/story_runtime_shell.py` (UPDATE—add branch seam)
- `world-engine/app/turn_execution.py` (UPDATE—branch-aware)
- `story_runtime_core/consequence_filter.py` (NEW)
- `world-engine/tests/branching/` (NEW—comprehensive)

**Deliverables:**
- Branching-aware turn execution contract (doc + tests)
- Consequence filtering rules (logic + tests)
- Determinism proof (same inputs → same outputs)
- Fallback envelope (graceful degradation)

**Success Criteria:**
- ✓ Turn execution unchanged for non-branching scenarios
- ✓ Branch decisions persist across 20+ turns
- ✓ Consequence filtering removes off-path facts
- ✓ Determinism verified (test: replay scenario 3x with same player moves → identical transcripts)

**Timeline:** Weeks 2-3 (implementation + testing)

---

### Workstream C: Branching Evaluation & Metrics

**Goal:** Measure whether branching actually works as experienced by evaluators

**Scope:**
- Session recording enhancement (capture branch points, path taken)
- Outcome divergence analysis (Phase 5 Scenario C data: 3 paths, measure divergence)
- Evaluator perception of replayability (Phase 5 Scenario E data: did replay feel different?)
- Branch coherence scoring (do different paths feel intentional or random?)

**Ownership:** Test lead + Analysis team

**Key Files:**
- `tests/branching/outcome_divergence_analyzer.py` (NEW)
- `tests/branching/determinism_verifier.py` (NEW)
- `analysis_templates/branching_metrics.xlsx` (NEW)
- `docs/branching/BRANCHING_VALIDATION_REPORT.md` (NEW)

**Deliverables:**
- Branching outcome comparison report (Phase 5 Scenario C data)
- Determinism verification (do 3 identical replays produce identical transcripts?)
- Replayability analysis (Phase 5 Scenario E: how many evaluators want to replay?)
- Branch coherence scoring (do paths feel meaningfully different?)

**Success Criteria:**
- ✓ Outcome divergence ≥ 60% across 3+ paths (different facts, different character arcs, different endings)
- ✓ Determinism: 3/3 identical replays produce byte-identical transcripts
- ✓ Replayability likelihood ≥ 70% (evaluators want to replay with different approach)
- ✓ Branch coherence: ≥ 80% evaluators perceive intentional divergence (not random)

**Timeline:** Weeks 2-4 (analysis) + Weeks 4-5 (validation testing)

---

### Workstream D: Branching Documentation & Closure

**Goal:** Document what branching proves and doesn't prove yet

**Scope:**
- Branching system specification (final)
- Decision point registry (all scenarios)
- Outcome divergence evidence (metrics + examples)
- Limitations and future work (4-way branching? recursive branching?)
- Handoff to Phase 7 (what concurrent session handling requires)

**Ownership:** Documentation team

**Key Files:**
- `docs/MVPs/MVP_World_Of_Shadows_Canonical_Implementation_Bundle/phase_6_branching_architecture.md` (NEW)
- `docs/MVPs/MVP_World_Of_Shadows_Canonical_Implementation_Bundle/branching_validation_evidence.md` (NEW)
- `docs/MVPs/MVP_World_Of_Shadows_Canonical_Implementation_Bundle/phase_6_completion_report.md` (NEW)

**Deliverables:**
- Branching specification (architecture + contracts)
- Branching validation report (metrics + evidence)
- Limitations document (what works, what doesn't)
- Phase 7 handoff (branching + concurrency requirements)

**Success Criteria:**
- ✓ Branching specification is implementation-grade (testable, falsifiable)
- ✓ All metrics from Workstream C included with evidence
- ✓ Limitations documented without hedging ("we don't support X" not "we might add X later")
- ✓ Phase 7 team can read handoff and immediately start scaling work

**Timeline:** Weeks 5-6 (documentation)

---

## Phase 6 Week-by-Week Breakdown

### Week 1 (2026-06-09 to 06-13): Design & Prototype

**Workstream A: Branching Design**
- [ ] Decision point taxonomy (when in turn execution do choices happen?)
- [ ] Path state representation (data structure for "which branch am I on?")
- [ ] Consequence binding rules (how do facts map to paths?)
- [ ] Outcome divergence formulas (how to measure "different"?)
- [ ] Prototype decision point system (5-10 test scenarios)

**Workstream B: Integration Planning**
- [ ] Analyze current turn execution seams (where to inject branching?)
- [ ] Design consequence filtering rules
- [ ] Plan determinism testing approach
- [ ] Design fallback envelope

**Workstream C: Evaluation Planning**
- [ ] Prepare Phase 5 Scenario C data (3 paths: A→A2, B→B2, C→C2)
- [ ] Design outcome divergence analysis (what metrics matter?)
- [ ] Plan determinism verification (how to prove same input → same output?)

**Workstream D: Documentation Planning**
- [ ] Outline final branching specification
- [ ] Plan validation evidence collection
- [ ] Design phase 6 completion report structure

**Success:** All 4 workstreams have detailed plans, prototype decision system works on 5 test scenarios

---

### Week 2 (2026-06-16 to 06-20): Build & Test

**Workstream A: Decision System Implementation**
- [ ] Implement decision point registry
- [ ] Implement path state tracking
- [ ] Implement consequence binding logic
- [ ] Unit test all components

**Workstream B: Runtime Integration**
- [ ] Update turn execution to support branch decisions
- [ ] Implement consequence filtering
- [ ] Implement fallback envelope
- [ ] Contract tests (branch decision works within turn seams)

**Workstream C: Phase 5 Data Analysis (Start)**
- [ ] Extract Phase 5 Scenario C transcripts (3 paths)
- [ ] Begin outcome divergence analysis
- [ ] Prepare determinism test plan

**Success:** Branching system integrated into turn execution, all unit tests pass, no regressions in non-branching scenarios

---

### Week 3 (2026-06-23 to 06-27): Integration Testing & Validation

**Workstream A: Testing**
- [ ] Integration test: branch decisions + turn execution + consequence filtering
- [ ] Determinism test: run scenario 3x with identical moves → verify identical transcripts
- [ ] Edge case testing (what if consequence binding fails? what if path state corrupts?)
- [ ] Load test (5+ concurrent branching sessions)

**Workstream B: Fallback Validation**
- [ ] Verify graceful degradation (branching fails → session continues with degraded behavior)
- [ ] Error logging (all branch failures recorded for analysis)

**Workstream C: Phase 5 Analysis (Continue)**
- [ ] Complete outcome divergence analysis on 3 paths
- [ ] Measure divergence percentage (target: ≥ 60%)
- [ ] Identify which facts/events differ across paths

**Success:** All integration tests pass, determinism verified (3/3 replays identical), Phase 5 Scenario C divergence measured

---

### Week 4 (2026-06-30 to 07-04): Phase 5 Revalidation

**Workstream A: Replayability Testing**
- [ ] Use Phase 5 evaluators (if available) or new evaluators
- [ ] Run Phase 5 Scenario C with 3 different approaches (same evaluators, if possible)
- [ ] Measure outcome divergence from evaluator perspective
- [ ] Collect replayability survey (would you play again with different approach?)

**Workstream B: Determinism Verification**
- [ ] Run determinism test: same player moves → identical transcript 5/5 times
- [ ] Verify no randomness leakage (all divergence from player choice, not RNG)

**Workstream C: Branch Coherence Scoring**
- [ ] Evaluators rate: do different paths feel intentional or random? (1-10 scale)
- [ ] Analyze: which branches feel most different? most same?
- [ ] Identify any "hollow" branches (no consequential difference)

**Success:** Outcome divergence ≥ 60%, determinism 5/5, branch coherence ≥ 80%

---

### Week 5 (2026-07-07 to 07-11): Analysis & Documentation

**Workstream C: Full Analysis**
- [ ] Outcome divergence report (metrics + evidence)
- [ ] Determinism verification summary
- [ ] Replayability analysis (likelihood + quotes from evaluators)
- [ ] Branch coherence scoring (which branches work, which don't)
- [ ] Limitations identified (4-way branching? recursive branches? complexity limits?)

**Workstream D: Documentation**
- [ ] Write branching specification (architecture + contracts)
- [ ] Write validation evidence document (all metrics + examples)
- [ ] Write limitations document (clear statement of what doesn't work)
- [ ] Draft Phase 7 handoff (what scaling requires)

**Success:** All analysis complete, all documentation drafted, ready for review

---

### Week 6 (2026-07-14 to 07-18): Final Review & Closure

**Workstream D: Final Documentation**
- [ ] Review branching specification (implementation-grade? testable?)
- [ ] Review validation evidence (all claims source-traceable?)
- [ ] Review limitations (honest assessment? no hedging?)
- [ ] Finalize Phase 7 handoff

**All Workstreams: Sign-Off**
- [ ] Workstream A: Branching system meets all success criteria ✓
- [ ] Workstream B: Turn execution + branching integrated, no regressions ✓
- [ ] Workstream C: All evaluation metrics collected and analyzed ✓
- [ ] Workstream D: All documentation complete and verified ✓

**Deliverables Ready:**
- ✓ Branching system specification
- ✓ Branching validation report
- ✓ Phase 6 completion report
- ✓ Phase 7 handoff document

---

## Phase 6 Success Criteria (Gate for Phase 7)

**Branching must prove:**

| Criterion | Target | Evidence |
|---|---|---|
| **Outcome divergence** | ≥ 60% across paths | Phase 5 Scenario C analysis: different facts, different arcs, different endings |
| **Determinism** | 5/5 identical replays → identical transcripts | Determinism test suite passes |
| **Replayability** | ≥ 70% evaluators want to replay | Phase 5 Scenario E survey + new evaluators |
| **Branch coherence** | ≥ 80% feel intentional | Evaluator perception rating |
| **No regressions** | Phase 5 scenarios still pass | All 5 scenarios still work without branching |
| **Integration clean** | Turn execution unchanged for non-branching | All existing tests pass |
| **Documentation complete** | Implementation-grade | All claims testable, source-traceable |

---

## Phase 6 Risks & Mitigation

### Risk 1: Branching Causes Regressions
**Mitigation:** Extensive integration testing. Non-branching scenarios must remain unchanged.  
**Contingency:** Rollback to Phase 5 if regressions exceed 5% test failure rate.

### Risk 2: Outcome Divergence < 60%
**Mitigation:** If paths too similar, redesign decision points (make choices more consequential).  
**Contingency:** If can't achieve 60% divergence, declare branching "conditional success" and defer 4-way/recursive branching to Phase 7.

### Risk 3: Determinism Fails (Randomness Leaks)
**Mitigation:** Audit all RNG sources. Ensure all divergence from player choice only.  
**Contingency:** If randomness leaks found, fix immediately. Don't proceed to Phase 7 without determinism verified.

### Risk 4: Replayability < 70%
**Mitigation:** Analyze which branches feel repetitive. Redesign those branches.  
**Contingency:** If can't achieve 70%, declare replayability "requires memory engines" (Phase 7+) and defer.

### Risk 5: Phase 6 Overruns Timeline
**Mitigation:** Prioritize (Workstream B—integration must work). De-prioritize if needed (Workstream D—docs can compress).  
**Contingency:** Extend Phase 6 to Week 7 (cost: 1 week delay to Phase 7 start, acceptable).

---

## Phase 6 Budget & Resources

### Personnel Time
- **Architecture Lead:** 30-40 hours (design, integration decisions)
- **World-engine Engineer:** 40-50 hours (implementation + testing)
- **Test Lead:** 20-30 hours (evaluation plan, metrics)
- **Data Analyst:** 20-25 hours (Phase 5 data analysis, metrics)
- **Documentation:** 15-20 hours (specs, reports)
- **Total:** 125-165 hours

### External Costs
- **Evaluators:** $50/session × 5-10 sessions (replayability testing) = $250-$500
- **Cloud/compute:** Minimal (same stack as Phase 5)

### Tech Stack
- Python (same as Phase 5)
- LangGraph (same)
- Pytest (same)
- Pandas/matplotlib (for outcome analysis)

---

## Phase 6 → Phase 7 Handoff

**By end of Phase 6:**
- ✓ Branching system proven (outcome divergence ≥ 60%, determinism verified)
- ✓ Limitations documented (what works: 3-8 outcomes; what's deferred: 4-way, recursive)
- ✓ Concurrency readiness assessed (single-session branching works; multi-session TBD)

**Phase 7 must address:**
1. **Concurrent branching sessions** (100+ simultaneous games, each with own branch path)
2. **Branch isolation** (one session's branch doesn't affect another)
3. **Performance limits** (at what point does branching slow down?)
4. **Scale testing** (can we handle 50 concurrent sessions with 5 decision points each?)

---

## Success = Phase 7 Ready

Phase 6 is complete when:
- ✓ Branching works reliably (no regressions)
- ✓ Outcomes are actually different (divergence ≥ 60%)
- ✓ Replays are deterministic (same input → same output)
- ✓ Players want to replay (replayability ≥ 70%)
- ✓ Everything is documented and proven

**Phase 7 can then focus on:** Taking proven branching system and making it scale to 100+ concurrent sessions.

---

## Next Action

**Approval Gate:** Review Phase 6 plan. Confirm:
- [ ] Architecture is sound
- [ ] Timeline is achievable
- [ ] Success criteria are measurable
- [ ] Risks are acceptable

**Then proceed to Phase 6 Week 1 kickoff.**
