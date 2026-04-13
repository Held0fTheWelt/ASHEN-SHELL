# 09 Cost, Usage, and Budgeting

## Why cost governance is part of the MVP

The system allows flexible provider/model routing.
Without cost visibility, the operator cannot safely use:
- AI-only mode
- hybrid mode
- preview generation
- semantic validation
- research synthesis
- writers-room assistance

## Cost measurement methods

### `provider_reported`
Use provider-reported billing/usage when available.

### `price_table_estimated`
Compute cost from token counts and configured price tables.

### `flat_per_request`
Use a flat configured cost per request.

### `none`
No cost estimation available.

## Usage event minimum capture

Each eligible runtime call should create an `AIUsageEvent` capturing:
- provider
- model
- task kind
- workflow scope
- success/failure
- latency
- tokens if available
- retry used
- fallback used
- degraded mode used
- estimated/actual cost

## Rollups

At minimum support:
- daily provider rollups
- daily model rollups
- daily workflow rollups
- retry/fallback cost impact visibility

## Budget policies

Budgets should support:
- global daily limit
- global monthly limit
- provider-level budget
- workflow-level budget
- warning threshold %
- optional hard-stop behavior

## Alerts

At minimum:
- budget warning threshold reached
- monthly budget exceeded
- unexpectedly high fallback cost rate
- provider usage spike
- expensive route in cost-aware profile

## UI requirements

### Costs & Usage page must show
- daily/monthly totals
- provider comparison
- model comparison
- workflow comparison
- cost method used
- missing billing confidence note if estimated only
- top expensive routes
- retry/fallback contribution

## Runtime configuration impact

The resolved runtime config must include enough pricing and budget policy data to:
- attribute usage correctly
- block invalid cost modes
- drive alerts and health summaries
