# D1 Refocus Gate Report — Writers-Room Production Workflow Deepening

Date: 2026-04-04

## 1. Scope completed

Deepened `patch_candidates` artifacts in the Writers-Room workflow. Each candidate now includes a `preview_summary` (a human-readable one-sentence description of the proposed change) and a `confidence` score (float 0–1) derived from the severity of the corresponding issue. This materializes the previously abstract hint dicts into reviewable artifacts, closing the gap that reviewers could not assess patch impact.

## 2. Files changed

- `backend/app/services/writers_room_service.py` — deepened `patch_candidates` generation to include `preview_summary` and `confidence` fields
- `backend/tests/test_writers_room_routes.py` — added one new test asserting `preview_summary` and `confidence` presence and validity

## 3. What is truly wired

- `patch_candidates` in the review report now contain:
  - `preview_summary`: a string describing the proposed revision with module and target context
  - `confidence`: a float derived from the issue severity map (`high` → 0.9, `medium` → 0.7, `low` → 0.4), defaulting to 0.7 when no matching issue exists
- Severity-to-confidence mapping is applied inline at generation time using the already-built `issues` list
- All existing workflow stages (proposal packaging, review state, decision routing) remain unchanged

## 4. What remains incomplete

- `patch_candidates` are still structured hints, not fully materialized diffs. They describe what should change but do not produce a concrete before/after text representation. Full materialization would require invoking the narrative generation model on the target content.
- `confidence` values are static per severity tier; they are not calibrated against retrieval signal strength or model generation quality.

## 5. Tests added/updated

Added: `test_writers_room_patch_candidates_have_preview_summary_and_confidence`

- Creates a writers-room review via POST `/api/v1/writers-room/reviews`
- Asserts at least one `patch_candidate` is present
- For each candidate: asserts `preview_summary` is a non-empty string
- For each candidate: asserts `confidence` is a float in [0.0, 1.0]

## 6. Exact test commands run

```
cd /mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows/backend && python -m pytest tests/ -k "writers_room" -v 2>&1 | tail -30
```

Result: `4 passed, 3277 deselected in 20.33s`

## 7. Pass / Partial / Fail

**Pass**

## 8. Reason for the verdict

All 4 writers-room tests pass (3 pre-existing + 1 new). The new test directly verifies the D1 REFOCUS requirement: `patch_candidates` now carry `preview_summary` and `confidence` fields with correct types and value ranges. No regressions introduced.

## 9. Risks introduced or remaining

- **Remaining**: Confidence values are tier-based (not model-derived), which may give false precision to reviewers. Future work should calibrate confidence against retrieval relevance scores.
- **Remaining**: `preview_summary` text is template-generated from the source path; it does not reflect the actual narrative content that would be changed. A future milestone should pass content excerpts to the model to produce meaningful summaries.
- **Introduced**: None. The change is additive and backward-compatible; existing code that reads `patch_candidates` will still work since new fields are simply added to each dict.
