---
id: SAD-PROJECT-SECURITY-GOVERNANCE
status: accepted
type: project-sad
owns-adrs: [ADR-0047, ADR-0050, ADR-0051, ADR-0052]
---
# Security Governance — Software Architecture (arc42, project-wide)

**Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Encryption, credential governance, browser mutation boundaries, and admin control plane security for
World of Shadows platform surfaces.

Security governance spans storage encryption policy, provider credential envelopes, admin-only mutation
routes, and browser-facing CSRF/CORS boundaries coordinated with backend configuration. Story canon
policy is out of scope here and lives in content-authority and runtime validation instead.

## 2. Constraints

Player/admin/MCP boundaries in [admin-player-mcp-surfaces](../../boundaries/admin-player-mcp-surfaces.md).

## 3. Context & Scope

Platform security ADRs 0047–0052; not story canon policy.

## 4. Solution Strategy

- Central route and MCP rate inventory (ADR-0048) complements MCP server SAD.
- Storage encryption governance separate from at-rest evidence boundary (partial ADR-0047).
- Admin mutations require authenticated backend sessions; browser tools never hold play-service secrets.

## 5. Building Block View

| Area | SAD route |
| --- | --- |
| Admin control plane | backend, administration-tool |
| Browser mutations | frontend |
| MCP auth | mcp-server |
| Provider credentials | backend + ai-stack |

## 6. Runtime View

Security checks at API middleware and MCP tool authorization layers.

## 7. Deployment View

Env-governed secrets ([ADR-0031](../../../archive/adr-retired-2026/adr-0031-env-configuration-governance.md)).

## 8. Crosscutting Concepts

[`SECURITY_REGRESSION_PROFILE.md`](../../../testing/SECURITY_REGRESSION_PROFILE.md).

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Browser mutation boundaries | Accepted | ADR-0050 |
| D2 | Storage encryption governance | Accepted | ADR-0051 |
| D3 | Admin control plane | Accepted | ADR-0052 |
| D4 | At-rest encryption evidence | Not Finished | ADR-0047 |
| D5 | Provider credential governance | Accepted | ADR-0049 |

### D1: Security governance for browser mutation boundaries

**Status:** 
**Origin:** ADR-0050 (retired 2026-06-23)

**Context.** The platform has more than one browser-facing security surface:

- backend compatibility web routes can receive a backend Flask `session` cookie and rely on Flask-WTF CSRF when `WTF_CSRF_ENABLED=True`
- backend JSON APIs under `/api/v1/*` are designed for `Authorization: Bearer ...` and are intentionally exempt from Flask-WTF CSRF
- the player frontend and administration tool use same-origin browser sessions to look up server-side tokens, then call backend APIs through controlled proxy/client code
- administration-tool and frontend session cookies use SameSite policy; JSON API mutations use Bearer tokens; same-origin proxies must not forward inbound browser cookies upstream
- the mutating cookie flows are documented in `docs/security/csrf-matrix.md` and pinned by backend, frontend, frontend API-client, and administration proxy regression tests
- production secrets require a dedicated store with rotation, audit, and access separation, while local `.env` remains the correct bootstrap path for `docker-up.py`
- production readiness also depends on operator-controlled policy for secret stores, Redis hardening, and regression evidence

A single "CSRF on/off" statement is too blunt for this topology. Operators need to see the matrix of mutating cookie-relevant flows, record the desired policy, and compare that policy with effective runtime values. At the same time, the administration UI must not become a switch that silently changes code-owned security boundaries such as the `/api/v1` CSRF exemption or proxy cookie stripping.

**Decision.** 1. The canonical CSRF contract is [docs/security/csrf-matrix.md](../../../security/csrf-matrix.md). It names every mutating browser/cookie-relevant flow family, its credential model, expected CSRF stance, and regression coverage.

   The accepted flow families are:

   - backend legacy web routes: backend `session` cookie, Flask-WTF CSRF when enabled
   - backend JSON API `/api/v1/*`: `Authorization: Bearer`, CSRF-exempt by design
   - frontend player forms: frontend `session` cookie with SameSite policy; backend calls use Bearer
   - frontend same-origin API proxy: frontend cookie only unlocks server-side token lookup; upstream calls omit inbound cookies
   - administration-tool proxy: admin cookie stays at the admin origin; upstream calls forward approved headers and strip `Cookie` / `Set-Cookie`

2. The backend exposes an admin-only security governance API:

   - `GET /api/v1/admin/security/governance`
   - `PATCH /api/v1/admin/security/governance`

   The endpoint requires an admin JWT and the `manage.ai_runtime_governance` feature.

3. Operator policy is persisted in `site_settings.security_governance_config` with schema `security_governance.v1`. It records review state, target `SameSite`, CSRF/Bearer/proxy regression requirements, secret-store policy, local Docker-Up preservation, and Redis hardening policy.

   Secret-store policy is metadata only. The governance record must not contain raw secret values, provider tokens, KMS plaintext material, Redis passwords, or Vault paths that reveal secrets.

4. The administration tool exposes `/manage/security-governance` as the operator truth surface. It must show:

   - target and effective cookie posture
   - editable operator policy for review state, target `SameSite`, CSRF/Bearer/proxy requirements, regression requirements, secret-store mode/provider/rotation/audit/access separation, and local Docker-Up preservation
   - the CSRF matrix returned by the backend
   - non-editable enforcement boundaries
   - full JSON evidence for audit and automation review, including Redis governance posture

5. The governance settings are policy and evidence, not hidden runtime toggles. These boundaries remain code/deployment-owned:

   - the `/api/v1` CSRF exemption in backend app setup
   - backend route authentication and role checks
   - frontend and admin proxy cookie stripping
   - actual Flask cookie configuration loaded at process start
   - secret materialization through deployment secret stores or `docker-up.py`
   - Redis ACL/TLS/certificate files generated on the host

6. Release readiness requires the policy, documentation, UI, and tests to move together. A change to a mutating cookie flow, JSON API auth expectation, same-origin proxy behavior, production secret-store boundary, or Redis hardening requirement must update the security governance documentation and relevant regression tests in the same change set.

7. The read-only backend info surface `/backend/security-features` must mirror the current CSRF/browser-mutation boundary: SameSite cookies for admin/frontend sessions, Bearer-token JSON APIs, same-origin proxy cookie stripping, links to `docs/security/csrf-matrix.md`, and concrete backend/frontend/proxy test evidence.

**Consequences.** **Positive:**

- Operators get one visible administration page for CSRF/cookie/security-governance posture.
- Security posture is explicit about which settings are editable policy and which values are enforced by code or deployment.
- The CSRF matrix becomes test-backed release evidence instead of a prose-only security note.
- `/backend/security-features` exposes the same matrix as a read-only backend evidence surface.
- Local `docker-up.py` remains the developer bootstrap path while production secret-store and Redis hardening are visible governance requirements.

**Negative / risks:**

- The admin page can create a false sense of enforcement if operators treat target policy as proof. The UI and docs must keep "effective posture" and "non-editable boundaries" visible.
- Some production evidence still lives outside the repository, especially secret-store audit records, KMS/provider settings, and Redis host-level material.
- If future teams add browser cookie-authenticated JSON mutations, the current bearer-token API exemption becomes insufficient and this ADR must be reviewed.

**Follow-ups:**

- Keep Redis hardening controls aligned with `docker-up.py`, `docker-compose.redis-production.yml`, and managed-service production runbooks.
- Add machine-readable route inventory if the CSRF matrix grows beyond the current curated route families.
- Consider release-report export of the full `security_governance.v1` payload.

**Testing.** - `backend/tests/test_csrf_protection.py` verifies the backend split between CSRF-protected web routes and CSRF-exempt Bearer-token JSON APIs.
- `frontend/tests/test_csrf_matrix.py` and `frontend/tests/test_api_client.py` verify frontend cookie flags and Bearer-only backend calls.
- `administration-tool/tests/test_proxy_contract.py` verifies admin proxy cookie/header stripping.
- `backend/tests/test_security_governance_routes.py` verifies the admin API contract, persistence, validation, matrix rows, and non-editable boundaries.
- `administration-tool/tests/test_manage_security_governance.py` verifies the administration page, navigation, secret-store controls, and PATCH wiring.
- `backend/tests/test_backend_info_routes.py::test_security_features_page_explains_csrf_matrix_regression_gate` verifies `/backend/security-features` renders the current CSRF/browser-mutation boundary and regression evidence.
- `tests/test_security_governance_documentation.py` verifies this ADR, the admin documentation, and the main documentation indexes stay linked.

Review this ADR if `/api/v1` begins accepting browser cookie authentication, if same-origin proxies forward cookies upstream, if admin governance settings become direct runtime enforcement switches, or if production security claims move from policy targets to automated evidence gates.

**Evidence.** `docs/architecture/project/security-governance/architecture.md#d1-browser-mutation-boundaries` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Storage-layer encryption governance

**Status:** 
**Origin:** ADR-0051 (retired 2026-06-23)

**Context.** ADR-0047 established that the repository must not claim full at-rest encryption until every persisted surface has documented encryption evidence. That decision left a practical gap: operators needed a first-class place to record, review, and diagnose the storage-layer evidence pack.

The persisted surfaces include backend SQLite, Redis AOF, world-engine runtime stores, Langfuse Postgres, ClickHouse, MinIO, Langfuse Redis, and backups/snapshots. Some deployments may satisfy these with managed encrypted services, others with encrypted hosts or Docker volume drivers, and some local-only surfaces may be explicitly marked not applicable.

The base `docker-compose.yml` is a local development stack. It already exposes the production-relevant runtime contract without claiming to encrypt local storage: backend database settings come from `env_file: .env` such as `DATABASE_URI`, and the play service receives `RUN_STORE_BACKEND`, `RUN_STORE_URL`, and `WORLD_ENGINE_JSON_AEAD_KEY`. Production Redis TLS/ACL separation is handled by `docker-compose.redis-production.yml`, but Redis AOF, database files, Docker volumes, and backups still require managed-service or encrypted-volume evidence.

The application cannot encrypt a host disk or prove cloud KMS state by itself from inside the admin browser. It can, however, provide a governed evidence contract, validate coverage, and make the missing pieces visible in diagnosis.

**Decision.** 1. Extend `security_governance.v1` with storage-layer encryption policy and evidence fields:
   - `storage_encryption_profile`
   - `require_storage_encryption_evidence`
   - `require_backup_encryption_evidence`
   - `require_storage_key_custody_evidence`
   - `require_storage_restore_test_evidence`
   - `storage_encryption_evidence`

2. Persist the evidence pack in `site_settings.security_governance_config`, the same backend-owned governance record used by the Security Governance Administration page.

3. Require evidence for these surface ids before a full at-rest claim is considered complete:
   - `backend_sqlite`
   - `backend_redis_aof`
   - `world_engine_json_run_store`
   - `world_engine_sqlalchemy_run_store`
   - `langfuse_postgres`
   - `langfuse_clickhouse`
   - `langfuse_minio`
   - `langfuse_redis`
   - `backups_snapshots`

4. Each evidence object records `status`, `control_type`, `evidence_ref`, `key_ref`, `last_verified_at`, `restore_test_ref`, and `notes`. Active encryption controls require an evidence reference and key-custody/KMS reference. Backup evidence also requires a restore-test reference when restore-test evidence is enabled.

5. The Administration Tool must expose storage-layer governance on `/manage/security-governance`, including policy switches, status, coverage, gate checks, and editable evidence JSON.

6. The backend API for this contract is `GET/PATCH /api/v1/admin/security/governance`.

7. The system diagnosis endpoint must expose a non-critical `storage_layer_encryption` check. It reports `running` only when required storage-layer evidence is complete; otherwise it reports `initialized` with the failing required-check count.

8. This governance does not replace deployment controls. Host full-disk encryption, Docker volume-driver encryption, managed-service encryption, server-side object storage encryption, backup encryption, and restore testing remain deployment/operator responsibilities.

9. The world-engine JSON store has a supported app-managed encryption path for deployments that do not replace it with SQL storage: `RUN_STORE_BACKEND=json_aead` writes AES-256-GCM `*.json.enc` envelopes using `WORLD_ENGINE_JSON_AEAD_KEY`. Production should still prefer SQL-backed managed encrypted storage when available; the AEAD JSON path exists for controlled single-node/self-hosted deployments and requires secret-store key custody plus backup evidence.

10. No additional functional change is required in the base `docker-compose.yml` for this ADR. The base compose file must remain local/dev oriented, expose the runtime-store environment contract, and avoid pretending that named volumes are encrypted. Production deployments must either provide a deployment-specific compose override/managed-service configuration or inject `DATABASE_URI`, `RUN_STORE_URL`, and Redis URLs from the production platform, then record the resulting evidence in `storage_encryption_evidence`.

11. `WORLD_ENGINE_JSON_AEAD_KEY` must not be auto-generated by the local `docker-up.py init-env` path. Local compose remains inspectable by default; production must inject the key from a secret store when `RUN_STORE_BACKEND=json_aead` is selected.

**Consequences.** **Positive:**

- Operators have a concrete place to prove storage-layer encryption instead of relying on prose outside the product.
- Diagnosis makes incomplete evidence visible without blocking local development.
- The backend view can distinguish "governance implemented" from "every deployment storage layer is encrypted."
- The evidence pack is auditable through one existing admin API.

**Negative / risks:**

- Evidence correctness still depends on operator-maintained references and deployment records.
- The product cannot independently verify every external KMS, volume, or backup setting without provider-specific integrations.
- Evidence JSON is flexible but requires disciplined review.
- Local compose remains intentionally local/dev; operators must not treat its named volumes as encrypted production storage.

**Testing.** - `backend/tests/test_security_governance_routes.py` verifies default storage evidence fields, PATCH persistence, and validation.
- `backend/tests/test_system_diagnosis.py` verifies the `storage_layer_encryption` diagnosis check is emitted.
- `administration-tool/tests/test_manage_security_governance.py` verifies the admin page and JavaScript expose storage-layer controls.
- `tests/test_at_rest_encryption_documentation.py` verifies this ADR and the at-rest evidence document stay linked.
- `world-engine/tests/test_aead_json_persistence.py` verifies AEAD JSON run-store and story-session persistence do not write plaintext JSON payloads.
- `backend/tests/test_backend_info_routes.py::test_security_features_page_explains_local_evidence_boundary` verifies `/backend/security-features` exposes the Storage-Layer Governance path.
- `tests/test_local_langfuse_docker_config.py` verifies the base compose exposes `RUN_STORE_BACKEND`, `RUN_STORE_URL`, and `WORLD_ENGINE_JSON_AEAD_KEY` without local AEAD key generation.

**Evidence.** `docs/architecture/project/security-governance/architecture.md#d2-storage-encryption-governance` (archived — see `docs/archive/adr-retired-2026/`)

### D3: Security Governance Admin Control Plane

**Status:** 
**Origin:** ADR-0052 (retired 2026-06-23)

**Context.** Security posture was split across code, environment variables, docs, tests, and Compose helpers:

- CSRF behavior is partly code-owned: backend web routes use Flask-WTF CSRF when enabled, while `/api/v1` JSON APIs are Bearer-token APIs and are CSRF-exempt by design.
- The administration tool proxies backend API calls but must not forward browser cookies upstream.
- Local `.env` files are practical and correct for local development and `docker-up.py`.
- Production deployments need a dedicated secret-store boundary with rotation, audit trails, and access separation.
- Production Redis posture requires passworded TLS connections, named ACL users, instance separation, no host-published ports, and validation.
- Full at-rest encryption claims require storage-layer evidence for databases, Redis persistence, runtime stores, object storage, Docker volumes, and backups.

Operators need one visible place to inspect and record these policies. At the same time, the administration UI must not become a browser-executed secret manager or a switch that rewires code-owned security controls.

**Decision.** 1. The Administration Tool exposes a Security Governance page at `/manage/security-governance`.

2. The backend exposes the governance contract at `GET/PATCH /api/v1/admin/security/governance`. The route requires JWT auth and the `manage.ai_runtime_governance` feature permission.

3. Operator policy is persisted as JSON in `site_settings.security_governance_config` with schema `security_governance.v1`.

4. The governance record stores policy and review state, including:

   - review status and target session `SameSite` posture
   - CSRF, Bearer-token API, proxy cookie-stripping, and regression-test policy
   - production secret-store requirement, provider/mode, rotation interval, audit requirement, and access-separation requirement
   - the invariant that local `docker-up.py` `.env` bootstrap stays available
   - production Redis hardening gates for TLS, named ACL users, instance separation, no host-published ports, and validation
   - storage-layer encryption profile, surface evidence, key-custody evidence, backup evidence, and restore-test evidence
   - short operator notes for audit context

5. The governance record is policy and evidence, not executable secret management or storage materialization. It must not store raw secrets, trigger provider-side rotation, encrypt host disks, or materialize Redis certificates/passwords from the browser.

6. Production secret-store integration remains deployment-owned. The provider or orchestrator must materialize the existing runtime environment contract before services start.

7. Local `docker-up.py` remains independent from production secret stores. Local Compose must not require Vault, KMS, cloud login, or production secret-store access.

8. Runtime/code-owned boundaries are returned as observed posture and non-editable boundaries, not as admin-toggleable behavior. This includes `/api/v1` CSRF exemption, proxy cookie stripping, Bearer-token API auth, local Docker bootstrap, and host-side Redis secret/TLS materialization.

**Consequences.** **Positive:**

- Operators get a visible administration control plane for security governance without mixing policy metadata with secret material.
- Production secret-store requirements become explicit and configurable while local `.env` workflows remain usable.
- CSRF, cookie, proxy, secret-store, Redis, and storage-layer evidence policies are testable through one backend contract.
- The page can show drift warnings when desired policy differs from observed runtime posture.

**Negative / risks:**

- The admin page is not a substitute for implementing a real production secret store, storage-layer encryption, KMS policy, or cloud/IaC access model.
- Provider-side rotation, audit evidence, and access separation still require deployment evidence outside the repository.
- Operators may misunderstand the page as enforcement unless docs and UI continue to label code-owned boundaries clearly.

**Follow-ups:**

- Add deployment-specific secret-store evidence packs once the production provider is selected.
- Expand release checks if a new security setting becomes executable behavior rather than governance metadata.
- Keep `/backend/security-features`, ADR-0050, this ADR, and the admin Security Governance page aligned when security claims change.

**Implementation status.** Implemented and tested.

- `/manage/security-governance` is the Administration Tool surface.
- `GET/PATCH /api/v1/admin/security/governance` is the backend governance contract.
- `site_settings.security_governance_config` persists the editable policy.
- The UI exposes review status, CSRF/cookie policy, secret-store policy, Docker-Up preservation, production Redis hardening gates, and storage-layer encryption evidence.
- Redis password/TLS/ACL materialization remains host/deployment-owned through `docker-up.py` or production infrastructure.
- Storage-layer encryption materialization remains host/deployment-owned; the admin page records the evidence pack.

**Testing.** - `backend/tests/test_security_governance_routes.py` verifies the backend governance contract, persisted settings, validation, secret-store policy fields, Redis hardening fields, storage-layer evidence fields, and non-editable boundaries.
- `administration-tool/tests/test_manage_security_governance.py` verifies the management route, navigation entry, secret-store controls, Redis controls, storage-layer controls, and backend endpoint usage.
- `tests/test_security_governance_documentation.py` verifies this ADR, ADR-0050, the admin documentation, the CSRF matrix, and primary documentation indexes stay linked.
- Future tests must comply with [ADR-0039](../../../archive/adr-retired-2026/adr-0039-gate-tests-no-hardcoded-oracle-bypass.md). They should prove state transitions, persisted policy, observed runtime posture, or generated deployment assets rather than only matching strings.

Review this ADR if the admin page begins storing raw secrets, triggering secret-provider mutations, changing Flask/route security behavior directly, or making local `docker-up.py` depend on production secret-store access.

**Evidence.** `docs/architecture/project/security-governance/architecture.md#d3-security-governance-admin-control-plane` (archived — see `docs/archive/adr-retired-2026/`)

### D4: At-rest encryption evidence boundary

**Status:** 
**Origin:** ADR-0047 (retired 2026-06-23)

**Context.** The repository has durable local persistence:

- backend SQLite at `backend/instance/wos.db`, mounted by Compose as `./backend/instance:/app/instance`
- app Redis append-only persistence in `redis-data:/data`
- world-engine runtime persistence via JSON files or SQLAlchemy `payload_json`
- local Langfuse named volumes for Postgres, ClickHouse, MinIO, and Redis: `langfuse-postgres-data`, `langfuse-clickhouse-data`, `langfuse-clickhouse-logs`, `langfuse-minio-data`, and `langfuse-redis-data`
- backup/export procedures documented in operations and database guides

The codebase also has real but narrower data-protection controls:

- governed provider credentials are field-encrypted through envelope encryption using `SECRETS_KEK`, per-secret DEKs, and AES-256-GCM
- exported database payloads can be encrypted on request
- Langfuse application `ENCRYPTION_KEY` and service passwords are generated for local Compose

These controls are useful, but they do not prove full database, volume, runtime-store, object-store, or backup encryption at rest. A previous security statement that simply said "database encryption at rest is a deployment responsibility" was too vague for an operator trying to decide whether the platform can claim full at-rest encryption.

**Decision.** 1. The platform must not claim "full at-rest encryption" unless every persisted surface is covered by documented storage-layer, database-layer, application-layer, or backup-layer encryption evidence.

2. Field-level credential encryption and encrypted exports are valid controls, but they are not substitutes for encrypting the live database file, Docker volumes, runtime stores, object storage, Redis persistence, or backups.

3. The canonical evidence document is [docs/security/AT_REST_ENCRYPTION.md](../../../security/AT_REST_ENCRYPTION.md). It must list:

   - implemented controls
   - persisted surfaces not fully covered
   - verification commands for repository evidence
   - the completion plan and operator evidence pack

4. Production deployments must choose and document one supported encryption boundary per persisted surface:

   - managed encrypted services with KMS/server-side encryption evidence
   - self-hosted encrypted host/storage/volume layers with key custody evidence
   - app-managed encryption such as SQLCipher or AEAD-encrypted runtime files where a local single-node path remains supported

5. Backups and snapshots are part of the at-rest boundary. A production-ready claim requires encrypted backup output, separate key custody, and a restore-test record.

6. Local `docker-up.py` remains a developer bootstrap path. Production secret-store, KMS, and managed-service controls must integrate by providing the same runtime environment contract or a documented deployment override; they must not make local Compose dependent on cloud login or production secret-store access.

7. The `/backend/security-features` read-only view must expose the same boundary: partial controls are visible, missing full at-rest evidence is explicit, and the evidence document is linked by path.

8. Storage-layer evidence governance is implemented through `security_governance.v1`; see ADR-0051 for the admin API, diagnosis check, and evidence-field contract.

**Consequences.** **Positive:**

- Operators get an honest security posture instead of a vague or over-broad encryption claim.
- The repo now distinguishes credential/export encryption from full live-data encryption.
- Production readiness has concrete evidence artifacts to collect.
- Local development remains ergonomic.

**Negative / risks:**

- Full at-rest encryption remains incomplete until deployment/storage choices are implemented and evidenced.
- Operators must maintain an evidence pack outside the repository for host, KMS, managed database, object storage, and backup settings.
- SQLite and JSON persistence require either local/dev-only scoping, storage-layer evidence, or app-managed encryption before production use.

**Follow-ups:**

- Decide whether SQLite is permanently local/dev-only or gains a SQLCipher-backed production path.
- Move production runtime persistence away from plain JSON, or add authenticated file encryption and key rotation.
- Add backup jobs or runbooks that produce encrypted backup artifacts and record restore tests.
- Upgrade export encryption to an authenticated payload format.

**Testing.** - `tests/test_at_rest_encryption_documentation.py` verifies the evidence document states the current boundary, references the code evidence, and is linked from operator/security documentation.
- `backend/tests/test_backend_info_routes.py::test_security_features_page_explains_local_evidence_boundary` verifies `/backend/security-features` renders the at-rest boundary and relevant persisted surfaces.
- Future implementation tests must be ADR-0039 compliant and prove configuration/state, not just string presence. Examples:
  - production Redis/storage validation reports `rediss://`, ACL users, TLS, and separate instances
  - backup smoke tests produce encrypted artifacts and perform a restore
  - SQLCipher or AEAD runtime-store tests prove plaintext is not written to the configured data file

Review this ADR if a persisted surface is added, a local-only store becomes production-supported, or an operator-facing page claims full at-rest encryption without a matching evidence pack.

**Evidence.** `docs/architecture/project/security-governance/architecture.md#d4-at-rest-encryption-evidence` (archived — see `docs/archive/adr-retired-2026/`)

### D5: Provider credential governance and local evaluator evidence

**Status:** 
**Origin:** ADR-0049 (retired 2026-06-23)

**Context.** Local evaluators and judge workflows can run against local Langfuse. That is useful for development diagnostics, but it created two security and governance risks:

1. Provider API keys could be accidentally treated as ordinary Compose configuration because backend and play-service both use `env_file: .env`.
2. Local judge scores could be mistaken for staging or production evidence if they were not visibly marked as local-only diagnostic evidence.

The runtime already has backend-governed provider configuration and encrypted credential storage. Provider access should therefore flow through that governance path, or through a production secret manager that materializes the same governed runtime contract. Direct provider credentials in Compose should not be the default runtime authority.

The same boundary applies to evaluator evidence: local Langfuse traces, MCP evidence reads, and local judge scores may explain diagnostics, but they must not mutate commit state, readiness truth, `validation_outcome`, or promotion status.

**Decision.** 1. Direct provider credentials are not a Compose-owned runtime control. Compose may carry non-secret provider base URLs and service wiring, but direct provider key slots for backend and play-service must be empty in the local Compose path.

2. `docker-up.py` may generate and preserve platform bootstrap secrets, but it must not generate, request, or persist provider API keys such as `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, or `HF_TOKEN`.

3. Provider credentials are governed runtime credentials. The accepted local and production access paths are:

   - backend AI Runtime Governance with encrypted provider credentials
   - a deployment secret manager that feeds the same governed runtime contract
   - mock/local providers that do not need external credentials

4. Runtime adapters must not silently fall back to direct environment API keys. OpenAI-compatible adapters may use explicit runtime credentials, and any environment-key fallback must be an explicit opt-in for narrowly scoped tooling, not the default application path.

5. Backend and writer/improvement workflows must build provider adapters from enabled provider configuration plus runtime credential lookup. If a provider is configured but no runtime credential is available, that adapter is unavailable; routing must filter to available adapters instead of leaking to an env-backed provider path.

6. Operator readiness must report provider credential source as `backend_governance_or_secret_manager`. Live provider readiness must be derived from governed provider credentials, not from direct `OPENAI_API_KEY` presence.

7. Local Langfuse traces and judge scores must be visibly marked with local-only evidence metadata:

   - `evidence_scope=local_langfuse`
   - `proof_level=local_only`
   - `local_only: true`
   - `live_or_staging_evidence=false`

8. MCP verification tools must surface `local_only` for judge scores and may infer it from trace metadata, score metadata, `proof_level=local_only`, or `evidence_scope=local_langfuse`.

9. `/backend/security-features` and operator documentation must explain the boundary: local evaluator evidence is diagnostic; provider access is governed; direct provider keys in Compose are not the accepted control plane.

**Consequences.** **Positive:**

- Provider API keys are less likely to leak through local Compose or `.env` inheritance.
- Backend governance becomes the single application-level source for external provider access.
- Local judge scores remain useful while being clearly excluded from production and staging evidence.
- Readiness and documentation align with the real security boundary.

**Negative / risks:**

- Developers cannot make OpenAI/OpenRouter work by only adding direct provider keys to `.env` in the Compose path; they must use the governed configuration path or an explicit secret-manager integration.
- Operators need a documented production secret-store integration before claiming provider credential governance is complete in their deployment.
- Some historical docs may still describe provider keys as Layer 2 `.env` credentials; they must be read as superseded by this ADR for backend/play-service runtime access.

**Follow-ups:**

- Add an operator UI/workflow for every supported provider credential type if one is not already covered.
- Version judge prompts, score names, provider ids, and evidence scopes in a central evaluator registry.
- Record production secret-store evidence without exposing raw key material.

**Testing.** - `tests/test_local_langfuse_docker_config.py` verifies that local Compose does not inject direct provider key values and carries empty overrides for provider key slots.
- `backend/tests/test_backend_info_routes.py::test_security_features_page_explains_local_evidence_boundary` verifies `/backend/security-features` exposes provider governance, local-only evidence metadata, and documentation links.
- `tools/mcp_server/tests/test_langfuse_verify_tools.py::test_judge_scores_inherit_local_only_trace_metadata` verifies judge scores inherit or expose `local_only`.
- `world-engine/tests/test_api_security.py::test_api_requires_play_service_ticket_for_access` covers the readiness surface that reports governed provider credential source.
- `tests/test_provider_credential_governance_documentation.py` verifies the ADR, security documentation, and operator links remain connected.

Review this ADR if a service reintroduces direct provider-key environment fallback, a new provider bypasses backend governance, local judge evidence changes promotion/readiness state, or production docs claim provider-governance compliance without a secret-store or backend-governance evidence path.

**Evidence.** `docs/architecture/project/security-governance/architecture.md#d5-provider-credential-governance` (archived — see `docs/archive/adr-retired-2026/`)

## 10. Quality Requirements

Security regression profile tests, operational governance route structure tests.

## 11. Risks & Technical Debt

ADR-0047 not finished—open exception.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Control plane | Admin/operator security configuration surface |
