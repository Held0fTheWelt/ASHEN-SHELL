# Operational Settings, Bootstrap & AI Runtime Governance MVP Suite

This suite replaces fragmented `.env`-first configuration and hidden code defaults with a single operational governance MVP.

## Core intent

The system must be:
- easy to bootstrap
- secure by default
- admin-configurable after first start
- flexible across mock, AI, and hybrid modes
- explicit about costs, routing, retrieval, validation, and runtime behavior
- recoverable when the user does not know where configuration lives

## What this suite covers

- Bootstrap / trust-anchor initialization
- `docker-up.py` guided setup flow
- Web-first bootstrap UI
- Encrypted backend-held provider credentials
- Settings governance for backend, world-engine, AI runtime, retrieval, notifications, and operator health
- Runtime mode selection: mock, AI, hybrid
- Model/provider/routing governance
- Cost and usage metering
- Admin UI surfaces
- Standard success and error envelopes
- Endpoint-level request/response examples
- Error code catalog
- Migrations, rollout order, and repo touchpoints
- Acceptance criteria and closure checklist

## Document map

- `01_scope_and_goals.md`
- `02_architecture_and_trust_model.md`
- `03_data_contracts.md`
- `04_api_catalog.md`
- `05_admin_bootstrap_and_ui.md`
- `06_runtime_modes_and_routing.md`
- `07_settings_inventory_backend_world_engine_ai.md`
- `08_secret_storage_and_crypto.md`
- `09_cost_usage_and_budgeting.md`
- `10_docker_up_bootstrap_flow.md`
- `11_migrations_and_repo_touchpoints.md`
- `12_acceptance_criteria_and_rollout.md`
- `13_architecture_decisions.md`
- `14_error_codes.md`

## Key simplification principle

This MVP intentionally simplifies the user experience by splitting configuration into two planes:

1. **Bootstrap / Trust-Anchor Plane**
   - initial setup only
   - easy to find
   - safe, guided, limited scope
   - launched from `docker-up.py`
   - optionally reopened in protected mode

2. **Operational Governance Plane**
   - normal administration after bootstrap
   - lives in the administration-tool
   - persists settings in backend-controlled stores
   - governs providers, models, routing, runtime, retrieval, costs, notifications, and health

## Non-goals

This suite does not attempt to move every deployment-only root secret into day-to-day admin UX.
Some trust-root values remain deployment-controlled, but the system must make that boundary obvious and searchable.

## Recommended implementation order

1. Bootstrap/trust-anchor models and APIs
2. Secret storage and crypto services
3. Runtime mode, provider, model, and route governance
4. Backend/world-engine settings governance
5. Cost/usage metering and budget alerts
6. Bootstrap UI and `docker-up.py` integration
7. Administration-tool operational settings pages
8. Tests, rollout docs, and closure proof

## Freeze notes for this revision

This revision adds the final implementation-readiness polish requested by architecture review:
- concrete example JSON requests and responses in the API catalog
- a dedicated error code catalog
- sharper crypto implementation defaults and key rotation guidance
