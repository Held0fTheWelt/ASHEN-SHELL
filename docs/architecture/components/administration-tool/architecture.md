# administration-tool — Software Architecture (arc42)

**Component:** administration-tool · **Folder:** `administration-tool/` · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Operator/admin UI: diagnostics, governance panels, play service controls, content management views—all
via backend APIs only.

Operators inspect live diagnostics through backend-proxied routes so credentials and rate limits stay
centralized. The administration tool does not embed world-engine secrets; it mirrors whatever governance
APIs expose for the active deployment profile.

## 2. Constraints

No direct world-engine commit path for operators unless via documented backend proxy routes.

## 3. Context & Scope

In scope: `route_registration*.py`, manage templates/static. Out of scope: player play UX.

## 4. Solution Strategy

Split route registration into proxy/pages/manage/security modules (despaghettify DS-004 pattern).
Static manage decks load diagnostics incrementally so large trace payloads do not block first paint.
Every destructive operator action routes through backend confirmation endpoints.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Routes | `route_registration.py`, `route_registration_*.py` |
| Manage UI | `templates/`, `static/manage_*.js` |

## 6. Runtime View

Operator browser → administration-tool → backend governance routes → optional read of play diagnostics.

## 7. Deployment View

Separate Flask app; backend URL configuration.

## 8. Crosscutting Concepts

Narrative gov operator truth ([mvp-live-runtime-completion MVP4-010](../../project/mvp-live-runtime-completion/architecture.md#mvp4-010-narrative-gov-operator-truth-surface)).

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Debug panel UI bounds | Accepted | ADR-0020 |
| D2 | Admin security control plane | Accepted | ADR-0052 |

### D1: Debug Panel UI — bounded diagnostics in session UI

**Status:** Accepted
**Origin:** ADR-0020 (retired 2026-06-23)

**Context.** Workstream W3 introduced a bounded debug panel for playable sessions that renders developer-facing diagnostics and player-visible summaries from canonical presenter output (`DebugPanelOutput`). The panel must be accessible, minimally invasive, and strictly driven by canonical data contracts.

**Decision.** - Render a collapsible debug panel into the session UI driven solely by `DebugPanelOutput` from `present_debug_panel(session_state)`.
- Use native HTML `<details>/<summary>` for collapsible diagnostics; summary always visible, diagnostics collapsed by default.
- The panel fields are strictly limited to the `DebugPanelOutput` schema (primary_diagnostic, recent_pattern_context, degradation_markers).
- Add tests validating presence, collapsed default, update-after-execution behavior, and graceful degradation.

**Consequences.** - Requires template updates and route context wiring; small CSS styling additions.
- Debug data exposure must be access-controlled in production (operator-only surfaces or gated by configuration).
- Acceptance tests added to ensure behavior and non-regression.

**Implementation status.** **Implemented — collapsible debug panel driven by `DebugPanelOutput`.**

- `backend/app/runtime/presentation/debug_presenter.py`: `present_debug_panel(session_state)` → `DebugPanelOutput` (primary_diagnostic, recent_pattern_context, degradation_markers, full_diagnostics).
- Session UI renders the panel via `<details>/<summary>` HTML elements; summary always visible, diagnostics collapsed by default.
- Strict schema contract: panel data flows only through `DebugPanelOutput`; no ad hoc diagnostic injection.
- `backend/tests/runtime/test_debug_presenter.py`: comprehensive coverage including presence, collapsed default, graceful degradation when short-term context is missing.
- Gap: full `TurnExecutionResult` fields (validation outcomes, timing) deferred to W3.5.2 per docstring note in `debug_presenter.py`. The `full_diagnostics` field is populated from `short_term_context` instead.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/components/administration-tool/architecture.md#d1-debug-panel-ui-bounds` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Admin security control plane

**Status:** Accepted
**Origin:** ADR-0052 (retired 2026-06-23)

**Context.** Operator tooling historically risked mutating governance flags or runtime secrets against world-engine directly, bypassing audit trails and centralized authorization. Security governance must remain a backend-owned control plane with explicit admin routes and test coverage.

**Decision.** Security governance mutations and operator security UI route through backend admin control plane only; administration-tool never mutates governance flags directly against world-engine. Manage templates call documented backend proxy endpoints; destructive actions require backend confirmation. Governance console surfaces read-only projections unless a backend mutation API explicitly allows the change.

**Consequences.** Additional round-trips for operator actions but consistent authz, logging, and contract tests. New operator capabilities must land backend-first before manage UI exposes them.

**Evidence.** [AT-M02](mechanism-catalog.md#at-m02) · [security-governance SAD D3](../../project/security-governance/architecture.md#d3-security-governance-admin-control-plane) · [`test_manage_governance_console_and_runtime_config_truth.py`](../../../../administration-tool/tests/test_manage_governance_console_and_runtime_config_truth.py) · [archive ADR-0052](../../../archive/adr-retired-2026/adr-0052-security-governance-admin-control-plane.md)

## 10. Quality Requirements

`administration-tool/tests/`, admin test matrix docs.

## 11. Risks & Technical Debt

Large static JS surfaces need alignment with backend route contracts.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Manage deck | Operator control center UI |
