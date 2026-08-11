---
id: SAD-PROJECT-GOVERNANCE
status: accepted
type: project-sad
owns-adrs: [ADR-0017, ADR-0029, ADR-0039]
uml-package: UML/Project/ecosystem-topology
links:
  - docs/architecture/project/DECISION_REGISTRY.md
  - docs/governance/gate_oracle_tightness_inventory.md
---
# Governance — Software Architecture (arc42, project-wide)

**System:** Architecture governance · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Defines how World of Shadows maintains architecture truth: SAD §9 decisions, UML companions,
DECISION_REGISTRY traceability, and gate tests that must not bypass oracles.

### 1.1 Quality goals

| Goal | Scenario |
| --- | --- |
| Traceable moves | Every doc relocation leaves a stub or registry entry until retirement |
| No silent drift | Residue removal follows ADR-0029 policy |
| Honest gates | Gate tests read canonical fixtures, not hardcoded bypass strings |
| SAD-only decisions | New cross-service decisions land in SAD §9, not new ADR files |

## 2. Constraints

- **Architecture decisions live only in SAD §9** (plus UML); retired ADRs live under `docs/archive/adr-retired-2026/`.
- Audience docs do not become architecture owners.
- Despaghettify execution governance (`'fy'-suites/despaghettify/state/`) is parallel evidence for code structure.

## 3. Context & Scope

Maintainers, agents, and CI consume this SAD when changing boundaries, contracts, or documentation.

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Decision, authority, exception and promotion governance spanning architecture documents and runtime control-plane policies.

**Authority rule:** Accepted decisions and explicit runtime governance services own policy; archives and reports are evidence, not parallel decision authority.

**Git/archaeology scope:** `docs/architecture/project`, `docs/adr`, `backend/app/services/governance`, `tests/gates`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Maintainer interaction with decision and runtime governance | [Architecture Governance - Context](../../../../UML/Project/governance/context/governance-context.md) | Accepted decisions and explicit runtime governance services own policy; archives and reports are evidence, not parallel decision authority. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

## 4. Solution Strategy

- **New decisions:** edit owning SAD §9 + UML + [`DECISION_REGISTRY.md`](../DECISION_REGISTRY.md); optional short note in `evidence/`.
- Documentation migration: SAD is normative; `docs/technical/` stubs route forward.
- Gate oracle changes require inventory update in [`gate_oracle_tightness_inventory.md`](../../../governance/gate_oracle_tightness_inventory.md).

## 5. Building Block View

| Artifact | Role |
| --- | --- |
| `docs/architecture/` | Normative SADs, contracts, gates |
| [`DECISION_REGISTRY.md`](../DECISION_REGISTRY.md) | ex-ADR → SAD §9 traceability during retirement |
| `docs/archive/adr-retired-2026/` | Historical ADR files (read-only) |
| `tests/gates/` | Architecture enforcement |
| `docs/governance/` | Oracle inventory, audit programs |
| `tools/architecture_assurance/config.json` | Executable architecture-governance policy |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound structural decomposition

Only elements that participate in a container or component view are listed as building blocks. Actors, runtime states, data types and deployment nodes remain in their proper viewpoints instead of being misrepresented as structural decomposition.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| Decision Registry (`decision_registry`) | `component` | Index accepted and retired decisions | Stable identifiers and status | [`docs/architecture/project/DECISION_REGISTRY.md`](../DECISION_REGISTRY.md) |
| Governance Evidence (`audit`) | `component` | Record actor, before/after and outcome | Immutable audit event | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| Policy Gates (`gates`) | `component` | Block invalid authority and decision drift | Executable CI checks | [`tests/gates/test_adr_live_runtime_commit_semantics_gate.py`](../../../../tests/gates/test_adr_live_runtime_commit_semantics_gate.py) |
| Runtime Governance Services (`runtime_policy`) | `component` | Validate and apply operational policy | Authorized audited mutation | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| SAD Decision Sections (`sad`) | `component` | Explain decisions in architecture context | Traceable rationale and consequences | [`docs/architecture/project/ecosystem-topology/architecture.md`](../ecosystem-topology/architecture.md) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Not a runtime system—governance applies at PR/CI time via pytest gates and human review against QUALITY-STANDARD.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| Draft, proposal, acceptance and supersession with preserved lineage | `state` | [Architecture Governance - Decision Lifecycle](../../../../UML/Project/governance/states/decision-lifecycle.md) | 4 |
| Accepted policy becomes audited runtime configuration and gate evidence | `sequence` | [Architecture Governance - Runtime Policy Change](../../../../UML/Project/governance/sequence/runtime-policy-change.md) | 5 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. A sequence or activity view must form one connected runtime path; a list of unrelated calls does not qualify as an end-to-end scenario. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

N/A

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

This scope does not claim an independently deployable runtime. Its deployment effect is expressed through the owning systems and the following implementation roots:

- `docs/architecture/project`
- `docs/adr`
- `backend/app/services/governance`
- `tests/gates`

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

- MVP locator/evidence artifacts under `tests/reports/MVP_Live_Runtime_Completion/` are program evidence, not ADRs.

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| Governance Evidence | Policy Gates | supports verification | machine-checkable evidence | [`tests/gates/test_adr_live_runtime_commit_semantics_gate.py`](../../../../tests/gates/test_adr_live_runtime_commit_semantics_gate.py) |
| Accepted Decision | Governed Exception | may bound | temporary explicit deviation | [`docs/architecture/project/governance/mechanism-catalog.md`](mechanism-catalog.md) |
| Runtime Governance Services | Governance Evidence | records mutation outcome | actor and before/after evidence | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| Decision Proposal | Accepted Decision | is accepted as | reviewed rationale | [`docs/architecture/project/DECISION_REGISTRY.md`](../DECISION_REGISTRY.md) |
| Decision Registry | SAD Decision Sections | indexes contextual decision | stable decision id | [`docs/architecture/project/ADR_ABSORPTION_MATRIX.md`](../ADR_ABSORPTION_MATRIX.md) |
| SAD Decision Sections | Runtime Governance Services | constrains implementation | accepted policy semantics | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Durable-truth migration policy | Accepted | ADR-0017 |
| D2 | Residue removal policy | Accepted | ADR-0029 |
| D3 | Gate tests must not hardcode oracle bypasses | Accepted | ADR-0039 |
| D4 | ADR duplicate resolution | Accepted | migration baseline B4 |
| D5 | SAD-only decision retirement | Accepted | ADR-0017 evolution |
| D6 | Revision review state machine | Not Finished | ADR-0006 |
| D7 | Revision conflict governance objects | Not Finished | ADR-0007 |
| D8 | Evaluation as promotion gate | Not Finished | ADR-0009 |
| D9 | Event-driven governance workflows | Not Finished | ADR-0010 |
| D10 | Decision boundary record schema | Not Finished | ADR-0024 |

### D1: Durable-truth migration verification and archive policy

**Status:** Accepted
**Origin:** ADR-0017 (retired 2026-06-23)

**Context.** During a documentation consolidation effort, many source documents were merged into canonical technical pages, while historical plans and specs were moved to `docs/archive/` for evidence preservation. The consolidation requires a clear, auditable policy for where decisions live and how archival sources are referenced.

**Decision.** Historical (2026-04-17): consolidation migrated decisions into ADRs under the former ADR tree. **Superseded by [D5](#d5-sad-only-decision-retirement)** (2026-06-23): normative decisions now live only in SAD §9 + UML; ADRs archived to `docs/archive/adr-retired-2026/`.

Legacy consolidation rules retained for audit:
- Migration verification tables remain in `docs/archive/documentation-consolidation-2026/` as evidence.

**Consequences.** - Some archive files were edited to include pointer lines; CI tests that reference archived paths must expect pointers or canonical SAD paths.
- Contractify discovery should prefer owning SAD §9 and [`DECISION_REGISTRY.md`](../DECISION_REGISTRY.md) while archive evidence remains discoverable for audit.

**Implementation status.** **Superseded implementation narrative (2026-04-17 ADR phase) — normative surface is now SAD-only per [D5](#d5-sad-only-decision-retirement).**

- Retired ADR files live under `docs/archive/adr-retired-2026/`; [ADR README](../../../ADR/README.md) is a redirect stub only.
- Archived files retain "Migrated Decision" pointer lines (observed in `docs/dev/architecture/runtime-authority-and-session-lifecycle.md`, runtime contracts, etc.).
- `docs/archive/documentation-consolidation-2026/` holds migration ledgers as evidence.
- ADRs 0001–0029 and MVP decisions were absorbed into SAD §9 during the 2026-06 retirement pass.
- Ongoing: new decisions must be written in owning SAD §9 + UML and registered in `DECISION_REGISTRY.md`.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d1-durable-truth-migration-policy` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Residue Removal Policy — operational criteria and handling

**Status:** Accepted
**Origin:** ADR-0029 (retired 2026-06-23)

**Context.** An audit pass (Task 4 — Residue Removal Report) applied operational criteria to classify documentation and artifacts as keep, demote/archive, or relocate. The audit used a 2-of-3 rule across omission, durable-role displacement, and transitional/history tests.

**Decision.** - Adopt the 2-of-3 residue criteria for operational cleanup:
  - Evaluate `omission` (active-value omission), `displacement` (durable-role displacement), and `transitional/history` status.
  - If at least 2 of 3 criteria are satisfied, mark the surface as a residue-candidate and plan demotion/archival or relocation.
- Use priority tiers (`P0` keep; `P1` candidate demote/relocate) to sequence work.
- For mixed-case collections (e.g., `docs/reports/*`) apply per-file evaluation and demote on a case-by-case basis.
- Move executed removals or relocations to tracked fixtures/locations (e.g., `backend/fixtures/…`, `docs/reports/` corrected paths).
- Legacy removal governance is executed through the `delagecy` fy-suite:
  - Newly found legacy surfaces must be entered in `delagecy_registry.json` and reported before removal begins.
  - Removal requires an explicit approval record; agents must not silently decide ambiguous removals.
  - Legacy is not active compatibility: if the current system still requires the behavior, preserve it and canonicalize the name or contract instead of deleting it.
  - UI, route, test, docs, diagnostics, compatibility aliases, and hidden compatibility blocks are residue until removed or reclassified as active canonical behavior with evidence.
  - If a removal risks system integrity or reveals conflicting ownership, pause and discuss rather than self-resolving the conflict.

**Consequences.** - Requires a downstream cleanup plan and owners to execute demotion/archival for `P1` candidates.
- Instrumentation and gating for relocation must be explicit (do not delete without provenance capture).
- Some files require extraction of decision-like content into canonical ADRs before demotion.

**Implementation status.** **Policy executed — 2026-04-17 consolidation pass applied the 2-of-3 rule.**

- The residue removal audit (Task 4) was run during the 2026-04-17 documentation consolidation.
- P0 (keep) and P1 (demote/relocate) candidates were classified; demotion/archival was executed for identified residue.
- `docs/archive/documentation-consolidation-2026/` holds migration ledgers and residue audit evidence.
- The 2-of-3 rule (omission, displacement, transitional/history) is documented as a policy; ongoing application is by convention and code review.
- Status promoted from "Proposed" because the initial residue removal was completed and the policy is active.

**Testing.** Contract / unit coverage as cited in **References**. Dedicated gate:

```bash
PYTHONPATH="'fy'-suites" python -m delagecy.tools scan --out "'fy'-suites/delagecy/reports/latest_scan.json"
PYTHONPATH="'fy'-suites" python -m delagecy.tools check --scan-json "'fy'-suites/delagecy/reports/latest_scan.json"
```

Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d2-residue-removal-policy` (archived — see `docs/archive/adr-retired-2026/`)

### D3: Gate Tests Must Not Use Hardcoded Oracles (No “Example-Shaped” Bypasses)

**Status:** ** Accepted
**Origin:** ADR-0039 (retired 2026-06-23)

**Context.** We repeatedly observe an anti-pattern when fixing failing gates or tightening checks:

1. A gate or regression test fails for a **legitimate semantic reason** (contract drift, missing integration, wrong authority surface, incomplete pipeline).
2. Instead of fixing the **system under test** (or the **contract**), a contributor “fixes green” by **hardcoding the expected outcome** that makes the test pass: literal strings, magic IDs, fixed counts, brittle substrings, or one-off payloads copied from a single local run.
3. The test then encodes **the symptom description** (what the ticket said) rather than the **invariant** (what must always be true). Semantically equivalent correct behavior can still fail; slightly wrong behavior can pass if it matches the hardcoded needle.

This produces **false confidence**: CI is green while the product regresses, because the test is a mirror of a workaround, not a guardrail. It also **ossifies accidents**: the hardcoded value becomes undeclared product truth that diverges from canonical modules, OpenAPI, ADRs, or runtime authority.

Gates exist to prove that **promotion criteria** hold under change. If a gate test’s oracle is arbitrary hardcoded material, the gate becomes a **lint rule for the patch author’s memory**, not a proof of system behavior.

### Tight coupling to ADR-0008 and ADR-0009

- **[ADR-0008](../../../archive/adr-retired-2026/adr-0008-validation-strategy-explicit-configurable.md)** defines *how strongly* runtime output is validated. Tests that claim to protect that behavior must not substitute hardcoded example text for real contract checks—otherwise the strategy toggle becomes theatre: CI can stay green while semantics drift.
- **[ADR-0009](../../../archive/adr-retired-2026/adr-0009-evaluation-is-a-promotion-gate.md)** defines that promotion is not automatic from artifact existence; evaluation evidence matters. When evaluation gate tests land, they are especially vulnerable to “assert this exact score text” shortcuts; this ADR forbids that pattern so evaluation remains a **genuine promotion signal**.

---

**Decision.** **Normative rule — binding for gate tests and promotion-style regression tests:**

> **Gate tests MUST NOT treat hardcoded literals as the primary oracle of correctness.**  
> Assertions must be derived from a **declared, shared source of truth** (contract, schema, canonical authored content, public API response shape, documented invariants) or from **computed baselines** that are themselves justified by such a source.

**Hardcoded values are forbidden when they function as:**

- A **bypass** for a missing semantic fix (“just assert this exact `consequence_text` substring”).
- A **single-example oracle** that only matches one narrative phrasing, one model run, or one author’s wording.
- A **duplicate truth surface** that contradicts or silently diverges from canonical YAML, runtime projection, or published contracts.

**Allowed patterns (non-exhaustive):**

- **Load the oracle** from canonical content (e.g. `content/modules/…`, compiled projections, fixtures generated from the same pipeline that production uses).
- **Assert structure and invariants** (types, keys, bounds, monotonicity, presence of required fields, forbidden classes absent) without pinning prose.
- **Compare against a stable artifact** only when that artifact is **versioned and reviewable** (e.g. golden JSON under `tests/fixtures/` with a documented generator, or snapshot tests under explicit team review policy — not ad-hoc copy-paste).
- **Use regex or semantic checks** sparingly and only when tied to a **named invariant** documented in an ADR or contract (not “this one German clause”).

**Pull requests that add or extend gate tests must be rejected if:**

- The primary assertion is a **long literal** or **opaque magic constant** with no pointer to the contract or content that defines it.
- The test would **pass** if the implementation returned **wrong behavior** that still matched the hardcoded string.
- The test would **fail** if the implementation improved while preserving all **documented** semantics (e.g. rephrased narrator text that still satisfies the same content keys and policies).

### Capability Matrix and Pi / Π vocabulary

For Capability Matrix work, Pi / Π labels are historical cross-reference vocabulary only. They must not become runtime IDs, score names, schema keys, routing keys, or control-flow branches. Production code must use stable semantic names such as `silence_negative_space`, `environment_state`, `dramatic_irony`, `callback_web`, `subtext`, `information_disclosure`, `social_pressure`, `sensory_context`, and `improvisational_coherence`.

Semantic names are allowed in production when they are contract-backed. Tests must distinguish forbidden Pi-number usage from valid semantic runtime surfaces. When a new Capability Matrix row gains implementation code, update `tests/gates/test_table_b_anti_hardcoding_gate.py` with the legacy label and any reviewed semantic runtime-aspect surface, or document why the row is out of scope.

ADR-0041 adds the Runtime Capability Authority boundary. Selector manifests, selector outputs, activation modes, scoped co-authority decision payloads, RuntimeAspectLedger evidence, MCP payloads, and Langfuse score names must follow the same semantic-name rule. A selector decision can explain why `narrator_authority`, `scene_energy`, or `npc_agency` was selected or excluded for a turn, but it must not use Pi / Π labels as active keys and must not be treated as implementation, promotion, or live/staging proof by itself.

ADR-0039 applies to every test file that references a Pi / Π capability label, including tests that use Table-B metadata only as fixture data. Those tests must be covered by `tests/gates/test_adr_0039_pi_scope.py`, and any new Pi-labeled test must either join that coverage manifest or remove the legacy label. A Pi-labeled test is not evidence by name alone; it must assert contract fields, validators, policy-derived values, runtime wiring, ledger projection, MCP extraction, or Langfuse/staging evidence.

Capability promotion evidence belongs in:

- `docs/MVPs/capability_matrix_status_and_adr_relations.md` for current truth, ADR relation, semantic name, and maturity.
- `docs/MVPs/capability_matrix_verification_log.md` for dated verification runs.
- `docs/MVPs/capability_matrix_live_claim_gates.md` for live/staging/Langfuse/MCP promotion rules.

### MCP, Langfuse, portability, and evidence quality

MCP and Langfuse verification tools are ADR-0039 gate surfaces when their output is used for Capability Matrix claims. They must derive repository paths from `Config.repo_root`, `REPO_ROOT`, or another repository-root discovery mechanism; production verification code must not embed machine-local roots such as a developer's drive, home directory, or mount path. Dated verification logs may preserve historical absolute commands only when they are explicitly marked as local environment transcripts and not reusable proof instructions.

Local pytest, mocked provider checks, fixture traces, and degraded/fallback paths prove local implementation behavior only. They must not be described as staging/live/Langfuse/MCP success unless the evidence includes the actual provider or environment metadata, reproducible trace/query identifiers where applicable, semantic score names, and the command or query used to retrieve it.

False-green prevention for MCP/Langfuse gates requires structured result fields: return codes, command/cwd or query metadata, environment scope, evidence scope, score names, and normalized runtime metadata. A PASS label, test name, trace id string, comment, or documentation statement is not proof unless the structured output supports the claim.

### Runtime surface governance (expanded scope)

ADR-0039 governs **runtime behavior and decision surfaces**, not only tests and documentation. Any path that can distort **runtime truth, readiness, player/session/turn flow, beat progression, or decision-tree behavior** is in scope, including:

- **`ai_stack`** — LangGraph executor, `run_validation_seam`, `runtime_aspect_ledger` / `runtime_aspect_ledger/runtime_intelligence_projection/`, ADR-0041 sidecar and flags (fail-closed defaults; projection must not impersonate seam or commit).
- **`world-engine`** — `StoryRuntimeManager`, commit/readiness models, narrative commit seam.
- **`backend`** — player-session bundle and readiness derivation (`evaluate_session_opening_readiness`, ADR-0041 veto-only consumer).
- **`frontend` Play Shell** — must **not manufacture** readiness, live, or healthy semantics; display only fields the backend/runtime bundle proves.
- **`administration-tool`** — operator UI and proxy to backend/world-engine; **display and approved control actions only**; must **not** treat local dashboard or proxy payload as canonical runtime, commit, or live health without the same fields from authoritative services.
- **`story_runtime_core`** — first-class: `interpret_player_input` / semantic language adapter (**preview** shaping only), **`recovery/no_dead_end`** (**diagnostic** evidence contract only), branching / callback / consequence helpers (**diagnostic** unless explicitly wired through world-engine commit). This package must **not** bypass canonical validation or commit authority.

**Normative inventory:** [`docs/MVPs/adr0039_runtime_surface_governance_inventory.md`](../../../MVPs/adr0039_runtime_surface_governance_inventory.md) (YAML front matter, gate-enforced). Code is authoritative over prose; update the inventory when surfaces change.

**Interaction with ADR-0041:** Scoped co-authority and readiness aggregation remain **bounded, explicit, and testable**; they must **not** silently mutate `validation_outcome`, commit, or seam-canonical readiness. `plan_enforced` without the LangGraph graph sidecar must remain **dry-run** on the ledger projection path.

---

**Consequences.** **Positive**

- Gates measure **whether the system honors contracts**, not whether it repeats yesterday’s wording.
- Canonical content and ADRs remain **single sources of truth**; tests stop inventing parallel truth.
- Refactors and localization (e.g. session output language) become **possible without whack-a-mole** string updates across gate tests.

**Negative / risks**

- Tests may require **more setup** (loaders, small harnesses) instead of a one-line `assert output == "..."`.
- Some genuinely brittle domains (timestamps, nonces) still need **controlled fixtures**; those fixtures must be **documented** and minimal, not full narrative oracles.

**Follow-ups**

- During code review, treat unexplained string literals in `tests/` and `**/test_*gate*` files as **blockers** unless referenced to contract or content.
- Prefer extending **canonical content** or **contract schemas** when a new invariant is needed, then binding tests to that extension.

---

**Evidence.** `docs/architecture/project/governance/architecture.md#d3-gate-tests-must-not-hardcode-oracle-bypasses` (archived — see `docs/archive/adr-retired-2026/`)

### D4: ADR duplicate resolution

**Status:** Accepted
**Origin:** ADR retirement hygiene (retired 2026-06-23)

**Context.** Retired ADR filenames collided (ADR-0058 pulse bus, ADR-0021 authority stub); registry and SAD anchors must point to one canonical decision each.

**Decision.**

- **ADR-0058 canonical:** `adr-0058-director-driven-pulse-block-stream-bus.md`. Deprecated duplicate: `adr-0058-director-driven-pulse-and-block-stream-bus.md` (stub only).
- **ADR-0021:** legacy file in `docs/archive/adr-retired-2026/legacy/`; root stub redirected → ADR-0001 / world-engine SAD D1.

**Evidence.** [2026-06-23 migration baseline audit](../../evidence/2026-06-23-migration-baseline-audit.md).

### D5: SAD-only decision retirement

**Status:** Accepted · **Origin:** ADR-0017 evolution · **Supersedes:** ADR-first authoring for new decisions

**Context.** Parallel ADR files and SAD §9 summaries drift; gates and agents cannot rely on a single normative path.

**Decision.** Normative architecture decisions live only in SAD §9 and UML. Register every ex-ADR in [`DECISION_REGISTRY.md`](../DECISION_REGISTRY.md). Do not create new active `adr-*.md` files. After audit readiness, archive ADRs under `docs/archive/adr-retired-2026/` and delete active copies.

**Consequences.** Link migration in main repo (excluding `'fy'-suites/`); gates read SAD paths; ADR README becomes a stub.

**Evidence.** [`scripts/adr_retirement_audit.py`](../../../../scripts/adr_retirement_audit.py), [`evidence/adr-retirement-audit.md`](../../evidence/adr-retirement-audit.md).

### D6: Revision review uses a state machine, not loose status strings

**Status:** 
**Origin:** ADR-0006 (retired 2026-06-23)

**Decision.** Revision lifecycle must be enforced through a formal workflow state machine with role permissions and side effects.

**Consequences.** - multi-operator work is safer
- approval paths become auditable
- system side effects like draft apply and evaluation launch can be attached to transitions

**Implementation status.** **Decision stated; no state machine implementation found in codebase.**

- The principle (revision lifecycle as a typed state machine with role-based transitions) is architecturally sound and referenced in MVP governance docs.
- No formal `RevisionStateMachine` or equivalent class was found in `backend/` or `world-engine/`.
- The writers-room review workflow (`/api/v1/writers-room/reviews`) has stages (accept/reject/revise) that approximate state transitions, but they are not implemented as a formal state machine with explicit RBAC gate enforcement per transition.
- Implementation is blocked on: defining revision state model, role permission matrix per transition, and side-effect hooks (draft apply, evaluation launch).
- Required before: full multi-operator revision workflows can be safely operated.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d6-revision-review-state-machine` (archived — see `docs/archive/adr-retired-2026/`)

### D7: Revision conflicts are explicit governance objects

**Status:** 
**Origin:** ADR-0007 (retired 2026-06-23)

**Decision.** Competing revision candidates targeting overlapping content units must create conflict records before draft apply.

**Consequences.** - no silent last-write-wins behavior
- operators can resolve conflicts deliberately
- revision batches remain inspectable

**Implementation status.** **Decision stated; conflict record implementation not found in codebase.**

- The principle (overlapping revision candidates produce an explicit conflict record before draft apply) is referenced in MVP governance docs.
- No `ConflictRecord` class, conflict detection logic, or conflict resolution workflow was found in `backend/` or `world-engine/`.
- The writers-room review workflow exists but does not include conflict detection between concurrent revision candidates.
- Prerequisite: ADR-0006 (revision state machine) must be implemented first, since conflict detection naturally integrates with revision lifecycle transitions.
- Required before: concurrent multi-author revision workflows can operate safely without silent last-write-wins behavior.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d7-revision-conflict-governance-objects` (archived — see `docs/archive/adr-retired-2026/`)

### D8: Evaluation is a promotion gate

**Status:** 
**Origin:** ADR-0009 (retired 2026-06-23)

**Context.** Preview and staging packages can exist indefinitely without proving narrative or governance quality. If promotion is informal, operators carry unwritten rules and regressions slip through. Formal **evaluation gates** and **approval** make “promotable” a defined state: measurable, comparable to baseline, and reviewable—once enforcement is complete (see **Implementation Status**).

**Decision.** A preview package is not promotable only because it exists. Promotion requires passing evaluation gates and manual approval.

Capability Matrix promotion follows the same principle: a row is not promotable only because source code, documentation, a test name, or a local PASS line exists. Runtime wiring, behavior tests, ADR relation, anti-hardcoding coverage, and any required live/staging/Langfuse/MCP evidence must be present before a capability is described as implemented or live-proven.

For hard runtime drift loops such as `tonal_consistency`, local runtime
enforcement and recoverable rejection are still not enough for a live/promoted
claim. A failed hard-loop validation must block healthy commit/live-success,
but promotion additionally requires dated provider traces, evaluator baselines,
Langfuse/MCP evidence, and explicit readiness coupling.

**Consequences.** - quality becomes measurable
- package changes can be compared to active baseline
- regression risk is materially reduced
- when evaluation gate tests are added or tightened, they are subject to [ADR-0039](../../../archive/adr-retired-2026/adr-0039-gate-tests-no-hardcoded-oracle-bypass.md): scoring and pass/fail oracles must not be reduced to hardcoded literals that only mirror a single failing ticket’s wording

**Implementation status.** **Partially implemented — evaluation pipeline exists; formal promotion gate enforcement is incomplete.**

- `ai_stack/quality_lab/evaluation_pipeline.py` exists and handles evaluation scoring/baselines.
- Backend operator routes under `/api/v1/admin/mvp4/...` expose evaluation recent-turns, baselines, and regression checks (per ADR-0032).
- What is NOT implemented: a hard gate that blocks package promotion without passing evaluation scores. The evaluation pipeline produces data but does not currently block a promotion action if scores fail.
- Manual approval path: not formalized as a system-enforced gate; relies on operator workflow convention.
- Required before: fully automated content promotion pipelines can trust quality guarantees.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Promotion / evaluation gate tests** (when implemented) must prove that failed scores or failed regression checks **block** promotion—or that approved overrides are explicit—not that a magic string in the test file matches last week’s output. Follow [ADR-0039](../../../archive/adr-retired-2026/adr-0039-gate-tests-no-hardcoded-oracle-bypass.md): derive expected evaluation artifacts from versioned baselines, published scoring contracts, or fixture generators tied to the same pipeline as production evaluation.

**Evidence.** `docs/architecture/project/governance/architecture.md#d8-evaluation-as-promotion-gate` (archived — see `docs/archive/adr-retired-2026/`)

### D9: Governance workflows are event-driven

**Status:** 
**Origin:** ADR-0010 (retired 2026-06-23)

**Decision.** Critical governance events must be emitted and may trigger admin banners, email, Slack, or webhooks.

**Consequences.** - operators do not need to manually poll all pages
- failed evaluations and urgent findings become visible
- async multi-role workflows become operational

**Implementation status.** **Decision stated; event bus/webhook implementation not found.**

- No event bus, governance event emitter, or webhook dispatch system was found in `backend/` or `world-engine/`.
- Admin banners, Slack/email notifications, and webhook triggers for governance events (failed evaluations, urgent findings) are not implemented.
- The observability layer (Langfuse) records governance events as traces/scores, which operators can monitor — but this is pull-based monitoring, not event-driven push.
- Required before: async multi-role governance workflows (operators notified of failures without manual polling) can be operational.
- This ADR describes MVP2-era governance workflow scope. Implementation has not been prioritized ahead of MVP4 runtime work.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d9-event-driven-governance-workflows` (archived — see `docs/archive/adr-retired-2026/`)

### D10: Decision Boundary Record — minimum schema for decision boundary recording

**Status:** 
**Origin:** ADR-0024 (retired 2026-06-23)

**Context.** The `ROADMAP_MVP_GoC.md` documents a set of minimum fields for runtime records including a Decision Boundary Record. Capturing decision boundary metadata consistently supports auditability and governance.

**Decision.** - Standardize a `Decision Boundary Record` with the following minimum fields:
  - `decision_name`
  - `decision_class`
  - `owner_layer`
  - `input_seam_ref`
  - `chosen_path`
  - `validation_result`
  - `failure_seam_used`
  - `notes_code`

- Ensure runtime and governance layers emit this record when a decision boundary is crossed.

**Consequences.** - Instrumentation work required in runtime components to populate the record.
- Downstream storage, retrieval, and reporting should include these fields for governance views.

**Implementation status.** **Schema defined; runtime emission not implemented.**

- The `Decision Boundary Record` minimum schema (decision_name, decision_class, owner_layer, input_seam_ref, chosen_path, validation_result, failure_seam_used, notes_code) is documented.
- No `DecisionBoundaryRecord` class or runtime emitter was found in `backend/`, `world-engine/`, or `ai_stack/`.
- ADR-0033 and `ai_stack/story_runtime/live_runtime_commit_semantics.py` produce diagnostics fields that partially fulfill the intent (route_id, validation_status, commit_applied, etc.) but do not use the standardized Decision Boundary Record schema.
- Required before: formal governance audit trails with cross-seam decision boundary records can be produced.
- This ADR describes future instrumentation work; it has not been prioritized ahead of MVP4 runtime concerns.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d10-decision-boundary-record-schema` (archived — see `docs/archive/adr-retired-2026/`)

### D11: Decision Framework — risk framing and kill criteria

**Status:** 
**Origin:** ADR-0023 (retired 2026-06-23)

**Context.** The NextVision Suite's risk and mitigation documentation defines a decision framework for evaluating new initiatives and kill criteria for continuing work. This framework guides go/no-go decisions across phases.

**Decision.** - Adopt a lightweight decision framework requiring explicit answers for: introduced risks, mitigations, worst-case scenarios, recoverability, and acceptability given upside.
- Use stated "Kill criteria" (3 consecutive phase failures, unit economics broken, fundamental technical impossibility, or market shift) as formal stop conditions for projects.
- Document risk acceptance levels and monitoring cadence in project roadmaps.

**Consequences.** - Teams must include explicit risk assessments and recovery plans in decision artifacts.
- Project dashboards must track monitoring indicators tied to the framework.

**Implementation status.** **Decision in force as a governance framework; applied to MVP planning.**

- The risk framework (explicit risks, mitigations, worst-case, recoverability, kill criteria) is used in MVP planning documents under `docs/MVPs/`.
- Kill criteria (3 consecutive phase failures, broken unit economics, fundamental technical impossibility, market shift) are documented in roadmap materials.
- No automated monitoring system enforces kill criteria; application is by engineering and product convention.
- Status promoted from "Proposed" because the framework has been applied to all active MVPs and is a stable governance convention.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/project/governance/architecture.md#d11-decision-framework-risk-and-kill-criteria` (archived — see `docs/archive/adr-retired-2026/`)

### D12: Environment Configuration Governance

**Status:** 
**Origin:** ADR-0031 (retired 2026-06-23)

**Context.** The previous environment-governance description overstated the role of `.env` and encoded obsolete Langfuse assumptions.

Those older assumptions are no longer correct:

1. `.env` is not the single source of truth for all runtime configuration.
2. Langfuse is not governed by a legacy mandatory `LANGFUSE_ENABLED` switch.
3. Some runtime truth now lives in backend-managed settings and shared runtime storage, not directly in static environment variables.

The current architecture uses three configuration layers:

### Layer 1: Platform bootstrap and wiring

These values belong in environment variables because containers and services need them before the application runtime is fully available.

Examples:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `SECRETS_KEK`
- `FRONTEND_SECRET_KEY`
- `PLAY_SERVICE_SHARED_SECRET`
- `PLAY_SERVICE_INTERNAL_API_KEY`
- `INTERNAL_RUNTIME_CONFIG_TOKEN`
- `BACKEND_RUNTIME_CONFIG_URL`
- `PLAY_SERVICE_INTERNAL_URL`
- `PLAY_SERVICE_PUBLIC_URL`
- `REDIS_URL`
- provider base URLs

### Layer 2: Provider credentials

These may originate from `.env` in local Docker setups, but they are still credentials, not behavioral governance rules.

Examples:

- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ANTHROPIC_API_KEY`
- optional `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` for bootstrap import

### Layer 3: Governed runtime settings

These are backend-managed settings that the application consumes operationally and may store encrypted or in database-backed form.

Examples:

- active Langfuse observability configuration
- runtime routing and provider governance
- evaluation, override, and session governance state

This ADR aligns environment governance with that actual split.

**Decision.** ### 1. `.env` is a bootstrap contract, not the sole runtime truth

The repository-root `.env` is authoritative for:

- local platform secret generation
- container-to-container wiring
- startup URLs
- local credential injection for provider access

It is not authoritative for all live operational behavior after startup.

In particular, MVP4 observability behavior is governed through backend configuration and runtime state, not by env flags alone.

### 2. Runtime-managed settings must not be reduced to legacy env toggles

For observability, the current correct model is:

- backend stores and exposes current observability status
- credentials can be written or rotated through backend routes
- `docker-up.py` may import `LANGFUSE_*` from `.env` into backend settings as a bootstrap convenience

The incorrect older model was:

- env toggle decides if observability exists
- missing toggle silently disables the feature
- services treat env as the primary Langfuse control plane

That model must not be reintroduced in docs or code.

### 3. Variable classes

All environment variables must fit one of these classes.

| Class | Purpose | Examples | Governance rule |
|---|---|---|---|
| Platform secrets | cross-service trust and cryptography | `JWT_SECRET_KEY`, `SECRETS_KEK`, `INTERNAL_RUNTIME_CONFIG_TOKEN` | generated once, preserved, never committed live |
| Runtime wiring | service discovery and URLs | `BACKEND_RUNTIME_CONFIG_URL`, `PLAY_SERVICE_PUBLIC_URL`, `REDIS_URL` | explicit in Docker/local deployment |
| Provider endpoints | non-secret upstream URLs/versions | `OPENAI_BASE_URL`, `ANTHROPIC_VERSION` | safe defaults allowed |
| Provider credentials | access to upstream providers | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `HF_TOKEN` (Hugging Face Hub read token for fastembed / hub downloads) | optional unless that provider path is used |
| Bootstrap import credentials | optional seeding into managed config | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | if present, must be complete pair |

**`docker-up.py` and optional credential slots:** For keys in `OPTIONAL_SECRET_KEYS`, the bootstrap only inserts a **missing key** with an empty value. It does **not** overwrite keys that already exist in `.env`, so saved AI provider keys, `HF_TOKEN`, and Langfuse bootstrap pairs remain stable across `init-env` / `up` runs.

**Admin UI coverage:** Langfuse operational credentials are managed under **Observability Settings** (`/manage/observability-settings`) once imported into backend storage. There is **no** administration-tool screen for `HF_TOKEN` or other Hugging Face Hub tokens today — operators set `HF_TOKEN` in the repository-root `.env` (see `.env.example`); compose `env_file` injects it into backend / play-service at runtime.

### 4. Environment validation must match actual ownership

Validation rules should be strict, but only for what env truly owns.

Valid examples:

- fail if required platform secrets are missing
- fail if `LANGFUSE_PUBLIC_KEY` is present without `LANGFUSE_SECRET_KEY`
- fail if Docker runtime expects Redis and `REDIS_URL` is malformed

Invalid examples:

- fail startup because `LANGFUSE_ENABLED` is absent
- document `.env` as the single source of truth for backend observability state
- require env toggles for settings that are intentionally backend-managed

### 5. Current Langfuse governance rule

The current correct Langfuse rule is:

- `.env` may contain optional bootstrap credentials
- backend settings are the operational source of truth
- play-service and runtime behavior consume the resolved backend-published configuration
- the Langfuse child-observation tree is governed by backend
  `enabled_observation_trees` and administered through the Administration Tool
  Observability Settings; connection-test traces remain flat health probes
- automated backend connection tests must exercise `test_observability_connection()` / `verify_langfuse_runtime_connectivity()` against that backend-managed config, not legacy `code` fields, `observability_config_id` credential joins, or direct adapter-created Cloud traces

This means a local operator can:

1. leave `LANGFUSE_*` blank and configure observability later through backend/admin settings, or
2. place both credentials in `.env` and let `docker-up.py` import them during bootstrap

### 6. Current Redis governance rule

Because backend runs multiple workers in Docker, shared runtime-governance state must not rely on per-process memory in the standard Docker path.

Therefore:

- `REDIS_URL` is part of bootstrap environment governance
- Docker Compose provisions Redis by default
- backend may fall back to in-process storage outside Docker, but that fallback is not the canonical Docker truth path

### 7. Production secret-store boundary

For local development, repository-root `.env` is the intended operator experience and is maintained by `docker-up.py`. It should stay convenient, repeatable, and disconnected from external infrastructure.

For production, `.env` files are not the recommended long-term secret source. Production deployments should inject the same environment contract from a dedicated secret store such as a cloud secret manager, Vault, or equivalent platform service. That store must provide rotation, audit, and access separation. It should feed runtime environment variables or orchestrator-native secrets before services start; it must not make local `docker-up.py init-env` or `python docker-up.py up` depend on production credentials or network access.

**Consequences.** ### Positive

- Documentation now matches the actual ownership boundaries in the implementation.
- Langfuse setup is described in a way that supports encrypted backend-managed settings.
- Redis-backed runtime-governance storage is treated as an operational requirement in Docker.

### Negative / risks

- Some older comments or examples may still mention `LANGFUSE_ENABLED`; they should be treated as transitional or historical, not normative.
- New features must be careful not to push backend-governed state back into `.env` out of convenience.
- Production rollout needs separate secret-store integration and rotation procedures; this ADR only defines the environment contract and local bootstrap behavior.

**Implementation status.** **Implemented — three-layer governance model in place.**

- Layer 1 (platform secrets/wiring): `docker-up.py` generates and preserves these; `backend/app/config.py` reads them.
- Layer 2 (provider credentials): optional in `.env`; `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY` must be a complete pair if present.
- Layer 3 (governed runtime settings): `backend/app/services/governance/observability_governance_service.py` owns Langfuse operational config; `/manage/observability-settings` is the admin UI surface.
- Langfuse connection verification uses backend-managed `observability_configs.service_id="langfuse"` plus active encrypted `observability_credentials` rows; direct Cloud/env-only checks are limited to explicitly marked live-cloud tests.
- `REDIS_URL` is part of bootstrap governance; Redis is provisioned in Docker Compose by default.
- No `LANGFUSE_ENABLED` legacy toggle exists; the old model is explicitly prohibited in this ADR.
- `HF_TOKEN` is a provider credential in Layer 2; no admin UI screen — set in `.env`.
- Production secret management is a deployment concern: use a dedicated secret store with rotation, audit, and access separation, while keeping `docker-up.py` as the local `.env` bootstrap.

**Testing.** ### Verification checklist

- [ ] `docker-up.py init-env` materializes required platform secrets
- [ ] incomplete `LANGFUSE_*` pairs fail bootstrap clearly
- [ ] complete `LANGFUSE_*` pairs can be imported into backend observability settings
- [ ] backend starts with valid env even when Langfuse is managed later through backend settings
- [ ] Langfuse connection checks read `service_id="langfuse"` backend config and active `secret_name` credentials before any network probe
- [ ] Docker path uses shared Redis-backed governance storage rather than worker-local state

**Evidence.** `docs/architecture/project/governance/architecture.md#d12-env-configuration-governance` (archived — see `docs/archive/adr-retired-2026/`)

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D1` | Maintainer interaction with decision and runtime governance | `context` | [Architecture Governance - Context](../../../../UML/Project/governance/context/governance-context.md) |
| `D1`, `D2` | Decision registry, SAD, runtime policy, evidence and gate chain | `component` | [Architecture Governance - Components](../../../../UML/Project/governance/components/governance-components.md) |
| `D2` | Proposals, accepted decisions and bounded exceptions | `class` | [Architecture Governance - Decision Model](../../../../UML/Project/governance/classes/decision-model.md) |
| `D3` | Draft, proposal, acceptance and supersession with preserved lineage | `state` | [Architecture Governance - Decision Lifecycle](../../../../UML/Project/governance/states/decision-lifecycle.md) |
| `D1`, `D2` | Accepted policy becomes audited runtime configuration and gate evidence | `sequence` | [Architecture Governance - Runtime Policy Change](../../../../UML/Project/governance/sequence/runtime-policy-change.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

`tests/gates/test_adr0039_runtime_surface_governance.py`, `test_table_b_anti_hardcoding_gate.py`.

## 11. Risks & Technical Debt

Incomplete DECISION_REGISTRY vs filesystem—run [`scripts/adr_retirement_audit.py`](../../../../scripts/adr_retirement_audit.py) before bulk delete.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

ADRs were absorbed and archived while runtime policy services expanded. Models preserve decision lineage and prevent archive text or operator projections from becoming a second truth.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 116 | 72 | 255 | 0 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| `DRIFT-011` | `superseded` | MVP completion labels are not architecture authority | Use capability lifecycle states proposed, implemented, integrated, proven and regressed. Only production-path evidence advances a capability to proven. |
| `DRIFT-012` | `confirmed_current` | Architecture coverage metrics can hide shallow semantics | Keep model selection concern-driven and source-bound. Coverage remains supporting evidence; semantic analyzability, drill-down and correspondence determine acceptance. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Decision registry | ex-ADR ID → SAD §9 anchor map during retirement |
| SAD-only | New decisions edit SAD + UML, not ADR files |
