# Original MVP Goals vs. Current Implementation Focus

**Analysis Date:** 2026-04-21  
**Source:** `world_of_shadows_mvp_v24_lean_finishable/mvp/` v22 canonical package  
**Current State:** Phase 4 documentation + Phase 5 planning ready  

---

## What the Original MVP Promised

### Core Vision Statement
From 00_MASTER_MVP.md:
- **World of Shadows is an authoritative narrative runtime**
- The world-engine is the only live truth boundary
- AI can propose, but only validated commits become canonical truth
- Runtime memory is multi-domain, temporal, conflict-aware, threshold-aware, carrier-aware, and effect-aware
- Emotional and consciousness layers are runtime participants, not decorative annotations

---

## Implementation Workstreams (Original 6 Streams)

| Stream | Goal | Status in Current Work |
|--------|------|---|
| **A: Runtime Authority & Session Truth** | Keep world-engine authoritative | ✓ FOCUSED (Wave 1-2, Phase 4) |
| **B: Runtime-safe MCP Surface** | Tool registry without false authority | ⚠️ PARTIAL (API spec done, ops still TBD) |
| **C: Player Route Purity** | Clean player routes, no operator leakage | ✓ FOCUSED (Wave 3, admin surfaces) |
| **D: AI Stack Integration** | LangGraph contracts, commit discipline | ✓ FOCUSED (Proof discipline, Wave 5) |
| **E: Governance & Review Surfaces** | Admin/writers-room separation | ⚠️ PARTIAL (Admin surfaces spec'd, writers-room not detailed) |
| **F: Validation & Release Honesty** | Prevent closure theater | ✓ FOCUSED (Phase 4 canonical docs, proof discipline) |

---

## Core Technical Promises

### 1. Memory Core Architecture (Doc 12)

**Original Promise:** 9 required engines for multi-domain, temporal, conflict-aware memory

```
Required engines:
- Identity and slotting
- Conflict detection and lineage tracking
- Temporal validity classification
- Relevance scoring
- Retrieval planning
- Transformation runtime
- Threshold engine
- Effect surface activation
- Governed consolidation
```

**Current Focus:**
- ✓ Entity identity (used in turn execution)
- ✓ Basic retrieval (AI stack retrieval documented)
- ✗ **NOT FOCUSED:** Conflict detection engine
- ✗ **NOT FOCUSED:** Temporal validity classification
- ✗ **NOT FOCUSED:** Threshold engine
- ✗ **NOT FOCUSED:** Effect surface activation
- ✗ **NOT FOCUSED:** Governed consolidation
- ✗ **NOT FOCUSED:** Transformation runtime (deep version)

**Gap:** Memory is documented as a conceptual requirement, but the nine engines are not implemented or detailed in Phase 4. Phase 5 focuses on evaluating whether 20+ turn drama **sustains** but doesn't yet prove the memory architecture **works**.

---

### 2. World Engine Product Spec (Doc 06)

**Original Promise:** Authoritative runtime control product for story authors, operators, QA, narrative engineers

```
Product areas:
- Live runtime control (session list, scene viewer, story-health dashboard, strategy, degraded mode)
- Authoring studio
- Diagnostics
- QA and replay
```

**Current Focus:**
- ✓ Live runtime control (partially—session execution proven)
- ✗ **NOT FOCUSED:** Authoring studio (no "writers' interface" implementation)
- ✓ Diagnostics (admin surfaces specified, not all implemented)
- ⚠️ QA and replay (branching/replay in Phase 6, multi-session in Phase 7)

**Gap:** No authoring studio has been built. Phase 4 documented the runtime, but the **editorial/writer interface** is not in scope.

---

### 3. Component Blueprints & Responsibility Matrix (Doc 54)

**Original Promise:** Implementation minimums for each component

| Component | Original Responsibility | Current Phase 4 Status |
|---|---|---|
| **Backend** | Request validation, auth, session orchestration, content publication, persistence, diagnostics | ✓ Specified (API contracts) |
| **World-engine** | Authoritative runtime, turn execution, commit truth, validation/rejection | ✓ Proven (Phase 4 authority model) |
| **Frontend** | Player routes, launcher/bootstrap/ticket flow, shell, rendering | ✓ Smoke tested (76 tests pass) |
| **Administration-tool** | Governance, inspection, editorial review, incident review | ⚠️ Specified but not fully tested (1,149 tests pass) |
| **Writers-room** | Authoring workflows, publish/review boundary, editorial ergonomics | ✗ **NOT ADDRESSED** (no implementation or spec for author-facing UI) |
| **AI stack** | Retrieval, packaging, governed orchestration, preview vs. commit, fallback | ✓ Detailed (LangGraph contracts, proof discipline) |
| **MCP** | Tool registry, safe handler exposure, operating-profile restrictions | ⚠️ Specified but not fully ops-validated |

**Gap:** Writers-room/authoring workflows are completely absent from current phase focus.

---

## What HAS Been Focused On

### Phase 1-3: Integration
- ✓ Intake and mapping (27,890 files)
- ✓ Code reconciliation (0 conflicts)
- ✓ Domain validation (5/6 domains smoke tested)

### Phase 4: Documentation (Just Completed)
- ✓ **Wave 1-2:** Authority model (three-level explicit authority)
- ✓ **Wave 2:** Turn seams (proposal, validation, commit, render)
- ✓ **Wave 3:** Content authority (YAML > published > builtins)
- ✓ **Wave 3:** Admin surfaces (GoC slice with five views, three incident pathways)
- ✓ **Wave 4-5:** API specification (four families)
- ✓ **Wave 5:** Proof discipline (eight claimed capabilities, source-traceable)
- ✓ **Waves 6-7:** Boundaries and closure

**Result:** 11 canonical documents, 3,590+ lines, all claims traceable to code.

### Phase 5: Planning (Ready to Launch)
- ✓ Five scenario specifications (Salon extended, Garden party, Branching, Character arc, Replayability)
- ✓ Infrastructure design (logging, pressure tracking, consistency audit, carry-forward analysis)
- ✓ Evaluator recruitment (7-10 participants)
- ✓ Week 1-7 timeline (prep, pilot, evaluate 15+ sessions, analyze, document)

**Focus:** Does drama **sustain** across 20+ turns? Do **multi-party dynamics** work? Do **choices matter** (branching)?

---

## What Has NOT Been Focused On

### Critical Gaps (Original MVP Promises, Not Yet Implemented)

| Gap | Original Promise | Why Not Yet | When? |
|---|---|---|---|
| **Memory Engines (9)** | Conflict detection, temporal validity, threshold, effect activation, consolidation | Requires deep runtime architecture design | Phase 6+ (after branching proven) |
| **Authoring Studio** | Writer-facing UI for content creation, story design, NPC behavior setup | Out of scope for single-user MVP | Post-Phase 7 (if multi-author needed) |
| **Writers-room Integration** | Publish/review boundaries, editorial workflows, content approval pipeline | No author-facing surface designed | Post-Phase 7 (multi-stakeholder feature) |
| **Multi-Session Concurrency** | Handling 100+ simultaneous sessions, session isolation, resource limits | Phase 7 goal (scale testing) | Phase 7 (2026-06+) |
| **Pressure Resolution** | Drama curve: high → tension → resolution → closure (validated mechanics) | Phase 5 tests escalation/resolution paths | Phase 5 (current) |
| **Branching Architecture** | Formal system for divergent outcomes, path coherence, replay differentiation | Phase 6 implementation | Phase 6 (2026-06-09+) |
| **Consequence Carry-Forward** | Facts established turn 1-5 carry through turn 20+, affect player choices | Phase 5 validates this through metrics | Phase 5 (current) |
| **Character Growth Arcs** | Measurable character evolution: Shame→Crisis→Resolution (Vanya) | Phase 5 tracks this with consistency audit | Phase 5 (current) |
| **Performance & Scale** | Sub-second turn latency, concurrent sessions, cost tracking | Phase 7 validation | Phase 7 (2026-06+) |
| **QA/Replay System** | Session recording, replay from checkpoint, variant testing | Not yet planned | Phase 6+ (post-branching) |

---

## Evidence of What Was Promised But Deferred

### From Original Implementation Workstreams (Doc 50):

**Workstream E — Governance and Review Surfaces:**
```
Primary paths:
- administration-tool/
- backend/app/api/v1/ai_stack_governance_routes.py
- writers-room/

Typical implementation points:
- inspector bundles,
- governance reports,
- review-bound surfaces,
- incident visibility,
- authoring/admin quality workflows.
```

**Current Status:** Administration-tool is 1,149 tests passing, but **writers-room** has no implementation or detailed specification. This is a **deferred component**.

---

## Missing Information: What Hasn't Been Detailed Yet

### 1. **Memory Conflict & Temporal Model**
- How do conflicting facts resolve? (e.g., two NPCs remember same event differently)
- Temporal validity: which facts are "still true" at turn N?
- Lineage: which choice led to which consequence?
- **Not in Phase 4 focus. Not in Phase 5 scope.**

### 2. **Character Emotional/Consciousness Layers**
Original promise: "Emotional and consciousness layers are runtime participants, not decorative annotations"
- How emotions affect NPC behavior choices
- Consciousness state machine for characters
- Threshold crossings (when does shame become visible?)
- **Phase 5 will measure this indirectly (evaluator observations), but no explicit model yet**

### 3. **Threshold Engine**
- When do characters break under pressure?
- When do they capitulate, become vindictive, seek reconciliation?
- Threshold mechanics are mentioned but not implemented
- **Not in scope for Phase 5; would be Phase 6+**

### 4. **Effect Surface Activation**
- When consequences become player-visible (timing, triggers)
- Interaction effects (consequence A + consequence B = consequence C)
- Propagation (one character's consequence affects another)
- **Not detailed in Phase 4; not tested in Phase 5**

### 5. **Governed Consolidation**
- Merging conflicting memories into a canonical version
- Review/approval of memory consolidation
- Fallback when consolidation fails
- **Not implemented; part of deferred memory architecture**

### 6. **Writers-room Authoring Workflow**
- How do narrative designers create new scenarios?
- Content creation UI (not terminal/JSON editing)
- Editorial approval process for new content
- Publishing pipeline
- **Completely deferred (Phase 7+)**

### 7. **Multi-Party Dynamics at Scale**
- Phase 5 tests 4-6 character scenarios
- What happens at 10+ characters? (alliance networks become exponential)
- Character interaction mesh (who talks to whom, who overhears)
- Complexity limits and degradation
- **Not tested; Phase 7 concern**

### 8. **Replay/Branching Closure**
- Can you replay a branching scenario with recorded outcome?
- Does replay produce identical results (determinism)?
- Can players discover new branches on second play?
- Replay with player *choice* versus recorded actions?
- **Phase 6 focus (not yet implemented)**

---

## Phase 5 Will Validate (Not Implement)

What Phase 5 **tests** but doesn't **implement**:

| Feature | Phase 5 Tests... | Not Yet Implemented |
|---|---|---|
| Long-form drama (20+ turns) | Whether it sustains coherently | The underlying memory engines required for true coherence |
| Character consistency | Via dialogue audit (word count, formality, tone) | The consciousness/emotion layer that should drive consistency |
| Pressure mechanics | Trajectory graphing (does it go up/down?) | Threshold engine (when does pressure cause NPC action?) |
| Consequence carry-forward | Manual mention counting | Automatic temporal validity and lineage tracking |
| Multi-party alliances | Evaluator observation of alliance stability | Formal alliance state machine and conflict resolution |
| Branching outcomes | Three explicit choice paths, outcome comparison | Dynamic branching system that adapts to player approach |

---

## Critical Missing Pieces for "Complete Implementation"

### Tier 1: Needed for Phase 5 Success
- ✓ Authority model (done)
- ✓ Turn execution (done)
- ✓ Player experience signals (done)
- ⚠️ **Character voice consistency engine** (currently manual, evaluator-observed)
- ⚠️ **Pressure accumulation mechanics** (currently working but not formally modeled)

### Tier 2: Needed for Phase 6 (Branching)
- ✗ **Formal branching decision tree system** (not yet designed)
- ✗ **Outcome divergence tracking** (how different are Path A vs Path B?)
- ✗ **Replayability determinism** (can same inputs produce identical outputs?)
- ✗ **Consequence divergence** (do different paths reference different facts?)

### Tier 3: Needed for Phase 7 (Scale)
- ✗ **Concurrent session isolation** (100+ simultaneous games)
- ✗ **Resource allocation & cost tracking**
- ✗ **Performance benchmarks** (turn latency, memory usage)
- ✗ **Fallback/degradation at scale** (when load-shedding kicks in)

### Tier 4: Needed for Production
- ✗ **Memory Conflict Engine** (how two true facts coexist)
- ✗ **Temporal Validity Classifier** (which facts are still canonical?)
- ✗ **Threshold Engine** (pressure → action mapping)
- ✗ **Effect Surface Activation** (consequence timing & visibility)
- ✗ **Writers-room UI** (non-technical content authoring)
- ✗ **QA/Replay System** (test variant scenarios)

---

## Recommendations for Phase 5 + Beyond

### For Phase 5 (Weeks 1-7)
**Keep current focus:** Validate that extended drama sustains, multi-party works, choices matter.

**Don't add:** Memory engine implementation (will distract from evaluation).

### For Phase 6 (After Phase 5, ~2026-06-09)
**Add to scope:**
1. Formal branching decision system (required for "player choice matters" claim)
2. Outcome divergence metrics (measure how different each path is)
3. Consequence carry-forward tracking (automate the manual mention counting)
4. Character growth arc formalization (emotional state machine)

### For Phase 7 (After Phase 6, ~2026-07+)
**Add to scope:**
1. Concurrent session handling
2. Performance benchmarking
3. Memory conflict resolution engine
4. Writers-room authoring studio
5. Full QA/replay system

---

## Conclusion

**What's been delivered:**
- ✓ Authority model proven
- ✓ Turn execution proven
- ✓ Player experience signals defined
- ✓ Admin surfaces specified
- ✓ API contracts documented

**What's still missing (unfocused):**
- ✗ Memory architecture (9 required engines)
- ✗ Character emotion/consciousness layer (as runtime participants)
- ✗ Threshold engine (pressure → behavior)
- ✗ Writers-room (content authoring UI)
- ✗ Formal branching system
- ✗ Multi-session concurrency
- ✗ Production-grade performance

**Current trajectory is correct:**
Phase 5 tests whether the **implemented core** (authority, turn execution, turn seams) actually **sustains** at scale (20+ turns, multi-party, branching scenarios). If Phase 5 succeeds, Phase 6 adds branching, Phase 7 adds scale. If Phase 5 fails, we identify which core assumption is wrong before building on top of it.

**Risk:** If Phase 5 reveals that character consistency breaks at turn 15, or pressure mechanics don't resolve, Phase 6-7 work would be built on a broken foundation. The deferred work (memory engines, emotion layers) might be **required** for Phase 5 success but isn't yet implemented.

**Next action:** Monitor Phase 5 evaluation closely for breakpoints. If evaluators report "character voice breaks," "pressure won't resolve," or "consequences feel disconnected," escalate the deferred work forward.
