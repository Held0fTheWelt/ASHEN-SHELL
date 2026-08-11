# Crosscutting architecture portfolios

Files under `project/` describe crosscutting processes, assurance systems and evidence programs.
They are not automatically independent product systems and do not override the
[whole-system SAD](../system/architecture.md).

| Portfolio | Classification | Authority route |
| --- | --- | --- |
| ecosystem-topology | legacy whole-system decomposition, being absorbed | System SAD |
| governance | crosscutting concept | active ADR lifecycle |
| documentation-supply-chain | repository process | ADR-0006 |
| quality-gates | verification concept/tooling | quality contracts |
| observability-traceability | crosscutting concept | ADR-0005 |
| security-governance | crosscutting concept | security decisions |
| mvp-live-runtime-completion | evidence program/history | component SADs and active ADRs |
| architecture-assurance | repository toolchain | ADR-0006 |

Every portfolio must state whether a claim is observed, normative, target or historical. Program
completion labels are never architecture authority.

[Portfolio rollout](ROLLOUT.md) · [Architecture lineage](../evidence/architecture-lineage.md)
