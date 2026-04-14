# Implementation report: story runtime complete playable MVP

**Scope:** Authoritative Turn 0 opening on session create, governed runtime wiring, bounded self-correction and degraded continuation, diagnostics and repro metadata, backend bridge surfacing of `opening_turn` on lazy World Engine bind, play-shell transcript + progressive narration styling.

## Summary

The World Engine story runtime commits an **opening** turn when sessions are created (production path). The create API returns `opening_turn` and `runtime_config_status`. The LangGraph executor supports **self-correction retries** and optional **degraded commit** after exhaustion, with playability helpers in `ai_stack/story_runtime_playability.py`.

The backend **first-turn bridge** (`session_routes.execute_session_turn`) now forwards `opening_turn` and `world_engine_opening_meta` when it creates the World Engine session in the same request, so the UI can show the opening without an extra round trip.

The frontend play shell **prepends** the opening transcript row when that payload is present, maps opening rows with `interpreted_input_kind: opening` and no raw prompt as player line, and applies a short **CSS reveal animation** on committed narration blocks.

## Tests

- World Engine: `pytest tests/ -k story_runtime` (story-runtime family)
- Frontend: `frontend/tests/test_routes_extended.py` (play shell routes)

## Follow-ups (optional)

- E2E browser test for `/play/<run>` first turn showing opening + player reply
- CHANGELOG entry if release notes require a customer-facing line
