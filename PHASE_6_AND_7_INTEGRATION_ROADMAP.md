# Phase 6 & 7: Integration Roadmap

**Overall Timeline:** 2026-06-09 to 2026-09-01 (12 weeks)  
**Status:** Ready to launch (Phase 5 completion unlocks Phase 6)  
**Vision:** From "proven MVP" → "production-ready system"

---

## The Bridge: Phase 5 → Phase 6 → Phase 7

### What Phase 5 Proves (Weeks 1-7, completing 2026-06-06)
- **Long-form drama sustains** (20+ turns without degradation)
- **Multi-party complexity works** (4-6 characters, alliance dynamics)
- **Player choices have consequences** (evidence collected for branching)
- **Characters show growth** (measurable arc through turn sequence)

### What Phase 6 Proves (Weeks 1-6, 2026-06-09 to 2026-07-18)
- **Branching outcomes actually diverge** (Path A ≠ Path B ≠ Path C by 60%+)
- **Branching is deterministic** (same input → same output, replayable)
- **Players want to replay** (70%+ replayability likelihood)
- **Branching doesn't break existing drama** (Phase 5 scenarios still work)

### What Phase 7 Proves (Weeks 1-6, 2026-07-21 to 2026-09-01)
- **System scales** (100 concurrent sessions, no degradation)
- **Sessions stay isolated** (Session A's facts don't leak to Session B)
- **Performance meets SLA** (median turn latency ≤ 2 seconds)
- **Operations are automated** (deploy, monitor, recover without manual intervention)
- **Economics are transparent** (cost per session-hour published)

---

## Phase 6: Branching Architecture (6 Weeks)

### Primary Goal
**Prove that player choice matters:** Different paths lead to meaningfully different outcomes that players can perceive and want to replay.

### What Gets Built

| Component | Current State | Phase 6 Change | Why |
|---|---|---|---|
| Decision Points | Implicit (hardcoded) | Explicit registry | Enable 5+ decision points, measure divergence |
| Path State | Not tracked | Tracked per session | Remember which branch player took |
| Consequences | Global (apply to all paths) | Filtered per path | Only show facts relevant to player's branch |
| Determinism | Not verified | Verified 5/5 | Prove same input → same output |
| Replayability | Unknown | Measured 70%+ | Proof that players want to replay with different choice |

### Success Metrics

```
Outcome Divergence:  ≥ 60% different facts/arcs/endings across paths
Determinism:         5/5 identical replays produce identical transcripts
Replayability:       ≥ 70% evaluators want to replay with different approach
Branch Coherence:    ≥ 80% perceive intentional divergence (not random)
No Regressions:      All Phase 5 scenarios still pass 100%
```

### Deliverables
- Branching system specification (architecture + contracts)
- Decision point registry (all scenarios)
- Outcome divergence analysis (metrics + evidence)
- Determinism verification (test results)
- Phase 6 completion report

### Critical Risk
If outcome divergence < 60%, branches feel too similar and replayability fails. Solution: redesign decision points to be more consequential.

### Timeline
```
Week 1: Design & prototype (branching system specification)
Week 2: Build & integrate (implement in turn execution)
Week 3: Integration testing (branching + turn execution)
Week 4: Revalidation (run Phase 5 Scenario C with branching)
Week 5: Analysis & documentation
Week 6: Final review & closure
```

### Hand-Off to Phase 7
**Proven:** Branching works, outcomes diverge, players like it.  
**Unknown:** Does branching work with 100 sessions running simultaneously?

---

## Phase 7: Large-Scale Deployment (6 Weeks)

### Primary Goal
**Prove the system works at production scale:** 100 concurrent sessions with acceptable performance, cost, and reliability.

### What Gets Built

| Component | Current State | Phase 7 Change | Why |
|---|---|---|---|
| Concurrency | Single-session proven | Multi-session proven | Enable 100 simultaneous games |
| Session Isolation | Assumed | Verified (stress test) | Guarantee no cross-session data leak |
| Performance | Baseline measured | SLA verified (100 sessions) | Turn latency ≤ 2s under load |
| Cost Tracking | Not implemented | Instrumented + analyzed | Transparency: cost per session-hour |
| Deploy Automation | Manual | Automated (CI/CD) | One-command deploy to 100 sessions |
| Incident Response | Ad-hoc | Documented & tested | Recovery in <5 seconds |

### Success Metrics

```
Concurrent Sessions:   100 sessions simultaneously
Cross-Session Leakage: 0 (zero fact leakage between sessions)
Performance SLA:       Median ≤ 2s, 99th percentile ≤ 5s at 100 sessions
Reliability:           99.9%+ success rate (≤1 failure per 1000 turns)
Cost Transparency:     Cost per session-hour published + break-even model
Deploy Automation:     One-command deploy, all 100 sessions updated, zero downtime
Incident Recovery:     <5 seconds from failure detection to resolution
```

### Deliverables
- Concurrency & isolation specification
- Performance benchmarks (load test results)
- Cost analysis (break-even model)
- Deploy automation (CI/CD pipeline)
- Incident response runbook
- Scale limits documentation
- Phase 7 completion report

### Critical Risk
If latency SLA fails at 100 sessions, system doesn't scale. Solution: identify bottleneck (LLM calls? storage? compute?) and optimize or reduce concurrent session limit.

### Timeline
```
Week 1: Design & baseline (measure current performance, cost)
Week 2: Build & implement (isolation, deploy automation, instrumentation)
Week 3: Optimize & validate (fix bottlenecks, load test)
Week 4: Deploy automation & incident response (tested, documented)
Week 5: Stress testing (100 sessions × 4 hours)
Week 6: Documentation & closure
```

### Hand-Off to Production
**Proven:** System works at scale, performance is acceptable, operations are automated.  
**Ready for:** Real players, real monitoring, real costs.

---

## Combined Phase 6+7 Timeline

```
2026-06-06: Phase 5 Complete
            ↓
2026-06-09: Phase 6 Kickoff (Week 1 starts)
            ├─ Week 1 (06-09 to 06-13): Design & prototype
            ├─ Week 2 (06-16 to 06-20): Build & integrate
            ├─ Week 3 (06-23 to 06-27): Integration testing
            ├─ Week 4 (06-30 to 07-04): Revalidation (Phase 5 + branching)
            ├─ Week 5 (07-07 to 07-11): Analysis & documentation
            └─ Week 6 (07-14 to 07-18): Final review & closure
            ↓
2026-07-18: Phase 6 Complete
            ↓
2026-07-21: Phase 7 Kickoff (Week 1 starts)
            ├─ Week 1 (07-21 to 07-25): Design & baseline
            ├─ Week 2 (07-28 to 08-01): Build & implement
            ├─ Week 3 (08-04 to 08-08): Optimize & validate
            ├─ Week 4 (08-11 to 08-15): Deploy automation & incident response
            ├─ Week 5 (08-18 to 08-22): Stress testing
            └─ Week 6 (08-25 to 08-29): Documentation & closure
            ↓
2026-09-01: Phase 7 Complete — PRODUCTION READY
```

---

## What Each Phase Answers

### Phase 4 (Complete)
**"Is the core system architected correctly?"**  
Answer: Yes. Authority model proven, turn seams documented, player experience signals defined.

### Phase 5 (In Progress, Complete 2026-06-06)
**"Does the core system work for extended, multi-party, branching scenarios?"**  
Answer: Yes (if Phase 5 passes). Drama sustains, characters work together, consequences carry forward.

### Phase 6 (2026-06-09 to 07-18)
**"Do branching choices actually matter to players?"**  
Answer: Yes (if Phase 6 passes). Outcomes diverge 60%+, players want to replay, determinism verified.

### Phase 7 (2026-07-21 to 09-01)
**"Can this system run at production scale?"**  
Answer: Yes (if Phase 7 passes). 100 sessions, <2s latency, zero cross-session leakage, transparent costs.

---

## Risk Cascade

Each phase depends on previous phases passing. Failure at any point cascades forward:

```
Phase 4 PASS  → Authority model works       → Proceed to Phase 5
              ↓
Phase 4 FAIL  → Core assumption wrong        → Stop and redesign core (back to Phase 1-2)

Phase 5 PASS  → Drama sustains, characters work → Proceed to Phase 6
              ↓
Phase 5 FAIL  → Long-form breaks somewhere  → Fix core drama mechanics (back to Phase 4)
              (likely: character voice, pressure resolution, consequence carry-forward)

Phase 6 PASS  → Branching outcomes differ   → Proceed to Phase 7
              ↓
Phase 6 FAIL  → Branching is too subtle     → Redesign decision points (within Phase 6)
              (divergence <60%, replayability <70%)

Phase 7 PASS  → System scales reliably      → Deploy to production
              ↓
Phase 7 FAIL  → Bottleneck at N sessions    → Optimize or cap concurrency (within Phase 7)
              (e.g., "system supports 50 concurrent, not 100")
```

---

## Resource Requirements: Phase 6 + 7

### Personnel (Combined 12 Weeks)

| Role | Phase 6 Hours | Phase 7 Hours | Total |
|---|---|---|---|
| Architecture/Design Lead | 35 | 40 | 75 |
| World-engine Engineer | 45 | 30 | 75 |
| Backend/Concurrency Engineer | 20 | 50 | 70 |
| Performance Engineer | 15 | 50 | 65 |
| Test Lead | 30 | 30 | 60 |
| DevOps/Operations | 10 | 40 | 50 |
| Data Analyst | 25 | 25 | 50 |
| Documentation | 20 | 20 | 40 |
| **Total** | **200** | **285** | **485 hours** |

### Costs

| Category | Phase 6 | Phase 7 | Total |
|---|---|---|---|
| Personnel (@ $150/hr) | $30K | $42.75K | $72.75K |
| Evaluators ($50/session) | $500 | $200 | $700 |
| Cloud/Infrastructure | $300 | $800 | $1,100 |
| Tools/Monitoring | $200 | $300 | $500 |
| **Total** | **$31K** | **$43.85K** | **$74.85K** |

---

## Success Definition: Phase 6 & 7

### Phase 6 Success
- ✓ Branching system implemented and integrated
- ✓ Outcome divergence ≥ 60% (measured and verified)
- ✓ Determinism verified (5/5 identical replays)
- ✓ Replayability ≥ 70% (evaluators want to replay)
- ✓ No regressions (Phase 5 scenarios still work)
- ✓ All documentation complete and honest

### Phase 7 Success
- ✓ 100 concurrent sessions proven reliable
- ✓ Session isolation verified (zero cross-session leakage)
- ✓ Performance SLA met (median ≤ 2s, 99th ≤ 5s)
- ✓ Cost transparency (break-even model published)
- ✓ Deploy automation working (zero-downtime deploy)
- ✓ Incident response tested and verified
- ✓ All documentation complete and honest

### Combined Success
**"World of Shadows is a production-ready dramatic narrative system that:**
- **Works at 100 concurrent players**
- **Respects player choice through branching**
- **Sustains drama across 20+ turn sessions**
- **Costs transparently**
- **Operates reliably**
- **Scales without hidden surprises"**

---

## What Happens After Phase 7

Once Phase 7 completes and system is production-ready, three paths open:

### Path A: Launch to Real Players (Recommended)
- Soft launch with 10-20 beta players
- Monitor real-world performance, cost, bugs
- Gather player feedback on experience
- Iterate on player-visible features (UI polish, scenario tuning)

### Path B: Extended Testing (Alternative)
- Expand stress testing (200+ concurrent sessions)
- Develop advanced features in parallel (writers-room UI, memory engines)
- Delay launch until more features ready

### Path C: Production Hardening (If Needed)
- Add legal/compliance features (user accounts, data retention, privacy)
- Add content moderation systems
- Add analytics/monitoring for production scale
- Delay launch until operational requirements met

**Recommendation:** Path A. Get real players. Learn from real usage. Iterate fast.

---

## Deferred Work (Post-Phase 7)

These features are **proven not required** for Phase 7 success but important for production:

### High Priority (Phase 8+)
1. **Memory Conflict Engine** (how conflicting facts resolve)
2. **Writers-room UI** (non-technical content authoring)
3. **User Accounts & Authentication** (required for real players)
4. **Content Moderation** (prevent harmful player behavior)

### Medium Priority (Phase 9+)
1. **Advanced Branching** (4-way, recursive, dynamic generation)
2. **Cross-Session State** (persistent world state)
3. **Analytics & Retention** (player insights)
4. **Character Emotion/Consciousness Layers** (as runtime participants)

### Low Priority (Phase 10+)
1. **Monetization** (pricing, payment processing)
2. **Legal Compliance** (GDPR, CCPA, terms)
3. **QA/Replay System** (test variant scenarios)
4. **Multi-Author Collaboration**

---

## How Phase 6+7 Address Original MVP Gaps

Recall from the gap analysis: original MVP promised 9 memory engines, authoring studio, writers-room, etc.

### What Phase 6+7 Implement
- ✓ **Branching architecture** (formalized decision points, outcome divergence)
- ✓ **Determinism** (same input → same output across replays)
- ✓ **Replayability mechanics** (players want to replay with different choices)
- ✓ **Scale testing** (100 concurrent sessions, performance validated)
- ✓ **Cost transparency** (break-even model published)

### What Phase 6+7 Defer
- ✗ **Memory engines** (conflict detection, temporal validity, threshold engine)
- ✗ **Emotion/consciousness layers** (runtime participants)
- ✗ **Writers-room UI** (authoring studio)
- ✗ **Multi-session state** (cross-session persistence)

**This is intentional.** Phase 6+7 focus on proving the **core MVP works at production scale**, not on implementing all future features. The deferred work can be added post-launch without breaking what's already working.

---

## Critical Dependencies

### Phase 6 Depends On:
- Phase 5 completing with 70%+ evaluators confident in Phase 5 scenarios
- Phase 4 canonical documentation (authority model, turn seams)
- Branching decision system design (completed in Phase 6 Week 1)

### Phase 7 Depends On:
- Phase 6 completing with branching proven to work
- Concurrency/isolation design (completed in Phase 7 Week 1)
- Load testing infrastructure (cloud resources for stress testing)

### Production Deployment Depends On:
- Phase 7 completing with SLA met and cost transparent
- User account system (required before real players)
- Content moderation (required to prevent harm)
- Legal review (terms of service, privacy policy)

---

## Sign-Off Gates

### Phase 6 Final Sign-Off
**Requires:** All metrics met (divergence, determinism, replayability, coherence)  
**Who:** Technical lead + test lead + documentation lead  
**What they verify:** "We can prove branching works and players like it"

### Phase 7 Final Sign-Off
**Requires:** All metrics met (concurrency, isolation, performance, cost transparency)  
**Who:** Technical lead + DevOps lead + operations lead + test lead  
**What they verify:** "System is operationally ready for 100 concurrent players"

### Production Readiness Gate
**Requires:** Phase 7 complete + legal review + user account system + content moderation  
**Who:** Technical lead + legal + operations + product  
**What they verify:** "Safe to launch to real players"

---

## Next Action

**Immediate (Complete Phase 5 First):**
1. Complete Phase 5 evaluation (all 15+ sessions, all 5 scenarios)
2. Collect and analyze Phase 5 data (pressure, consistency, carry-forward)
3. Publish Phase 5 validation reports (5 reports covering each scenario)

**Then (Phase 6 Kickoff):**
1. Review Phase 6 plan with team
2. Confirm timeline and resources
3. Assign owners to each workstream
4. Begin Week 1: Design & prototype

**Then (Phase 7 Kickoff):**
1. Review Phase 7 plan with team
2. Confirm SLA targets are realistic
3. Assign owners to each workstream
4. Begin Week 1: Design & baseline

---

## Summary

**Phases 6 & 7 are the bridge from MVP to production.**

- **Phase 6** proves that player choice matters (branching outcomes diverge, players like it)
- **Phase 7** proves the system can scale (100 concurrent, SLA met, costs transparent)
- **Together** they transform "interesting prototype" into "production-ready system"

If both phases succeed, World of Shadows is ready to serve real players with confidence:
- We know the drama works (Phase 5)
- We know choices matter (Phase 6)
- We know it scales reliably (Phase 7)
- We know the cost (Phase 7)
- We know how to operate it (Phase 7)

**Let's build it.**
