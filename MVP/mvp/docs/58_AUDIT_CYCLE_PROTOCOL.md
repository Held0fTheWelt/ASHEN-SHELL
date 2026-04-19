# 58 — Audit Cycle Protocol

## Purpose

World of Shadows needs a controlled improvement cycle instead of isolated one-off audits.
This protocol defines that cycle.

## Role separation

### Audit system
The audit system:
- inspects the MVP and repository-facing evidence,
- records the current state,
- chooses the next work field,
- generates a master prompt for a separate implementation AI,
- and re-audits the result afterward.

The audit system does **not** implement the work itself.

### Implementation AI
The implementation AI:
- performs the actual code, document, and test work requested in the handoff,
- stays inside the target architecture,
- and returns changed material plus evidence.

## Cycle

1. Audit current state.
2. Classify maturity by work field.
3. Select the next implementation target.
4. Generate an implementation master prompt.
5. Hand the work to a separate implementation AI.
6. Receive updated files, bundle, or patch set.
7. Re-audit against the prior instruction.
8. Record delta, drift, gains, and remaining gaps.
9. Either continue the same field or choose the next field.

## Short-horizon continuity rule

The audit system must keep its own prior instruction in view over the short cycle horizon.
It must compare:
- what it asked for,
- what the implementation AI returned,
- what changed in evidence,
- and what still remains incomplete.

## Minimum required outputs per audit cycle

- current-state verdict
- work-field maturity matrix
- next priority decision
- implementation handoff prompt
- re-audit checklist
- delta note versus the prior cycle

## Failure modes the audit must catch

- text expansion without implementation depth
- renamed files without improved runtime behavior
- catalog growth without behavioral constraints
- tests that do not touch the claimed behavior
- claims of completeness unsupported by owning-component evidence
- architectural drift away from authoritative runtime law
