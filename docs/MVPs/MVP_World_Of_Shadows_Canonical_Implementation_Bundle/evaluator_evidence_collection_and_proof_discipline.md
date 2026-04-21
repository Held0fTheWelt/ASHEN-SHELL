# Evaluator Evidence Collection and Proof Discipline

## Valid Evidence Categories

What counts as acceptable evidence for GoC slice claims:

### Category 1: Observable Behavior (Highest Weight)
**What it is:** Player-visible behavior that demonstrates a claim

**Examples:**
- "Pressure accumulates": Player sees character become increasingly angry across turns; captured in game output
- "Consequences carry forward": Character references turn 3's event in turn 5's dialogue (visible in turn trace)
- "Character voice is distinct": Reader identifies speaker from dialogue without attribution (test with blind readers)

**How to collect:** Run sessions, record outputs, extract evidence

**Evidence artifact:** Turn logs, game screenshots, dialogue transcripts

### Category 2: Comparative Metrics (Medium Weight)
**What it is:** Measured differences between conditions (WoS vs. generic chat)

**Examples:**
- "Pressure accumulation": Measure pressure magnitude change per turn; WoS shows cumulative increase, generic chat is random
- "Voice distinctness": Count unique vocabulary per character; WoS shows consistency, generic chat varies
- "Consequence carry-forward": Count how many prior-turn facts are mentioned in narration; WoS is higher

**How to collect:** Run controlled tests with human evaluators or automated metrics

**Evidence artifact:** Spreadsheet with metrics, graphs showing differences

### Category 3: Participant Feedback (Medium Weight)
**What it is:** Evaluator responses to structured questions

**Examples:**
- "Did the system feel different from generic chat?" → 7/8 said yes
- "Could you predict character responses?" → 6/8 said yes, responses felt grounded
- "Did consequences matter?" → 8/8 said yes, felt like actions had weight

**How to collect:** Administered post-session survey

**Evidence artifact:** Survey data, participant quotes

### Category 4: Expert Assessment (Medium Weight)
**What it is:** Trained evaluators assessing quality dimensions

**Examples:**
- Technical reviewer assesses: "Pressure seams are implemented correctly per code audit"
- Narrative reviewer assesses: "Character voices are differentiated and consistent"
- Design reviewer assesses: "Five quality signals are all present in sample turns"

**How to collect:** Structured review by domain experts

**Evidence artifact:** Review report with specific findings and citations

### Category 5: Code Audit (Supporting Weight)
**What it is:** Code analysis showing claimed mechanisms exist and are used

**Examples:**
- "Pressure tracking exists": Code audit shows pressure vectors are read/written in all seams
- "Consequences carry forward": Code audit shows turn log is consulted in render seam
- "Validation gates exist": Code audit shows rule engine blocks invalid moves

**How to collect:** Read source code; trace execution paths

**Evidence artifact:** Code review document with file/line references

---

## Invalid Evidence (What Does NOT Count)

### ❌ Process Narrative
"We implemented pressure tracking." ← Says nothing about whether it works

### ❌ Aspirational Wording
"The system is designed to create dramatic immersion." ← Describes intent, not evidence

### ❌ Unverified Claims
"Players found it immersive." ← Without data; no evaluator names, no questions asked

### ❌ Feature Checklist
"✓ Implemented: pressure tracking, consequence carry-forward, voice distinctness" ← Existence ≠ working

### ❌ Comparative Claims Without Baseline
"This is better than generic chat." ← Better than what specifically? What metrics?

### ❌ Self-Reported Claims
"The team believes this works." ← Beliefs are not evidence

All claims must be evidence-backed. Vague narrative is not acceptable.

---

## Evidence Binding Rules

Every non-trivial claim in canonical documentation must have a source:

**Strong binding (required):**
```
Claim: "Pressure accumulates across turns"
Evidence: "GoC slice acceptance test showed pressure magnitude increased 
          from turn 1 (5) → turn 3 (8) → turn 5 (7) in 80% of sessions.
          See: validation_runs/2026-04-21/goc_evaluation_report.md"
```

**Weaker binding (acceptable if no stronger evidence exists):**
```
Claim: "Characters have distinct voices"
Evidence: "Code audit of voice_prompt_injection.py shows character-specific
          prompts are used. Blind test of 10 dialogue pairs had 90% 
          accuracy in identifying speaker. See: validation_runs/.../voice_audit.md"
```

**Unacceptable (no binding):**
```
Claim: "The system creates immersion"
Evidence: (none provided)
← This claim must be removed or reworded with evidence
```

Every claim must be able to point to at least one evidence artifact.

---

## Proof of Claimed Implementation

### Claim: "Turn execution has four explicit seams"
**Evidence sources:**
1. Code audit: `world-engine/app/story_runtime_shell.py` shows four named seams
2. Turn traces: Sample turn_log entries show all four seams in `diagnostics_refs`
3. Documentation: This document specifies the four seams with code paths

**Verified:** ✓

### Claim: "Pressure vectors shape character behavior"
**Evidence sources:**
1. Code audit: `scene_assessment.py` reads pressure_state; `select_scene_function.py` uses it for ranking
2. Observable behavior: Turn trace shows character dialogue changes with pressure (see god_of_carnage_evaluation_turn_samples.md)
3. Metrics: Pressure alignment audit shows 95% of dialogue matches active pressure vector

**Verified:** ✓

### Claim: "Consequences carry forward across turns"
**Evidence sources:**
1. Code audit: `render_visible.py` includes `established_facts` in scene context before calling model
2. Observable behavior: Sample turns show turn 2 facts referenced in turn 4-5 dialogue
3. Participant feedback: 7/8 evaluators reported consequences felt persistent
4. Metrics: Count of prior-turn references per turn (WoS: avg 2.3, generic chat: avg 0.1)

**Verified:** ✓

### Claim: "Players feel qualitative difference from generic chat"
**Evidence sources:**
1. Comparative test: 8 evaluators ran both conditions; 7/8 reported difference
2. Feedback quotes: "WoS felt grounded; generic chat felt random"
3. Behavioral evidence: WoS evaluators made more thoughtful moves (25% free-form moves vs. 10% generic)

**Verified:** ✓ (conditional on H1 threshold of 80% being met; currently 87.5%)

### Claim: "YAML is the canonical source and builtins cannot override it"
**Evidence sources:**
1. Code audit: `backend_loader.py` shows precedence: YAML > published > builtins
2. Test case: Deliberately set YAML and builtin values to conflict; confirmed YAML wins
3. Documentation: This document specifies the precedence rule with code path

**Verified:** ✓

---

## Unproven Claims (Deferred to Future Work)

These claims are **not** part of Phase 4 scope:

### Claim: "Long-term satisfaction (20+ turn sessions)"
**Why unproven:** Only tested up to 18 turns; drama sustainability unknown
**When to prove:** Phase 5 (extended evaluation)

### Claim: "Multi-party complexity (4+ characters negotiating)"
**Why unproven:** Only GoC (3 characters) tested; complex scenarios untested
**When to prove:** Phase 5 (multi-party slice)

### Claim: "Narrative branching (world could've gone differently)"
**Why unproven:** State is deterministic from turn sequence; branching not tested
**When to prove:** Phase 6 (branching/choice architecture)

### Claim: "Replay value (different approaches create different stories)"
**Why unproven:** Only linear progression tested; alternate outcomes untested
**When to prove:** Phase 5-6 (branching architecture)

All unproven claims are explicitly flagged; no aspirational language about them.

---

## Evidence Corpus for GoC Slice

### Current Evidence Available

**Validation runs:**
- `validation_runs/2026-04-21/goc_evaluation_report.md` — Evaluator feedback from 8 participants
- `validation_runs/2026-04-21/pressure_metrics.csv` — Pressure tracking per turn across sessions
- `validation_runs/2026-04-21/character_voice_analysis.md` — Voice distinctness audit

**Code audits:**
- `code_audits/2026-04-21/seam_implementation_audit.md` — Four seams verified
- `code_audits/2026-04-21/content_authority_audit.md` — YAML precedence verified
- `code_audits/2026-04-21/voice_prompt_injection_audit.md` — Voice guidance confirmed

**Session archives:**
- `validation_runs/2026-04-21/sessions/` — 50 complete session logs (10 sessions × 5 player approaches)
- Turn traces include full seam execution details
- Consistency check results for all turns

**Comparative baseline:**
- `validation_runs/2026-04-21/baseline_comparison.md` — WoS vs. generic chat metrics

### Evidence Quality Checklist
- [ ] Evaluator identities (names, no. of participants) are recorded
- [ ] Questions asked to evaluators are explicit (not paraphrased)
- [ ] Evaluator responses are verbatim or quoted (not interpreted)
- [ ] Code audits reference specific files/lines
- [ ] Metrics are defined (what was measured, how)
- [ ] Confidence intervals are provided (where applicable)
- [ ] Limitations are documented (what's outside scope)
- [ ] All evidence is machine-readable and reproducible

All evidence artifacts must pass this checklist.

---

## Acceptance Gate: Proof Discipline

Phase 4 closure requires:

1. **All architectural claims are source-traceable** — Every claim points to evidence
2. **Evidence is properly weighted** — Strong evidence (observable behavior) used for strong claims
3. **Unproven claims are flagged** — Future work is explicit; not aspirational
4. **No process narrative** — Documentation describes what works, not what was attempted
5. **No vague language** — All claims are specific and testable
6. **Evidence corpus is complete** — All validation runs, code audits, and evaluations are archived
7. **Metrics are defined** — No "feels immersive"; use testable criteria
8. **Comparative baseline exists** — WoS vs. generic chat metrics are recorded

All eight must be satisfied for Phase 4 sign-off.

---

## Proof Posture for Running Sessions

All running sessions maintain proof evidence:

**Every turn records:**
- Full seam execution details
- Consistency check results
- Any fallback or degradation
- Model latency and tokens
- Validation outcomes

**Every session records:**
- Complete turn log
- Final state snapshot
- Governance interventions (if any)
- Evaluation evidence (if this is evaluation session)

**All data is auditable:** Operators can reconstruct exactly what happened in any session.

This data becomes part of evidence corpus for future analysis/evaluation.

