# Quality Gates architecture models

Layered test discovery, execution, evidence and CI policy for repository, subsystem, contract, architecture and end-to-end quality.

**Architecture authority:** The central runner and declared CI matrix define executed scope; presence-only tests and isolated green suites are not proof of system quality.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Developer verification through one authoritative gate system | `context` | [Quality Gates - Context](context/quality-context.md) | D1 |
| Selection, execution, boundary proof, evidence and CI promotion | `component` | [Quality Gates - Components](components/quality-components.md) | D1, D2 |
| Every selected suite is executed and reported before promotion | `activity` | [Quality Gates - Validation Flow](activity/validation-flow.md) | D1 |
| Suite definitions, exact executions and actionable findings | `class` | [Quality Gates - Evidence Model](classes/evidence-model.md) | D2 |
| Declared and selected suites cannot silently bypass execution | `state` | [Quality Gates - Lifecycle](states/gate-lifecycle.md) | D2 |

## Drift focus

Historical audits repeatedly found undiscovered tests, mock-only integration and runner divergence. Models expose suite ownership, promotion and evidence semantics.

[Decision/view/source traceability](TRACEABILITY.md)
