# 13 Architecture Decisions

## ADR-001: Split bootstrap from normal operations
**Decision:** The suite separates bootstrap/trust-anchor setup from normal operational governance.

**Why:** Bootstrap concerns are security-sensitive and low-frequency. Normal operations are frequent and broader.

## ADR-002: Resolved Runtime Config is the MVP execution model
**Decision:** Backend resolves effective runtime config; runtime services consume resolved config.

**Why:** This centralizes governance without forcing a full backend LLM gateway in the MVP.

## ADR-003: Credentials are backend-held and write-only from UI
**Decision:** Provider secrets are encrypted in backend-controlled storage and never re-rendered raw.

**Why:** Operators need configurability without secret leakage.

## ADR-004: Mock / AI / Hybrid are explicit governed modes
**Decision:** Runtime execution mode is a first-class admin setting.

**Why:** The current system has distributed mode behavior. This must become explicit.

## ADR-005: `docker-up.py` is the canonical bootstrap entry point
**Decision:** Fresh-start discoverability is anchored in `docker-up.py`.

**Why:** Operators naturally look there first; they should not need to discover hidden setup paths.

## ADR-006: Presets are first-class bootstrap helpers
**Decision:** Bootstrap includes preset-driven setup.

**Why:** The system has multiple realistic operation modes and should not force low-level manual assembly at first launch.

## ADR-007: Costs are part of governance, not a later add-on
**Decision:** Usage and cost metering are included in the MVP.

**Why:** Provider/model flexibility without cost visibility is operationally unsafe.

## ADR-008: Some trust-root values remain outside normal admin operations
**Decision:** KEK roots and similar deployment-trust anchors are not treated as ordinary operator settings.

**Why:** They are higher-security bootstrap concerns and should not be mixed casually into day-to-day UI administration.
