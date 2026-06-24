# Architecture Documentation Quality Standard

Acceptance bar for documents under `docs/architecture/`. Adapted from Tiny Tool Development
[QUALITY-STANDARD](https://github.com/) patterns for World of Shadows component and project SADs.

## 1. Scope

Applies to:

- component SADs under `components/<system>/architecture.md`;
- project SADs under `project/<system>/architecture.md`;
- `contracts/`, `gates/`, `boundaries/`, `integrations/`, `combinations/`, `operations/`, `evidence/`, `views/`;
- `project/TRACEABILITY.md`, `project/ROLLOUT.md`, `DOC-HEALTH.md`.

## 2. Document ownership

| Document kind | Owner |
| --- | --- |
| Deployable component | `components/<system>/architecture.md` |
| Cross-cutting process | `project/<system>/architecture.md` |
| Normative contract | `contracts/` linked from owning SADs |
| Gate | `gates/` linked from contract or SAD |
| Boundary / integration | `boundaries/` or `integrations/` routing to SAD §9 |
| Migration audit | `evidence/` with inputs, findings, follow-up |

One source of truth per topic. Cross-category documents route to the owning SAD decision.

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

Each `### Dn:` block in §9 must include:

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
| `Implemented` | Linked implementation and verification exist |
| `Partially implemented` | Implemented vs missing parts separated |
| `Target-state` | Must not imply production readiness |

Non-trivial workflows need UML or an explicit pending gap in the SAD.

## 5. Link quality

- Descriptive link text (`Governance SAD D3`, not bare `architecture.md`).
- Evidence, UML, gate, and source mentions are Markdown links.
- After moves, repair inbound links and run architecture documentation gate.

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
| Status honesty | Implemented/partial/target explicit |
| Evidence | Claims link tests, UML, gates |
| Links | Resolve locally |
| Agent usability | Read order, owner, gaps clear without hidden context |

## 8. Severity model

| Severity | Meaning |
| --- | --- |
| Blocker | Claims readiness without evidence; broken links; ownership ambiguity |
| Major | Missing traceability, gates, or §9 absorption |
| Minor | Wording/formatting only |
