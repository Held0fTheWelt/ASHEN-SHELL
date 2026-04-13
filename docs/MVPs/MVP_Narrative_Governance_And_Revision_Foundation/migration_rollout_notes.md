# Narrative Governance Migration and Compatibility Notes

## Schema change summary

- Added migration `042_narrative_governance_foundation.py` after revision `041`.
- Migration `042` introduces additive governance tables:
  - `narrative_packages`
  - `narrative_package_history_events`
  - `narrative_previews`
  - `narrative_revision_candidates`
  - `narrative_revision_conflicts`
  - `narrative_revision_status_history`
  - `narrative_evaluation_runs`
  - `narrative_evaluation_coverage`
  - `narrative_notification_rules`
  - `narrative_notifications`
  - `narrative_runtime_health_events`
  - `narrative_runtime_health_rollups`

## Migration ordering

1. Existing chain through `041` remains unchanged.
2. Apply `042` in additive-only deployment.
3. Deploy backend/world-engine code capable of handling empty narrative tables.
4. Import/backfill historical package metadata where artifacts exist.
5. Enable governance UI sections and mutation workflows.

## Indexing and query posture

- Added indexes for module-scoped package history, revision filtering, conflict lookups, notification feeds, and runtime health windows.
- Compound indexes are used for high-frequency operator queries:
  - module + status
  - module + target
  - module + window_start
  - acknowledged/severity + created_at feeds

## Backward compatibility expectations

- Existing `game_experience_templates` governance flow remains intact and additive.
- New narrative governance APIs operate in parallel and do not remove existing routes.
- Admin pages are resilient to empty narrative tables by design.

## Mixed-version rollout behavior

- Backend can return empty envelopes for narrative endpoints before backfill.
- World-engine internal narrative endpoints initialize runtime registries lazily, allowing safe startup before package artifacts exist.
- Rollback and preview load endpoints fail explicitly when artifacts are incomplete or missing.

## Rollback behavior

- Migration rollback (`downgrade`) drops only new narrative governance tables/indexes.
- Runtime rollback flow (`/api/v1/admin/narrative/packages/<module_id>/rollback-to/<version>`) validates artifact completeness before pointer changes.
- Package history remains append-only for successful promotion/rollback operations.
