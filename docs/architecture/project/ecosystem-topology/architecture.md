---
id: SAD-PROJECT-ECOSYSTEM-TOPOLOGY
status: accepted
type: project-sad
owns-adrs: []
uml-package: UML/Project/ecosystem-topology
components: [world-engine, backend, frontend, administration-tool, ai-stack, story-runtime-core, mcp-server, content-authority]
links:
  - docs/architecture/components/world-engine/architecture.md
  - docs/technical/architecture/architecture-overview.md
---
# Ecosystem Topology — Software Architecture (arc42, project-wide)

**System:** Ecosystem Topology · **Scope:** project-wide · **Status:** `internal`  
**Last reconciled to code:** `2026-06-23`

## 1. Introduction & Goals

World of Shadows is a multi-service narrative platform: player web app, admin app, Flask backend,
FastAPI play service, shared runtime library, AI stack, canonical YAML content, and MCP tooling.
This SAD explains how those deployables compose and which service owns which class of truth.

### 1.1 Quality goals

| Goal | Scenario |
| --- | --- |
| Clear authority | An engineer can name the commit owner for a live turn without reading ten ADRs |
| Stable boundaries | No feature adds a second runtime graph without an explicit governance decision |
| Traceable capabilities | Each capability row routes to exactly one component SAD |

### 1.2 Stakeholders

| Stakeholder | Concern |
| --- | --- |
| Runtime engineer | Service map and proxy paths |
| Platform engineer | Backend vs play service env alignment |
| Technical writer | Internal vs audience doc boundaries |

## 2. Constraints

- Play authority in world-engine ([world-engine SAD D1](../../components/world-engine/architecture.md#d1-runtime-authority-in-world-engine)).
- Backend transitional runtime is not production play host ([backend-runtime-classification](../../../technical/architecture/backend-runtime-classification.md)).
- GoC slice contracts stay under `docs/MVPs/MVP_VSL_And_GoC_Contracts/`.

## 3. Context & Scope

```mermaid
flowchart TD
  FE[frontend] --> BE[backend]
  ADM[administration-tool] --> BE
  BE --> WE[world-engine]
  WE --> AI[ai_stack]
  WE --> SRC[story_runtime_core]
  BE --> CONTENT[content compile]
  MCP[tools/mcp_server] --> BE
  MCP --> WE
```

Authoritative: [UML ecosystem context](../../../../UML/Project/ecosystem-topology/components/c4-context.md)

### 3.1 In / out of scope

| In scope | Out of scope |
| --- | --- |
| Service responsibilities, URLs, proxy paths | Module-level Python layout inside each service |
| Capability catalog | Player marketing copy |

## 4. Solution Strategy

- Separate deployables per process/container; align secrets between backend and world-engine.
- Keep AI orchestration in `ai_stack` but commit only in world-engine.
- Treat `content/modules/` as authored truth compiled by backend, consumed by engine.
- Route all architecture questions through component SADs first, this SAD second.

## 5. Building Block View

| Layer | Location | Responsibility |
| --- | --- | --- |
| Player UI | `frontend/` | Public routes, play shell |
| Admin UI | `administration-tool/` | Operations UI via backend |
| Backend | `backend/` | REST, auth, persistence, compile, proxy |
| Play service | `world-engine/` | Live sessions, turns, commits |
| Shared models | `story_runtime_core/` | Interpretation contracts, adapters |
| AI stack | `ai_stack/` | Graph, RAG, capabilities, research |
| Content | `content/modules/` | YAML modules |
| MCP | `tools/mcp_server/` | Operator/dev tools |

## 6. Runtime View

Typical player turn: browser → frontend → backend game routes → world-engine story API → ai_stack graph → validate/commit in engine → response chain back. See [turn-execution-canonical UML](../../../../UML/Project/turn-execution-canonical/README.md).

## 7. Deployment View

Run frontend, backend, administration-tool, and world-engine as separate processes. Use `docker-up.py` for local bootstrap. CORS must include frontend origins on backend.

## 8. Crosscutting Concepts

- Ticket bridge: `PLAY_SERVICE_SHARED_SECRET` / `PLAY_SERVICE_SECRET` ([world-engine README](../../../../world-engine/README.md)).
- Internal API key optional hardening for join-context and termination endpoints.
- Writers-room is optional demo UI over backend APIs—not production truth.

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Layered multi-service map | Accepted | architecture-overview consolidation |

### D1: Layered multi-service map

**Status:** Accepted
**Origin:** architecture-overview consolidation (retired 2026-06-23)

**Context.** Service boundaries were scattered across contract stubs; operators needed one canonical map tying backend, world-engine, ai-stack, and frontend responsibilities for onboarding and incident response.

**Decision.** The table in §5 is the canonical service map; legacy `current_service_boundaries` contract stubs were retired in favor of this SAD.

**Consequences.** Incident runbooks and onboarding cite §5; contract stubs must not be reintroduced as parallel truth.

**Evidence.** [`docs/technical/architecture/service-boundaries.md`](../../../technical/architecture/service-boundaries.md).

### D2: `docker-up.py` as Complete Local Bootstrap

**Status:** 
**Origin:** ADR-0030 (retired 2026-06-23)

**Context.** `docker-up.py` is the canonical operator entry point for a local World of Shadows stack. The current implementation is no longer a thin wrapper around `docker compose up`; it is responsible for preparing a usable runtime before Compose starts.

Three implementation realities are important:

1. Platform secrets are generated on the host and persisted in the repository-root `.env`.
2. The Docker stack now includes Redis as shared runtime-governance storage because backend runs multiple Gunicorn workers.
3. Langfuse is runtime-configured in backend settings; `docker-up.py` only imports `LANGFUSE_*` credentials when they are explicitly present in `.env`.
4. Local Redis and production Redis have different security postures: local app Redis remains internal with no host port, while production must enforce separate app/Langfuse Redis instances, passwords, ACL users, and TLS.

This ADR replaces older assumptions such as:

- "docker-up only starts containers"
- "Langfuse is enabled through `LANGFUSE_ENABLED` in `.env`"
- "governance runtime state can safely live in process memory in Docker"

**Decision.** ### 1. `docker-up.py` owns first-run environment materialization

Before any `up`, `build`, or `restart` flow, `docker-up.py` ensures the repository-root `.env` exists and contains:

- generated stable platform secrets:
  - `SECRET_KEY`
  - `JWT_SECRET_KEY`
  - `SECRETS_KEK`
  - `PLAY_SERVICE_SHARED_SECRET`
  - `PLAY_SERVICE_INTERNAL_API_KEY`
  - `FRONTEND_SECRET_KEY`
  - `INTERNAL_RUNTIME_CONFIG_TOKEN`
- defaulted runtime URLs:
  - `OPENAI_BASE_URL`
  - `OPENROUTER_BASE_URL`
  - `OLLAMA_BASE_URL`
  - `ANTHROPIC_BASE_URL`
  - `ANTHROPIC_VERSION`
  - `REDIS_URL`
- empty-but-present provider credential slots:
  - `OPENAI_API_KEY`
  - `OPENROUTER_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `LANGFUSE_PUBLIC_KEY`
  - `LANGFUSE_SECRET_KEY`

This is the authoritative first-run behavior. Operators are not expected to hand-author a minimal `.env` before the stack can start.

### 2. Docker bootstrap includes a shared Redis runtime-governance store

The local Compose stack must start:

- `backend`
- `frontend`
- `administration-tool`
- `play-service`
- `redis`

Redis is not optional in the standard Docker path because MVP4 runtime governance now persists:

- token budget state
- truthful cost summaries
- evaluation annotations and baselines
- recent turn quality signals
- active override indexes

Without Redis, each backend worker would keep its own in-memory view, which is not acceptable for Docker-operated observability and governance.

### 3. Backend initialization remains the source of governed runtime truth

`docker-up.py up` must:

1. ensure `.env`
2. run `docker compose up -d --build`
3. wait for backend health
4. create the bootstrap admin user
5. optionally import Langfuse config into backend settings

`docker-up.py` does not become the long-term owner of runtime settings. It only helps seed them.

### 4. Langfuse bootstrap is optional import, not env-flag activation

Current behavior is:

- if both `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are absent in `.env`, `docker-up.py` leaves backend observability settings unchanged
- if both are present, `docker-up.py` calls the backend initialization endpoint and imports the Langfuse configuration
- if only one key is present, bootstrap fails loudly

This means Docker bootstrap supports two valid operator flows:

1. Configure Langfuse later in backend/admin settings
2. Preseed Langfuse from `.env` during bootstrap

It does not rely on a legacy `LANGFUSE_ENABLED` environment toggle.

### 5. Failure must remain explicit

The current exit-code contract stays in force for `up`:

- `0` success
- `1` Docker/Compose failure
- `2` backend migration/bootstrap failure
- `3` admin-user creation failure
- `4` Langfuse initialization failure when credentials were supplied
- `5` backend health check failure
- `6` `.env` validation/materialization failure

### 6. Production secret stores must not break local bootstrap

Production deployments should source secrets from a dedicated secret store with rotation, audit logging, and separated access. That production store is a deployment responsibility outside this local helper.

`docker-up.py` must remain able to create or repair a local repository-root `.env` without contacting a central secret manager. Any future production integration must inject environment variables before the services start, or wrap deployment-specific infrastructure outside `docker-up.py`, while preserving the existing `init-env`, `up`, `build`, and `restart` behavior for local Compose.

### 7. Production Redis hardening is a first-class bootstrap path

`docker-up.py init-production-redis` must materialize the production Redis contract without manual file authoring:

- `APP_REDIS_USERNAME`, `APP_REDIS_PASSWORD`, `APP_REDIS_URL`, and TLS CA path for backend runtime governance Redis
- `LANGFUSE_REDIS_USERNAME`, `LANGFUSE_REDIS_PASSWORD`, `LANGFUSE_REDIS_CONNECTION_STRING`, TLS paths, and CA validation for Langfuse Redis
- ignored local ACL files under `.docker/redis-production/` with `default` disabled
- ignored local TLS certificates for the separate app Redis and Langfuse Redis services

`docker-compose.redis-production.yml` is layered only when `--production-redis`, `WOS_DOCKER_PRODUCTION_REDIS=1`, or `production-redis-up` is used. The override keeps Redis services internal, switches Redis to TLS-only, and injects the hardened app Redis URL into backend as `REDIS_URL`.

Validation is explicit: `python docker-up.py validate-production-redis` fails if URLs are not `rediss://`, TLS flags are false, ACL users/passwords are missing or shared, app and Langfuse Redis hosts are not separate, or generated ACL/cert assets are missing.

**Consequences.** ### Positive

- Local operators get a runnable stack from one command path.
- The generated `.env` and Redis service reflect the actual current runtime architecture.
- MVP4 governance data stays coherent across backend workers in Docker.
- Langfuse setup supports both env-preseed and backend-managed configuration.
- Production operators get a repeatable Redis hardening path instead of hand-editing passwords, ACL files, and TLS paths.

### Negative / risks

- The repository-root `.env` becomes part of normal local operations and must be preserved carefully.
- Redis is now a standard local dependency for Docker-based governance truth.
- Older docs or habits that assume env-only observability control are incorrect and must not be followed.

**Implementation status.** **Implemented and tested.**

- `docker-up.py` is the canonical operator entry point; it materializes `.env` before any Compose operation.
- All required secrets (`SECRET_KEY`, `JWT_SECRET_KEY`, `SECRETS_KEK`, `PLAY_SERVICE_SHARED_SECRET`, `PLAY_SERVICE_INTERNAL_API_KEY`, `FRONTEND_SECRET_KEY`, `INTERNAL_RUNTIME_CONFIG_TOKEN`) and runtime URLs (`REDIS_URL`, etc.) are generated on first run.
- `docker-compose.yml` includes `redis` service; Redis is not optional in the standard Docker path.
- Langfuse bootstrap is optional import (credentials from `.env` only if both keys present); not governed by legacy `LANGFUSE_ENABLED` flag.
- Production secret stores are explicitly out of scope for `docker-up.py`; the helper remains the local `.env` bootstrap path and must not require Vault/KMS/cloud-secret access.
- Production Redis hardening for Compose is automated through `docker-up.py init-production-redis` and `docker-compose.redis-production.yml`.
- Exit-code contract (0–6) is in force.
- Test coverage: `tests/test_docker_up_complete_bootstrap.py`.
- First-party Compose service images use **Python 3.14** per [ADR-0064](../../../archive/adr-retired-2026/adr-0064-python-314-unified-interpreter-standard.md) (`backend`, `play-service`, `frontend`, `administration-tool` Dockerfiles).

**Testing.** ### Verification checklist

- [ ] `python docker-up.py init-env` creates or repairs repository-root `.env`
- [ ] generated secrets are non-placeholder values
- [ ] `REDIS_URL=redis://redis:6379/0` is present unless intentionally overridden
- [ ] `docker compose config --services` includes `redis`
- [ ] `python docker-up.py up` reaches healthy backend and bootstrap admin creation
- [ ] if both `LANGFUSE_*` keys are present, backend observability initialization succeeds
- [ ] if only one `LANGFUSE_*` key is present, `docker-up.py up` fails with exit code `4`
- [ ] `python docker-up.py init-production-redis` creates Redis ACL/TLS material and distinct app/Langfuse Redis URLs
- [ ] `python docker-up.py validate-production-redis` fails if Redis TLS, ACL users, passwords, or instance separation are missing

### Canonical test locations

- `tests/test_docker_up_complete_bootstrap.py`
- `tests/test_production_redis_docker_config.py`
- Compose validation via `docker compose -f docker-compose.yml config`

**Evidence.** `docs/architecture/project/ecosystem-topology/architecture.md#d2-docker-up-complete-bootstrap` (archived — see `docs/archive/adr-retired-2026/`)
## 10. Quality Requirements

| Requirement | Verification |
| --- | --- |
| Service boundary tests | Integration tests under `tests/integration/` |
| Foundation gate | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` |

## 11. Risks & Technical Debt

| Risk | Mitigation |
| --- | --- |
| Backend/runtime shim confusion | backend SAD + classification doc |
| Duplicate docs in `docs/architecture/` stubs | documentation-supply-chain migration |

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Play service | world-engine FastAPI app |
| Platform backend | Flask `backend/` |

## Capability catalog

| Capability | Owning SAD |
| --- | --- |
| Live session authority | [world-engine](../../components/world-engine/architecture.md) |
| Platform API & auth | [backend](../../components/backend/architecture.md) |
| Turn graph & RAG | [ai-stack](../../components/ai-stack/architecture.md) |
| Player shell | [frontend](../../components/frontend/architecture.md) |
| Operator UI | [administration-tool](../../components/administration-tool/architecture.md) |
| MCP tools | [mcp-server](../../components/mcp-server/architecture.md) |
| Canonical content | [content-authority](../../components/content-authority/architecture.md) |
| Gates & CI | [quality-gates](../quality-gates/architecture.md) |
| Traces | [observability-traceability](../observability-traceability/architecture.md) |
| Security | [security-governance](../security-governance/architecture.md) |
| MVP program | [mvp-live-runtime-completion](../mvp-live-runtime-completion/architecture.md) |
