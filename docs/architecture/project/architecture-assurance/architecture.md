# Architecture Assurance — Software Architecture (arc42)

**Project capability:** Better Tomorrow architecture assurance

## 1. Introduction & Goals

Maintain a source-bound, machine-verifiable architecture corpus with the same
operational depth expected by current AKDB and Tiny Tool Development standards.

## 2. Constraints

AKDB is an external, pinned dependency. Tests may not access persistent AKDB
state. Documentation claims may never invent a source binding.

## 3. Context & Scope

The assurance tool reads Better Tomorrow SADs and implementation surfaces,
generates bindings and depth views, verifies canon drift and emits CI evidence.

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Executable architecture correspondence system for declarations, source bindings, semantic views, machine-readable drift edges, reports and canonical AKDB export.

**Authority rule:** Human-authored SAD decisions and the semantic model catalog define intent; source anchors and Git evidence establish implementation correspondence; generated evidence never invents authority.

**Git/archaeology scope:** `tools/architecture_assurance`, `tests/architecture_assurance`, `docs/architecture`, `UML`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Human intent, repository truth and disposable external AKDB | [Architecture Assurance - Context](../../../../UML/Project/architecture-assurance/context/assurance-context.md) | Human-authored SAD decisions and the semantic model catalog define intent; source anchors and Git evidence establish implementation correspondence; generated evidence never invents authority. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

## 4. Solution Strategy

Use deterministic standard-library tooling, versioned schemas and a single audit
result rendered to human-readable JSON, JUnit and SARIF.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Schema contracts | `tools/architecture_assurance/schemas.py` |
| SAD parser | `tools/architecture_assurance/sad_parser.py` |
| Source discovery | `tools/architecture_assurance/discovery.py` |
| Binding generator | `tools/architecture_assurance/manifest_builder.py` |
| Depth audit | `tools/architecture_assurance/audit.py` |
| Report renderers | `tools/architecture_assurance/reporters.py` |
| Canon projection | `tools/architecture_assurance/canon.py` |
| Command line | `tools/architecture_assurance/cli.py` |
| Assurance support | `tools/architecture_assurance/` |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound structural decomposition

Only elements that participate in a container or component view are listed as building blocks. Actors, runtime states, data types and deployment nodes remain in their proper viewpoints instead of being misrepresented as structural decomposition.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| Drift Edge Catalog (`drift_edges`) | `class` | Describe authority, proposal, projection and evidence flows | Resolvable model nodes, claim ids, source anchors and carried fields | [`tools/architecture_assurance/drift_edge_catalog.json`](../../../../tools/architecture_assurance/drift_edge_catalog.json) |
| Audit Engine (`audit`) | `component` | Evaluate correspondence and model semantics | Stable findings and exit policy | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Authority and Envelope Gate (`drift_gate`) | `component` | Resolve drift edges and reject competing writers or lost envelope fields | Source-bound topology with stable CI rule identifiers | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Binding Manifest Builder (`manifest`) | `component` | Bind SAD declarations to source, tests and views | One deterministic manifest per scope | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Canon Exporter (`canon`) | `component` | Create idempotent AKDB source projection | Hash-stable destination manifest | [`tools/architecture_assurance/canon.py`](../../../../tools/architecture_assurance/canon.py) |
| Report Exporters (`reports`) | `component` | Emit human, JSON, JUnit and SARIF evidence | Schema-stable deterministic serialization | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |
| Repository Discovery (`discovery`) | `component` | Enumerate implementation and document evidence | Ignored/local evidence excluded | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Semantic Model Catalog (`catalog`) | `component` | Define individualized elements, contracts, relations and viewpoints | Validated source-bound JSON with no retired placeholder evidence | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Semantic View Builder (`views`) | `component` | Project catalog models into PlantUML and companion documents | No generic inferred star graphs | [`tools/architecture_assurance/view_builder.py`](../../../../tools/architecture_assurance/view_builder.py) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Generate discovers source units and writes idempotent bindings and views. Audit
re-discovers the same units, compares their anchors, evaluates five depth axes
and renders the single result to requested formats.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| From authored intent and source discovery through drift invariants to classified evidence | `activity` | [Architecture Assurance - Audit Flow](../../../../UML/Project/architecture-assurance/activity/audit-flow.md) | 9 |
| Audit, multi-format reporting, canonical export and external validation | `sequence` | [Architecture Assurance - Export Sequence](../../../../UML/Project/architecture-assurance/sequence/export-sequence.md) | 5 |
| Intent, correlation, evaluation, export and later drift | `state` | [Architecture Assurance - Evidence Lifecycle](../../../../UML/Project/architecture-assurance/states/evidence-lifecycle.md) | 5 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. A sequence or activity view must form one connected runtime path; a list of unrelated calls does not qualify as an end-to-end scenario. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

The package runs from the repository in local quality gates and CI. CI checks
the locked AKDB revision into a separate directory only for disposable tests.
The same workflow downloads a version- and SHA-256-pinned PlantUML renderer,
renders every checked-in diagram to SVG outside the source tree, verifies
one preview per source, and publishes the checksum-indexed result as the
`better-tomorrow-uml-previews` artifact.

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

This scope does not claim an independently deployable runtime. Its deployment effect is expressed through the owning systems and the following implementation roots:

- `tools/architecture_assurance`
- `tests/architecture_assurance`
- `docs/architecture`
- `UML`

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

All paths are repository-relative; all JSON is key-sorted; every claimed
implemented or accepted declaration needs a real anchor; dry-run never writes.

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| Audit Engine | Report Exporters | emits findings | normalized result model | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |
| Correspondence Bindings | Audit Findings | produce gaps or proof | traceable evidence locations | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Semantic Model Catalog | Repository Discovery | scopes evidence | history roots and source anchors | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Semantic Model Catalog | Drift Edge Catalog | resolves drift topology | subsystem and element references | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Semantic Model Catalog | Semantic View Builder | projects viewpoints | semantic elements and edge contracts | [`tools/architecture_assurance/semantic_models.py`](../../../../tools/architecture_assurance/semantic_models.py) |
| Architecture Declarations | Correspondence Bindings | are grounded by | stable declaration ids | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Repository Discovery | Binding Manifest Builder | supplies inventory | normalized repository paths | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Drift Edge Catalog | Audit Findings | produce authority or envelope violations | stable gate findings with source locations | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Drift Edge Catalog | Authority and Envelope Gate | supplies authority and field-flow contracts | versioned drift-edge schema | [`tools/architecture_assurance/drift_edge_catalog.json`](../../../../tools/architecture_assurance/drift_edge_catalog.json) |
| Authority and Envelope Gate | Audit Engine | emits hard invariant findings | write-conflict and field-loss rules | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Binding Manifest Builder | Audit Engine | supplies declared correspondence | binding schema | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Report Exporters | Canon Exporter | joins canonical evidence | accepted report state | [`tools/architecture_assurance/canon.py`](../../../../tools/architecture_assurance/canon.py) |
| Semantic View Builder | Audit Engine | supplies analyzable models | view requirements and source links | [`tools/architecture_assurance/semantic_models.py`](../../../../tools/architecture_assurance/semantic_models.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

## 9. Architecture Decisions

### D1: Versioned architecture evidence contracts

**Status:** Accepted
**Origin:** Better Tomorrow AKDB modernization

Evidence artifacts use explicit Better Tomorrow schema versions and validation.
This makes every producer and consumer reject incompatible or incomplete
objects at the repository boundary. A bound claim must carry at least one valid
anchor, while a claimed-only entry is forbidden from carrying one. The
separation prevents status labels from masquerading as implementation evidence
and permits future schema evolution without silently changing the meaning of a
historical report. Evidence: `tools/architecture_assurance/schemas.py`.

### D2: File-only discovery and anti-fabrication bindings

**Status:** Accepted
**Origin:** Better Tomorrow AKDB modernization

Bindings are computed from parsed declarations and discoverable source anchors.
Unbound claims remain visibly `claimed_only`; discovery never fabricates a
symbol to improve a percentage. Supported lanes parse Python definitions and
routes, schema objects, content roots, web assets and deployment services. A
fresh discovery pass is compared with the committed manifest, so removed,
added or moved source surfaces become explicit drift findings. Representation
also requires either a declared owner or a written out-of-scope reason. Evidence:
`tools/architecture_assurance/discovery.py`,
`tools/architecture_assurance/manifest_builder.py`.

### D3: One result, three CI report formats

**Status:** Accepted
**Origin:** Better Tomorrow AKDB modernization

JSON, JUnit and SARIF are deterministic views of the same audit. They are not
three independently calculated checks: the structured report is evaluated
once, then rendered for archival evidence, test dashboards and code-scanning
annotations. Rule identifiers and source locations remain stable across
formats, while sorted serialization makes unchanged output byte-identical.
This avoids contradictory CI outcomes and lets local review reproduce the
exact evidence uploaded by automation. Evidence:
`tools/architecture_assurance/reporters.py`.

### D4: Dry-run is a non-writing execution mode

**Status:** Accepted
**Origin:** Better Tomorrow AKDB modernization

Every export path compares intended bytes and reports `would_write` without
mutation in dry-run mode. Generation still performs parsing, discovery,
validation and action planning, so dry-run exercises the real code path rather
than a superficial syntax check. Parent directories and destination files are
created only after that mode is excluded. CI combines dry-run with repository
tests that require every generated artifact to report `unchanged`, providing a
reviewable drift check without modifying a checkout. Evidence:
`tools/architecture_assurance/cli.py`.

### D5: Canon exports are idempotent

**Status:** Accepted
**Origin:** Better Tomorrow AKDB modernization

The canon manifest pins sorted paths, byte sizes and SHA-256. Re-export skips
matching files. Canon input selection comes from the project configuration,
every subsystem SAD, its bindings and every required view. Export preserves
repository-relative paths and writes only files whose digest differs, so a
second run is both semantically and operationally idempotent. Verification
reports missing and mismatched files separately and does not depend on an AKDB
service or database being available. Evidence:
`tools/architecture_assurance/canon.py`.

### D6: AKDB integration tests are strictly disposable

**Status:** Accepted
**Origin:** Better Tomorrow AKDB modernization

The integration fixture redirects every AKDB data and output path to a temporary
directory and verifies the external checkout remains clean. It asserts the
external Git revision against the lock, hashes all tracked files before and
after, snapshots persistent AKDB locations, disables cascades and automatic
exports, and uses a temporary SQLite database. Two independent canon exports
must have the same tree digest before verification against the fixture source.
No production or developer database is discovered, opened, copied or cleaned
by this test. Evidence:
`tests/architecture_assurance/test_disposable_akdb_integration.py`.

### D7: Semantic models require executable source correspondence

**Status:** Accepted
**Origin:** architecture synthesis repair and DRIFT-012

An existing file is insufficient implementation evidence when the file is a retired or empty
source placeholder. Element and relationship anchors must resolve to the current executable
implementation, an active contract, or an authoritative data/document source appropriate to the
view. The semantic catalog validator rejects known retired-shard markers. A source assembly or
unsharding migration must update model anchors in the same change that retires the old source.
Evidence: `tools/architecture_assurance/semantic_models.py` and
`tests/architecture_assurance/test_semantic_models_and_drift.py`.

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D1`, `D4` | Human intent, repository truth and disposable external AKDB | `context` | [Architecture Assurance - Context](../../../../UML/Project/architecture-assurance/context/assurance-context.md) |
| `D1`, `D2`, `D3`, `D7` | Discovery, correspondence, semantic projection, drift invariants, audit, reporting and canon seams | `component` | [Architecture Assurance - Components](../../../../UML/Project/architecture-assurance/components/assurance-components.md) |
| `D1`, `D2`, `D7` | From authored intent and source discovery through drift invariants to classified evidence | `activity` | [Architecture Assurance - Audit Flow](../../../../UML/Project/architecture-assurance/activity/audit-flow.md) |
| `D3`, `D4` | Audit, multi-format reporting, canonical export and external validation | `sequence` | [Architecture Assurance - Export Sequence](../../../../UML/Project/architecture-assurance/sequence/export-sequence.md) |
| `D1`, `D7` | Declarations, correspondence bindings, drift edges and explainable findings | `class` | [Architecture Assurance - Evidence Model](../../../../UML/Project/architecture-assurance/classes/evidence-model.md) |
| `D2`, `D3` | Intent, correlation, evaluation, export and later drift | `state` | [Architecture Assurance - Evidence Lifecycle](../../../../UML/Project/architecture-assurance/states/evidence-lifecycle.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

Critical subsystems require complete arc42 structure, full accepted binding and
representation coverage, a concern-complete individualized viewpoint suite,
reproducible discovery and a matching canon projection. Pinned census values
prevent silent regression, while the semantic gate prevents a high file count
from masking shallow or generic diagrams. No semantic element or edge may use a retired source
placeholder as implementation correspondence.

## 11. Risks & Technical Debt

Static discovery intentionally sees only supported source lanes. New languages
or generated surfaces require an explicit scanner before they can count.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

The previous migration proved file coverage while shallow star diagrams hid semantic gaps. This model separates discovery, correspondence, interpretation, drift-edge invariants, projection and export.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 353 | 87 | 636 | 0 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| `DRIFT-010` | `superseded` | Historical snapshots contain paths that no longer map to current architecture | Retain hashes, claim headings and path-diff evidence. Port only a claim or behavior after current-source reconciliation; never copy a full old package over HEAD. |
| `DRIFT-011` | `superseded` | MVP completion labels are not architecture authority | Use capability lifecycle states proposed, implemented, integrated, proven and regressed. Only production-path evidence advances a capability to proven. |
| `DRIFT-012` | `confirmed_current` | Architecture coverage metrics can hide shallow semantics | Keep model selection concern-driven and source-bound. Coverage remains supporting evidence; semantic analyzability, drill-down and correspondence determine acceptance. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

**Binding:** verified link from a declaration to source. **Canon:** deterministic
architecture file projection. **Disposable:** isolated state destroyed after a
test. **Depth view:** bounded, source-linked model rather than a label sketch.
