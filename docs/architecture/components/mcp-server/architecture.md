# mcp-server — Software Architecture (arc42)

**Component:** mcp-server · **Folder:** `tools/mcp_server/` · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Stdio MCP server exposing suite-scoped tools, resources, and prompts for developers and operators.
Aligns with `ai_stack/mcp/mcp_canonical_surface.py`.

The server is a transport and handler shell: tool names, authorization modes, and capability budgets are
defined in the canonical surface so CI can diff registry changes. Operators use MCP for diagnostics;
players never connect to this process in production play paths.

## 2. Constraints

Phase-A security baseline ([ADR-0028](../../../archive/adr-retired-2026/adr-0028-mcp-security-baseline-phase-a.md)); rate limits ([ADR-0048](../../../archive/adr-retired-2026/adr-0048-central-route-and-mcp-rate-limit-inventory.md)).

## 3. Context & Scope

In scope: handlers, diagnostics, backend session factories. Out of scope: live turn commit.

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Local MCP protocol adapter exposing explicit filesystem, backend-session, governance, evaluation, research and observability tools.

**Authority rule:** The MCP server owns protocol validation and tool routing only; domain mutations remain with backend or world-engine authorities.

**Git/archaeology scope:** `tools/mcp_server`, `scripts/wos_mcp_stdio_launcher.py`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Protocol adapter boundary against domain authorities | [MCP Server - Context](../../../../UML/Components/mcp-server/context/mcp-context.md) | The MCP server owns protocol validation and tool routing only; domain mutations remain with backend or world-engine authorities. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

## 4. Solution Strategy

Canonical surface defines tool names and authorization; server implements transport.
Handler factories share session construction with backend tests so MCP and HTTP paths see the same
session shapes. Rate-limit inventory from ADR-0048 is checked when adding new public tools.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Handlers | `tools/mcp_server/handlers/` |
| Session factories | `backend_session_mcp_handler_factories.py` |
| Tests | `tools/mcp_server/tests/` |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound building-block catalog

Each block has one stated responsibility, an interaction or ownership contract, and a current source anchor. The list is individualized for this scope; it is not derived from a fixed diagram count.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| MCP Client (`client`) | `actor` | Discover and invoke Better Tomorrow tools | JSON-RPC over stdio | [`tools/mcp_server/README.md`](../../../../tools/mcp_server/README.md) |
| Backend Client (`backend_client`) | `component` | Delegate governed session and platform operations | Authenticated HTTP with normalized errors | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| Capability Registry (`registry`) | `component` | Publish stable tool, resource and prompt metadata | Unique names and schemas | [`tools/mcp_server/registry.py`](../../../../tools/mcp_server/registry.py) |
| Filesystem Tools (`fs`) | `component` | Inspect explicitly allowed repository paths | Resolved-root containment | [`tools/mcp_server/handlers/tools_registry_handlers_filesystem.py`](../../../../tools/mcp_server/handlers/tools_registry_handlers_filesystem.py) |
| Handler Families (`handlers`) | `component` | Implement bounded capability groups | Validated arguments and structured result | [`tools/mcp_server/handlers/__init__.py`](../../../../tools/mcp_server/handlers/__init__.py) |
| Langfuse Tracing (`observability`) | `component` | Correlate MCP calls without leaking credentials | Redacted trace events | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |
| RPC Router (`router`) | `component` | Decode methods and produce protocol errors | JSON-RPC request/response | [`tools/mcp_server/rpc_method_router.py`](../../../../tools/mcp_server/rpc_method_router.py) |
| Rate Limiter (`rate_limit`) | `component` | Bound expensive or mutating calls | Per-operation policy | [`tools/mcp_server/rate_limiter.py`](../../../../tools/mcp_server/rate_limiter.py) |
| Backend Process (`backend_node`) | `node` | Execute governed remote actions | HTTP | [`backend/Dockerfile`](../../../../backend/Dockerfile) |
| Local Stdio Process (`stdio`) | `node` | Host MCP protocol adapter | One client transport | [`scripts/wos_mcp_stdio_launcher.py`](../../../../scripts/wos_mcp_stdio_launcher.py) |
| Repository Workspace (`repo`) | `node` | Provide scoped read/write targets | Configured root containment | [`tools/mcp_server/repo_dotenv.py`](../../../../tools/mcp_server/repo_dotenv.py) |
| Backend (`backend`) | `system` | Authorize and execute platform mutations | Authenticated backend API | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| MCP Server (`server`) | `system` | Validate protocol and dispatch registered capabilities | MCP JSON-RPC | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| World Engine (`world`) | `system` | Expose safe session inspection and commands | Runtime API | [`world-engine/app/api/http.py`](../../../../world-engine/app/api/http.py) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Operator/dev invokes MCP → server → backend/world-engine read surfaces per tool contract.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| Protocol validation through bounded handler execution | `sequence` | [MCP Server - JSON-RPC Call](../../../../UML/Components/mcp-server/sequence/json-rpc-call-sequence.md) | 6 |
| Mutation requests remain under backend authority | `sequence` | [MCP Server - Governed Delegation](../../../../UML/Components/mcp-server/sequence/governed-delegation-sequence.md) | 5 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

Run as stdio MCP alongside configured backend; see [`MCP.md`](../../../technical/integration/MCP.md).

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

| Concern | Model | Nodes / stores |
| --- | --- | --- |
| Local stdio process, scoped repository and backend boundary | [MCP Server - Deployment](../../../../UML/Components/mcp-server/deployment/mcp-deployment.md) | Local Stdio Process, Repository Workspace, Backend Process |

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

Quality lab diagnostics ([ADR-0040](../../../archive/adr-retired-2026/adr-0040-quality-lab-mcp-runtime-diagnostics.md)).

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| Handler Families | Backend Client | delegates remote operation | normalized backend request | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| Handler Families | Filesystem Tools | delegates local operation | scoped filesystem request | [`tools/mcp_server/handlers/tools_registry_handlers_filesystem.py`](../../../../tools/mcp_server/handlers/tools_registry_handlers_filesystem.py) |
| Handler Families | Rate Limiter | checks policy | budget before execution | [`tools/mcp_server/rate_limiter.py`](../../../../tools/mcp_server/rate_limiter.py) |
| Handler Families | Langfuse Tracing | emits call evidence | redacted trace | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |
| Capability Registry | Handler Families | binds handler | schema-compatible callable | [`tools/mcp_server/tools_registry.py`](../../../../tools/mcp_server/tools_registry.py) |
| RPC Router | Capability Registry | resolves capability | registered canonical name | [`tools/mcp_server/registry.py`](../../../../tools/mcp_server/registry.py) |
| MCP Server | RPC Router | dispatches method | protocol envelope | [`tools/mcp_server/rpc_method_router.py`](../../../../tools/mcp_server/rpc_method_router.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | MCP host Phase A | Accepted | ADR-0026 |
| D2 | Transport connectivity | Accepted | ADR-0027 |
| D3 | Security baseline | Accepted | ADR-0028 |
| D4 | Rate limit inventory | Accepted | ADR-0048 |

### D1: MCP Phase A — Host & Runtime defaults

**Status:** Accepted
**Origin:** ADR-0026 (retired 2026-06-23)

**Context.** MCP (Model Context Protocol) usage during Phase A requires a safe, low-friction host and runtime contract for operator workflows and debugging.

**Decision.** - Run the MCP server locally (stdio transport) for Phase A operator workflows.
- MCP tools communicate with the backend remotely over HTTPS.
- MCP in Phase A functions as an operator console (inspect/debug) and must not be used as an in-game mechanic.

**Consequences.** - Operator tooling should be documented for local setup and required backend access.
- Future phases may evolve the host and runtime assumptions; changes require ADRs.

**Implementation status.** **Implemented — MCP server exists as local stdio operator console.**

- `tools/mcp_server/` is the MCP server implementation for operator workflows.
- Runs locally (stdio transport) and communicates with backend via HTTPS — matches the ADR decision exactly.
- Used as operator console (inspect/debug), not as in-game mechanic.
- `docs/mcp/01_M0_host_and_runtime.md` has "Migrated Decision: See ADR-0026" pointer.
- Status promoted from "Proposed" because the Phase A implementation is in place and stable.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/components/mcp-server/architecture.md#d1-mcp-host-phase-a` (archived — see `docs/archive/adr-retired-2026/`)

### D2: MCP Transport & Connectivity — Phase A defaults

**Status:** Accepted
**Origin:** ADR-0027 (retired 2026-06-23)

**Context.** MCP transport and connectivity need stable defaults for Phase A operator/QA usage.

**Decision.** - Use `stdio` as the MCP transport for Phase A (local runs).
- Use HTTPS for backend connectivity.
- Baseline timeouts and retries: backend HTTP timeout 5s, retry once on network errors.
- Include trace headers on MCP→backend calls: `X-WoS-Trace-Id`, `X-WoS-Client`, and optional `Authorization`.

**Consequences.** - Implementers should ensure tooling honours timeouts and header conventions.

**Implementation status.** **Implemented — stdio transport, HTTPS connectivity, and trace headers in place.**

- MCP server uses stdio transport locally (confirmed by `tools/mcp_server/` structure and `docs/mcp/02_M0_transport_connectivity.md`).
- Backend HTTP timeout 5s, single retry on network errors — documented in `docs/mcp/02_M0_transport_connectivity.md`.
- Trace headers `X-WoS-Trace-Id`, `X-WoS-Client`, and optional `Authorization` included on MCP→backend calls.
- `docs/mcp/02_M0_transport_connectivity.md` has "Migrated Decision: See ADR-0027" pointer.
- Status promoted from "Proposed" because the transport and header conventions are implemented.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/components/mcp-server/architecture.md#d2-transport-connectivity` (archived — see `docs/archive/adr-retired-2026/`)

### D3: MCP Security Baseline — Phase A minimal policy

**Status:** Accepted
**Origin:** ADR-0028 (retired 2026-06-23)

**Context.** Phase A for MCP requires conservative security defaults to prevent accidental state changes and exposure of secrets during operator workflows.

**Decision.** - Restrict MCP to read/preview-only behavior in Phase A; `write` operations are forbidden.
- Use `Authorization: Bearer <SERVICE_TOKEN>` for backend calls; tokens stored securely and not committed to repo.
- Rate limit MCP locally to max 30 calls/min per token.
- Logs must not contain PII or secrets; request bodies should be hashed when stored.

**Consequences.** - Tooling and endpoints must respect permission levels and logging constraints.
- Future phases may relax or change these rules with an ADR.

**Implementation status.** **Implemented at policy level; MCP rate-limiting is verified by the central limit inventory and MCP rate-limit tests. Log-hashing remains governed by separate logging coverage.**

- Phase A MCP is read/preview-only for operator workflows; write operations are not exposed through the MCP tool set.
- Bearer token authentication (`Authorization: Bearer <SERVICE_TOKEN>`) is used for backend calls per the ADR.
- Tokens are stored in local config, not committed to repo.
- Rate limiting (30 calls/min per token) is enforced in `tools/mcp_server/server.py`, sourced from `ai_stack/quality_lab/limit_inventory.py`, and mirrored per tool in `tools/list` metadata. Request-body hashing in logs remains a separate logging constraint.
- Status promoted from "Proposed" because the Phase A security posture is in force and the MCP server is operational.
- Review if rate limiting is not implemented in `tools/mcp_server/` before expanding Phase A scope.

**Testing.** Contract / unit coverage as cited in **References**. Rate-limit drift is covered by `tools/mcp_server/tests/test_rate_limit.py` and the backend info inventory tests. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/components/mcp-server/architecture.md#d3-security-baseline` (archived — see `docs/archive/adr-retired-2026/`)

### D4: Central route and MCP rate-limit inventory

**Status:** Accepted
**Origin:** ADR-0048 (retired 2026-06-23)

**Context.** The backend API, authentication routes, and MCP server already have rate-limit controls, but the evidence lived in different places:

- Flask route decorators and Flask-Limiter defaults for HTTP/API routes.
- `admin_security` policy wrappers for admin-sensitive routes.
- MCP dispatch constants and the MCP `RateLimiter`.
- Human-facing info pages and API reference prose.

That split made it easy for operator-facing views or tests to drift from runtime behavior. The MCP security ADR already described conservative local limits, while API/Auth pages needed a route-level inventory that could show which routes use explicit decorators, which fall back to defaults, and how MCP tool metadata maps back to the dispatch limiter.

**Decision.** 1. `ai_stack/quality_lab/limit_inventory.py` is the central helper for route and MCP rate-limit metadata.

2. HTTP/API inventory entries must be derived from runtime route evidence where possible: Flask URL map, OpenAPI/catalog metadata, handler decorators, `admin_security` rate-limit wrappers, and the configured default limiter value.

3. The API catalog must expose a structured `rate_limit` object per endpoint. The API Explorer and backend info pages must read that structured field instead of maintaining independent prose-only tables.

4. MCP dispatch limits must use the same constants exported by `ai_stack/quality_lab/limit_inventory.py`. MCP `tools/list` metadata must mirror that inventory for every registered tool.

5. The following operator-facing surfaces must include the inventory or link directly to it:

   - `/backend/security-features`
   - `/backend/api`
   - `/backend/auth`
   - `/backend/mcp`
   - `/backend/api-explorer`

6. Tests must verify structured inventory fields and rendered info surfaces. A prose-only mention of rate limiting is not sufficient evidence.

7. The inventory is an evidence and drift-prevention layer. Enforcement remains owned by Flask-Limiter route/default configuration for HTTP and by the MCP `RateLimiter` for JSON-RPC dispatch.

8. Production limit changes must not be justified from inventory coverage alone. Tuning requires live or staging telemetry for request volume, 429/MCP blocked calls, quota utilization, retry/backoff behavior, and edge/gateway throttling.

9. Rate-limit telemetry must be privacy-preserving: hashed limiter keys only, no raw bearer tokens, cookies, IP addresses, email addresses, request bodies, prompts, reset tokens, or provider credentials.

10. The generated OpenAPI YAML is an artifact, not a hand-maintained source.
    The OpenAPI drift test may run `generate_openapi_spec.py --write` before
    `--check` so route changes refresh the YAML from the Flask URL map before
    inventory/catalog assertions consume it.

**Consequences.** **Positive:**

- Operators can inspect API/Auth/MCP rate-limit coverage from one consistent model.
- Info pages and API Explorer no longer need to duplicate limit tables by hand.
- MCP rate-limit documentation, runtime constants, `tools/list`, and tests now share the same source.
- Regression tests can detect missing route metadata or MCP constant drift.

**Negative / risks:**

- Decorator extraction depends on known wrapper patterns. New non-standard wrappers must be added to the inventory helper and tests.
- The inventory proves local code/configuration evidence, not production-edge WAF/CDN throttling or traffic telemetry.
- Default route limits are visible as fallback policy, but they are less specific than explicit route decorators.
- Production telemetry adds another operational surface that must be kept separate from local/dev diagnostic evidence.

**Follow-ups:**

- Instrument production/staging telemetry for `rate_limit_requests_total`, `rate_limit_hits_total`, quota utilization, retry-after behavior, and edge throttle events.
- Add optional production telemetry summaries once limiter metrics are available.
- Consider extending the inventory shape with auth role, CSRF, and service-token policy fields if the info surfaces need a broader security matrix.
- Review this ADR when a new MCP transport, API gateway, or external rate-limit layer becomes canonical.

**Testing.** Current verification:

- `PYTHONPATH=backend python -m pytest backend/tests/test_openapi_drift.py -q --tb=short --no-cov`
- `PYTHONPATH=backend python -m pytest backend/tests/test_backend_info_routes.py -q --tb=short --no-cov`
- `PYTHONPATH=backend python -m pytest backend/tests/test_backend_info_routes.py tools/mcp_server/tests/test_rate_limit.py tools/mcp_server/tests/test_registry.py -q --tb=short --no-cov`
- `python -m pytest tools/mcp_server/tests/test_mcp_operational_parity_and_registry.py -q --tb=short --no-cov`

Review this ADR if:

- any API catalog endpoint loses its structured `rate_limit` field
- MCP dispatch constants no longer match `tools/list` metadata
- an info page hardcodes a limit that does not come from the inventory
- a route wrapper adds enforcement that the inventory cannot see
- production docs claim tuned limits without telemetry baseline, shadow run, canary result, and rollback threshold

**Evidence.** `docs/architecture/components/mcp-server/architecture.md#d4-rate-limit-inventory` (archived — see `docs/archive/adr-retired-2026/`)

 Quality Requirements

`ai_stack/tests/test_mcp_canonical_surface_extended.py`, MCP integration docs.

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D1` | Protocol adapter boundary against domain authorities | `context` | [MCP Server - Context](../../../../UML/Components/mcp-server/context/mcp-context.md) |
| `D1`, `D2`, `D3` | Routing, registry, handler, safety and observability seams | `component` | [MCP Server - Components](../../../../UML/Components/mcp-server/components/mcp-components.md) |
| `D1`, `D3` | Protocol validation through bounded handler execution | `sequence` | [MCP Server - JSON-RPC Call](../../../../UML/Components/mcp-server/sequence/json-rpc-call-sequence.md) |
| `D2` | Mutation requests remain under backend authority | `sequence` | [MCP Server - Governed Delegation](../../../../UML/Components/mcp-server/sequence/governed-delegation-sequence.md) |
| `D4` | Local stdio process, scoped repository and backend boundary | `deployment` | [MCP Server - Deployment](../../../../UML/Components/mcp-server/deployment/mcp-deployment.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

- Public handlers, session factories and transport routes must be discoverable.
- Accepted MCP security and connectivity decisions require source anchors.
- Required context, container, component and class views remain source-linked.

## 11. Risks & Technical Debt

Tool surface must stay aligned with canonical registry.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

A formerly broad tools module has split into registries, routers and handler families. Models make aliases, deferred tools, filesystem scope and mutation delegation explicit.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 107 | 86 | 358 | 13 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| `DRIFT-008` | `open_target` | Observability contracts are fragmented across services | Define a minimal TurnTrace contract with propagated identity, owned spans, explicit gaps and redaction. Each service adapts locally but must satisfy the shared trace tree. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Canonical surface | Single registry of allowed MCP tools |
