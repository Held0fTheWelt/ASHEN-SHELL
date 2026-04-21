# Phase 5: Task Execution Plan - Immediate Next Steps

**Status:** Ready to begin  
**Date:** 2026-04-21  
**First Week Goal:** Finalize infrastructure and launch pilot extended session

---

## Phase 5 Overview

Phase 5 tests three critical unproven capabilities:
1. **Long-form drama sustainability** (20+ turn sessions maintain coherence)
2. **Multi-party complexity** (4+ character scenarios work)
3. **Branching architecture** (player choices lead to different outcomes)

**15+ test sessions planned** (Weeks 3-5)  
**7-10 evaluators needed** (mix of Phase 4 participants + new)  
**1000-1500 turns to be recorded and analyzed**

---

## Week 1 Tasks (This Week)

### Task 1: Finalize Scenario Specifications
**Owner:** Design team  
**Due:** End of day Friday  
**Deliverable:** 5 complete scenario specs with branching trees

**Subtasks:**
- [ ] Scenario A: Salon Mediation Extended (confirm 20+ turn structure, branching points)
- [ ] Scenario B: Garden Party (confirm 4+ character setup, responder rules)
- [ ] Scenario C: Branching Architecture (define 3 decision points at turns 5/10/15)
- [ ] Scenario D: Character Arc (pick 3 focus characters, define arc targets)
- [ ] Scenario E: Replayability (confirm A can be replayed with different approach)

**Success criteria:** Each scenario has clear start/end conditions and victory/failure states

### Task 2: Build Session Infrastructure
**Owner:** Engineering team  
**Due:** Mid-week  
**Deliverable:** Logging, transcription, and survey tools ready

**Subtasks:**
- [ ] Session logging (full turn capture: player action, seam execution, output)
- [ ] Pressure magnitude recording (CSV per turn)
- [ ] Turn transcript export (formatted for analysis)
- [ ] Post-session survey tool (structured + open feedback)
- [ ] Session metadata (evaluator, scenario, approach, start/end time)

**Success criteria:** Can run a test session and have clean transcript + data within 2 hours

### Task 3: Begin Evaluator Recruitment
**Owner:** Evaluation coordinator  
**Due:** End of week (recruitment complete next week)  
**Deliverable:** Signed evaluators, calendars blocked

**Subtasks:**
- [ ] Contact 3-4 Phase 4 evaluators (ask to continue)
- [ ] Recruit 4-6 new evaluators (no prior system knowledge)
- [ ] Schedule orientation session (explain Scenario A, set expectations)
- [ ] Calendar: Block 18-19 time slots (Weeks 3-5, 2-hour blocks including debrief)
- [ ] Send briefing document (what to expect, what game is about, evaluation role)

**Success criteria:** 7-10 confirmed evaluators with scheduled sessions, briefing materials sent

### Task 4: Create Pilot Extended Session Plan
**Owner:** Test lead  
**Due:** Early next week (run pilot Week 2)  
**Deliverable:** Detailed plan for first 20+ turn test

**Subtasks:**
- [ ] Design Scenario A pilot (20+ turns, 1 evaluator, Escalation path)
- [ ] Identify potential blockers (drama breakdown points, character consistency issues)
- [ ] Create checkpoint protocol (every 5 turns: pressure check, character consistency check)
- [ ] Plan mitigations (if drama breaks at turn X, what's the fix?)
- [ ] Schedule pilot (Week 2, ideally mid-week so feedback can inform Week 3 launch)

**Success criteria:** Pilot session can run autonomously; data is collected; debrief identifies issues

### Task 5: Set Up Analysis Infrastructure
**Owner:** Data/analysis team  
**Due:** Mid-week  
**Deliverable:** Tools and spreadsheet templates ready

**Subtasks:**
- [ ] Pressure trajectory CSV template (turn # → pressure vector values)
- [ ] Character consistency audit template (turn # → character, lines, voice score)
- [ ] Consequence mention tracker (turn # → which facts referenced)
- [ ] Evaluator feedback aggregation tool (collect survey responses)
- [ ] Graph generation setup (matplotlib or similar for trajectory visualization)

**Success criteria:** Can import 1000+ turns of data and generate analysis graphs

---

## Week 2 Tasks (Pilot & Prep)

### Task 6: Run Pilot Extended Session
**Owner:** Test lead + facilitator  
**Due:** Mid-week (Scenario A, 20+ turns)  
**Deliverable:** Complete transcript, pressure data, evaluator feedback

**Subtasks:**
- [ ] Run Scenario A with first evaluator (Escalation path)
- [ ] Collect full transcript (all turns, all seams)
- [ ] Record pressure magnitude each turn
- [ ] Take checkpoint notes every 5 turns
- [ ] Run post-session debrief (structured survey + open feedback)

**What we're looking for:**
- Can 20+ turn session run without major bugs?
- Does drama sustain or break mid-arc?
- Is character voice consistent across all turns?
- Are consequences visible in narration?
- Does evaluator stay engaged?

**Blockers to watch:**
- Turn latency increases over arc (indicates performance degradation)
- Character dialogue becomes generic after turn 15
- Pressure vectors don't accumulate (stays flat)
- Evaluator reports disengagement around turn 10-12

### Task 7: Analyze Pilot Results & Adjust
**Owner:** Analysis team + design team  
**Due:** End of week (final adjustments before Week 3)  
**Deliverable:** Lessons learned + adjusted approach for Weeks 3-5

**Subtasks:**
- [ ] Plot pressure trajectory (does it build, plateau, resolve?)
- [ ] Audit character dialogue (consistency score)
- [ ] Count consequence mentions (which facts carried forward?)
- [ ] Review evaluator feedback (what worked, what didn't?)
- [ ] Identify needed fixes (if any) for Weeks 3-5 sessions

**Expected outcomes:**
- If drama sustains: Proceed with full evaluation Week 3
- If drama breaks: Identify breakpoint and implement fix
- If character inconsistency found: Debug character prompts
- If pressure doesn't accumulate: Review pressure mechanics

---

## Week 3 Start (Full Evaluation Begin)

### Task 8: Launch Scenario A Sessions (Salon, 20+ turns)
**Owner:** Facilitators + evaluators  
**Due:** Full week (3 sessions, different evaluators/approaches)  
**Deliverable:** 3 complete session transcripts + data

**Subtasks:**
- [ ] Session A1: Escalation path (evaluator 1)
- [ ] Session A2: Resolution path (evaluator 2)
- [ ] Session A3: Evasion path (evaluator 3)

**Parallel work:**
- Begin Scenario B infrastructure (4+ character setup)
- Continue evaluator orientation (sessions B and beyond)

---

## Critical Decisions (Week 1)

### Decision 1: Parallel vs. Sequential Sessions
**Question:** Should all 15+ sessions run in parallel (faster) or sequentially (simpler)?

**Parallel approach:**
- Pros: Faster (complete by end of Week 5)
- Cons: Requires 7-10 evaluators simultaneously, complex logistics

**Sequential approach:**
- Pros: Simpler (one session at a time), easier debugging
- Cons: Slower (extend into Week 6-7)

**Recommendation:** Run Scenario A (3 sessions) in parallel Week 3, then based on pilot results decide for B-E

### Decision 2: Branching Complexity (Scenario C)
**Question:** How many branching points and outcomes?

**Option 1:** Light branching (3 decision points = 8 outcomes)
- Simpler to manage
- Sufficient to test basic divergence

**Option 2:** Deep branching (5+ decision points = 32+ outcomes)
- More comprehensive
- Risk of combinatorial explosion

**Recommendation:** Start with 3 decision points; if clean, expand to 5 in Phase 6

### Decision 3: Multi-Party Scale (Scenario B)
**Question:** How many characters in garden party scenario?

**Option 1:** 4 total (3 core + 1 new)
- Easier for responder logic
- Still proves multi-party works

**Option 2:** 6 total (3 core + 3 new)
- More realistic party scene
- Risk of responder selection chaos

**Recommendation:** Start with 4; expand to 6 if 4 works cleanly

---

## Success Metrics for Week 1

By end of Week 1, we should have:
- ✓ All 5 scenarios finalized (specs ready for execution)
- ✓ Infrastructure built (logging, surveys, analysis tools)
- ✓ 7-10 evaluators recruited and briefed
- ✓ Pilot session planned (Week 2, Scenario A)
- ✓ Analysis infrastructure ready (data collection tools)

**Go/No-go decision:** If all above complete, move to Week 2 pilot. If any critical piece missing, delay pilot 1 week.

---

## Budget & Resource Needs

### Personnel
- 1 scenario designer (finalize 5 specs)
- 2 engineers (infrastructure)
- 1 coordinator (evaluator recruitment)
- 1 test lead (pilot planning)
- 1 analyst (analysis infrastructure)
- 7-10 evaluators (external, ~50 hours each over Weeks 3-5)

### Timeline
- Week 1: Infrastructure & prep (4 people, part-time)
- Week 2: Pilot (3 people, full-time)
- Weeks 3-5: Full evaluation (7-10 evaluators, 1 facilitator)
- Week 6: Analysis (1 analyst, full-time)
- Week 7: Documentation (2 people, part-time)

### Infrastructure
- Session logging system (code exists? need audit)
- Survey tool (Google Forms? custom?)
- CSV/graphing tools (Python + matplotlib?)
- Evaluator orientation materials (slides, video, handout)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Drama breaks at turn 12 | Medium | High | Pilot Week 2; if breaks, debug before Week 3 |
| Evaluator fatigue | Medium | Medium | Max 45-min sessions; 15-min breaks |
| Multi-party responder logic fails | Low | High | Code audit before Scenario B |
| Branching becomes combinatorial chaos | Low | Medium | Start with 3 points, expand later |
| Character voice degrades | Medium | High | Voice prompt audit; checkpoint every 5 turns |
| Infrastructure not ready | Low | Medium | Build in parallel; use temporary workarounds if needed |

---

## Next Steps (This Week)

**Today/Tomorrow:**
1. [ ] Review this plan with team
2. [ ] Assign owners to each task
3. [ ] Create shared calendar (18-19 time blocks reserved)
4. [ ] Send evaluator recruitment message (reach out to Phase 4 participants first)

**This Week:**
1. [ ] Finalize scenario specs (all 5 complete)
2. [ ] Build session infrastructure (logging + surveys working)
3. [ ] Recruit 7-10 evaluators (confirmations + briefing sent)
4. [ ] Plan pilot session (Week 2 date set, Scenario A structure finalized)
5. [ ] Create analysis templates (pressure CSV, consistency audit, etc.)

**End of Week Decision:**
- **Go:** All prep complete → Proceed with pilot Week 2
- **Hold:** Something incomplete → Extend prep 1 week, pilot Week 3

---

## Handoff to Phase 5

Once Week 1 is complete:
- `Plan_Phase5.md` is the master plan (goals, methodology, scenarios)
- Task execution follows this document (Week-by-week tasks)
- Each session records: transcript, pressure data, evaluator feedback
- Weekly analysis: pressure trends, character consistency, consequence tracking
- Final deliverable Week 7: 5 validation reports + updated canonical bundle

