# Architecture entry document

Use this route to distinguish target architecture, current implementation and historical intent.

| Question | Read first | Then inspect |
| --- | --- | --- |
| What system are we building? | [System SAD](system/architecture.md) | active ADRs |
| What does the code currently do? | owning component SAD | source anchors and scenario `Observed` path |
| Is the implementation known to be wrong or incomplete? | [Violation register](violations/README.md) | drift reconciliation and closure tests |
| Why does this path exist? | [Architecture lineage](evidence/architecture-lineage.md) | Git/AKDB evidence |
| How should a player turn work? | [Canonical turn scenario](scenarios/canonical-turn.md) | World Engine UML and SAD |
| Who may write which data? | [Data ownership](data/data-ownership.md) | ADR-0001 and component SAD |
| What is deployed and trusted? | [Deployment topology](data/deployment-topology.md) | security portfolio |
| Which decision is current? | [Active ADR index](decisions/README.md) | retired ADR only for history |
| How is architecture verified? | [Architecture Assurance portfolio](project/architecture-assurance/architecture.md) | assurance tests and evidence |

## Evidence order

For disputed behavior use this order:

1. executable current source and production-path test;
2. accepted system/component decision;
3. open violation and repair contract;
4. Git/AKDB lineage and historical artifacts.

Historical evidence can reveal lost intent or a regression. It cannot silently replace current
source or decide the target.

## Verification commands

```powershell
py -3.14 -m tools.architecture_assurance generate --dry-run
py -3.14 -m tools.architecture_assurance audit --dry-run
py -3.14 -m pytest tests/gates/test_architecture_documentation_gate.py -q --no-cov
```
