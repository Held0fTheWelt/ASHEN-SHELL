# Architecture documentation

Internal architecture authority for Better Tomorrow / World of Shadows.

## Canonical reading order

1. [System SAD](system/architecture.md) — one whole-system arc42 architecture.
2. [Runtime scenarios](scenarios/README.md) — implementation-facing behavior and failures.
3. Owning component SAD — local structure and code correspondence.
4. [Active ADR](decisions/README.md) — target decision and trade-offs.
5. [Violation register](violations/README.md) — known difference between code and target.
6. [UML package](../../UML/README.md) and [data ownership](data/data-ownership.md).
7. Tests, generated bindings and [evidence](evidence/README.md).

Historical ADRs, MVP packages and Git/AKDB snapshots explain origin. They do not override the
system SAD or an active ADR.

## Architecture layers

| Layer | Purpose | Authority |
| --- | --- | --- |
| `system/` | product boundary, quality goals, system decomposition and current/target posture | whole-system normative |
| `components/` | deployable or explicitly owned implementation portfolio | local normative, subordinate to system |
| `scenarios/` | L3 runtime paths, state, failure and data correspondence | normative scenario contract |
| `data/` | data ownership, writer and deployment/trust topology | normative boundary contract |
| `concepts/` | crosscutting routing to detailed portfolios | normative through linked ADR/SAD |
| `decisions/` | active decisions with independent implementation state | normative target |
| `violations/` | known nonconformance and repair evidence | current architecture state |
| `contracts/` | versioned cross-service contracts | normative interface |
| `project/` | detailed process, governance and evidence portfolios | supporting, not peer system SADs |
| `evidence/` | generated provenance, drift and audit results | descriptive evidence |

## Component and module catalog

| Scope | Runtime kind | Architecture portfolio | UML |
| --- | --- | --- | --- |
| World Engine | deployable, live-story authority | [SAD](components/world-engine/architecture.md) | [models](../../UML/Components/world-engine/README.md) |
| Backend | deployable platform/control plane | [SAD](components/backend/architecture.md) | [models](../../UML/Components/backend/README.md) |
| Frontend | deployable player/public UI | [SAD](components/frontend/architecture.md) | [models](../../UML/Components/frontend/README.md) |
| Administration Tool | deployable operator UI | [SAD](components/administration-tool/architecture.md) | [models](../../UML/Components/administration-tool/README.md) |
| MCP Server | deployable/local adapter | [SAD](components/mcp-server/architecture.md) | [models](../../UML/Components/mcp-server/README.md) |
| AI Stack | runtime collaborator/package | [SAD](components/ai-stack/architecture.md) | [models](../../UML/Components/ai-stack/README.md) |
| Story Runtime Core | shared library | [SAD](components/story-runtime-core/architecture.md) | [models](../../UML/Components/story-runtime-core/README.md) |
| Content Authority | authored data/compiler boundary | [SAD](components/content-authority/architecture.md) | [models](../../UML/Components/content-authority/README.md) |
| Model Governance | backend module | [portfolio](components/model-governance/architecture.md) | [models](../../UML/Components/model-governance/README.md) |
| Architecture Assurance | repository toolchain | [portfolio](project/architecture-assurance/architecture.md) | [models](../../UML/Project/architecture-assurance/README.md) |

## Current posture

The documentation and assurance pipelines are structurally operational, but the product
architecture is not declared fully conforming. Known conflicts and proof gaps are listed in the
[violation register](violations/README.md). `Accepted` decisions and green documentation gates must
not be read as blanket implementation correctness.

## Verification

```powershell
py -3.14 -m tools.architecture_assurance audit --dry-run
py -3.14 -m pytest tests/gates/test_architecture_documentation_gate.py -q --no-cov
```

[Quality standard](QUALITY-STANDARD.md) · [Fast entry](START-HERE.md) ·
[Health](DOC-HEALTH.md) · [Rollout](project/ROLLOUT.md)
