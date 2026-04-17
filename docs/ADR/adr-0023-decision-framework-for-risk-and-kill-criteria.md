# ADR-0023: Decision Framework — risk framing and kill criteria

Date: 2026-04-17

Status: Accepted

## Context

The NextVision Suite's risk and mitigation documentation defines a decision framework for evaluating new initiatives and kill criteria for continuing work. This framework guides go/no-go decisions across phases.

## Decision

- Adopt a lightweight decision framework requiring explicit answers for: introduced risks, mitigations, worst-case scenarios, recoverability, and acceptability given upside.
- Use stated "Kill criteria" (3 consecutive phase failures, unit economics broken, fundamental technical impossibility, or market shift) as formal stop conditions for projects.
- Document risk acceptance levels and monitoring cadence in project roadmaps.

## Rationale

- Standardizes decision-making across projects, enabling consistent go/no-go evaluation.
- Provides clear exit criteria that are objective and testable.

## Consequences

- Teams must include explicit risk assessments and recovery plans in decision artifacts.
- Project dashboards must track monitoring indicators tied to the framework.

## Migrated from

`docs/MVPs/future/NextVision-Suite/09_risks_and_mitigation.md` ("Decision Framework")

---

(Automated migration entry created 2026-04-17)
