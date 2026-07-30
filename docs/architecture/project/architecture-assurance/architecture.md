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

## 6. Runtime View

Generate discovers source units and writes idempotent bindings and views. Audit
re-discovers the same units, compares their anchors, evaluates five depth axes
and renders the single result to requested formats.

## 7. Deployment View

The package runs from the repository in local quality gates and CI. CI checks
the locked AKDB revision into a separate directory only for disposable tests.

## 8. Crosscutting Concepts

All paths are repository-relative; all JSON is key-sorted; every claimed
implemented or accepted declaration needs a real anchor; dry-run never writes.

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

## 10. Quality Requirements

Critical subsystems require complete arc42 structure, full accepted binding and
representation coverage, four model-depth views, reproducible discovery and a
matching canon projection. Pinned census values prevent silent regression.

## 11. Risks & Technical Debt

Static discovery intentionally sees only supported source lanes. New languages
or generated surfaces require an explicit scanner before they can count.

## 12. Glossary

**Binding:** verified link from a declaration to source. **Canon:** deterministic
architecture file projection. **Disposable:** isolated state destroyed after a
test. **Depth view:** bounded, source-linked model rather than a label sketch.
