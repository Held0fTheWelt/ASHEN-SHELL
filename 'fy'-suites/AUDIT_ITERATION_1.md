# Audit Iteration 1 — Initial State Assessment

**Date:** 2026-04-18  
**Scope:** `'fy'-suites/` only  
**Auditor:** Claude Audit Agent (fy v2 MVP readiness)

---

## Current State Findings

### Suite Ecosystem

**Suites found:** 19 suites organized by purpose

**Core governance suites (in README catalog):**
- `fy_platform/` — Shared portability primitives, workspace governance
- `contractify/` — Contract discovery, OpenAPI ↔ Postman drift
- `despaghettify/` — Structure checks, spike detection, wave planning
- `docify/` — Python docstring audit and synthesis
- `documentify/` — Multi-track documentation generation
- `postmanify/` — Postman collection refresh from OpenAPI
- `templatify/` — Template governance and validation
- `testify/` — Test consolidation and ADR reflection
- `dockerify/` — Container tooling
- `usabilify/` — UI/UX automation
- `securify/` — Security lane integration
- `observifyfy/` — Internal observability for fy-suites
- `mvpify/` — MVP bundle orchestration
- `metrify/` — AI usage and cost measurement

**Experimental/support suites:**
- `brokenify/`, `templatify/`, `usabilify/`, `observifyfy/` — newer additions
- `internal/` — Internal docs mirroring

**Architecture:**
- Platform-level code concentrated in `fy_platform/ai/` 
- Each suite follows pattern: `<suite>/{adapter/,tools/,tests/,superpowers/}`
- Shared entry point: `fy_platform/tools/ai_suite_cli.py` (suite-first CLI)
- Secondary orchestration CLI: `fy_platform/tools/cli.py` (platform governance commands)

**Current structure:** Suite-first, not platform-first. Suites are primary runtime units; platform is support layer.

---

### Test Baseline

**Current status:** ✓ **75 tests passing** (pytest -q, 202.48s runtime)  
- Repository is stable and green
- Adequate baseline for transition work

---

## Against Task_Audit.md Gap Assessment

### Gap 1: Platform-first vs suite-first surface

**Finding:**  
- **Current primary entry:** `fy_platform/tools/ai_suite_cli.py` — takes `suite + command` signature
- **Secondary entry:** `fy_platform/tools/cli.py` — has platform commands (`bootstrap`, `status`, `doctor`, `release`, etc.)
- **Desired:** Platform-shaped surface like `fy analyze --mode contract`, `fy govern --mode release`
- **Reality:** No platform-mode entry surface exists yet. Suites are still the primary unit, platform is support.

**Risk level:** **Critical** — This is the foundation-layer blocker. Without a platform-shaped CLI shell, the fy v2 transition cannot credibly begin.

**Blocker?** **Yes** — The entire fy v2 foundation premise is that a platform-first technical surface emerges, not that suite-first CLI is enhanced. This must be built first.

---

### Gap 2: Shared core concentration

**Finding:**  
- `fy_platform/ai/base_adapter.py` — **exactly 700 lines** (matched audit expectation)
- **Responsibilities merged:** initialization, workspace wiring, status page attachment, governance wiring, inspect/explain/triage/context-pack flow orchestration, run lifecycle, payload bundle writing, storage
- **Current state:** Heavy shared adapter is real; every suite inherits from it
- **Structural hotspot risk:** Medium-to-high. Not yet the place where fy v2 gets stuffed, but at critical decision point.

**Risk level:** **High** — The base adapter is already on the boundary of acceptable concentration. It will absorb fy v2 transition logic if no explicit lane runtime exists.

**Blocker?** **No** — Can be addressed *after* platform shell exists, as part of first core-thinning wave.

---

### Gap 3: Explicit lane runtime

**Finding:**  
- `fy_platform/ai/graph_recipes/` exists with 5 lightweight recipe files:
  - `audit_graph.py`, `context_pack_graph.py`, `inspect_graph.py`, `recipe_base.py`, `triage_graph.py`
- **Reality:** These are thin wrappers around command orchestration, not real lane-based runtime
- **Missing:** Explicit `inspect`, `govern`, `generate`, `verify`, `structure` lane modules as real execution units

**Risk level:** **High** — Without explicit lanes, the new platform CLI will simply delegate to suite adapters without creating a real internal seam for fy v2 to stand on.

**Blocker?** **Yes** — A minimal explicit lane runtime must be created alongside the platform shell. This is a load-bearing foundation piece.

---

### Gap 4: Minimal shared IR

**Finding:**  
- `fy_platform/ai/contracts.py` — minimal 988-line schemas file (just basic type hints)
- **Missing objects:** `ContractProjection`, `TestObligation`, `DocumentationObligation`, `SecurityRisk`, `StructureFinding`, `EvidenceLink`, `DecisionRecord`
- **Current IR strategy:** Vague envelopes and schemas, no typed transition IR
- **Reality:** No minimal shared IR seed for fy v2 transition yet

**Risk level:** **Critical** — Without explicit IR, the platform shell will remain a command router without a coherent transition story. Suites will continue to emit incompatible outputs.

**Blocker?** **Yes** — Minimal IR must be created as part of the foundation pass. This is what makes the transition real, not rhetorical.

---

### Gap 5: Deterministic-first enforcement

**Finding:**  
- `fy_platform/ai/model_router/` exists with policy-shaped routing
- **Reality:** Policy exists but is not enforced as a gate. No deterministic pre-pass before model escalation.
- **Current stage:** Deferred from fy v2 foundation priority

**Risk level:** **Medium** — Important for fy v2 quality, but not load-bearing for foundation slice.

**Blocker?** **No** — Can follow after platform shell and lane runtime are real.

---

### Gap 6: Metrify as governor

**Finding:**  
- `metrify/adapter/service.py` is reporting-oriented, not enforcement-oriented
- **Reality:** Metrify measures but does not gate. No hard policy enforcement.

**Risk level:** **Medium** — Valuable later, but not foundation-blocking.

**Blocker?** **No** — Can follow lane runtime stabilization.

---

### Gap 7: Cross-suite intelligence depth

**Finding:**  
- `fy_platform/ai/cross_suite_intelligence.py` exists (3622 lines)
- **Reality:** Still relies on static related-suite maps, not a typed dependency/influence graph
- **Current capability:** Basic suite awareness, not real dependency tracing

**Risk level:** **Low-to-Medium** — Useful for fy v2 maturity, but not foundation-blocking.

**Blocker?** **No** — Can follow IR implementation.

---

### Gap 8: Despaghettify as transition stabilizer

**Finding:**  
- Current implementation: Detects file/function spikes, emits wave plan (simple spike detector)
- **Missing:** Does NOT inspect fy shared core itself. Does NOT detect over-splitting, wrapper proliferation, re-fattening, unstable glue, low-cohesion extraction.
- **Reality:** Useful for general structure audit, but not yet a platform transition guardian

**Risk level:** **High** — Without transition-aware despaghettify, the platform can fragment itself during thinning waves without feedback.

**Blocker?** **Yes** — Despaghettify must gain a transition-stabilization mode as part of the foundation pass. This is how the platform self-corrects during evolution.

---

## Overall Assessment

### fy v2 Foundation Readiness: **NOT READY**

The repository is **stable and coherent** (75 tests passing, good shared platform base), but the fy v2 transition cannot land as a single pass. The following **critical blockers** prevent implementation-readiness:

1. **No platform-shaped CLI shell** — Suites are still primary; platform remains support
2. **No explicit lane runtime** — graph_recipes are wrappers, not real execution units
3. **No minimal shared IR** — Transition lacks a coherent typed object model
4. **Despaghettify not yet a transition stabilizer** — Cannot guard against platform fragmentation

### Test Baseline
✓ 75 tests passing  
✓ Repository is green and stable for transition work

---

## Next Target Selection

### Selected Target

**fy v2 foundation pass: platform entry shell + minimal lane runtime + transition IR seed + despaghettify stabilization + first core-thinning wave**

This is the **single highest-leverage next slice** because it:

1. **Opens fy v2 transition:** Introduces real platform-shaped technical surface (not just renamed suite CLI)
2. **Reduces structural risk:** Explicit lanes prevent base_adapter bloat; IR prevents output chaos
3. **Preserves compatibility:** Legacy suite CLI stays alive; existing code paths unchanged
4. **Enables despaghettify cleanup:** As platform evolves, despaghettify actively prevents fragmentation
5. **Proves transition is real:** Not documentation, not renaming — tangible new runtime structure

### Why Other Targets Wait

- **Full metrify governor:** Better after lanes exist; no execution seam for policy yet
- **Typed dependency/influence graph:** Better after minimal IR exists; current static approach is adequate foundation base
- **Broader suite consolidation:** Better after platform modes are real and compatible

---

## Implementation Prompt for Next Agent

Your task is **not** to implement all of fy v2. Your task is to implement the **foundation slice that makes fy v2 technically real and compatible**.

### What you must implement

**Outcome:** A real platform-shaped CLI shell + minimal lane runtime + transition IR + despaghettify upgrade + one core-thinning wave

1. **Platform CLI shell** — New entry surface supporting commands like:
   - `fy analyze --mode contract`
   - `fy analyze --mode docs`
   - `fy govern --mode release`
   - `fy inspect --mode structure`
   - `fy repair-plan --mode structure`
   - Must be real, not documentation-only
   - Legacy suite CLI must remain compatible

2. **Minimal explicit lane runtime** — Real modules for:
   - `inspect` lane
   - `govern` lane
   - `generate` lane
   - `verify` lane
   - `structure` lane
   - May delegate to existing adapters internally; the seam itself must be real and testable

3. **Minimal shared fy v2 transition IR** — Typed object model with:
   - `Contract`
   - `ContractProjection`
   - `TestObligation`
   - `DocumentationObligation`
   - `SecurityRisk`
   - `StructureFinding`
   - `EvidenceLink`
   - `DecisionRecord`
   - Use style consistent with repo (dataclasses acceptable)
   - At least one or two flows must emit/consume these objects

4. **Despaghettify transition stabilization** — Upgrade despaghettify to:
   - Audit the fy shared core itself (not just user code)
   - Emit wave plan for shared-core cleanup
   - Detect transition risks: over-splitting, wrapper proliferation, low-cohesion extraction, unstable glue, re-fattening
   - Provide feedback to platform evolution process

5. **First core-thinning wave** — One real extraction from `fy_platform/ai/base_adapter.py`:
   - Extract mechanical responsibilities (run lifecycle helpers, payload bundle writing, etc.)
   - Prove shared core becomes less concentrated
   - Preserve all behavior
   - No random wrapper explosion

6. **Tests prove stability** — Add tests for:
   - New platform shell works
   - Legacy suite CLI still works
   - New lanes are real and callable
   - Despaghettify transition mode works
   - Core-thinning wave did not break baseline

### Implementation constraints

**Do NOT:**
- Try to finish all fy v2 phases
- Fake platform progress with docs alone
- Create wrapper explosion making platform more fragmented
- Break current suite-first UX
- Implement full influence graph just to mention it

**Do:**
- Prefer small, composable, testable modules
- Preserve backward compatibility
- Make transitional seams explicit
- Keep the foundation slice honest and narrow
- Return **entire updated archive** with implementation report, changed-files list, and test results

---

## Re-audit Criteria (Iteration 2)

When implementation returns, re-audit must verify:

### Pass Criteria (all must be true)
1. **Real platform CLI exists** — Not documented, actually runnable commands like `fy analyze --mode contract`
2. **Legacy suite CLI still works** — Backward compatibility proven via tests
3. **Real explicit lanes exist** — Modules you can import and test, not just prose
4. **Real minimal IR exists** — Typed objects flowing through at least one or two real code paths
5. **Despaghettify audits platform itself** — Can inspect fy_platform/ai/ and emit transition guidance
6. **One core-thinning wave landed** — Real extraction from base_adapter.py, measurable reduction in concentration
7. **Tests prove slice works** — No red tests, compatibility demonstrated
8. **Repository more coherent, not more fragmented** — Line counts down, no glue explosion

### Partial Pass Criteria
If direction is correct but 1 piece weak:
- Platform shell is real but lanes are thin
- IR exists but not flowing through flows yet
- Despaghettify upgraded but not platform-aware yet
- Core-thinning incomplete but directionally sound

→ **Re-audit decision:** Repair prompt targeting only the weak piece

### Fail Criteria
If any of these is true:
- Fake "platform shell" that is just renamed suite CLI
- New IR that is decorative, not actually used
- Wrapper explosion making platform more fragmented
- Core-thinning wave increased base_adapter concentration
- Tests red or compatibility broken

→ **Re-audit decision:** Corrective prompt to re-center on narrowest missing foundation

---

## Outcome Decision Framework (After Iteration 2)

### Outcome A — Pass and Advance
If foundation slice is fully delivered: Choose next highest-leverage target
- Deterministic-first enforcement + metrify governor
- Typed dependency/influence graph
- Broader platform mode coverage
- Second core-thinning wave

### Outcome B — Partial Pass, Repair
If direction correct but pieces weak: Narrow repair prompt for missing parts only

### Outcome C — Fail, Re-center
If implementation broadened or faked: Corrective prompt to refocus on narrowest blocker

---

## Summary

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Platform-first CLI | **Missing** | Suite-first entry at ai_suite_cli.py is primary; cli.py lacks --mode pattern |
| Explicit lanes | **Missing** | graph_recipes are command wrappers, not real execution units |
| Minimal shared IR | **Missing** | contracts.py is 988 lines but lacks transition IR objects |
| Despaghettify stabilizer | **Missing** | Only simple spike detection; cannot audit platform itself |
| Core-thinning wave | **Not started** | base_adapter.py still at full 700 lines, undivided |
| Test baseline | **Green** | 75 tests passing; foundation solid for transition work |

**Next step:** Implementation agent executes foundation pass prompt. Results will be re-audited in Iteration 2.

