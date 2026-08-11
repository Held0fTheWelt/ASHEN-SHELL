# Architecture Documentation Quality Standard

Acceptance bar for documents under `docs/architecture/`. Adapted from Tiny Tool Development
[QUALITY-STANDARD](https://github.com/) patterns for World of Shadows component and project SADs.

## 1. Scope

Applies to:

- the canonical system SAD under `system/architecture.md`;
- component SADs under `components/<system>/architecture.md`;
- crosscutting and evidence portfolios under `project/<system>/architecture.md`;
- active decisions under `decisions/`, runtime scenarios under `scenarios/`, data ownership under
  `data/`, and known nonconformance under `violations/`;
- `contracts/`, `gates/`, `boundaries/`, `integrations/`, `combinations/`, `operations/`, `evidence/`, `views/`;
- `project/TRACEABILITY.md`, `project/ROLLOUT.md`, `DOC-HEALTH.md`.

## 2. Document ownership

| Document kind | Owner |
| --- | --- |
| Whole-system architecture | `system/architecture.md` |
| Deployable component | `components/<system>/architecture.md` |
| Shared library or in-process module | Owning deployable SAD plus a subordinate implementation portfolio when needed |
| Cross-cutting concept or evidence program | `project/<system>/architecture.md`, subordinate to system SAD and active ADR |
| Active decision | `decisions/ADR-NNNN-*.md` |
| Known implementation conflict | `violations/README.md` |
| Implementation-facing runtime slice | `scenarios/<scenario>.md` |
| Normative contract | `contracts/` linked from owning SADs |
| Gate | `gates/` linked from contract or SAD |
| Boundary / integration | `boundaries/` or `integrations/` routing to SAD §9 |
| Migration audit | `evidence/` with inputs, findings, follow-up |

One source of truth per topic. Cross-category documents route to the owning SAD decision.

Every material statement is classifiable as `Observed`, `Normative`, `Target`, `Violation` or
`Historical`. Observed code is not silently promoted to normative architecture. An accepted target
with nonconforming code links an open violation and executable closure evidence.

## 3. SAD acceptance bar

Every SAD contains 12 arc42 sections:

1. Introduction & Goals  
2. Constraints  
3. Context & Scope  
4. Solution Strategy  
5. Building Block View  
6. Runtime View  
7. Deployment View  
8. Crosscutting Concepts  
9. Architecture Decisions  
10. Quality Requirements  
11. Risks & Technical Debt  
12. Glossary  

Sections must be **useful**, not placeholders:

- goals as concrete quality scenarios;
- constraints link governing SADs, ADR exceptions, contracts, gates;
- building blocks and runtime link to UML or document a pending UML gap;
- §9 decisions are testable, consolidated, evidence-linked;

Section 9 is a concise decision synthesis and index. Full context, options and trade-offs belong to
an active ADR. Large historical ADR bodies must not be concatenated into a SAD.

Each locally owned `### Dn:` block in §9 must include:

| Field | Required |
| --- | --- |
| **Status** | Accepted / Partially implemented / Proposed / Not Finished |
| **Context.** | Why the decision was needed (omit only when merged into a parent D) |
| **Decision.** | Normative statement |
| **Consequences.** | Positive, risks, follow-ups |
| **Evidence.** | Markdown links to tests, gates, source |
| **Origin:** | ex-ADR-ID during retirement (optional after archive) |
| **Supersedes:** | Prior `Dx` when applicable |

During ADR retirement, register every ex-ADR in [`project/DECISION_REGISTRY.md`](project/DECISION_REGISTRY.md).

Active target decisions use [`decisions/ADR-TEMPLATE.md`](decisions/ADR-TEMPLATE.md) and keep
decision status separate from implementation state. Historical mappings remain in the retired
registry but do not require prose duplication in current SADs.

- risks list drift hazards and mitigation.

Project SADs use frontmatter per [`project/FRONTMATTER.md`](project/FRONTMATTER.md).

### 3.1 Mechanism catalog

Complex deployable components and runtime-critical project SADs maintain a companion
[`mechanism-catalog.md`](components/_template/mechanism-catalog.template.md) next to the SAD.

| Column | Required |
| --- | --- |
| ID | Stable mechanism id (`WE-M01`, `AI-M01`, `GOV-M01`) |
| Mechanism | Short name |
| Definition | One-paragraph normative behavior |
| Normative sources | Links to SAD `### Dn:` blocks and contracts |
| UML / evidence | Diagram or test/gate links |
| Proof state | `Implemented` / `Partial` / `Target` |

Required when: pilot components (world-engine, ai-stack), any component with ≥8 §9
decisions, or backend / story-runtime-core / mcp-server. Light catalogs (≥5 rows) suffice
for frontend, content-authority, administration-tool.

### 3.2 Evidence matrix

High-risk mechanisms also maintain [`evidence-matrix.md`](components/_template/evidence-matrix.template.md):
claim → source path → test or gate → proof state. One row per mechanism that affects
runtime authority, commit, readiness, or security boundaries.

## 4. Evidence and traceability

| Status | Meaning |
| --- | --- |
| `Implemented` | Linked implementation exists; this does not by itself prove conformance |
| `Partially implemented` | Implemented vs missing parts separated |
| `Target-state` | Must not imply production readiness |
| `Nonconforming` | Current implementation conflicts with an accepted target and links a violation |
| `Conforming` | Current production-path implementation and executable closure evidence agree with the target |

Non-trivial workflows need UML or an explicit pending gap in the SAD.

Coverage is reported in separate categories:

- **directly represented:** owned by an architectural element or scenario;
- **explicitly excluded:** outside the bounded architecture scope with reason;
- **unmapped current implementation:** discovered in scope but not yet owned;
- **known violation:** deliberately represented as nonconforming code.

Only the first category counts as representation coverage. Classification coverage may combine all
four but must never be labeled architectural coverage.

Every discovered in-scope semantic unit must resolve to a building block. Ownership is declarative:
the most specific source path wins, while an explicitly documented aggregate block may own supporting
implementation below its bounded root. Aggregate ownership is not proof of conformance; known wrong
implementations remain linked through the violation register. The configured
`critical_floor.representation_coverage` is `1.0`, so a new unit outside all declared block paths
breaks the architecture gate instead of being silently accepted as `unmapped`.

## 5. Link quality

- Descriptive link text (`Governance SAD D3`, not bare `architecture.md`).
- Evidence, UML, gate, and source mentions are Markdown links.
- After moves, repair inbound links and run architecture documentation gate.
- One concern has one active model path. Replaced views remain in Git, not beside the current view.
- End-to-end sequence views form a connected stimulus-to-response path and include critical
  no-write/degradation alternatives.

## 5.1 Freshness

Normative SADs record a reconciled Git commit. A change to an owned source path after that commit
marks the document stale until reviewed. Dates are display metadata, not a freshness proof.

## 6. Publication boundary

`docs/architecture` is **internal**. Do not copy SAD/ADR/UML/gate paths into `docs/user/`, `docs/start-here/`, or player-facing copy.

Direction of truth:

`implementation + tests → SAD → contracts/gates → technical stubs → audience docs`

## 7. Review checklist

| Check | Pass |
| --- | --- |
| Structure | Correct category; indexed from README or START-HERE |
| Ownership | One authoritative SAD per system |
| Completeness | 12 sections meaningful |
| No linklist SAD | Narrative explains context before tables |
| Status honesty | Observed/normative/target/violation/historical and implementation state explicit |
| Evidence | Claims link tests, UML, gates |
| Links | Resolve locally |
| Agent usability | Read order, owner, gaps clear without hidden context |
| Synthesis | §9 is an index, not the dominant body; abstraction levels are not mixed |
| Runtime closure | Critical sequence has connected request, response, failures and write boundary |
| Freshness | Reconciled commit and changed owned paths are checked |

## 8. Severity model

| Severity | Meaning |
| --- | --- |
| Blocker | Claims readiness without evidence; broken links; ownership ambiguity |
| Major | Missing traceability, gates, or §9 absorption |
| Minor | Wording/formatting only |
