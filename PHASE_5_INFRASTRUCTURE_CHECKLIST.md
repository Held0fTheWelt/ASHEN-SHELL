# Phase 5: Infrastructure Setup Checklist

**Status:** Week 1 - BUILDING  
**Owner:** Infrastructure Engineer + Test Lead  
**Due:** End of Week 1 (Friday)

---

## Infrastructure Categories

### 1. Session Logging & Recording

**Requirement:** Capture complete transcript of every session

**Components:**
- [ ] Session input logger (capture every player move)
- [ ] Game state snapshot capture (after each turn)
- [ ] Seam execution recorder (which seams ran for each turn)
- [ ] Output capture (what was shown to evaluator)
- [ ] Session metadata (start time, end time, evaluator ID, scenario, approach)

**Output format:**
```json
{
  "session_id": "A1-eval001-2026-05-05",
  "evaluator": "Alice",
  "scenario": "A",
  "approach": "Escalation",
  "start_time": "2026-05-05T14:00:00Z",
  "turns": [
    {
      "turn_number": 1,
      "player_action": "Vanya greets Annette warily",
      "scene_assessment": {...},
      "proposed_state_effects": [...],
      "validation_outcome": {...},
      "committed_result": {...},
      "visible_output_bundle": {...},
      "pressure_vectors": {
        "blame": 5,
        "dignity_injury": 7,
        "exposure": 4
      },
      "timestamp": "2026-05-05T14:02:15Z"
    },
    ...
  ]
}
```

**Tools needed:**
- [ ] Logging middleware (hook into turn execution)
- [ ] Session output formatter (convert logs to JSON)
- [ ] Transcript exporter (convert JSON to readable markdown)

**Validation:** Run test session, confirm complete transcript captures all data.

---

### 2. Pressure Tracking & Recording

**Requirement:** Record pressure magnitude per turn for analysis

**Components:**
- [ ] Pressure vector capture (blame, dignity_injury, exposure, alliance_shift, etc.)
- [ ] Per-turn pressure CSV export
- [ ] Pressure history per session

**Output format (CSV):**
```
turn_number,blame,dignity_injury,exposure,alliance_shift,timestamp
1,5,7,4,0,2026-05-05T14:02:15Z
2,6,7,5,0,2026-05-05T14:03:00Z
3,8,8,6,1,2026-05-05T14:03:45Z
...
```

**Tools needed:**
- [ ] Pressure state extractor
- [ ] CSV writer
- [ ] Graphing setup (matplotlib/plotly for trajectory visualization)

**Validation:** Run test session, confirm pressure CSV has all turns, can generate pressure trajectory graph.

---

### 3. Character Consistency Audit

**Requirement:** Measure voice consistency across turns

**Components:**
- [ ] Dialogue extractor (pull all character lines per character)
- [ ] Voice consistency template (word count, formality, emotional tone)
- [ ] Manual audit spreadsheet

**Audit template:**
```
Turn | Character | Dialogue | Word Count | Formality (1-10) | Emotional Tone | Issues
1    | Vanya     | "Annette..." | 25 | 8 | Formal, distant | --
2    | Annette   | "Let's not..." | 10 | 7 | Sharp, direct | --
3    | Vanya     | "You knew..." | 35 | 8 | Still formal | Consistent ✓
...
```

**Tools needed:**
- [ ] Dialogue extractor script
- [ ] Audit spreadsheet template (Google Sheets or Excel)
- [ ] Consistency scoring formula

**Validation:** Run test session, extract all dialogue, audit for consistency, produce consistency score per character.

---

### 4. Consequence Carry-Forward Tracker

**Requirement:** Count how many turns reference previously established facts

**Components:**
- [ ] Fact extractor (identify facts established in turns 1-5)
- [ ] Mention tracker (find where facts referenced in turns 6+)
- [ ] Carry-forward report

**Report template:**
```
Session: A1-eval001
Fact Established Turn 3: "Vanya had affair with servant"
Mentions:
  - Turn 5: Annette: "...the affair with servant..."
  - Turn 8: Vanya: "You knew about the servant..."
  - Turn 12: Annette: "...humiliated by affair..."
  - Turn 15: Vanya (internal): "The servant incident..."
Total mentions: 4 out of 22 turns = 18% carry-forward rate
```

**Tools needed:**
- [ ] Fact extraction script (mark facts in turns 1-5)
- [ ] Mention finder (search for fact references in turns 6+)
- [ ] Report generator

**Validation:** Run test session, identify facts, count mentions, produce carry-forward report.

---

### 5. Evaluator Feedback Collection

**Requirement:** Capture structured feedback after each session

**Components:**
- [ ] Post-session survey (quantitative + open-ended)
- [ ] Survey delivery method (Google Form or Typeform)
- [ ] Response aggregation

**Survey structure:**
- Quantitative (1-10 scales):
  - Arc satisfaction
  - Character consistency
  - Player agency
  - Pressure coherence
  - Consequence visibility
  - Engagement level
- Open-ended:
  - What felt real?
  - What felt fake?
  - Character observations
  - Replay interest
  - Biggest takeaway

**Tools needed:**
- [ ] Survey creation (Google Forms or Typeform)
- [ ] Response collection
- [ ] Data export (CSV for analysis)

**Validation:** Create sample survey, collect responses from test session, export data.

---

### 6. Analysis Templates & Reporting

**Requirement:** Set up analysis infrastructure for Week 6

**Components:**
- [ ] Pressure trajectory graphing (matplotlib)
- [ ] Character consistency spreadsheet
- [ ] Consequence analysis tracker
- [ ] Evaluator feedback compilation
- [ ] Session comparison matrix

**Tools needed:**
- [ ] Python script for pressure graphing
- [ ] Excel/Sheets templates for all metrics
- [ ] Report generation template

**Validation:** Import test session data, generate all analysis outputs (graphs, charts, reports).

---

## Implementation Schedule

### Days 1-2 (Today/Tomorrow)
**Task:** Session logging infrastructure

- [ ] Design logging middleware
- [ ] Implement turn capture
- [ ] Implement state snapshot
- [ ] Test with 1 sample session

**Success:** Sample session produces complete JSON log with all turns

### Days 3-4
**Task:** Data exporters and CSV generation

- [ ] Implement pressure CSV exporter
- [ ] Implement dialogue extractor
- [ ] Implement transcript markdown exporter
- [ ] Test with sample session

**Success:** Can export JSON → pressure CSV, dialogue list, readable transcript

### Days 5 (Friday AM)
**Task:** Evaluator feedback system

- [ ] Create survey (Google Form or Typeform)
- [ ] Set up response collection
- [ ] Test survey with test evaluator
- [ ] Confirm data export works

**Success:** Evaluator can complete survey, responses export to CSV

### Days 5-6 (Friday PM)
**Task:** Analysis templates

- [ ] Create pressure graphing script
- [ ] Create character consistency spreadsheet
- [ ] Create consequence analysis tracker
- [ ] Create evaluator feedback compilation template

**Success:** Can import test session data and generate all analysis outputs

### Days 6 (Friday EOD)
**Task:** Integration test

- [ ] Run complete test session
- [ ] Export all data (transcript, pressure, dialogue)
- [ ] Collect evaluator feedback
- [ ] Generate all analysis outputs
- [ ] Verify everything flows from session to report

**Success:** Complete pipeline works end-to-end

---

## Risk Mitigation

### Risk: Logging captures incomplete data
**Mitigation:** Design logging to be comprehensive upfront; test on sample session
**Fallback:** Manual transcript if automated capture fails

### Risk: Analysis takes too long (delays Week 6)
**Mitigation:** Create templates and scripts in Week 1; test on sample data
**Fallback:** Streamlined analysis (focus on key metrics only)

### Risk: Survey response rate low
**Mitigation:** Send survey immediately after session; make it 10 min max
**Fallback:** Phone debrief if evaluator skips online survey

### Risk: Evaluator doesn't engage with checkpoints
**Mitigation:** Pause automatically every 5 turns; make checkpoints obvious
**Fallback:** Use engagement metric from evaluator survey instead

---

## Infrastructure Readiness Checklist

### By End of Week 1 (Friday), Confirm:

**Session Recording:**
- [ ] Session logging captures all turns
- [ ] State snapshots record every change
- [ ] Seam execution recorded (proposal, validation, commit, render)
- [ ] Session metadata complete (evaluator, scenario, approach, timestamps)

**Data Export:**
- [ ] JSON logs export without errors
- [ ] Pressure CSV generates correctly (one row per turn)
- [ ] Dialogue extraction works (all character lines captured)
- [ ] Transcript markdown readable

**Evaluator Experience:**
- [ ] Survey is intuitive and takes ~10 min
- [ ] Survey responses export to CSV
- [ ] Evaluator instructions clear and easy to follow
- [ ] Checkpoint notes can be captured (pen/paper or digital)

**Analysis Ready:**
- [ ] Pressure trajectory graph generates from CSV
- [ ] Character consistency spreadsheet accepts dialogue input
- [ ] Consequence analysis tracker identifies facts and mentions
- [ ] Evaluator feedback compilation aggregates responses

**End-to-End:**
- [ ] Sample session runs → all data captured → analysis outputs generated
- [ ] Complete pipeline verified (logging → export → analysis → reporting)

---

## Detailed Task Breakdown

### For Engineering Team (Infrastructure)

**Task 1: Session Logging Middleware** (Days 1-2)
```python
# Pseudocode
class SessionLogger:
    def __init__(self, session_id, evaluator, scenario, approach):
        self.session_id = session_id
        self.turns = []
    
    def log_turn(self, turn_number, player_action, scene_assessment, 
                 proposed_effects, validation_outcome, committed_result,
                 visible_output, pressure_vectors, timestamp):
        turn_record = {
            "turn_number": turn_number,
            "player_action": player_action,
            # ... all fields ...
            "timestamp": timestamp
        }
        self.turns.append(turn_record)
    
    def export_json(self):
        return json.dumps({
            "session_id": self.session_id,
            "evaluator": self.evaluator,
            # ... metadata ...
            "turns": self.turns
        }, indent=2)
    
    def export_pressure_csv(self):
        # Extract pressure vectors, return as CSV
        pass
    
    def export_transcript_markdown(self):
        # Format turns as readable markdown
        pass
```

**Task 2: Data Exporters** (Days 3-4)
- Pressure CSV from JSON
- Dialogue list from JSON
- Transcript markdown from JSON
- Character consistency audit template

**Task 3: Survey System** (Days 5)
- Create Google Form or Typeform
- Quantitative questions (1-10 scales)
- Open-ended questions
- Response collection and CSV export

**Task 4: Analysis Tools** (Days 5-6)
- Pressure trajectory graphing
- Character consistency scorecard
- Consequence mention counter
- Evaluator feedback aggregator

---

## Testing Protocol

### Sample Session (Days 1-2)

Run one complete test session with infrastructure engineer playing evaluator:

1. **Setup:** Run Scenario A (Escalation) for ~10 turns (abbreviated)
2. **Logging:** Confirm all logging middleware works
3. **Export:** Export JSON, pressure CSV, dialogue, transcript
4. **Analysis:** Generate all analysis outputs
5. **Check:** Verify completeness and accuracy

**Success criteria:** All data captured, exports work, analysis outputs are correct

### Full Test Session (Days 5-6)

Run second test session with actual evaluator:

1. **Full session:** 20+ turns of actual gameplay
2. **All pipelines:** Run complete logging → export → analysis flow
3. **All outputs:** Generate pressure graph, consistency audit, consequence report
4. **Evaluator feedback:** Collect survey responses
5. **Integration:** Verify entire pipeline (session → analysis → report)

**Success criteria:** End-to-end pipeline works; can produce all analysis reports by Week 6

---

## Week 2 Readiness

By end of Week 1, infrastructure should be:
- ✓ Tested with sample session
- ✓ Ready for production use in Week 2 pilot
- ✓ Scalable to 15+ sessions in Weeks 3-5
- ✓ Capable of generating all analysis outputs by Week 6

**Gating:** If infrastructure not ready, delay pilot to Week 3 (no infrastructure = no data = no analysis)

---

## Status: READY TO BUILD

All infrastructure requirements documented:
- ✓ 6 major categories (logging, pressure, consistency, consequences, feedback, analysis)
- ✓ Implementation schedule (Days 1-6 of Week 1)
- ✓ Testing protocol (sample session, full test session)
- ✓ Readiness checklist

**Next step:** Begin implementation (Task 1: Session logging middleware, Days 1-2)

