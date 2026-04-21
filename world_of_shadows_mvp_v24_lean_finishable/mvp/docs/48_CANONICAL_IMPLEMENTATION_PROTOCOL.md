# 48 — Canonical Implementation Protocol

## Role

Implement World of Shadows by changing real code in the real owning component.
The MVP is the source of truth for what to build, where it belongs, and how it is accepted.

## Constitutional implementation laws

Every implementation must respect:
1. One truth boundary.
2. Commit is truth.
3. Turn 0 is canonical.
4. Ordinary player route purity.
5. Publish-bound authoritative birth.
6. Fail closed on authority seams.
7. Fail closed on internal auth.
8. Degraded-safe stays explicit.
9. Story persistence incidents stay visible.
10. Non-graph seams remain testable.
11. Payloads self-classify.
12. Release honesty is mandatory.

## Non-negotiable operating rules

- Patch the owning repository component.
- Prefer extending an existing seam over creating a parallel implementation.
- Preserve world-engine authority.
- Do not hide degraded or partial behavior behind success-shaped responses.
- Do not let docs overstate what code and tests do.
- Keep player and operator audiences cleanly separated.

## Accepted implementation inputs

### Audit finding
Translate the finding into owner, target files, tests, and validation commands.

### Feature request
Implement the feature across code, config, tests, and any required implementation-facing documentation.

## Execution sequence

1. Identify the target component.
2. Read the owning contract chapters in this MVP.
3. Inspect the current repository seam and its tests.
4. Patch the true owner.
5. Add or update tests.
6. Validate with the component suite and any required smoke/e2e coverage.
7. Update implementation-facing docs only after the behavior is real.

## Minimum acceptable output for implementation work

- exact files changed,
- implemented behavior,
- tests added or updated,
- commands actually run,
- concise honesty note about anything not validated.
