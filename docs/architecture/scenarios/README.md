# Architecture runtime scenarios

Runtime scenarios are implementation-facing architecture slices. Each scenario records
preconditions, observed code path, normative target, state and data transitions, failures,
observability and executable acceptance evidence.

| Scenario | Owner | Status |
| --- | --- | --- |
| [Canonical player turn](canonical-turn.md) | World Engine | Pilot, target accepted / implementation partial |

New scenarios must not describe only a happy-path message chain. Critical alternatives and
no-write behavior are part of the architecture.
