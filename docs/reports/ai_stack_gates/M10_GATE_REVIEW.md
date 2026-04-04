# Milestone 10 Gate Review

Date: 2026-04-04  
Status: PASS  
Recommendation: Proceed

## Scope delivered

- Added canonical improvement loop architecture document:
  - `docs/architecture/improvement_loop_in_world_of_shadows.md`
- Added operational improvement service with variant/experiment/evaluation/package flow:
  - `backend/app/services/improvement_service.py`
- Added governance-facing improvement API endpoints:
  - `backend/app/api/v1/improvement_routes.py`
  - `POST /api/v1/improvement/variants`
  - `POST /api/v1/improvement/experiments/run`
  - `GET /api/v1/improvement/recommendations`
- Registered routes in API blueprint:
  - `backend/app/api/v1/__init__.py`
- Added automated tests for lifecycle and governance accessibility:
  - `backend/tests/test_improvement_routes.py`

## Prerequisite verification summary

- M9 Writers-Room unified stack remains functional.
- M8 capability/governance surfaces remain functional.
- Session governance endpoints remain passing.

## Design decisions

- First-generation improvement storage uses structured JSON artifacts under `backend/app/var/improvement` for deterministic operational behavior.
- Sandbox execution is explicit and isolated (`publish_state=isolated_non_authoritative`).
- Evaluation metrics are concrete and exposed in recommendation package payloads.
- Recommendation packages are review-oriented artifacts and never auto-publish state changes.

## Migrations or compatibility shims

- No destructive migration required in M10; JSON-backed operational model establishes coherent lineage and enables later DB migration.

## Tests run

```bash
python -m pytest "backend/tests/test_improvement_routes.py" "backend/tests/test_writers_room_routes.py" "backend/tests/test_session_routes.py" -q --tb=short
```

Result: all commands passed.

## Acceptance criteria status

| Criterion | Status |
|---|---|
| Variants/experiments modeled coherently | Pass |
| Sandbox/controlled evaluation path is real | Pass |
| Evaluation/report outputs are concrete | Pass |
| Human-reviewable recommendation packages exist | Pass |
| Automated tests prove loop operation | Pass |

## Required milestone-specific answers

### What exact improvement loop is now canonical?

- `create variant -> run sandbox experiment -> evaluate metrics -> generate recommendation package -> list package from governance API`.

### How are variants linked to baselines and evaluations?

- Variant stores `baseline_id` and lineage.
- Experiment stores both `variant_id` and `baseline_id`.
- Recommendation package embeds candidate and baseline references plus evaluation payload.

### What metrics/heuristics are truly implemented?

- `guard_reject_rate`
- `trigger_coverage`
- `repetition_signal`
- `structure_flow_health`
- `transcript_quality_heuristic`
- `scene_marker_coverage`
- notable failure flags

### What governance surface now receives outputs?

- `GET /api/v1/improvement/recommendations` exposes recommendation packages for governance-side inspection.

### What remains deferred before full product-grade experimentation?

- persistent relational storage and migrations,
- richer comparative analytics across many variants/runs,
- dedicated admin UI for review decisions and approvals.

## Known limitations

- Current sandbox uses deterministic simulation rather than high-fidelity multi-agent runtime playback.

## Risks left open

- Scaling and analytics depth will require stronger persistence/query infrastructure and richer governance UX.
