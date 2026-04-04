# Improvement Loop in World of Shadows

Status: Canonical Milestone 10 architecture and implementation baseline.

## Canonical loop

1. Select baseline (`baseline_id`, e.g. `god_of_carnage`).
2. Create candidate variant with explicit lineage.
3. Execute sandbox experiment (isolated from authoritative publish state).
4. Evaluate run outputs with concrete metrics.
5. Build recommendation package for governance review.
6. Expose packages through backend governance API.

## Variant and experiment model

Implemented JSON-backed models:

- Variant:
  - `variant_id`
  - `baseline_id`
  - `candidate_summary`
  - `metadata`
  - `lineage`
  - `review_status`
- Experiment:
  - `experiment_id`
  - `variant_id`
  - `baseline_id`
  - sandbox transcript
  - execution metadata
- Recommendation package:
  - baseline and candidate references
  - evaluation payload
  - recommendation summary
  - governance review state

## Sandbox execution boundary

Sandbox experiments run through controlled simulation (`execution_mode=sandbox`) and are explicitly marked non-authoritative (`publish_state=isolated_non_authoritative`).

No direct live publish mutation occurs in this path.

## Evaluation dimensions implemented

- `guard_reject_rate`
- `trigger_coverage`
- `repetition_signal`
- `structure_flow_health`
- `transcript_quality_heuristic`
- `scene_marker_coverage`
- notable failure flags

## Recommendation and review package

Packages include:

- baseline reference,
- candidate reference,
- experiment reference,
- evaluation evidence and metrics,
- recommendation summary (`promote_for_human_review` or `revise_before_review`),
- governance review status (`pending_governance_review`).

## Governance integration surface

Backend APIs:

- `POST /api/v1/improvement/variants`
- `POST /api/v1/improvement/experiments/run`
- `GET /api/v1/improvement/recommendations`

These provide governance-side inspection and decision support without automatic publish.

## Deferred beyond M10

- richer statistical experiment comparison across large run sets,
- dedicated admin UI for recommendation triage and approvals,
- robust persistent database-backed experiment storage and migrations.
