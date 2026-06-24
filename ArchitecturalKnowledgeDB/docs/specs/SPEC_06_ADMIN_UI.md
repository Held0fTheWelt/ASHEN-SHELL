# SPEC 06 — Admin UI

Status: Proposed
Date: 2026-06-16
Depends on: SPEC_01–05 (full service)

## 1. Purpose

A minimal local admin and inspection UI over the service, so the author can manage projects, run
import/export, and inspect consistency, staleness, and context packs without the CLI or raw MCP
calls. It is an inspection and operations surface, not a graphical UML editor.

## 2. Scope

In scope (per base spec §11):

- List / add / edit projects; register repositories.
- Trigger operations: ADR import/export, UML import/export, Git scan, index rebuild — all through
  the same gated core operations used by CLI/MCP.
- Show index and round-trip status (last import/export, conformance-gate result).
- Consistency dashboard: findings from SPEC_03, ordered by authority/severity.
- Staleness report page (SPEC_04).
- Context-pack playground: run a test task query and preview the pack (SPEC_05).
- Link inspector: inbound/outbound links for an item.

Out of scope (per ADR-0004): multi-user permissions, cloud tenancy, remote sync, visual UML
editing.

## 3. Success criteria

1. An admin user can register a project and repository, run an import, and see round-trip status.
2. The consistency and staleness dashboards render current findings.
3. The context-pack playground returns the same pack the API/MCP would for the same input.
4. Every mutating action goes through the existing core (no UI-only write path).

## 4. Architecture

Served by the SPEC_05 FastAPI app. Server-rendered templates (Jinja) or a small static front-end —
chosen during planning; either way the UI only calls existing core operations and HTTP routes, so it
holds no business logic of its own.

```
architectural_knowledge_db/admin/
  views.py        # page routes
  templates/      # project list, repo registration, dashboards, playground
  static/         # minimal assets
```

## 5. Testing

- Route smoke tests for every page.
- Each admin action invokes the expected core operation (asserted via the service layer).
- Context-pack playground output matches the API for identical input.

## 6. Open decisions

- Server-rendered templates vs. a small SPA — proposed default: server-rendered Jinja for zero
  build tooling, consistent with the local, offline-first nature of the product.
