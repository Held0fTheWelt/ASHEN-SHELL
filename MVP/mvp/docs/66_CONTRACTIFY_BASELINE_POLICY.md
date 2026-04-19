# Contractify Baseline Policy

Contractify is adopted in this package as the primary contract-governance suite.

## What Contractify is expected to do in this MVP

- discover anchored and projected contracts,
- record relation edges between documents, code boundaries, tests, and machine surfaces,
- identify drift signals,
- support version-aware comparison,
- and provide a stronger basis for re-audit after each implementation wave.

## Required uses

At minimum, each major implementation wave should use Contractify to keep these chains visible:

- `source_of_truth`
- `documented_in`
- `implemented_by`
- `validated_by`
- `projected_as`

## MVP-relevant contract zones

Contractify should be especially used for:

- world-engine authority boundaries,
- backend ↔ world-engine contracts,
- player-visible vs operator/internal surface distinctions,
- memory and state mutation rules,
- AI-stack runtime-turn seams,
- governance and approval boundaries,
- and test/acceptance evidence links.

## Success condition

The package is considered healthier when implementation changes can be traced across:

normative document → repository surface → tests/evidence → follow-up audit.
