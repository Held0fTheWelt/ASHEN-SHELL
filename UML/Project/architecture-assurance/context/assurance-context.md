# Architecture Assurance - Context

**Viewpoint:** `context`
**Concern:** Human intent, repository truth and disposable external AKDB

[PlantUML source](assurance-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Architect / Maintainer | State decisions, classify drift and approve target architecture | Reviewed SAD and model-catalog changes | [`docs/architecture/project/architecture-assurance/architecture.md`](../../../../docs/architecture/project/architecture-assurance/architecture.md) |
| Architecture Assurance | Discover, correlate, validate and export architecture evidence | Deterministic CLI and report schemas | [`tools/architecture_assurance/cli.py`](../../../../tools/architecture_assurance/cli.py) |
| Better Tomorrow Repository | Provide current code, documents and Git history | Read-only discovery except generated architecture artifacts | [`.git`](../../../../.git) |
| External AKDB | Validate and export canonical architecture knowledge | Pinned disposable checkout | [`tests/architecture_assurance/test_disposable_akdb_integration.py`](../../../../tests/architecture_assurance/test_disposable_akdb_integration.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Architect / Maintainer | Architecture Assurance | authors intent and runs audit | reviewed invocation | [`tools/architecture_assurance/cli.py`](../../../../tools/architecture_assurance/cli.py) |
| Architecture Assurance | Better Tomorrow Repository | discovers and correlates | source and Git evidence | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Architecture Assurance | External AKDB | validates disposable export | pinned external checkout | [`tests/architecture_assurance/test_disposable_akdb_integration.py`](../../../../tests/architecture_assurance/test_disposable_akdb_integration.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
