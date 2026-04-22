# Task.md — Whole-System Runtime Authority, Narrative Coherence, and Governance Repair Plan

**Date:** 2026-04-22  
**Branch:** master  
**Scope:** Entire live narrative runtime, including frontend, backend, world-engine, administration surfaces, runtime authority path, structured output contracts, validation lanes, commit truth, routing semantics, diagnostics, and scene/beat continuity behavior.

---

## 1. Objective

Repair the runtime so it behaves as **one coherent, governable, operator-truthful narrative system**.

The implementation must eliminate authority splits, preserve planner truth into the persistent session record, harden routing and generation semantics, unify runtime output contracts, integrate real validation into the live turn path, and strengthen scene/beat continuity so the system functions as one whole rather than a set of partially connected subsystems.

This task is not a documentation pass.
This task is not a shallow seam fix.
This task is not complete until the live player turn path, governance surfaces, commit lane, schema lane, and validator lane all reflect the same runtime truth.

---

## 2. Core repair goals

### 2.1 Runtime authority
There must be one clear, truthful, live narrative authority lane.

The system currently contains multiple authority candidates or partially overlapping truth sources, including:
- repository content inputs,
- package or compiled narrative artifacts,
- loader state,
- graph runtime state,
- and live player-turn execution state.

These must be reconciled so that:
- the live turn path uses one canonical authority source,
- reload / promotion / rollback truly affect live runtime behavior,
- and operator surfaces truthfully report the active authority source.

### 2.2 Commit truth
The authoritative persistent narrative record must preserve the dramatic planner truth that the runtime used to validate and shape the turn.

Validation context, scene-function choices, responder scope, pacing/silence decisions, social state, character-mind signal, and other planner outputs must not disappear before the session record is written.

### 2.3 Routing and generation truth
Generation mode and route resolution must be explicit, truthful, governed, and visible.

The system must not silently:
- fall from live story generation into preview/research/writers-room routes,
- collapse distinct generation modes into one ambiguous hybrid,
- or use degraded/mock fallbacks without surfacing them clearly.

### 2.4 One output contract
There must be one canonical structured runtime output contract.

Parallel schema families, duplicate contracts, legacy field names, and orphaned JSON schema definitions must be unified or retired.

### 2.5 One live validator lane
The validation stack used for scope, legality, responder correctness, and corrective retry must participate in real live player turns.

Parallel or orphaned validation lanes that are not part of the canonical turn path must either be wired into the live runtime or formally retired.

### 2.6 Stronger narrative continuity
After authority, commit, routing, schema, and validator truth are stabilized, the runtime must strengthen:
- beat continuity,
- scene-function continuity,
- responder logic,
- social outcome continuity,
- character-mind continuity,
- retrieval continuity,
- and packaging/rendering continuity.

---

## 3. Required operating rules

1. **Do not trust docs, labels, or admin surfaces over active code.**  
   Live runtime behavior is the source of truth.

2. **Do not preserve authority splits.**  
   If package state, loader state, repository YAML, and live execution disagree, reconcile them.

3. **Do not preserve misleading diagnostics.**  
   If a surface claims a route, mode, authority source, or validation path that is not actually active, fix it.

4. **Do not treat “loaded” as “live.”**  
   A loaded package or runtime structure is not authoritative unless live player turns actually use it.

5. **Do not leave stale cache behavior unresolved.**  
   Reload / promotion / rollback must invalidate or version all caches that affect live dramatic behavior.

6. **Do not leave multiple live contracts in place.**  
   There must be one structured output contract.

7. **Do not hide degraded or fallback behavior.**  
   If fallback exists, it must be governed, surfaced, and truthfully labeled.

8. **Do not fake module generality.**  
   If the runtime is effectively module-specific, that scope must be made honest until broader support is truly implemented.

9. **Do not weaken tests to simulate success.**  
   Runtime proof must come from stronger implementation and truthful validation.

10. **Do not stop at local bug fixes.**  
    Repair the system-level handoffs, truth lanes, and missing integrations.

---

## 4. System summary to align implementation

The target system is:

- a governed live runtime,
- with one authoritative content/authority lane,
- one truthful route-resolution lane,
- one truthful generation-mode lane,
- one canonical structured output contract,
- one active validation lane used by real turns,
- one persistent commit lane that preserves planner truth,
- and one coherent packaging/rendering path that does not flatten away important narrative state.

The final system must be:
- operator-truthful,
- testable,
- explainable,
- and materially stronger as an integrated dramatic runtime.

---

## 5. Priority-ordered implementation waves

---

## Wave 0 — Governance / truth-surface surfacing

Implement the low-risk surfacing and truth-alignment fixes first.

### 0.1 Surface runtime execution truth
Expose at minimum:
- `runtime_graph_mode`
- `langgraph_available`
- `generation_execution_mode`
- active route family
- expected live route family
- whether fallback/degraded execution occurred
- actual authority source
- actual validator layers used
- actual prompt-template source
- commit-contract version
- schema-contract version or schema count

### 0.2 Surface hidden behavior-shaping defaults
Publish all materially behavior-shaping defaults used in live turns, including:
- opening leniency controls,
- commit strictness,
- pacing/silence heuristics,
- retrieval bounds,
- actor-mind selection bounds,
- continuity/history truncation bounds,
- and any hidden keyword or threshold lists still shaping behavior.

### 0.3 Fix false or misleading diagnostics
Correct any surface that currently:
- claims content authority is active when load failed,
- reports loader/package state as if it were live execution authority,
- hardcodes routing-policy or repro metadata that no longer matches live semantics,
- or hides the difference between intended route and actual route taken.

### 0.4 Log-safety hardening
Remove any secret leakage or partial credential printing from governed runtime setup, adapter construction, diagnostics, or startup logs.

**Acceptance for Wave 0**
- Operators can inspect the actual runtime mode, route, authority source, validator lane, and generation mode.
- Truth surfaces no longer misstate load success, routing semantics, or authority state.
- Logs no longer print secret material or secret prefixes.

---

## Wave 1 — Runtime authority reconciliation

This is the first structural repair wave.

### 1.1 Choose and enforce one canonical live authority source
Decide and implement one live authority lane for narrative runtime content and scene authority.

The decision must eliminate ambiguity between:
- raw repository content,
- compiled/package artifacts,
- loader state,
- and live graph/runtime authority.

### 1.2 Bind authority changes to live turns
Ensure that:
- reload,
- promotion,
- rollback,
- preview-vs-active switching,
- or other authority-changing operations

actually affect the canonical live player turn path.

### 1.3 Fix cache invalidation / stale authority state
Any authority source used by the live runtime must invalidate or version caches correctly.
No stale YAML/content authority may survive after the system claims a new active authority state.

### 1.4 Make runtime-state endpoints truthful
Any runtime-state or narrative-state endpoint must distinguish clearly between:
- loaded state,
- preview state,
- package state,
- cached state,
- and live player-turn authority state.

**Acceptance for Wave 1**
- There is one implemented live authority source.
- A reload/promotion/rollback changes real live runtime behavior.
- Cache invalidation is proven by test.
- Runtime-state endpoints no longer confuse loader/package state with live authority.

---

## Wave 2 — Commit-truth consolidation

This is the highest-value narrative repair after authority truth.

### 2.1 Extend the authoritative narrative commit record
The persistent turn/session record must preserve at minimum:
- selected scene function,
- responder scope / selected responder set,
- scene assessment core,
- pacing mode,
- silence/brevity mode,
- primary social state summary,
- character-mind summary,
- scene-plan reference,
- validation status,
- validation reason,
- dramatic effect gate result,
- emotional shifts,
- social outcome,
- dramatic direction,
- and any planner truth needed to explain why the turn was accepted and committed.

### 2.2 Pass graph/planner state into commit resolution
The commit resolver must receive the dramatic graph state it needs.
Do not derive the persistent record only from a narrow generation payload.

### 2.3 Preserve validation provenance
Whatever the validator used to approve or degrade a turn must remain visible in the committed truth.
Validation must not operate on richer state than the commit keeps.

### 2.4 Surface committed planner truth downstream
The committed-turn authority, story window, runtime diagnostics, and bounded shell/admin surfaces must be able to read the planner truth from the committed record.

**Acceptance for Wave 2**
- Planner truth used by validation survives into persistent session state.
- Commit records can explain accepted turns truthfully.
- Downstream surfaces no longer depend on ephemeral graph-only state for narrative truth.

---

## Wave 3 — Routing and generation hardening

### 3.1 Enforce distinct generation-mode semantics
Implement and verify distinct, truthful behavior for each supported generation mode.

In particular:
- modes that claim AI-only behavior must not silently use mock fallback,
- routed modes must not collapse into the same semantics as hybrid/degraded modes,
- and hybrid/fallback-capable modes must surface when degraded execution actually occurred.

### 3.2 Harden live route resolution
Live player story turns must not silently fall into unrelated route families.
If the required live route family is unavailable, fail explicitly or degrade in an operator-truthful governed way.

### 3.3 Make route reason truthful
Route reason metadata must distinguish:
- correct primary selection,
- governed fallback,
- degraded execution,
- missing live route,
- and invalid route-family substitution.

**Acceptance for Wave 3**
- Live story turns cannot silently leak into preview/research/writers-room routes.
- Generation modes behave distinctly and truthfully.
- Mock or degraded execution is operator-visible and governed.

---

## Wave 4 — Canonical schema unification

### 4.1 Define one structured output contract
Create one canonical runtime turn output model used by:
- generation parsing,
- validation,
- corrective retry,
- commit transformation,
- diagnostics,
- and rendering/packaging consumers.

### 4.2 Remove or retire parallel schema families
Unify or retire:
- legacy V1/V2-style contract drift,
- duplicate field families,
- orphaned schema definitions,
- and inconsistent responder field shapes.

### 4.3 Canonicalize actor/responder fields
Use one canonical field shape for responder selection, actor references, and scope validation.

### 4.4 Align parser and validator
The parser and validator must accept and validate the same model.
Do not maintain one schema for parsing and another for legality/scope validation.

**Acceptance for Wave 4**
- There is one canonical output contract.
- Legacy duplicate schemas are removed or formally retired.
- Parser, validator, commit, and downstream consumers all use the same structure.

---

## Wave 5 — Live validator lane integration

### 5.1 Integrate real validation into live turns
The live player turn path must use:
- scene packet / scene scope context,
- responder validity checks,
- trigger legality checks,
- state-effect legality checks,
- vocabulary validation,
- and corrective retry or safe fallback where appropriate.

### 5.2 Retire orphaned validator lanes
Any validation endpoint or runtime lane not used by the live path must be:
- integrated,
- demoted to operator introspection,
- or retired.

### 5.3 Publish validator-lane truth
Operators must be able to see which validator layers ran on a given turn.

**Acceptance for Wave 5**
- Real player turns go through the full intended validator lane.
- No parallel “real validator” remains orphaned outside the canonical path.
- Validator use is visible in diagnostics/truth surfaces.

---

## Wave 6 — Beat and dramatic continuity architecture

This wave begins only after authority, commit, routing, schema, and validator truth are stabilized.

### 6.1 Resolve beat/runtime architectural split
If the repository contains both:
- a legacy beat-aware runtime lane,
- and a newer canonical live path without equivalent beat continuity,

choose one explicit architecture and implement it.

### 6.2 Implement one canonical beat progression model
Whether legacy, hybrid, or newly consolidated, the runtime must have one committed dramatic continuity structure that persists across turns.

That continuity model must capture at minimum:
- beat or dramatic phase identity,
- beat slot / progression position,
- pressure state,
- pacing carry-forward,
- responder focus carry-forward,
- continuity carry-forward reason,
- and advancement reason.

### 6.3 Feed continuity back into director decisions
Beat/dramatic progression must shape:
- scene assessment,
- pacing/silence selection,
- responder selection,
- and next-turn model context.

### 6.4 Retire parallel beat runtime if not chosen
If one beat runtime lane is not adopted, formally retire it and update docs/truth surfaces accordingly.

**Acceptance for Wave 6**
- There is one explicit beat/dramatic continuity architecture.
- Continuity is persisted and reused across turns.
- The live path does not contain a silent split between legacy and canonical continuity logic.

---

## Wave 7 — Narrative strengthening after structural truth is fixed

### 7.1 Responder reconciliation
Reconcile director-selected responder sets with model-proposed responder fields.
The model must not introduce out-of-scope actors.

### 7.2 Character-mind truth
Replace hardcoded character-name selection logic with data-driven actor scope and scene authority.
Character-mind generation and selection must come from canonical scene/cast authority, not embedded fixed-name assumptions.

### 7.3 Social-state truth
Social-state computation must be validated, committed where needed, and reused across turns rather than remaining a prompt-only temporary feature.

### 7.4 Narrative thread feedback
Narrative-thread continuity must not be output-only.
It must feed back into scene assessment, pacing, and responder logic.

### 7.5 Retrieval strengthening
Retrieval should become continuity-aware and behavior-aware where required:
- actor precedents,
- responder precedents,
- function-type precedents,
- social outcome precedents,
- continuity pressure context.

### 7.6 Packaging and rendering coherence
Do not flatten rich upstream state into a narrow narration-only result.
Preserve bounded, truthful dramatic context for:
- operator/admin surfaces,
- story window,
- and limited player-safe shell surfaces where appropriate.

### 7.7 Honest module scope
If the runtime remains effectively module-specific, publish that honestly until broader module-general support is truly implemented.

**Acceptance for Wave 7**
- Character logic is data-driven rather than hardcoded.
- Social, responder, and thread continuity survive beyond prompt assembly.
- Packaging/rendering preserves more of the runtime’s real dramatic intelligence.

---

## 6. Required tests and proof

The implementation must add and/or run targeted tests covering at minimum:

### Runtime authority
- active authority source reaches the live player turn path,
- reload/promotion/rollback changes live authority,
- cache invalidation prevents stale authority behavior,
- runtime-state endpoints report live authority truthfully.

### Diagnostics and truth surfaces
- content-authority failure is reported truthfully,
- `generation_execution_mode` is surfaced,
- actual route family is surfaced,
- runtime graph mode is surfaced,
- repro/routing metadata matches active governed behavior,
- no secret material is printed in logs.

### Routing and generation
- routed modes do not silently use mock fallback when not allowed,
- live story turns do not fall into preview/research/writers-room families,
- degraded execution is surfaced truthfully.

### Commit truth
- committed planner truth is preserved,
- validation provenance survives into the committed record,
- downstream committed-turn authority includes dramatic planner fields.

### Schema and validation
- one canonical runtime output contract is used everywhere,
- responder scope validation works,
- scene packet / legality validation runs in live turns,
- orphan validator lanes are retired or demoted.

### Beat / continuity
- the chosen beat/dramatic continuity architecture is committed and reused,
- continuity state changes pacing and/or scene/director behavior across turns.

### Narrative strengthening
- character-mind selection is data-driven,
- non-supported module scope is rejected or reported honestly,
- packaging/rendering includes the intended bounded dramatic surfaces.

---

## 7. Required documentation updates

Update documentation only where implementation truth changed or drift was corrected.

At minimum, keep aligned:
- runtime architecture docs,
- governance/runtime-mode docs,
- commit contract docs,
- structured output contract docs,
- beat/dramatic continuity docs,
- and operator/admin truth-surface documentation.

Do not leave docs claiming:
- broader authority binding than exists,
- broader module generality than exists,
- broader validator coverage than exists,
- or routing semantics that no longer match code.

---

## 8. Acceptance criteria for task completion

This task is complete only when all of the following are true:

1. **One live narrative authority lane exists.**
2. **Reload/promotion/rollback truly affect live runtime behavior.**
3. **Truth surfaces report actual authority, route, validator lane, and generation mode.**
4. **The persistent commit record preserves dramatic planner truth.**
5. **One canonical output schema is used everywhere.**
6. **The real validator stack participates in live player turns.**
7. **Generation modes and route families behave distinctly and truthfully.**
8. **Degraded or fallback execution is governed and surfaced.**
9. **Beat/dramatic continuity has one explicit architecture and is committed across turns.**
10. **Character, social, responder, and narrative-thread continuity are materially stronger than before.**
11. **Packaging/rendering no longer flatten away most runtime intelligence.**
12. **Tests prove the live path now matches the claimed runtime truth.**

---

## 9. Remaining-risk handling

If a wave cannot be fully completed in one pass:
- finish the highest-priority structurally blocking portion,
- leave the repository in a consistent continuation-ready state,
- update this task only if implementation reality proves the order or wording was wrong,
- and document precisely what remains open.

Do not hide unfinished structural problems behind broad “partial success” language.

---

## 10. Continuation priority

If work must continue across multiple implementation passes, use this order:

1. Wave 0 — truth-surface and log-safety fixes  
2. Wave 1 — runtime authority reconciliation  
3. Wave 2 — commit-truth consolidation  
4. Wave 3 — routing and generation hardening  
5. Wave 4 — schema unification  
6. Wave 5 — live validator integration  
7. Wave 6 — beat/dramatic continuity architecture  
8. Wave 7 — deeper narrative strengthening

This order is deliberate.
Do not start deeper dramatic strengthening while authority, commit, route, schema, and validator truth are still structurally split.

---

## 11. Final implementation bar

The repository must move toward:

- one authority lane,
- one commit lane,
- one route/generation truth lane,
- one schema lane,
- one validator lane,
- and one coherent dramatic continuity lane.

Anything less is not whole-system coherence.