# 59 — Next Work-Field Selection Policy

## Purpose

The next work field must be selected by implementation value, not by novelty or document volume.

## Primary criteria

Rank candidate work fields by the following factors:

1. **Runtime criticality**
   - Does the field affect authoritative turn truth, validation, commit discipline, or runtime continuity?

2. **Architectural centrality**
   - Does the field sit on a core seam that many other capabilities depend on?

3. **Unblock value**
   - Will implementing it unlock multiple downstream fields?

4. **Implementation readiness**
   - Is the field constrained enough that another AI can implement it without inventing the system?

5. **Evidence deficit**
   - Is the current weakness mainly missing proof, missing code, or both?

6. **Dependency structure**
   - Does the field have upstream prerequisites that must be settled first?

7. **Improvement leverage**
   - Will this field materially increase runtime capability rather than merely broadening conceptual scope?

## Tie-breaker rule

If multiple candidates are close, prioritize the one that most directly strengthens:
- runtime authority,
- validation/commit correctness,
- or testable end-to-end behavior.

## Anti-patterns

Do not choose the next field simply because it is:
- thematically exciting,
- broad,
- heavily discussed,
- or easy to describe in abstract terms.

## Recommended decision output

Each audit should explicitly say:
- which field is next,
- why it is next,
- what concrete gain it should create,
- and why the other top candidates are not first priority yet.
