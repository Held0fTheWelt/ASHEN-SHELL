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

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Operator-facing Flask application for read models, governed mutations, moderation and runtime diagnostics.

**Authority rule:** The tool owns presentation and operator intent only; backend governance services remain mutation authority.

**Git/archaeology scope:** `administration-tool`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Who operates the tool and where mutation authority resides | [Administration Tool — System Context](../../../../UML/Components/administration-tool/components/c4-context.md) | The tool owns presentation and operator intent only; backend governance services remain mutation authority. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

## 4. Solution Strategy

Split route registration into proxy/pages/manage/security modules (despaghettify DS-004 pattern).
Static manage decks load diagnostics incrementally so large trace payloads do not block first paint.
Every destructive operator action routes through backend confirmation endpoints.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Routes | `route_registration.py`, `route_registration_*.py` |
| Manage UI | `templates/`, `static/manage_*.js` |
| Control-plane application | `administration-tool/` |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound structural decomposition

Only elements that participate in a container or component view are listed as building blocks. Actors, runtime states, data types and deployment nodes remain in their proper viewpoints instead of being misrepresented as structural decomposition.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| Backend Proxy (`proxy`) | `component` | Forward allow-listed reads and mutations to backend | Method, path, timeout and response policy | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Manage Route Catalog (`manage`) | `component` | Expose named operator workbench surfaces | Stable /manage route vocabulary | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Page Routes (`pages`) | `component` | Route public and manage page requests to bounded templates | GET-only page composition | [`administration-tool/route_registration_pages.py`](../../../../administration-tool/route_registration_pages.py) |
| Proxy Policy (`policy`) | `component` | Classify mutation endpoints and confirmation requirements | Default-deny unsafe or undeclared proxy operations | [`administration-tool/route_registration_proxy_policy.py`](../../../../administration-tool/route_registration_proxy_policy.py) |
| Security Routes (`security`) | `component` | Apply session and operator security checks | Authenticated, CSRF-aware browser mutation boundary | [`administration-tool/route_registration_security.py`](../../../../administration-tool/route_registration_security.py) |
| Manage Templates (`templates`) | `container` | Present backend-derived read models and mutation forms | Escaped HTML and explicit form intent | [`administration-tool/templates/manage/dashboard.html`](../../../../administration-tool/templates/manage/dashboard.html) |
| Administration Tool (`admin`) | `system` | Render operator workbenches and translate intent into backend requests | Flask routes; no direct domain persistence | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Backend Admin API (`backend`) | `system` | Authorize and execute governed mutations | HTTP /api/v1/admin and operator endpoints | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Operator browser → administration-tool → backend governance routes → optional read of play diagnostics.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| End-to-end authorization and delegation of an operator mutation | `sequence` | [Administration Tool — Governed Mutation](../../../../UML/Components/administration-tool/sequence/governed-mutation-sequence.md) | 6 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. A sequence or activity view must form one connected runtime path; a list of unrelated calls does not qualify as an end-to-end scenario. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

Separate Flask app; backend URL configuration.

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

| Concern | Model | Nodes / stores |
| --- | --- | --- |
| Browser, administration process and backend trust boundary | [Administration Tool — Deployment](../../../../UML/Components/administration-tool/deployment/administration-tool-deployment.md) | Operator, Browser, Administration Flask Process, Backend Flask Process |

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

Narrative gov operator truth ([mvp-live-runtime-completion MVP4-010](../../project/mvp-live-runtime-completion/architecture.md#mvp4-010-narrative-gov-operator-truth-surface)).

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| Administration Tool | Manage Route Catalog | dispatches manage pages | named manage route registration | [`administration-tool/route_registration_manage.py`](../../../../administration-tool/route_registration_manage.py) |
| Administration Tool | Page Routes | dispatches public pages | page route registration | [`administration-tool/route_registration.py`](../../../../administration-tool/route_registration.py) |
| Manage Route Catalog | Backend Proxy | submits requested operation | normalized proxy request | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Manage Route Catalog | Security Routes | requires operator session | authorization before rendering or mutation | [`administration-tool/route_registration_security.py`](../../../../administration-tool/route_registration_security.py) |
| Manage Route Catalog | Manage Templates | renders workbench | template plus backend read model | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Proxy Policy | Backend Admin API | forwards approved operation | service key and operator evidence | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Backend Proxy | Proxy Policy | classifies request | default-deny mutation policy | [`administration-tool/route_registration_proxy_policy.py`](../../../../administration-tool/route_registration_proxy_policy.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

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

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D2` | Who operates the tool and where mutation authority resides | `context` | [Administration Tool — System Context](../../../../UML/Components/administration-tool/components/c4-context.md) |
| `D1`, `D2` | How routes, policy, security and templates collaborate without owning domain state | `component` | [Administration Tool — Internal Components](../../../../UML/Components/administration-tool/components/c4-component.md) |
| `D2` | End-to-end authorization and delegation of an operator mutation | `sequence` | [Administration Tool — Governed Mutation](../../../../UML/Components/administration-tool/sequence/governed-mutation-sequence.md) |
| `D2` | Browser, administration process and backend trust boundary | `deployment` | [Administration Tool — Deployment](../../../../UML/Components/administration-tool/deployment/administration-tool-deployment.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

`administration-tool/tests/`, admin test matrix docs.

## 11. Risks & Technical Debt

Large static JS surfaces need alignment with backend route contracts.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

Git history shows rapid expansion of manage templates and route-registration splits. Models separate page routing, proxy policy and backend mutation authority so presentation growth cannot become an accidental control plane.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 187 | 145 | 829 | 1 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| Scope-specific watch | `open_target` | No global claim currently maps to this root. | Keep source-bound views and review on structural Git changes. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Manage deck | Operator control center UI |
