# ADR-0007 — Bounded emergent narration

**Decision status:** Accepted
**Implementation state:** Partial
**Owners:** AI Stack, World Engine, Content Authority
**Date:** 2026-08-11
**Violations:** `AR-V010`

## Context

The first God of Carnage runtime treated the numbered canonical path as both a dramatic reference
and a mandatory output program. Later free-action work stopped some player actions from advancing
the path, but left the current step as the compulsory dialogue and LDSS rendering template. The
player could act locally while the narrator repeatedly returned to a fixed script. That preserves
state consistency but does not create coherent, responsive drama.

## Decision drivers

- player action must be accepted wherever it is physically, socially and canonically valid;
- God of Carnage must retain its pressure, relationships, themes and recognizable dramatic arc;
- World Engine must remain the only live-state commit authority without becoming a prose author;
- scripted reenactment, bounded emergence and sandbox play must be selectable by module/profile;
- canonical material must not silently become a required line on an emergent player turn.

## Considered options

1. **Mandatory canonical spine for every turn.** Rejected as too rigid for interactive narration.
2. **Unbounded generative sandbox.** Rejected because it loses dramatic identity and canon safety.
3. **Configurable bounded emergence.** Accepted: committed state and hard invariants bound play;
   dramatic state selects the next pressure move; canonical steps remain reference opportunities.

## Decision

Each content module declares a versioned `narrative_governance_policy` with supported modes. The
runtime profile selects one active mode. In `bounded_emergence`:

- World Engine validates and atomically commits state; it does not choose prose or force a beat;
- the Director derives a `NarrativeMoveProposal` from player intent, committed dramatic state,
  responder state, continuity, pacing and module policies;
- canonical steps, quotes and mandatory beats are exposed as reference opportunities, not output
  obligations, on live player turns;
- hard world, actor-lane, access, safety and continuity invariants remain mandatory;
- an off-path action is absorbed into dramatic state and causes replanning rather than an
  automatic rejection or return to the same scripted line;
- opening/system turns may still use deterministic authored staging.

Unconfigured modules default to `reenactment` for compatibility. Adding a mode requires a declared
policy; engine code must not branch on a module ID.

## Consequences

The canonical path becomes one dramatic memory source among structured state sources. Dynamic
dramaturgy must carry enough evidence for validation and replay. Deterministic canonical LDSS
rendering is bypassed for bounded-emergence player turns; compatibility output must not reassert
the script after the Director has planned an emergent response.

## Implementation correspondence

| Target element | Current evidence | State | Closure evidence |
| --- | --- | --- | --- |
| Mode declaration | `content/modules/god_of_carnage/module.yaml#runtime_intelligence.narrative_governance` | Conforming | policy loader test |
| Profile selection | `runtime_profiles/god_of_carnage_solo.yaml#narrative_mode` | Conforming | profile override test |
| Canonical reference demotion | `semantic_scene_plan/content_frame.py::_apply_narrative_governance` | Implementing | bounded vs reenactment planner tests |
| LDSS compatibility boundary | `live_dramatic_scene_simulator.py::_run_canonical_ldss_path` | Implementing | mode-specific LDSS test |
| State-only commit authority | ADR-0001 and World Engine commit resolver | Partial | one-writer plus off-path scenario test |

## Git and AKDB lineage

Commit `fc3621578` introduced the rich free-role-play commit vocabulary and changed some blocked
actions to partial acceptance. It explains why free actions can commit while the scene remains
fixed; it does not prove emergent narration. AKDB canon exports this ADR, the linked violation and
the implementation bindings as the current repair target.
