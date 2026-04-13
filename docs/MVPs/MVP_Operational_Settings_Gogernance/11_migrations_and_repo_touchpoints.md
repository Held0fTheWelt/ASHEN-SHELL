# 11 Migrations and Repo Touchpoints

## Migration groups

### Group A: bootstrap and trust-anchor
Tables:
- `bootstrap_configs`
- `bootstrap_presets` (optional seeded)
- `setting_audit_events`

### Group B: providers, credentials, models, routes
Tables:
- `ai_provider_configs`
- `ai_provider_credentials`
- `ai_model_configs`
- `ai_task_routes`

### Group C: settings and resolved runtime config
Tables:
- `system_setting_records`
- `resolved_runtime_config_snapshots` (optional cached)
- `provider_health_checks`

### Group D: usage and costs
Tables:
- `ai_usage_events`
- `cost_budget_policies`
- `cost_rollups`

## Index requirements

At minimum:
- provider lookups by `provider_id`, `provider_type`, `is_enabled`
- model lookups by `model_id`, `provider_id`, `is_enabled`
- route lookups by `task_kind`, `workflow_scope`, `is_enabled`
- usage events by `created_at`, `provider_id`, `model_id`, `workflow_scope`
- rollups by `rollup_date`, `provider_id`, `model_id`
- audit events by `changed_at`, `scope`, `target_ref`

## Backfill rules

This MVP mainly introduces new governed config rather than migrating all historical env values automatically.

Recommended backfills:
- seed default presets
- seed mock provider/model if absent
- optionally import known current provider base URLs from current env on first bootstrap

## Repo touchpoints

### Backend
Expected areas:
- models
- migrations
- settings governance services
- provider/model/routing services
- secret/crypto service
- runtime config resolution service
- usage/cost services
- admin APIs

### World-engine
Expected areas:
- runtime config fetch/refresh integration
- governed validator/retry/fallback settings consumption
- provider/model adapter construction from resolved config
- usage event emission hooks

### story_runtime_core / shared runtime
Expected areas:
- adapter construction must accept resolved config rather than own env-first assumptions
- registry defaults must stop being the authoritative operational source

### ai_stack
Expected areas:
- retrieval/governed runtime config consumption
- usage event emission where relevant

### administration-tool
Expected areas:
- bootstrap suite pages if applicable
- operational settings pages
- provider/model/route UI
- cost and health pages
- audit page

### docker-up.py
Expected areas:
- bootstrap detection
- web launch / CLI fallback
- stack start gating

## Compatibility rule

Existing env support may remain as a fallback for bootstrapping and deployment compatibility, but:
- it must not remain the primary operator-facing configuration method
- the system must make governed settings the canonical runtime source after initialization
