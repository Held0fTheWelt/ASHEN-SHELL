# Architecture Assurance - Export Sequence

**Viewpoint:** `sequence`
**Concern:** Audit, multi-format reporting, canonical export and external validation

[PlantUML source](export-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Architect / Maintainer | State decisions, classify drift and approve target architecture | Reviewed SAD and model-catalog changes | [`docs/architecture/project/architecture-assurance/architecture.md`](../../../../docs/architecture/project/architecture-assurance/architecture.md) |
| Architecture Assurance | Discover, correlate, validate and export architecture evidence | Deterministic CLI and report schemas | [`tools/architecture_assurance/cli.py`](../../../../tools/architecture_assurance/cli.py) |
| Audit Engine | Evaluate correspondence and model semantics | Stable findings and exit policy | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Report Exporters | Emit human, JSON, JUnit and SARIF evidence | Schema-stable deterministic serialization | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |
| Canon Exporter | Create idempotent AKDB source projection | Hash-stable destination manifest | [`tools/architecture_assurance/canon.py`](../../../../tools/architecture_assurance/canon.py) |
| External AKDB | Validate and export canonical architecture knowledge | Pinned disposable checkout | [`tests/architecture_assurance/test_disposable_akdb_integration.py`](../../../../tests/architecture_assurance/test_disposable_akdb_integration.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Architect / Maintainer | Architecture Assurance | authors intent and runs audit | reviewed invocation | [`tools/architecture_assurance/cli.py`](../../../../tools/architecture_assurance/cli.py) |
| Architecture Assurance | Audit Engine | evaluates current repository projection | complete deterministic audit report | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Audit Engine | Report Exporters | emits findings | normalized result model | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |
| Report Exporters | Canon Exporter | joins canonical evidence | accepted report state | [`tools/architecture_assurance/canon.py`](../../../../tools/architecture_assurance/canon.py) |
| Canon Exporter | External AKDB | round-trips canonical export | pinned disposable AKDB validation | [`tests/architecture_assurance/test_disposable_akdb_integration.py`](../../../../tests/architecture_assurance/test_disposable_akdb_integration.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
