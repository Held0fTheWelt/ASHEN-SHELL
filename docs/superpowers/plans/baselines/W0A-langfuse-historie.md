# W0-A — Langfuse history evaluation

**Date:** 2026-07-31  
**Host queried:** `http://127.0.0.1:3000` (Docker DNS `langfuse-web:3000` is not reachable from host)  
**Langfuse health:** `{"status":"OK","version":"3.174.1"}`  
**Stack start:** `python docker-up.py langfuse-up` → exit 0; containers healthy.

## Result

**Usable history: no** (under current credentials).

| Check | Result |
| --- | --- |
| Health endpoint | OK |
| `/api/public/traces` with `.env` `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | **HTTP 401 Unauthorized** |
| Trace count / oldest / newest | unavailable |
| Prompt size median / p95 | unavailable |
| Adapter / invocation-mode distribution | unavailable |

## Escape strategy applied

- **A17** (keys missing or mismatched for this local project): keys are present in `.env` but rejected by the running local instance (likely project reset / key mismatch after volume vs. env drift). Creating a new UI project and writing keys into tracked files is forbidden; `.env` updates for secrets are local-only and were not automated here because interactive signup is required.
- **A16** / **A15**: treat history as unusable; proceed to **W0-B** instrumentation. Call-count-per-turn was never available from history anyway (max two `story.model.generation` observations per turn).

## Explicit non-deliverables from history

- Model calls per turn (median / p95) — **not** derivable from Langfuse history (structural blind spot D27).
- Translation / self-correction / fallback call attribution — invisible in history.

## Next measurement source

W0-B `TurnCallLedger` + post-instrumentation reference playthrough.
