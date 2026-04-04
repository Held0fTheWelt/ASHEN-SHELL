# Gate H Report — Content Governance and Publishing Hardening

Date: 2026-04-04

## 1. Scope completed

- Editorial **content lifecycle** on `game_experience_templates` with enforced transitions and **publish gating** (moderator cannot publish from arbitrary draft without approval, except the narrow seeded canonical exception).
- **Governance provenance** JSON on experiences (`origin_kind`, optional workflow refs, append-only `lifecycle_history`).
- **Unpublish** and governance API routes mirrored on `/game/content/...` and `/game-admin/...`.
- **Improvement** recommendation packages: persisted **`governance_review_state`** (HITL) plus **`POST /api/v1/improvement/recommendations/<package_id>/decision`** (`accept` | `reject` | `revise`).
- **Writers-Room** persisted reviews: top-level **`artifact_provenance`** stamp (workflow output vs canonical DB row).
- **AI stack evidence** improvement signals extended so human governance status is visible and **not equivalent** to “publishable” when no acceptance.
- **Administration-tool** game content page: lifecycle/provenance in list cards, governance action buttons, structured publish error display.

## 2. Files changed (primary)

- `backend/migrations/versions/040_game_experience_content_governance.py`
- `backend/app/models/game_experience_template.py`
- `backend/app/services/game_content_service.py`
- `backend/app/api/v1/game_routes.py`
- `backend/app/api/v1/game_admin_routes.py`
- `backend/app/services/improvement_service.py`
- `backend/app/api/v1/improvement_routes.py`
- `backend/app/services/ai_stack_evidence_service.py`
- `backend/app/services/writers_room_service.py`
- `backend/tests/test_game_content_service.py`
- `backend/tests/test_game_routes.py`
- `backend/tests/test_game_admin_routes.py`
- `backend/tests/test_improvement_routes.py`
- `backend/tests/test_writers_room_routes.py`
- `backend/tests/test_m11_ai_stack_observability.py`
- `administration-tool/templates/manage/game_content.html`
- `administration-tool/static/manage_game_content.js`
- `docs/reports/ai_stack_gates/H_GATE_REPORT.md`

## 3. What was deepened vs what already existed

| Area | Before | After |
|------|--------|--------|
| Experience publish | `is_published` toggle only | Lifecycle must be `approved` or `publishable` (or seed bypass) before publish; `published` / `unpublished` explicit |
| Provenance | `source` column only | `governance_provenance_json` with `origin_kind`, optional IDs, `lifecycle_history` |
| Improvement HITL | `review_status` string at creation | Full `governance_review_state` + HTTP decision endpoint + terminal states |
| WR artifact identity | Implicit file payload | Explicit `artifact_provenance` on stored review |
| Evidence bundle | Tool/retrieval signals | Adds `governance_human_status`, `distinct_from_publishable_recommendation`, etc. |

## 4. Lifecycle states (explicit)

`draft`, `review_pending`, `revision_requested`, `approved`, `rejected`, `publishable`, `published`, `unpublished`, `archived` (defined for completeness; **no dedicated archive endpoint** in this milestone — `archived` reserved for future use).

## 5. Provenance contract (experiences)

Stored under `governance_provenance` (from `governance_provenance_json`):

- **`origin_kind`**: `canonical_authored` | `writers_room_workflow` | `improvement_workflow` | `derived_candidate` | `published_bundle_reimport`
- Optional: `writers_room_review_id`, `improvement_package_id`, `variant_id`, `notes`
- **`lifecycle_history`**: append-only events (`action`, `from`, `to`, `at`, `by_user_id`, `note`)

Writers-Room file artifacts: **`artifact_provenance`**: `kind`, `workflow`, `created_at`, `module_id`, `trace_id`.

## 6. Publishing readiness

- **Operator-driven “readiness” step**: `approved` → `publishable` via `POST .../governance/mark-publishable` (honest moderator checkpoint, not automated proof).
- **Publish**: allowed from `approved` or `publishable`; sets `published`, `is_published=true`.
- **Seed bypass**: `template_id == god_of_carnage_solo` and `source == authored_seed` may publish without prior approval (backward compatibility for seeded canonical row).
- **Edit after publish**: content update **unpublishes** and returns lifecycle to **`draft`** with a history event (no silent drift of live content).

## 7. Admin / backend surfaces

- Game content list shows **lifecycle**, **live/offline**, **origin_kind**, **version**.
- Buttons: submit for review, approve, reject, request revision, mark publishable, publish, unpublish.
- API errors for blocked publish include **`code: lifecycle_blocks_publish`** and **`content_lifecycle`**.

## 8. Intentionally lightweight

- No automatic linkage from Writers-Room **accept** to an experience row (provenance refs are manual / API-provided on create).
- No full “archive” workflow beyond state constant.
- No distributed signed audit store; history remains in JSON on the row / package.

## 9. Tests added or updated

- Game content: lifecycle transitions, publish gating, seed lifecycle, provenance validation, reject path, unpublish, update-invalidates-publish, lifecycle filter.
- Game routes / game-admin: governance steps before publish; blocked publish 409 with code.
- Improvement: `governance_review_state` on packages; service-level decision flow; HTTP route with patched store.
- Writers-Room: `artifact_provenance` assertions.
- M11: improvement evidence influence flags for pending vs accepted.

## 10. Test commands run (exact)

```text
cd backend
python -m pytest tests/test_game_content_service.py tests/test_game_routes.py tests/test_game_admin_routes.py tests/test_improvement_routes.py tests/test_writers_room_routes.py tests/test_m11_ai_stack_observability.py -q --tb=line --no-cov
```

Result: **97 passed** (runtime ~9 minutes in this environment; dominated by existing integration tests that exercise real improvement/retrieval paths).

Additional check:

```text
cd backend
python -m pytest tests/test_game_experience_model.py -q --tb=short --no-cov
```

Result: **3 passed** (shadow model tests; separate from production `game_experience_templates`).

## 11. Verdict

**Pass**

## 12. Reason

- Lifecycle semantics are **materially stronger** than `is_published` alone, with **test-proven** transitions and publish blocking.
- Provenance is **explicit and queryable** on experiences and stamped on Writers-Room artifacts.
- Improvement packages have **distinct terminal governance states** and a **real decision API**; evidence surfaces expose **non-publishable** pending/rejected posture.
- Admin list and API errors improve **decision usefulness** without a new parallel governance product.

## 13. Remaining risk

- **JSON history** is not an immutable compliance ledger; tampering or loss is possible outside DB backups.
- **Seed bypass** must stay narrow; new seeded templates should not reuse it casually.
- Full end-to-end “WR accept → experience publish” remains **human-operated** (by design this milestone).
