# A2-next Gate Report — Authoritative narrative commit and progression semantics

Date: 2026-04-04

## 1. Scope completed

- **Merged model `proposed_scene_id`** from `generation.metadata.structured_output` into authoritative scene progression when `generation.success` is true and the id is known to the runtime projection, using a **deterministic priority**: explicit travel command → model structured output → player-input token scan.
- **Enriched `progression_commit`** with `candidate_sources`, `selected_candidate_source`, and `model_proposed_scene_id` (raw model value for audit, including unknown ids that cannot be selected).
- Added **`committed_interpretation_effect`** on each committed history record: interpreted kind, confidence, progression source, allowed flag, and an explicit note that this is a progression ledger stub, not full world state.
- Updated architecture doc for merge order, diagnostics vs committed history, and conservative scope.

## 2. Files changed

- `world-engine/app/story_runtime/manager.py`
- `world-engine/tests/test_story_progression_merge.py` (new)
- `world-engine/tests/test_story_runtime_rag_runtime.py`
- `docs/architecture/world_engine_authoritative_narrative_commit.md`
- `docs/reports/ai_stack_gates/A2_NEXT_GATE_REPORT.md`

## 3. What was deepened versus what already existed

- **Already existed:** Scene legality via `transition_hints`, token/command extraction, `progression_commit` on history/diagnostics, separation of diagnostics envelopes from `get_state` committed snapshot shape.
- **Deepened:** Model output participates in proposals under the same gates; **audit trail** of all candidate sources; explicit **interpretation ↔ progression** stub on committed records; tests for command-over-model priority and unknown model ids.

## 4. How committed runtime semantics became stronger

- Authoritative `current_scene_id` can advance from a **validated** structured model proposal when the player text carries no scene token, preserving projection and hint rules.
- **Explicit commands remain stronger** than model proposals, reducing hallucinated scene jumps when the player used a travel command.

## 5. How progression continuity became stronger

- Multi-turn behavior unchanged in rule shape, but **history** now carries `committed_interpretation_effect` per turn for clearer cross-turn auditing alongside `progression_commit`.

## 6. What still remains intentionally conservative

- Only **scene id** progression is committed; no full action/reaction/speech simulation state.
- **Failed or unparsed** model generations do not supply a model candidate (no synthetic `proposed_scene_id`).
- **Unknown** model scene ids are recorded but **not** selected; token scan is not used to “fix” an invalid model id.

## 7. Tests added/updated

- New: `test_story_progression_merge.py` (model commit, command beats model, unknown model audit, diagnostics vs committed tail).
- Updated: `test_story_runtime_rag_runtime.py` (selected source assertions, `committed_interpretation_effect` on tail).

## 8. Exact test commands run

```text
cd c:\Users\YvesT\PycharmProjects\WorldOfShadows\world-engine
$env:PYTHONPATH="c:\Users\YvesT\PycharmProjects\WorldOfShadows;c:\Users\YvesT\PycharmProjects\WorldOfShadows\world-engine"
python -m pytest tests\test_story_progression_merge.py tests\test_story_runtime_rag_runtime.py -v --tb=short
```

Result: **12 passed**, exit code **0** (Windows, Python 3.13.12).

```text
cd c:\Users\YvesT\PycharmProjects\WorldOfShadows\world-engine
$env:PYTHONPATH="c:\Users\YvesT\PycharmProjects\WorldOfShadows;c:\Users\YvesT\PycharmProjects\WorldOfShadows\world-engine"
python -m pytest tests\test_story_runtime_api.py -v --tb=short
```

Result: **2 passed**, exit code **0**.

## 9. Verdict

**Pass**

## 10. Reason for verdict

- Committed semantics are materially stronger: model proposals participate with explicit priority and audit fields; committed history is more useful without claiming full narrative simulation.
- Multi-turn and illegal-rejection paths are covered; diagnostics vs committed tail distinction is test-proven.
- Report states conservative boundaries explicitly.

## 11. Remaining risk

- When LangChain structured parsing fails, `structured_output` may be absent—model-driven progression is best-effort and tied to parse success (unchanged honesty constraint).
- Token scan can still pick the first embedded known id in long prose; authors should keep scene ids distinctive in content if that is undesirable.
