# C2-next gate report — evidence quality and central tool dependence

## Verdict: **Pass**

## Scope completed

- **Richer retrieval trace:** `build_retrieval_trace` now emits a four-level **`evidence_tier`** (and **`evidence_strength`** with the same value for compatibility) using `hit_count`, optional `top_hit_score`, and a short **`evidence_rationale`**. Additional fields: `retrieval_route`, `top_hit_score` passthrough.
- **Audit summaries:** Context-pack audits include `evidence_tier`, `evidence_rationale`; review-bundle audits include **`workflow_impact`**; successful transcript reads include **`transcript_turn_count`**, **`repetition_turn_count`**, and **`workflow_impact`** describing how results feed downstream workflows.
- **Improvement experiment route:** Persists sandbox transcript JSON under `world-engine/app/var/runs/improvement_<experiment_id>.json`, invokes **`wos.transcript.read`**, and derives a **suffix on `recommendation_summary`** (`|tr_turns=…|tr_rep=…`) only from tool-returned content. If **`repetition_turn_count` ≥ 2**, the summary is forced to **`revise_before_review`** before the suffix (material governance branch).
- **Response + persistence:** HTTP payload includes **`transcript_evidence`** metadata; the recommendation package JSON under `var/improvement/recommendations/` is **rewritten** after augmentation so stored artifacts match the API (includes embedded **`transcript_evidence`**).
- **Writers-Room copy:** Review summaries use **`[evidence_tier:…]`** aligned with the new trace field.

## Files changed

| Area | Files |
|------|--------|
| Capabilities / trace | `wos_ai_stack/capabilities.py` |
| Improvement API | `backend/app/api/v1/improvement_routes.py` |
| Writers-Room service | `backend/app/services/writers_room_service.py` |
| Tests | `wos_ai_stack/tests/test_capabilities.py`, `backend/tests/test_improvement_routes.py`, `backend/tests/test_writers_room_routes.py` |

## Evidence model improvement (truth)

- Replaced the **binary** hit/no-hit signal with **none / weak / moderate / strong**, driven by hit count bands and optional top-hit score (from hybrid retrieval).
- **Not** a statistical calibration layer; tiers are **transparent heuristics** suitable for governance hints, not ML confidence.

## Workflow depending on transcript / tool evidence

- **`POST /api/v1/improvement/experiments/run`** always runs transcript persistence + **`wos.transcript.read`** and **mutates** `recommendation_package.recommendation_summary` (and stored package) from parsed tool JSON.

## Tools still secondary / aspirational

- **`wos.transcript.read`** is not wired into **Writers-Room** or **runtime** turn loops in this milestone; **runtime** remains focused on `wos.context_pack.build`.
- **Admin** mode for transcript remains available but not exercised in these tests.

## Tests added/updated

- **Capabilities:** tier matrix tests; context-pack audit tier fields; transcript success audit with `workflow_impact`; review-bundle `workflow_impact`.
- **Improvement routes:** assertions for `evidence_tier`, transcript audit `allowed`, `|tr_turns=3|`, `transcript_evidence.turn_count`; **monkeypatch** of `_transcript_tool_evidence_for_improvement` proves recommendation text **loses** `tr_turns` when the helper is bypassed; mocks updated for transcript + failure ordering; empty-retrieval mock implements transcript stub.
- **Writers-Room routes:** accept four-valued evidence fields.

## Exact test commands run

```text
python -m pytest wos_ai_stack/tests/test_capabilities.py -v --tb=short
cd backend && python -m pytest tests/test_improvement_routes.py tests/test_writers_room_routes.py -v --tb=short
```

## Reason for verdict

Evidence is **materially** more informative than a binary flag; improvement workflow **depends** on transcript tool output for recommendation text and stored packages; audits expose **impact-oriented** fields; permission/denial semantics for other capabilities are unchanged; tests prove **operational** dependence (including bypass). Aspirational scope (runtime/writers transcript) is **not** misrepresented as complete.

## Remaining risk

- Tier thresholds are **hand-tuned**; production tuning may need telemetry.
- Transcript files under `world-engine/app/var/runs` are **test/dev oriented**; concurrent experiment IDs must remain unique (UUID-based today).

## Implementation note

- `improvement_routes` resolves the monorepo root with `Path(__file__).resolve().parents[4]` (file lives under `backend/app/api/v1/`) so RAG ingestion and transcript paths align with `world-engine/` at the repository root.
