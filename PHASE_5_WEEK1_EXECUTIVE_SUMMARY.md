# Phase 5: Week 1 Executive Summary & Kickoff Checklist

**Week:** 2026-04-21 to 2026-04-25  
**Status:** READY TO LAUNCH  
**Goal:** Complete all Week 1 prep so Week 2 pilot can run smoothly

---

## What Week 1 Accomplishes

By end of Friday (2026-04-25):
- ✓ All 5 scenario specifications finalized and locked
- ✓ 7-10 evaluators recruited and scheduled
- ✓ Session infrastructure built and tested
- ✓ Evaluator materials prepared and distributed
- ✓ Pilot session scheduled for Week 2

**Impact:** Week 2 can run first extended session with complete infrastructure; Weeks 3-5 can run 15+ sessions at full scale

---

## Three Core Work Streams

### Stream 1: Scenario Specification (Owner: Scenario Designer)

**Deliverable:** `PHASE_5_SCENARIO_SPECIFICATIONS.md` ✓ COMPLETE

**What's in it:**
- Scenario A: Salon Mediation Extended (20+ turns, three approaches: Escalation/Resolution/Evasion)
- Scenario B: Garden Party Multi-Party (15+ turns, 4-6 characters, three approaches)
- Scenario C: Branching Architecture (15+ turns, three decision points, outcome divergence)
- Scenario D: Character Arc Sustainability (20+ turns, one focus character, three arcs)
- Scenario E: Replayability Test (20+ turns, same scenario replayed with different approaches)

**All scenarios include:**
- ✓ Clear goals and setup
- ✓ Multiple player approaches (branches)
- ✓ Character descriptions
- ✓ Decision points
- ✓ Success metrics
- ✓ Evaluation protocols
- ✓ Data collection procedures

**Status:** LOCKED — Ready for Week 2 pilot, Weeks 3-5 evaluation

---

### Stream 2: Evaluator Recruitment (Owner: Recruitment Coordinator)

**Deliverable:** `PHASE_5_EVALUATOR_RECRUITMENT_PACKAGE.md` ✓ COMPLETE

**What's needed:**
- [ ] Send recruitment messages (Days 1-2)
  - Message to Phase 4 returnees (suggest they come back)
  - Message to new evaluators (no prior experience needed)
- [ ] Collect confirmations (Days 3-5)
  - Target: 7-10 confirmations by Friday
  - Mix: 3-4 returnees + 3-4 new
- [ ] Schedule orientation meetings (Days 5-6)
  - Brief evaluators on role
  - Confirm tech setup
  - Distribute scenario materials
- [ ] Calendar blocking (End of Week 1)
  - Weeks 3-5 time slots reserved
  - Evaluator availability confirmed

**Materials ready:**
- ✓ Evaluator role overview
- ✓ Session flow walkthrough
- ✓ Sample scenario briefs
- ✓ Compensation details ($50/session)
- ✓ FAQ and troubleshooting
- ✓ Post-session survey template
- ✓ Two recruitment messages (returnees + new)

**Timeline:**
- Days 1-2: Send recruitment
- Days 3-5: Collect confirmations
- Days 5-6: Schedule orientations
- End of week: Confirm all 7-10 evaluators

**Status:** Materials ready; recruitment starts TODAY

---

### Stream 3: Infrastructure Setup (Owner: Infrastructure Engineer + Test Lead)

**Deliverable:** `PHASE_5_INFRASTRUCTURE_CHECKLIST.md` ✓ COMPLETE

**Six infrastructure categories:**

1. **Session Logging & Recording**
   - Capture complete transcript every session
   - Record all seam execution (proposal, validation, commit, render)
   - Session metadata (evaluator, scenario, approach, timestamps)

2. **Pressure Tracking**
   - Record pressure vectors per turn (CSV)
   - Enable pressure trajectory graphing

3. **Character Consistency Audit**
   - Extract dialogue per character
   - Manual audit for voice consistency
   - Consistency scoring

4. **Consequence Carry-Forward Tracker**
   - Identify facts established in turns 1-5
   - Track mentions in turns 6+
   - Generate carry-forward report

5. **Evaluator Feedback Collection**
   - Post-session survey (quantitative + open-ended)
   - Response collection (Google Form or Typeform)
   - CSV export for analysis

6. **Analysis Templates & Reporting**
   - Pressure trajectory graphing (matplotlib)
   - Character consistency spreadsheet
   - Consequence analysis tracker
   - Evaluator feedback compilation

**Implementation schedule:**
- Days 1-2: Session logging middleware
- Days 3-4: Data exporters (CSV, dialogue, transcript)
- Days 5: Evaluator feedback system (survey)
- Days 5-6: Analysis templates and scripts
- Days 6: Integration test (full pipeline)

**Validation:**
- Sample session test (Days 1-2)
- Full test session (Days 5-6)
- Complete pipeline verification by Friday EOD

**Status:** Design complete; implementation starts TODAY

---

## Week 1 Day-by-Day Breakdown

### Monday-Tuesday (Days 1-2): Launch Phase 1

**Recruitment Coordinator:**
- [ ] Send recruitment messages (returnees + new evaluators)
- [ ] Monitor responses, collect initial confirmations

**Infrastructure Engineer:**
- [ ] Design session logging middleware
- [ ] Implement turn capture and state snapshots
- [ ] Test with sample session (10 turns)
- [ ] Confirm logging captures all data

**Scenario Designer:**
- [ ] Final review of all 5 scenarios
- [ ] Confirm branching trees are clear
- [ ] Prepare scenario brief materials
- [ ] Ready to distribute to evaluators

**Test Lead:**
- [ ] Monitor infrastructure progress
- [ ] Begin pilot session planning (Week 2)

### Wednesday-Thursday (Days 3-5): Build & Recruit

**Recruitment Coordinator:**
- [ ] Collect confirmations from evaluators (target: 7-10)
- [ ] Begin scheduling orientation meetings
- [ ] Send evaluator briefing materials
- [ ] Confirm compensation details

**Infrastructure Engineer:**
- [ ] Implement data exporters (pressure CSV, dialogue, transcript)
- [ ] Create post-session survey (Google Form/Typeform)
- [ ] Begin analysis templates (pressure graphing, consistency audit)
- [ ] Validate exports with sample data

**Scenario Designer:**
- [ ] Final preparation of scenario briefs
- [ ] Prepare pilot scenario (Scenario A, Escalation path)
- [ ] Brief infrastructure team on pilot expectations

**Test Lead:**
- [ ] Coordinate with infrastructure on full test session (Days 5-6)
- [ ] Prepare evaluator instructions for pilot
- [ ] Confirm Week 2 pilot schedule

### Friday (Day 6): Verify & Lock

**All Teams:**
- [ ] Run full integration test
  - Complete session → all data captured → analysis outputs generated
  - Verify entire pipeline works
- [ ] Confirm all 7-10 evaluators scheduled (Weeks 3-5)
- [ ] Verify infrastructure ready for Week 2
- [ ] Sign-off on readiness

**Specific tasks:**

**Infrastructure Engineer:**
- [ ] Complete analysis templates
- [ ] Run full test session (20+ turns)
- [ ] Export all data (pressure CSV, dialogue, transcript)
- [ ] Generate all analysis outputs (graphs, consistency audit, etc.)
- [ ] Verify complete pipeline (session → export → analysis → report)

**Recruitment Coordinator:**
- [ ] Finalize all evaluator confirmations
- [ ] Schedule all orientation meetings
- [ ] Confirm Week 3 start date (first session)

**Scenario Designer:**
- [ ] Lock all scenarios (no changes after Friday)
- [ ] Confirm pilot scenario materials ready
- [ ] Prepare evaluator briefing slides

**Test Lead:**
- [ ] Confirm pilot is go for Week 2
- [ ] All infrastructure systems verified
- [ ] Evaluators briefed and ready
- [ ] Success criteria documented

---

## Week 1 Success Criteria

### By Friday (EOD), Confirm:

**Scenarios:**
- [ ] All 5 scenarios fully specified with branching trees
- [ ] Each scenario has clear goals, approaches, metrics
- [ ] Evaluation protocols documented

**Evaluators:**
- [ ] 7-10 evaluators confirmed and scheduled
- [ ] Mix of 3-4 returnees + 3-4 new
- [ ] Orientation meetings scheduled (Week 2)
- [ ] All materials distributed

**Infrastructure:**
- [ ] Session logging captures complete data
- [ ] Data exporters work (CSV, dialogue, transcript)
- [ ] Evaluator survey created and tested
- [ ] Analysis templates ready
- [ ] Full pipeline tested end-to-end

**Readiness:**
- [ ] All systems tested with sample session
- [ ] No blockers to Week 2 pilot
- [ ] Team confident in launch

**Go/No-Go Decision:**
- If all above: **GO** to Week 2 pilot
- If any critical piece missing: **HOLD** and address blocker

---

## Week 2 Preview (Pilot Extended Session)

Once Week 1 complete:

### Goal
Run first 20+ turn extended session; validate infrastructure and identify any issues before Weeks 3-5 full evaluation.

### Session Details
- **Scenario:** A (Salon Mediation Extended)
- **Approach:** A1 (Escalation path)
- **Duration:** 20+ turns, 45-60 minutes
- **Evaluator:** Test coordinator or volunteer (high comfort with system)
- **All systems:** Logging, pressure tracking, evaluator feedback, analysis

### Outcomes
1. Confirm infrastructure captures everything correctly
2. Identify any drama sustainability issues (drama breaks at turn X?)
3. Check character consistency through full arc
4. Verify consequence carry-forward works
5. Validate evaluator experience and survey

### Decision
- **Success:** Proceed to Week 3 full evaluation (all 15+ sessions)
- **Issues found:** Debug and retry Week 2 (before full evaluation)

---

## Week 1 Communications

### Internal Kickoff (Today)
- [ ] Team meeting to review Week 1 plan
- [ ] Assign owners to each stream
- [ ] Confirm resource availability
- [ ] Set daily check-in times

### Evaluator Recruitment (Days 1-2)
- [ ] Send recruitment email (returnees)
- [ ] Send recruitment email (new evaluators)
- [ ] Post in recruitment channels (if applicable)

### Evaluator Orientation (Days 5-6)
- [ ] Schedule group orientation or individual meetings
- [ ] Distribute scenario materials
- [ ] Answer questions, confirm tech setup

### Final Readiness Review (Friday)
- [ ] Team meeting to confirm all Week 1 deliverables
- [ ] Go/no-go decision on pilot
- [ ] Handoff to Week 2 lead

---

## Budget & Resource Summary

### Personnel Time
- **Scenario Designer:** 10-15 hours (specs locked, pilot prep)
- **Recruitment Coordinator:** 5-10 hours (recruitment, scheduling)
- **Infrastructure Engineer:** 20-30 hours (build, test, verify)
- **Test Lead:** 5-10 hours (oversight, pilot planning)
- **Total:** 40-65 hours across team

### External Costs
- **Evaluator Compensation:** $50/session × 15+ sessions = $750-$1,000 (but most happens Weeks 3-5, not Week 1)

### Tech Stack (Needed)
- Session logging system (custom or existing)
- Google Form or Typeform (survey)
- Matplotlib or Plotly (graphing)
- Spreadsheet (Google Sheets or Excel)
- Zoom (if remote sessions)

---

## Risk Mitigation

### Risk: Week 1 takes longer than planned
**Mitigation:** Prioritize (scenarios locked first, recruitment second, infrastructure third); parallelize streams
**Contingency:** Extend Week 1 by 2-3 days if needed (delays pilot to mid-Week 2, but doesn't affect full evaluation schedule)

### Risk: Evaluators don't confirm
**Mitigation:** Start recruitment immediately (Monday); have backup list of 5-10 potential evaluators
**Contingency:** If can't reach 7-10, reduce to 5-7 (smaller dataset but still viable)

### Risk: Infrastructure not ready by Friday
**Mitigation:** Build incrementally; test sample session as you build (don't wait until Friday to test)
**Contingency:** Delay pilot to Week 3, extend infrastructure build through Week 2

### Risk: Scenarios need major revision
**Mitigation:** Finalize specs by Thursday; Friday is review only (no changes)
**Contingency:** Revised scenarios lock by end of Week 2 (pilot uses updated specs)

---

## Phase 5 Roadmap (Big Picture)

```
Week 1 (2026-04-21 to 04-25): Prepare
  ├─ Scenarios specified (LOCKED)
  ├─ Evaluators recruited (7-10 confirmed)
  ├─ Infrastructure built & tested
  └─ Ready for pilot

Week 2 (2026-04-28 to 05-02): Pilot
  ├─ Run first extended session (20+ turns)
  ├─ Test all infrastructure
  ├─ Identify issues (if any)
  └─ Go/no-go for Week 3

Weeks 3-5 (2026-05-05 to 05-23): Evaluate
  ├─ Scenario A: 3 sessions (Escalation/Resolution/Evasion)
  ├─ Scenario B: 3-4 sessions (Alliance/Divide/Harmony)
  ├─ Scenario C: 3 sessions (Branching paths)
  ├─ Scenario D: 3 sessions (Character arcs)
  ├─ Scenario E: 3 pairs (Replayability)
  └─ Total: 15+ sessions, 1000-1500 turns

Week 6 (2026-05-26 to 05-30): Analyze
  ├─ Pressure trajectory analysis
  ├─ Character consistency audit
  ├─ Consequence carry-forward analysis
  ├─ Evaluator feedback compilation
  └─ Branching outcome mapping

Week 7 (2026-06-02 to 06-06): Document
  ├─ 5 validation reports
  ├─ Updated canonical bundle
  ├─ Extended evaluation runbook
  └─ Phase 5 COMPLETE

↓

Phase 6 (2026-06-09+): Branching Architecture Implementation
```

---

## Status: READY TO BEGIN

**All Week 1 deliverables prepared:**
- ✓ Scenario specifications (5 scenarios, all locked)
- ✓ Evaluator recruitment package (materials ready)
- ✓ Infrastructure checklist (build plan, test protocol)
- ✓ Executive summary and day-by-day breakdown

**Next action:** Send recruitment emails TODAY (Monday 2026-04-21)

**Kickoff meeting:** Monday morning to brief team on Week 1 plan

**Target:** All Week 1 complete by Friday 2026-04-25 EOD

---

## Key Contacts & Responsibilities

| Role | Name | Email | Responsibilities |
|------|------|-------|------------------|
| **Scenario Designer** | [TBD] | -- | Scenarios, pilot brief |
| **Recruitment Coordinator** | [TBD] | -- | Evaluators, scheduling |
| **Infrastructure Engineer** | [TBD] | -- | Logging, exporters, analysis |
| **Test Lead** | [TBD] | -- | Oversight, pilot, go/no-go |

**Action:** Assign owners to each role before kickoff meeting.

---

## Week 1 Checklist (Print & Post)

**Monday-Tuesday:**
- [ ] Send recruitment emails
- [ ] Start infrastructure build (logging)
- [ ] Test sample session
- [ ] Monitor evaluator responses

**Wednesday-Thursday:**
- [ ] Confirm 7-10 evaluators
- [ ] Build data exporters
- [ ] Create survey
- [ ] Plan full test session

**Friday:**
- [ ] Run full integration test
- [ ] Finalize evaluator materials
- [ ] Lock all systems
- [ ] Go/no-go decision

**Friday EOD:**
- [ ] All Week 1 deliverables complete
- [ ] Team confident in Week 2 pilot
- [ ] Ready to launch Phase 5 evaluation

---

**PHASE 5 WEEK 1: LET'S BUILD**

