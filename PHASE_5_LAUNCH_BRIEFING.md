# Phase 5: Extended Evaluation and Multi-Party Validation - Launch Briefing

**Phase Status:** Launching Week of 2026-04-21  
**Objective:** Prove long-form drama sustainability, multi-party complexity, and branching viability  
**Timeline:** 7 weeks (Weeks 1-7: prep → pilot → evaluation → analysis → documentation)  
**Deliverable:** 5 validation reports + extended evaluation evidence + updated canonical bundle

---

## What Phase 5 Tests

### Unproven Capabilities from Phase 4

Phase 4 proved:
- ✓ Authority boundaries (YAML → published → runtime)
- ✓ Turn execution seams (4 seams, all explicit)
- ✓ Pressure accumulation (5-8 turns)
- ✓ Character distinctness (Vanya ≠ Annette)
- ✓ Player agency (free-form moves work)

Phase 5 proves:
- ? **Long-form coherence** (20+ turn sessions maintain drama)
- ? **Character evolution** (characters change/grow over arc, not repeat)
- ? **Pressure resolution** (high pressure can decrease)
- ? **Multi-party dynamics** (4+ characters with competing interests)
- ? **Branching divergence** (different player choices → different outcomes)

---

## Five Test Scenarios

### Scenario A: Salon Mediation Extended (20+ turns, 3 characters)
**Goal:** Prove long-form sustainability  
**Sessions:** 3 (Escalation / Resolution / Evasion paths)  
**Focus:** Pressure trajectory, character consistency, consequence carry-forward  

### Scenario B: Garden Party Multi-Party (15+ turns, 4-6 characters)
**Goal:** Prove multi-party complexity  
**Sessions:** 3-4 (Alliance-building / Divide-and-conquer / Harmony paths)  
**Focus:** Alliance stability, multi-way pressure, responder selection  

### Scenario C: Branching Architecture (15+ turns, 3 decision points)
**Goal:** Explore branching viability  
**Sessions:** 3 (different decision sequences)  
**Focus:** Outcome divergence, path coherence, consequence divergence  

### Scenario D: Character Arc Sustainability (20+ turns, 1 focus character)
**Goal:** Prove character development  
**Sessions:** 3 (Vanya shame / Annette vindication / Mediator neutrality)  
**Focus:** Arc completeness, character growth, pressure resolution  

### Scenario E: Replayability Test (20+ turns, replay with different approach)
**Goal:** Prove replayability signal  
**Sessions:** 3 pairs (same scenario, different player approach)  
**Focus:** Outcome divergence, dialogue variation, "different story" feeling  

**Total: 15-19 sessions across 5 scenarios, 1000-1500 turns recorded**

---

## Week-by-Week Execution

### Week 1: Infrastructure & Prep (This Week)
**Goal:** Finalize specs, build infrastructure, recruit evaluators

**Critical tasks:**
1. Finalize all 5 scenario specifications (branching trees, victory conditions)
2. Build session logging infrastructure (transcript capture, pressure recording)
3. Recruit 7-10 evaluators (mix of Phase 4 returnees + new)
4. Set up analysis tools (CSV templates, graphing setup)
5. Plan pilot session (Scenario A, Week 2)

**Success metric:** All infrastructure ready, evaluators scheduled, scenarios locked

### Week 2: Pilot Extended Session
**Goal:** Validate that 20+ turn sessions work

**Critical task:**
1. Run Scenario A pilot (20+ turns, 1 evaluator, Escalation path)
2. Identify any breaking points (drama breakdown, character inconsistency, etc.)
3. Collect pressure trajectory, character consistency score, consequence mentions
4. Get evaluator feedback (structured + open)

**Decision:** If pilot succeeds, proceed to Week 3 full evaluation. If issues, debug and delay.

### Weeks 3-5: Full Extended Evaluation
**Goal:** Run all 15+ test sessions, collect evidence

**Parallel execution:**
- Scenario A: 3 sessions (Week 3)
- Scenario B: 3-4 sessions (Weeks 3-4)
- Scenario C: 3 sessions (Week 4)
- Scenario D: 3 sessions (Week 4-5)
- Scenario E: 3 pairs (Week 5)

**Each session captures:**
- Full turn transcript (player action → committed output)
- Pressure magnitude per turn (CSV)
- Consistency metrics (character voice, fact references)
- Evaluator feedback (structured survey + open)

### Week 6: Analysis
**Goal:** Analyze all data, generate trends

**Deliverables:**
1. Pressure trajectory analysis (graphs showing build/resolution)
2. Character consistency audit (voice scores across arc)
3. Consequence carry-forward analysis (fact mention counts)
4. Evaluator feedback compilation (themes + quotes)
5. Branching outcome map (visual of divergent paths)
6. Character arc growth assessment (evolution over turns)

### Week 7: Documentation
**Goal:** Write validation reports, update canonical bundle

**Deliverables:**
1. Extended evaluation runbook (how to run 20+ turn sessions)
2. Multi-party scenario specification (4+ character rules)
3. Pressure resolution mechanics spec (how high pressure releases)
4. Branching architecture design proposal (implementation plan)
5. Replayability assessment (likelihood of replaying)

---

## Success Criteria

### Must Pass (Primary)
- [ ] 80%+ evaluators report drama coherent at turn 20+
- [ ] 85%+ character consistency (voice stable across arc)
- [ ] 70%+ turns reference prior facts (carry-forward)
- [ ] 60%+ sessions show pressure decrease (resolution works)
- [ ] 75%+ free-form moves have consequences through turn 20+

### Should Pass (Secondary)
- [ ] 70%+ characters show measurable growth
- [ ] 80%+ alliance consistency (not random flip)
- [ ] Engagement remains 7+/10 through turn 15+
- [ ] 60%+ outcome difference across branches
- [ ] 60%+ evaluators want to replay differently

### Nice to Have (Exploratory)
- [ ] Identify satisfying narrative closure patterns
- [ ] Determine formal branching architecture feasibility
- [ ] Identify extended session scalability limits

---

## Risks & Mitigations

**Risk: Drama breaks at turn 12**
- Mitigation: Pilot Week 2; debug before Week 3
- Contingency: If breaks, identify blockage and fix character prompts or pressure mechanics

**Risk: Character voice becomes generic after turn 10**
- Mitigation: Checkpoint consistency check every 5 turns during pilot
- Contingency: If detected, tighten character voice prompts before Week 3

**Risk: Multi-party responder logic fails with 4+ characters**
- Mitigation: Code audit of responder selection before Scenario B
- Contingency: Fall back to 3-character scenarios; defer multi-party to Phase 6

**Risk: Evaluator fatigue (fatigued evaluators give poor feedback)**
- Mitigation: Max 45-minute sessions; mandatory 15-minute breaks
- Contingency: Reduce session length; increase evaluator count

**Risk: Branching becomes combinatorial chaos**
- Mitigation: Start with 3 decision points (8 outcomes); test before expanding
- Contingency: Reduce to 2 points (4 outcomes); expand in Phase 6

---

## What Happens Next

### If All Criteria Pass
- Long-form drama is **proven sustainable** (20+ turns maintain coherence)
- Multi-party scenarios are **viable** (4+ characters work)
- Character development is **real** (growth over arc, not repetition)
- Branching **is feasible** (different outcomes from different choices)
- **Foundation for Phase 6:** Implement formal branching architecture

### If Primary Criteria Pass, Secondary Fail
- Core goals (long-form sustainability, multi-party, branching) are achieved
- Some aspects (character growth, replayability) need refinement
- Proceed to Phase 6 with noted improvements

### If Primary Criteria Fail
- Identify specific failure (drama breaks at turn X, character inconsistency, etc.)
- Plan targeted fixes
- Consider scope reduction (cap at 15 turns? simplify characters?)
- Potentially delay Phase 5 completion until fixes are in place

---

## Phase 5 Roadmap

```
Phase 4 Complete (canonical documentation done)
     ↓
Week 1: Prepare (specs, infrastructure, evaluators)
     ↓
Week 2: Pilot (first 20+ turn session, lessons learned)
     ↓
Weeks 3-5: Evaluate (15+ sessions across 5 scenarios)
     ↓
Week 6: Analyze (pressure, character, consequences, branching)
     ↓
Week 7: Document (runbooks, specs, validation reports)
     ↓
Phase 5 Complete (evidence + specifications for Phase 6)
     ↓
Phase 6 Begin (branching architecture implementation)
```

---

## Phase 5 Team

### Required Roles
- **Scenario Designer** — Finalize 5 scenarios, branching trees
- **Facilitator** — Run sessions, manage evaluator experience
- **Test Lead** — Oversee evaluation protocol, identify issues
- **Data Analyst** — Collect data, generate trends, write reports
- **Infrastructure Engineer** — Build/maintain logging and analysis tools
- **Evaluators** — 7-10 people running test sessions (external)

### Decisions Needed This Week
1. **Parallel vs. sequential sessions?** (faster vs. simpler)
2. **Branching complexity?** (3 decision points vs. 5+)
3. **Multi-party scale?** (4 characters vs. 6)
4. **Which evaluators to recruit first?** (Phase 4 returnees vs. all new)

---

## Critical Success Factors

1. **Drama sustains at 20+ turns** — If drama breaks mid-arc, all testing fails
2. **Evaluator quality remains high** — Fatigued evaluators invalidate feedback
3. **Consistent data collection** — Every session must have complete transcript + metrics
4. **No major bugs introduced** — Phase 5 tests features, not bug fixes
5. **Clear success/failure criteria** — Know what "pass" means before starting

---

## Getting Started

**This week (by Friday):**
1. [ ] Review and approve Phase 5 plan
2. [ ] Assign team leads to each role
3. [ ] Finalize 5 scenario specifications
4. [ ] Begin evaluator recruitment (contact Phase 4 participants first)
5. [ ] Schedule Week 2 pilot session (date + evaluator locked)

**Next week (Week 2):**
1. [ ] Run pilot extended session
2. [ ] Analyze pilot results
3. [ ] Adjust approach based on findings
4. [ ] Confirm Week 3 go/no-go (full evaluation launch)

**End of Week 2:**
- Decision: Proceed to Week 3 evaluation (if pilot succeeds)
- OR: Delay 1 week, debug issues, retry pilot Week 3

---

## Reference Documents

- `Plan_Phase5.md` — Master plan (goals, methodology, 5 scenarios, timeline)
- `PHASE_5_TASK_EXECUTION_PLAN.md` — Week-by-week tasks, decisions, success metrics
- `PHASE_4_COMPLETION_SUMMARY.md` — What Phase 4 proved (foundation for Phase 5)

---

## Phase 5 is Ready to Launch

All infrastructure planned. All scenarios designed. All success criteria defined.

**Ready to prove long-form drama, multi-party complexity, and branching viability.**

**What's next: Week 1 prep (finalize specs, recruit evaluators, build infrastructure).**

