# fy v2 MVP — Platform Compiler Transition with Despaghettify Stabilization

## Purpose

This MVP is **not** just a core-thinning exercise.
It is the first serious transition from **a family of semi-autonomous suites** toward **one deterministic analysis and transformation platform with domain lenses, optional AI lanes, and staged internal cleanup**.

It directly implements the stronger strategic direction:

1. stop treating fy-suites primarily as many technical tools,
2. move toward a shared platform with domain modes and common lanes,
3. introduce a compiler-style processing model with a shared intermediate representation,
4. enforce deterministic pre-processing before any model invocation,
5. turn metrify into a governor instead of a passive reporter,
6. replace static suite relationships with a typed dependency and influence graph,
7. thin and simplify the shared core,
8. let despaghettify actively reduce existing structural debt while the new platform shape is assembled,
9. make templating the default output path,
10. gradually reduce visible fragmentation without losing internal specialization.

This MVP exists to create a **credible, testable, cost-aware transition path**.
It must improve the system while it is being re-assembled, rather than letting the architecture drift or splinter during the transition.

---

## Core Thesis

The reified "suite family" has value as a governance and communication model, but it is too expensive as the **primary technical unit**.

The more mature architecture is:

- one shared platform,
- multiple domain lenses,
- common execution lanes,
- common artifact and policy machinery,
- shared intermediate representation,
- optional AI lanes only where deterministic processing cannot resolve the task,
- and despaghettify acting as an internal structural governor during the transition.

So the system should increasingly behave like:

```bash
fy analyze --mode contract
fy analyze --mode docs
fy generate --mode report
fy govern --mode release
fy inspect --mode quality
fy repair-plan --mode security
```

rather than continuing to grow as many semi-independent tool personalities.

The suite names may remain as **domain lenses** or **product-facing vocabulary**, but they should stop being the dominant technical boundary.

---

# MVP Goals

## Primary Goal

Create the first platform-shaped fy runtime that can execute shared lanes across multiple domain modes while keeping the system stable and reducing existing core structural debt.

## Secondary Goal

Use `despaghettify` from day one as an **active internal cleanup and anti-fragmentation mechanism**, not just as a report generator for external repositories.

## Tertiary Goal

Establish the minimum shared architecture required for a future fy v2 migration without forcing a full rewrite.

---

# What This MVP Must Prove

This MVP should prove all of the following:

1. fy can operate as a **shared platform** rather than only as a set of suite-specific entry points.
2. a **lane-based execution model** can be introduced without breaking the existing suite ecosystem.
3. a **minimal shared IR** can represent the most important analysis outputs across multiple domains.
4. deterministic pre-processing can reduce unnecessary AI work.
5. `metrify` can become a policy gate for AI execution.
6. `despaghettify` can reduce structural debt in stages while the transition is in progress.
7. the shared core can become **smaller and dumber**, not bigger and more magical.
8. the transition can be made without letting the system drift into a fragmented half-state.

---

# Strategic Position

## Today

The current architecture already shows:

- a strong shared core,
- recurring adapter patterns,
- recurring report and artifact patterns,
- recurring status/run/registry/journal logic,
- deterministic building blocks,
- suite-specific wrappers around a lot of common mechanics.

## Problem

That means the architecture is currently paying the cost of:

- repeated suite-facing mechanics,
- repeated command and adapter framing,
- repeated readiness/status/report logic,
- weaker cross-domain coupling than the structure could support,
- a growing risk that the shared core becomes a "mega-adapter" system.

## Direction

The MVP should not simply add more suites or more wrappers.
It should begin turning fy into a:

- deterministic development analysis machine,
- shared transformation platform,
- compiler-like processing system,
- optional AI-enhanced synthesis system,
- and self-governing architecture that uses despaghettify to keep itself under control.

---

# Architecture Principles for the MVP

## 1. Suites become domain lenses, not primary technical units

Keep names like `contractify`, `testify`, `documentify`, `docify`, `securify`, `despaghettify`, `metrify`, and `templatify`.

But internally move toward:

- shared platform lanes,
- shared policies,
- shared IR,
- shared artifact rules,
- shared observability and metrics,
- shared execution flow.

The suite names continue to matter for:

- human communication,
- governance framing,
- capability segmentation,
- staged migration.

But they should not remain the primary technical decomposition forever.

---

## 2. The system should behave like a compiler

The better architecture is a multi-stage compiler for development knowledge.

### Inputs

- repository code
- tests
- documentation
- templates
- contracts
- policies
- security signals
- usage and run history
- existing artifacts

### Intermediate Representation

The MVP introduces a small but real shared IR layer based on typed objects.

### Outputs

- reports
- fix plans
- status bundles
- review bundles
- readiness decisions
- human-facing documentation
- machine-facing actions

This means the core unit of work shifts from "suite writes a file" toward "platform transforms evidence through typed stages".

---

## 3. Deterministic work happens first, always

No model invocation is allowed before the cheap and reproducible work has been done.

The required processing order is:

1. inspect
2. normalize
3. parse
4. diff
5. match
6. rank
7. only then escalate if ambiguity or synthesis demand remains

That means:

- trivial classification must not hit an LLM,
- standard report drafting must not hit an LLM,
- raw extraction must not hit an LLM,
- known structured transformations must not hit an LLM.

The model lanes are reserved for:

- synthesis,
- ambiguity resolution,
- conflict reasoning,
- cross-object prioritization,
- audience-sensitive explanation,
- recovery when deterministic evidence remains incomplete.

---

## 4. Metrify must govern, not merely observe

`metrify` must become the policy checkpoint for all AI usage.

Every model call should be forced through rules such as:

- does this task truly require an SLM or LLM?
- is there a valid cache hit?
- does equivalent evidence already exist?
- has the deterministic path already been exhausted?
- is expected utility high enough?
- is the budget still available for this lane?
- is the task inside permitted risk and quality thresholds?

That turns cost control into architecture instead of after-the-fact reporting.

---

## 5. Despaghettify must stabilize the transition while it is happening

This is a mandatory part of the MVP.

`despaghettify` must not only diagnose the existing problems.
It must help clean them up **in staged waves** while the new shared platform is assembled.

The key requirement is:

> The system must improve while it is being recomposed, and must not fall apart into a fragmented in-between state.

That means `despaghettify` must serve three roles simultaneously:

1. **Debt detector** — identify oversized files, mixed responsibilities, fragile glue zones, repeated local patterns, and misplaced logic.
2. **Wave planner** — define staged extraction and simplification plans.
3. **Anti-fragmentation guard** — prevent the new architecture from scattering responsibilities into uncontrolled shards.

So `despaghettify` is not merely about file splitting.
It is about **controlled simplification under active transition**.

---

# MVP Structural Model

## New Platform Shape

### External Shape

The system begins to expose platform-style commands, while legacy suite entry points remain temporarily compatible.

Examples:

```bash
fy analyze --mode contract
fy analyze --mode test
fy analyze --mode docs
fy analyze --mode security
fy generate --mode report
fy generate --mode documentation
fy govern --mode release
fy govern --mode production
fy inspect --mode structure
fy inspect --mode quality
fy repair-plan --mode structure
```

### Internal Shape

Internally, processing moves toward:

- shared lanes,
- shared IR,
- shared policy gates,
- shared artifact emission,
- shared metrics and observability,
- shared anti-spaghetti enforcement.

---

# Lane Architecture for the MVP

The MVP introduces explicit lanes.

## Required Lanes

### Inspect Lane
Collect repository and artifact evidence.

### Normalize Lane
Normalize evidence into stable representations.

### Govern Lane
Apply policy, readiness, and structural rules.

### Generate Lane
Produce reports, docs, and bundles.

### Verify Lane
Check consistency, coverage, completeness, and structural validity.

### Explain Lane
Produce human-facing synthesis only where needed.

### Repair-Plan Lane
Produce staged change plans when real remediation is needed.

### Structure Lane
Reserved for `despaghettify`-driven structural inspection and decomposition guidance.

---

# Shared Intermediate Representation (MVP Scope)

The MVP does **not** need a huge IR.
It needs a small, high-value one.

## MVP IR Object Types

### `Contract`
A governed system contract or expectation.

### `ContractProjection`
A concrete surface derived from or reflecting a contract.

### `TestObligation`
A test expectation tied to a contract, change, or risk.

### `DocumentationObligation`
A documentation duty implied by a change or governed area.

### `SecurityRisk`
A risk, exposure, or hygiene issue with severity and scope.

### `TemplateAsset`
A reusable output template or schema-linked rendering unit.

### `ReadabilityIssue`
A human-facing clarity or usability problem.

### `StructureFinding`
A despaghettify-origin finding about architectural or local structural debt.

### `EvidenceLink`
A provenance link between objects and source evidence.

### `RepoChange`
A normalized change object.

### `DecisionRecord`
A platform decision or governance outcome.

---

# Dependency and Influence Graph

The MVP replaces shallow static suite relations with typed influence edges.

## Required Edge Types

- `depends_on`
- `informs`
- `validates`
- `projects_to`
- `conflicts_with`
- `blocks`
- `improves`
- `requires_review_from`
- `supersedes`
- `stabilizes`

This allows the platform to reason about downstream effects such as:

- a contract change producing test obligations,
- a structure change invalidating documentation,
- a security decision forcing documentation updates,
- a new artifact making an older report obsolete,
- a despaghettify extraction wave requiring re-verification of adjacent outputs.

---

# Despaghettify in This MVP

This is one of the defining features of the MVP.

## Despaghettify Mission in the MVP

`despaghettify` must actively help the platform transition without collapse.

It should do this in **stages**.

### Stage A — Baseline and pressure map

Detect current structural debt in the shared core and surrounding platform zones.

Focus areas include:

- oversized shared files,
- mixed responsibility modules,
- adapter overreach,
- hidden fallback behavior,
- repeated orchestration fragments,
- files that mix IO, policy, rendering, and flow control,
- unstable glue zones between existing suites and the shared platform.

### Stage B — Guided extraction waves

Generate extraction waves that are intentionally **small, ordered, and reversible**.

Each wave should define:

- target module or responsibility,
- why it should move,
- where it should move,
- what tests must hold,
- what artifacts might change,
- what influence edges are affected,
- what must be verified after the extraction.

### Stage C — Anti-fragmentation enforcement

This is crucial.

When parts of the system are split out, `despaghettify` must verify that the result is not becoming a random collection of tiny files and weak glue.

It should explicitly detect:

- over-splitting,
- meaningless wrapper proliferation,
- service scattering,
- low-cohesion extraction,
- duplication caused by premature splitting,
- newly created unstable glue points.

### Stage D — Ongoing structural gate

Once the first cleanup waves land, `despaghettify` becomes a standing platform hygiene gate.

It should guard:

- max file size for shared-core hotspots,
- mixed responsibility density,
- unnecessary branching growth,
- repeated helper patterns,
- accidental re-fattening,
- decomposition without ownership clarity.

---

# Anti-Fall-Apart Requirement

The user requirement is explicit and must be honored:

> despaghettify must clean up in stages while the rest assembles and the system must not fall apart.

So the MVP must include a structural stability rule set.

## Required Stability Rules

### Rule 1 — No uncontrolled splitting

A large module may only be split if the resulting pieces have clear ownership and stable boundaries.

### Rule 2 — No parallel architecture drift

New platform lanes and legacy suite pathways may coexist temporarily, but they must not diverge into incompatible behavior.

### Rule 3 — No glue explosion

The number of coordination-only wrappers and pass-through helpers must be constrained and measured.

### Rule 4 — No refactor without verification

Each extraction wave must define the tests, artifact checks, and regression checks that prove the move is safe.

### Rule 5 — Core must get thinner overall

The total shared-core complexity must trend downward across waves.
A split that merely redistributes confusion is not a valid success.

### Rule 6 — Transitional seams must be explicit

Where temporary compatibility layers remain, they must be visible and bounded.
They must not become hidden permanent residue.

---

# Templatify in This MVP

`templatify` should become the default rendering backbone for standard outputs.

The rule is:

- structured data first,
- output schema second,
- template resolution third,
- optional model-assisted prose only when needed.

That means:

- standard reports should be template-led,
- standard readiness summaries should be template-led,
- standard migration wave plans should be template-led,
- standard review packs should be template-led.

This reduces cost and increases consistency.

---

# Evidence Economy (MVP Form)

The MVP introduces basic artifact valuation.

Each major artifact should carry or be derivable with:

- `confidence`
- `freshness`
- `scope_relevance`
- `downstream_utility`
- `replacement_cost`
- `conflict_risk`

This allows the platform to decide whether to:

- reuse,
- refresh,
- supersede,
- discard,
- escalate for human review,
- or block a model call because existing evidence is already sufficient.

---

# The Shared Core Must Get Smaller and Dumber

This is still mandatory.

The shared core should be limited toward responsibilities such as:

- run orchestration,
- artifact IO,
- governance hooks,
- policy evaluation,
- dependency resolution,
- lane coordination.

It should **not** keep accumulating:

- suite-specific heuristics,
- text-heavy rendering logic,
- ad hoc branching,
- hidden fallback behavior,
- mixed responsibility helpers.

`despaghettify` is responsible for helping enforce this through staged cleanup.

---

# MVP Phases

## Phase 0 — Baseline Freeze and Structural Pressure Mapping

### Goal
Freeze the current state and produce a serious map of shared-core and transition risk.

### Deliverables
- baseline structural report
- baseline despaghettify report on shared-core hotspots
- initial lane mapping proposal
- initial anti-fragmentation rule set
- shortlist of first extraction waves

### Despaghettify Role
- detect current hotspot files and mixed responsibility zones
- classify shared-core debt
- rank extraction candidates
- identify zones most likely to fragment if changed carelessly

---

## Phase 1 — Platform Entry Shape and Legacy Compatibility

### Goal
Introduce a first platform-style CLI surface while preserving legacy suite compatibility.

### Deliverables
- first `fy` platform commands with mode-based routing
- compatibility wrappers for existing suites
- shared command dispatch layer
- initial lane routing

### Despaghettify Role
- detect duplicate wrapper logic
- prevent wrapper sprawl
- flag compatibility code that grows too heavy
- recommend where wrappers should remain thin

---

## Phase 2 — Minimal Lane Runtime + Shared IR

### Goal
Introduce the first real lane-based execution flow and shared IR objects.

### Deliverables
- inspect lane
- normalize lane
- govern lane
- generate lane
- verify lane
- structure lane
- first shared IR object types
- influence graph support

### Despaghettify Role
- ensure lane introduction does not create random utility scattering
- identify low-cohesion extractions
- guide which responsibilities should remain central vs distributed
- block naive splitting that increases structural confusion

---

## Phase 3 — Deterministic First + Metrify Governor

### Goal
Enforce deterministic pre-pass rules and begin governing AI invocation.

### Deliverables
- deterministic-first policy
- model escalation rules
- metrify gate integration
- cache-aware model call path
- avoided-call tracking

### Despaghettify Role
- detect policy logic leaking into the wrong places
- detect repeated AI-call precheck fragments
- keep the gating logic centralized and coherent

---

## Phase 4 — Templated Outputs + Structured Cleanup Waves

### Goal
Move standard outputs to template-driven rendering and run the first major cleanup waves.

### Deliverables
- template-led report generation
- schema-bound output variants
- core cleanup wave 1
- core cleanup wave 2
- anti-re-fattening checks

### Despaghettify Role
- generate cleanup wave plans
- verify cleanup effectiveness
- ensure the split outcome is not fragmented
- enforce core-thinning trend

---

## Phase 5 — Public Surface Consolidation

### Goal
Start reducing visible fragmentation while keeping internal lanes rich.

### Deliverables
- grouped public capability surfaces
- clearer external capability taxonomy
- migration notes for legacy suite entry points

### Despaghettify Role
- detect consolidation layers that become too thick
- detect duplicated public-facing routing logic
- prevent the new surface from becoming another monolith

---

# Public Capability Grouping (Transition Direction)

The MVP does not need to fully collapse everything, but it should prepare for a clearer public shape.

## Likely Public Grouping Direction

### Governance
- contractify
- postmanify
- parts of securify

### Quality
- testify
- despaghettify
- parts of securify

### Knowledge
- documentify
- docify
- usabilify

### Platform
- templatify
- observifyfy
- metrify
- mvpify
- fy_platform

Internally, these are lenses over lanes and shared objects.
Externally, they remain understandable capability groupings.

---

# MVP Acceptance Criteria

This MVP is successful only if all of the following are true.

## Architectural
- a platform-style command surface exists
- at least a minimal lane runtime exists
- a shared IR exists and is actually used
- influence edges exist across domains

## Cost and AI Governance
- deterministic pre-pass is enforced for model use
- metrify is part of model-call governance
- avoided model calls are explicitly tracked

## Structural
- despaghettify audits the shared core during the transition
- despaghettify produces staged cleanup waves
- despaghettify detects anti-patterns caused by the transition itself
- the shared core gets thinner or cleaner rather than simply redistributed

## Stability
- legacy compatibility remains bounded and intentional
- platform and legacy surfaces do not diverge into separate behaviors
- the migration does not create uncontrolled glue sprawl

## Output Discipline
- standard outputs increasingly flow through templates
- generative prose is reserved for genuinely high-value cases

---

# What This MVP Does Not Attempt

To stay honest, this MVP does **not** try to fully deliver:

- a final fy v2 architecture,
- a complete IR universe,
- full provider-backed LLM orchestration,
- full suite surface collapse,
- final organizational packaging.

It is a transition MVP.
Its job is to make fy materially more coherent, more deterministic, more governable, and less structurally fragile.

---

# Why This Is the Right MVP

Because it does not only describe the future.
It actively prevents the transition from making the system worse.

That matters.

Without this, the likely failure mode is:

- new platform ideas are layered onto old suite mechanics,
- the shared core gets fatter,
- wrappers multiply,
- the architecture enters a confused hybrid state,
- cleanup is postponed,
- cost control stays optional,
- and the suite family becomes harder to reason about.

This MVP directly counters that outcome by making `despaghettify` part of the transition machinery itself.

---

# Final Summary

This MVP establishes the first serious fy v2 transition shape:

- suites become domain lenses,
- the platform becomes the real technical substrate,
- a shared compiler-like flow begins,
- lanes become explicit,
- a minimal IR becomes real,
- deterministic work precedes AI,
- metrify starts governing model usage,
- templating becomes the output backbone,
- and despaghettify cleans up the existing structural debt in controlled waves while preventing the migration from fragmenting the system.

That is the correct foundation for evolving fy from a capable suite family into a powerful, efficient, platform-grade internal development system.
