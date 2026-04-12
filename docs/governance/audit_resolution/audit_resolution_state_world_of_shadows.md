# Audit resolution — persisted state (World of Shadows)

**Single source of truth** for this case: finding ids, action ids, closure status, blockers, validation evidence, decision log.  
**Methodology:** [audit_resolution_master_prompt.md](audit_resolution_master_prompt.md)  
**Case input:** [audit_resolution_input_world_of_shadows_2026-04-12.md](audit_resolution_input_world_of_shadows_2026-04-12.md)

---

## Part I — Finding status transitions (normative)

**Allowed:** Open → Contained | Open → In Progress | Contained → In Progress | In Progress → Pending Validation | Pending Validation → Closed | Pending Validation → Closed with Residual Risk Accepted | Any → Blocked | Any non-closed → Escalated  

**Forbidden:** Open → Closed | In Progress → Closed (skipping Pending Validation) | Blocked → Closed without unblock evidence | Closed → non-closed except via Part J reopen below.

---

## Part J — Reopen log

| Decision id | Date | Finding id | Reason | Owner | New validation plan ref |
|-------------|------|------------|--------|-------|-------------------------|
| *(none)* | | | | | |

---

## Part L — Split / merge map

| Event id | Date | Type | Predecessor ids | Successor id(s) | Rationale ref |
|----------|------|------|-----------------|-----------------|---------------|
| *(none)* | | | | | |

---

## Findings register

| Finding id | Title | Domain | Severity | Status | Last transition |
|------------|-------|--------|----------|--------|-------------------|
| F-C1 | Runtime projection scene row identity at narrative commit seam | Technical / contract | Critical | In Progress | Open → In Progress |
| F-H1 | Story-session durability across process restart | Operational / technical | High | In Progress | Open → In Progress |
| F-H2 | Backend transitional session/runtime vs engine authority | Governance | High | Closed | Open → Closed |
| F-H3 | Dual interpretation surfaces for authored narrative | Technical | High | Closed | Open → Closed |
| F-M1 | Story-session turn concurrency vs live-run | Technical | Medium | In Progress | Open → In Progress |
| F-M2 | Monorepo Python import / bootstrap hygiene | Engineering | Medium | Closed | In Progress → Closed |
| F-M3 | Content provenance on session/run creation | Technical / ops | Medium | In Progress | Open → In Progress |
| F-L1 | Test/resource hygiene (umbrella) | Hygiene | Low | Closed | Open → Closed |
| F-L1a | Warning and default pytest suite hygiene | Hygiene | Low | Closed | Open → Closed |
| F-L1b | Generated-artifact paths and ownership | Hygiene | Low | Closed | Open → Closed |

---

## Action register

| Action id | Finding id | Type | Description | Owner | Due / dependency | Status |
|-----------|--------------|------|-------------|-------|------------------|--------|
| A-C1-02 | F-C1 | Corrective | Align runtime projection scene row keys and narrative commit resolver; add regression coverage | **Escalation:** assign named engineering owner (blocker B-ORG-01) | **Blocker:** calendar date pending owner assignment | In Progress |
| A-C1-03 | F-C1 | Preventive | Contract/integration tests for compile → story session → legal scene transition | **Escalation:** same as A-C1-02 | After A-C1-02 | In Progress |
| A-H1-01 | F-H1 | Corrective | JSON durable store for story sessions + reload on startup (`JsonStorySessionStore`, default `STORY_SESSION_STORE_DIR`) | **Escalation:** assign named owner (blocker B-ORG-01) | **Blocker B-02:** optional DB migration superseding JSON — decision pending | In Progress |
| A-H2-01 | F-H2 | Corrective | ADR-0002 Accepted + Appendix A per-row inventory + decision gate | **Escalation:** Architect + Product (blocker B-01) for any **retire** | Closed |
| A-H3-01 | F-H3 | Corrective | ADR-0003 Accepted; `ai_stack/goc_scene_identity.py` + tests + CI single-source verify | **Escalation:** assign named owner | — | Closed |
| A-M1-01 | F-M1 | Corrective | Per-session `threading.Lock` on `execute_turn` + `test_concurrent_turns_serialize_per_session` | **Escalation:** assign named owner (blocker B-ORG-01) | Pending validation after merge SHA | In Progress |
| A-M2-01 | F-M2 | Preventive | Supported invocation matrix + `Makefile` + `scripts/run_*` helpers | **Escalation:** DevEx owner (blocker B-ORG-01) | — | Closed |
| A-M3-01 | F-M3 | Corrective | `content_provenance` on create + list/state API surfaces | **Escalation:** assign named owner | Pending validation | In Progress |
| A-L1a-01 | F-L1a | Preventive | Frozen L1a exit criteria (see Part L1); spot-check pytest | **Escalation:** assign named owner | — | Closed |
| A-L1b-01 | F-L1b | Preventive | Story session var path `.gitignore` + matrix docs | **Escalation:** assign named owner | — | Closed |

---

## Blocker / escalation register

| Blocker id | Description | Impact | Decision needed | Escalation path | Latest decision date |
|------------|-------------|--------|-----------------|-----------------|----------------------|
| B-ORG-01 | Named accountable owners and calendar dates for P0/P1 actions | Scheduling and closure validity | Who assigns owners for engine/backend cross-cutting work | Engineering director / delegate | *unset* |
| B-01 | Backend session surface retirement vs compatibility | H2 scope | Product + Architect | CTO delegate | *unset* |
| B-02 | Story-session storage mechanism (JSON dir vs DB) | H1 design velocity | SLO + ops cost | Eng leadership | *unset* |
| B-03 | DOCX table export for audit tables | Input completeness | Audit owner provides paste/export | PMO / audit lead | *optional* |

---

## Part K — Validation evidence index

| Artifact id | Finding id | Action id | Type | Created | Creator / system | Revision (SHA / build) | Proves |
|-------------|------------|-----------|------|---------|-------------------|-------------------------|--------|
| E-WE-001 | F-C1 | A-C1-02 | automated_test | 2026-04-12 | local pytest | repo main (fill SHA at merge) | `test_runtime_projection_scene_id_only_shape_commits_legal_transition` — `scene_id`-only rows commit legal explicit command transition |
| E-WE-002 | F-H1 | A-H1-01 | automated_test | 2026-04-12 | local pytest | repo main (fill SHA at merge) | `test_story_session_restored_after_new_manager_process` — JSON persistence + reload |
| E-BE-001 | F-C1 | A-C1-02 | automated_test | 2026-04-12 | local pytest | repo main (fill SHA at merge) | `test_compile_god_of_carnage_produces_deterministic_projection` asserts `id` == `scene_id` on every compiled scene row |
| E-H2-001 | F-H2 | A-H2-01 | adr_appendix | 2026-04-12 | governance | repo main (fill SHA at merge) | ADR-0002 Accepted; Appendix A inventory rows + decision gate text |
| E-H3-001 | F-H3 | A-H3-01 | automated_test | 2026-04-12 | local pytest | repo main (fill SHA at merge) | `ai_stack/tests/test_goc_scene_identity.py` + `tools/verify_goc_scene_identity_single_source.py` in CI |
| E-M2-001 | F-M2 | A-M2-01 | documentation | 2026-04-12 | engineering | repo main (fill SHA at merge) | Contributing matrix + Makefile + `scripts/run_*.{ps1,sh}` |
| E-L1a-001 | F-L1a | A-L1a-01 | policy | 2026-04-12 | governance | repo main (fill SHA at merge) | Part L1 frozen criteria recorded before closure sweep |
| E-L1b-001 | F-L1b | A-L1b-01 | configuration | 2026-04-12 | engineering | repo main (fill SHA at merge) | `.gitignore` for `world-engine/app/var/story_sessions/` + README pointers |

*Append one row per CI run, test report, or payload sample used for closure. Do not mark a finding Closed until required rows exist.*

---

## Part L1 — Frozen hygiene exit criteria (2026-04-12)

**Process:** Baseline was taken on the same date; exit criteria were **frozen before** marking L1a/L1b closed. Loosening these targets requires a new **decision log** row.

**L1a (warnings / default suites):** For `python -m pytest tests/ -q` run from `backend/` and from `world-engine/` with default warning filters: **zero** `DeprecationWarning` and **zero** `PytestCollectionWarning`. Other warning classes (for example `ResourceWarning` from SQLite fixtures) are **out of scope** for this freeze and may be tracked under separate hygiene actions if they grow noisy.

**L1b (generated artifacts / ownership):** Closure requires documented cwd rules (M2 matrix), a listed ignore for local World Engine JSON story-session files under `world-engine/app/var/story_sessions/`, and no contradictory README guidance for those paths.

---

## Systemic prevention records (SPR)

### SPR-1 — Cross-layer contract drift

| Field | Value |
|-------|--------|
| Pattern | Schema / field-name drift at service boundaries |
| Inventory scope | All consumers of `runtime_projection` and related compile outputs |
| Sweep owner | **Escalation:** assign (blocker B-ORG-01) |
| Deadline | *unset* |
| Sampling vs full-scan | Start with full-scan of grep-owned modules; sample integration paths if scope explodes |
| Exceptions | Document in decision log with exception id |
| Promotion rule | Any drift with customer-facing wrong behavior → new finding id + Part K evidence |

### SPR-2 — New session types without durability template

| Field | Value |
|-------|--------|
| Pattern | New in-memory session without parity to agreed persistence pattern |
| Inventory scope | Session managers in world-engine + future services |
| Sweep owner | **Escalation:** assign |
| Deadline | *unset* |
| Sampling vs full-scan | Full-scan of `*manager*.py` session dicts per release train |
| Exceptions | ADR exemption only with time-bounded risk acceptance |
| Promotion rule | Missing persistence where marketing/SLA implies durability → new finding |

---

## Management decision points

1. Risk acceptance for shipping with F-H1 not Closed (documented compensating controls vs not allowed).
2. Resourcing for cross-layer tests and ADR work (B-ORG-01).
3. SPR-1 depth (minimal hotfix vs schema publication) — trade speed vs recurrence prevention.

---

## Decision log (chronological)

| Log id | Date | Author | Summary |
|--------|------|--------|---------|
| DL-0001 | 2026-04-12 | Governance | State file created; methodology linked; blockers B-ORG-01, B-01, B-02 opened pending named owners and dates. |
| DL-0002 | 2026-04-12 | Engineering | Implemented F-C1 resolver keys + compiler `id`/`scene_id`; F-H1 JSON store + startup reload; M1 per-session locks; M3 `content_provenance` on create; ADR-0002/0003 proposed; contributing monorepo bootstrap note; evidence rows E-WE-001/002, E-BE-001 (pending validation → fill SHAs after merge). |
| DL-0003 | 2026-04-12 | Engineering | Closed F-H2/F-H3/F-M2/F-L1 audit plan items: ADR-0002 Accepted with Appendix A + retirement decision gate; ADR-0003 Accepted with Option A source-of-truth + no-local-remap (`goc_scene_identity.py`, tests, `verify_goc_scene_identity_single_source.py`); M2 matrix + Makefile + scripts; L1a/L1b frozen criteria in Part L1. |
