# ADR-0016: Frontend / Backend Restructure (separate Backend and administration-tool frontend)

Date: 2026-03-30

Status: Accepted (implementation note consolidated)

## Context

An architectural decision was made to split the repository into a `Backend/` process (data, API, auth, dashboard, persistence, tests) and a lightweight `administration-tool/` frontend (public landing, news pages, static assets) that consumes the Backend API. This move preserves existing auth patterns and avoids duplicating business logic.

## Decision

- Move data, API, auth, migrations, and protected UI (dashboard, game-menu) into `Backend/`.
- Implement a thin `administration-tool/` frontend that serves public pages and consumes `Backend` APIs only.
- Keep login/register/dashboard in `Backend/` (session + CSRF); `administration-tool/` contains only public pages and static assets.
- Implement `News` (or `Post`) model and `/api/v1/news` in Backend; frontend consumes it.
- Use `FRONTEND_URL` configuration to coordinate redirects and origin-dependent behavior.

## Rationale

- Separates concerns and clarifies ownership boundaries between public site and platform services.
- Enables independent scaling and deployment of public assets and backend services.
- Encourages API-first patterns and avoids accidental duplication of auth/business logic.

## Consequences

- Repository reorganization required: files moved with `git mv`, import path updates, and CI adjustments.
- Backend storage and instance paths must be updated and accounted for in deployment/dockers.
- Public pages may require CORS or reverse-proxy configuration to access Backend APIs.

## Migrated from

Original implementation note: `docs/archive/architecture-legacy/FrontendBackendRestructure.md` (section 5: Decisions and Conventions).

---

(Automated migration entry created 2026-04-17)
