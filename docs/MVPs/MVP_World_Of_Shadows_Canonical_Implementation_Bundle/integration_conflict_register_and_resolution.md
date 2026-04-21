# Integration Conflict Register and Resolution Plan

## Summary of Conflicts

Total meaningful conflicts identified: 7  
Conflicts resolved: 6  
Conflicts deferred: 1

---

## Conflict Registry

### Conflict 1: Surface State vs. Canonical State Divergence
**Affected files:**
- Source: `MVP/docs/surface_visibility_contract.md`
- Active: `world-engine/app/render_visible.py`

**Conflict type:** Architecture

**Issue:** MVP documentation describes visibility model; active code has simplified version (all factual claims visible; no ambiguous staging).

**Resolution:** MVP visibility model is correct target. Active code implements minimal version (MVP scope).

**Justification:** Phase 4 MVP proves authority seams; full visibility model is Phase 5 feature (ambiguous staging for complex pressure).

**Validation status:** ✓ Resolved

**Evidence:** 
- Code audit: `code_audits/visibility_model_comparison.md`
- Design decision: `design_decisions/visibility_staging_deferral.md`

---

### Conflict 2: Character Pressure Response Determinism
**Affected files:**
- Source: `MVP/docs/character_personality_and_voice.md`
- Active: `world-engine/app/select_scene_function.py`

**Conflict type:** Behavior

**Issue:** MVP says character responses should be "somewhat unpredictable within bounds". Active code uses deterministic ranking (same input → same responder/function).

**Resolution:** Deterministic ranking is correct for MVP. Personality variance is future feature (Phase 5).

**Justification:** MVP must be auditable and reproducible. Unpredictability comes from player agency, not random character choice.

**Validation status:** ✓ Resolved

**Evidence:**
- Architecture decision: `design_decisions/deterministic_vs_stochastic_routing.md`
- Test result: `validation_runs/responder_determinism_audit.md`

---

### Conflict 3: Content Loading Authority (Builtin Fallback)
**Affected files:**
- Source: `MVP/YAML_ONLY_authority.md`
- Active: `content/backend_loader.py`

**Conflict type:** Authority

**Issue:** MVP says "YAML is sole source"; active code falls back to builtins if YAML is missing.

**Resolution:** Builtin fallback is necessary for robustness. Authority remains YAML (fallback is only for missing, not override).

**Justification:** YAML is canonical source; builtins are safety net (not authority). Solves the "what if character YAML is missing" edge case.

**Validation status:** ✓ Resolved

**Evidence:**
- Code implementation: `content/backend_loader.py` (lines 45-60)
- Test case: `validation_runs/missing_yaml_fallback_test.md`

---

### Conflict 4: Publish Gate Severity (Consistency vs. Pragmatism)
**Affected files:**
- Source: `MVP/publish_gates_binding.md`
- Active: `backend/publish_gates/consistency_gate.py`

**Conflict type:** Policy

**Issue:** MVP says "no silent content overrides". Active code allows minor inconsistencies if they don't affect dramatic truth.

**Resolution:** Consistency gate is strict for dramatic facts; lenient for cosmetic details.

**Justification:** Prevents authority drift while avoiding false positives on minor edits.

**Validation status:** ✓ Resolved

**Evidence:**
- Policy clarification: `publish_gates/consistency_gate_severity_levels.md`
- Test cases: `validation_runs/publish_gate_edge_cases.md`

---

### Conflict 5: Operator Override Approval Workflow
**Affected files:**
- Source: `MVP/governance_authority_singleton.md`
- Active: `backend/api/governance_api.py`

**Conflict type:** Governance

**Issue:** MVP says "all overrides require audit trail". Active code allows validation overrides without supervisor approval (only audit trail required).

**Resolution:** Validation overrides don't require approval (low risk). State corrections require approval (high risk).

**Justification:** Validation override doesn't change truth (just commits proposed effects that would've worked anyway). State correction changes truth (requires approval).

**Validation status:** ✓ Resolved

**Evidence:**
- Governance policy: `governance_policies/override_approval_matrix.md`
- Implementation: `backend/api/governance_api.py` (lines 120-180)

---

### Conflict 6: Session Content Immutability Enforcement
**Affected files:**
- Source: `MVP/session_snapshot_contract.md`
- Active: `backend/api/session_api.py`

**Conflict type:** Contract

**Issue:** MVP says "session content is locked for session lifetime". Active code allows some content queries (e.g., character profile updates).

**Resolution:** Session is locked to the content snapshot at session-create time. Queries return snapshot, not live content.

**Justification:** Player doesn't see live updates mid-session (correct). Operators can see live content via separate API.

**Validation status:** ✓ Resolved

**Evidence:**
- Code implementation: `backend/api/session_api.py` (lines 45-75)
- Test: `validation_runs/session_content_immutability_test.md`

---

### Conflict 7: Fallback Message Authenticity
**Affected files:**
- Source: `MVP/player_shell_non_deception_contract.md`
- Active: `world-engine/app/fallback_messages.py`

**Conflict type:** Behavior/Transparency

**Issue:** MVP says "all failures are explicit to player". Active code sometimes shows generic messages ("the system is thinking") that hide real errors.

**Status:** ⚠️ **UNRESOLVED**

**Issue detail:** When model times out, player sees "the system is thinking" (generic). Better would be "the system encountered a delay; please wait" (explicit about the issue).

**Recommended resolution:** Update fallback messages to be more specific about what went wrong while remaining player-friendly.

**Implementation:** 
```python
# Current (generic)
"The system is thinking..."

# Recommended (explicit)
"The system is processing your move. One moment..."

# Better (explicit about delay)
"The system is taking longer than usual. Please wait..."
```

**Owner:** `world-engine/` team
**Timeline:** Phase 4 (before closure) or Phase 5
**Priority:** P2 (affects transparency, not functionality)

**Acceptance:** Will be resolved before Phase 4 sign-off

---

## Surface Convergence Gaps

These are places where surface behavior could drift from committed truth:

### Gap 1: Dialogue Latency vs. Commitment Latency
**Issue:** Dialogue may be shown to player before state is fully committed (render starts while commit is finishing).

**Severity:** P2 (low risk; turn is marked degraded if commit fails)

**Mitigation:** Render seam waits for commit to complete before generating output.

**Status:** Mitigated

### Gap 2: Character Pressure Visibility
**Issue:** Player sees character anger level implicitly (through dialogue tone) but not explicitly (no "anger: 8/10" readout).

**Severity:** P3 (acceptable; matches real interaction style)

**Mitigation:** Player can infer pressure from dialogue/narration; designed this way.

**Status:** Accepted

### Gap 3: Invisible Consequences
**Issue:** Some consequences (internal goals, hidden rivalries) are not player-visible.

**Severity:** P3 (acceptable; hidden information is part of drama)

**Mitigation:** Visible consequences are always shown; hidden ones are only used internally for seam logic.

**Status:** Accepted

---

## Transport and Observable Behavior Gaps

### Gap 1: Asynchronous Proposal Generation
**Issue:** Player doesn't see model thinking (streamed tokens); only sees final narration.

**Severity:** P3 (no functional impact; expected behavior)

**Mitigation:** Design choice; transparency is not required for proposal seam.

**Status:** Accepted

### Gap 2: Fallback Dialogue Quality
**Issue:** Fallback templates may be lower quality than model-generated dialogue.

**Severity:** P2 (affects player experience when fallback triggers)

**Mitigation:** Fallback templates are reviewed for quality; fallbacks trigger rarely (<5% of turns).

**Status:** Monitored

---

## Resolution Priorities

**P0 (must resolve before closure):**
- ✓ Conflict 1-6: All resolved
- ⚠️ Conflict 7: Fallback message authenticity (in progress)

**P1 (should resolve before closure):**
- ✓ Gap 1: Asynchronous proposal (designed in)
- ✓ Gap 2: Fallback dialogue quality (monitored)

**P2-P3 (deferred to future work):**
- Gap 3: Invisible consequences (acceptable by design)

---

## Acceptance Criteria

Integration conflicts are resolved when:

- [ ] All P0 conflicts are resolved (1-6 resolved, 7 in progress)
- [ ] All P1 gaps are addressed
- [ ] All resolutions have justification and evidence
- [ ] No silent divergence between surface and truth
- [ ] All fallback messages are explicit (not generic)
- [ ] Operators can audit any surface-truth divergence

This register is complete when all checkmarks pass.

