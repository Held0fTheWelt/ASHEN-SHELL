# 55 — No-Stub Implementation Rules

This MVP must lead to real implementation work, not placeholder closure.

## Forbidden implementation patterns

- empty functions that only reserve names,
- `NotImplementedError` in a seam that the MVP presents as available behavior,
- docs that claim a route, tool, surface, or workflow exists when only a placeholder exists,
- test names that imply runtime support while the implementation path is still missing,
- “temporary” side paths that quietly become permanent architecture.

## Allowed placeholders

The MVP may describe future work at the product level, but it must not present an unavailable seam as if it were already implemented.
When a seam is not yet built in the real repository, the MVP must describe:
- who owns it,
- where it belongs,
- what contract it must satisfy,
- and how it will be validated.

## Scaffold rule

The scaffold is allowed because it is executable proof code.
It is not a placeholder. It exists to show the minimum runtime shape in running code.

## Repository rule

When a repository seam is chosen for implementation from this MVP, the result must be runnable code plus validation evidence.
