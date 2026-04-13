# 12 Acceptance Criteria and Rollout

## Acceptance criteria

### Bootstrap
- A fresh system clearly indicates that bootstrap is required.
- `docker-up.py` can guide the operator into setup.
- A web-first bootstrap path exists or a clear CLI fallback exists.
- Bootstrap completion is persisted and inspectable.

### Secrets
- Provider credentials are write-only from admin UI.
- Credentials are encrypted at rest.
- Raw credential values are never returned by normal APIs.
- Rotation is supported and audited.

### Modes
- Operator can choose between mock, AI, and hybrid through admin-governed settings.
- Mode changes are validated against real provider/model/route availability.
- Current effective mode is visible.

### Providers / models / routes
- Providers can be enabled, disabled, and health-tested.
- Models are configurable and role-tagged.
- Routes can be assigned and validated.
- Resolved runtime config can be inspected without exposing secrets.

### Backend / world-engine settings
- Operationally relevant backend and world-engine settings are visible and editable through governance APIs/UI.
- Hidden code defaults are reduced in favor of governed settings.

### Costs
- Usage events are recorded for supported workflows.
- Costs are measurable via a declared cost method.
- Rollups and budgets are visible.
- Alerts exist for threshold breaches.

### Discoverability
- Operator can find bootstrap/trust-anchor configuration path without searching source code.
- Administration-tool surfaces the normal post-bootstrap operational settings.

### Safety
- Deployment-only trust-root secrets are not casually exposed as day-to-day admin toggles.
- The boundary between trust-anchor setup and normal administration is explicit.

## Rollout order

1. add schema and services
2. seed presets and mock-safe defaults
3. add bootstrap detection to `docker-up.py`
4. add bootstrap UI
5. add providers/models/routes/settings pages
6. switch world-engine/backend runtime consumers to resolved config
7. enable usage/cost metering
8. de-emphasize legacy env-first operator workflows in docs

## Open risks

- Some environments may still require temporary env fallback during migration.
- External secret manager support may lag behind same-DB/separate-DB encrypted modes.
- Cost reporting quality differs by provider.
- Provider-specific health checks may need custom logic.
