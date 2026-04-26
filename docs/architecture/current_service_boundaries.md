# Current Service Boundaries

**Status:** Active contract — 2026-04-26

This document defines the authoritative service boundary model for World of Shadows.

---

## Service Map

| Service | Role | Authority |
|---------|------|-----------|
| **backend** | API gateway, auth, policy, content publishing, session surface | Request validation, role gating, content module serving |
| **frontend** | Player/public UI service | Player-facing rendering; calls backend at service boundary |
| **administration-tool** | Admin/management UI | Operator diagnostics, session inspection; proxies backend |
| **world-engine / play-service** | Authoritative live runtime | Commits state, executes turns, owns runtime authority |
| **writers-room** | Authoring area | Not production truth; drafts only |
| **ai_stack** | Orchestration/integration support | Proposal generation; NOT engine truth |
| **content/modules/god_of_carnage** | Canonical God of Carnage content | Story truth for GoC; not a runtime module |

---

## Hard Boundaries

### Backend
- Validates selected player role and content/profile contract
- Calls play-service/world-engine at the service boundary (not direct function call)
- Does NOT render the canonical player frontend
- Does NOT own runtime state

### Frontend
- Separate service from backend
- Calls backend API at the HTTP service boundary
- Renders player-facing UI from backend response
- Cannot be the only enforcement layer for backend/runtime rules

### World-Engine / Play-Service
- **Sole authority** for committed runtime state
- AI proposals are NOT committed truth — the engine validates and commits
- Rejected deltas leave committed state unchanged
- Event log / diagnostics record rejection reasons

### AI Stack
- Produces proposals for the engine to evaluate
- Never commits state directly
- Langfuse/observability must emit real traces through configured trace adapter, not merely set local trace_id fields

### Writers-Room
- Authoring area only
- Output requires editorial review and explicit publishing step before becoming production content
- Writers-room output is NOT canon until published through content pipeline

### Content Modules
- `content/modules/god_of_carnage` = canonical story truth (characters, scenes, triggers, endings)
- `god_of_carnage_solo` = runtime/session profile only (no story truth; sources from canonical module at runtime)
- Built-in/demo content is fallback/local/demo only; NOT canonical production proof

---

## Prohibited Patterns

| Pattern | Status |
|---------|--------|
| Backend renders canonical player pages | FORBIDDEN |
| Frontend as sole enforcement of backend rules | FORBIDDEN |
| AI proposal committed without engine validation | FORBIDDEN |
| `visitor` as a live runtime actor | FORBIDDEN |
| `god_of_carnage_solo` used as canonical content module | FORBIDDEN |
| Built-in content claimed as production proof | FORBIDDEN |
| Fallback/degraded output accepted as success | FORBIDDEN |
| Writers-room output treated as production truth | FORBIDDEN |

---

## ADR References

- ADR-0021: Runtime authority
- ADR-0016: Frontend/backend restructure
- ADR-mvp1-005: Canonical content authority
- ADR-mvp1-003: Role selection and actor ownership
- ADR-mvp4-009: Langfuse traceable decisions
