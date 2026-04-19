# V24 next MVP runtime increment integration-readiness report

## MVP blueprint surfaces now clean enough to port

The strongest current MVP blueprint surfaces are:

- `frontend/app/routes.py`
  - canonical player-shell bridge composition for initial load, observe refresh, and execute JSON flow;
- `frontend/templates/session_shell.html`
  - stable render anchors for authoritative status, run details, transcript preview, runtime readiness, and refresh interaction;
- `frontend/static/play_shell.js`
  - single client-side apply path for initial hydration, execute response, and observe refresh;
- `backend/app/services/game_service.py`
  - existing backend bridge into authoritative world-engine-backed run/transcript behavior;
- `backend/app/api/v1/game_routes.py`
  - authoritative run detail/transcript bridge endpoints already used by the shell.

## Seams now clean enough to port into the frozen repo

These seams are now integration-friendly:

1. **Initial load → authoritative shell bundle**
2. **Execute JSON → authoritative shell bundle**
3. **Observe refresh → authoritative shell bundle**
4. **Single frontend render/update path fed by one response dialect**

This is a stronger blueprint than a collection of separate micro-patches because the same response shape now drives all three shell entry points.

## Seams that remain intentionally bounded or partial

- live runtime observation remains request/response based rather than streamed;
- backend-local compatibility/bootstrap residue still exists outside this shell path, but it remains bounded and non-authoritative;
- cached shell observation remains a continuity/fallback aid only and is explicitly marked as such.

## What the later repo-integration pass must pay special attention to

- preserve the canonical shell response shape when porting, rather than re-splitting initial load / execute / observe into separate ad hoc render contracts;
- preserve `observation_meta` semantics (`fresh`, `cached_fallback`, `unavailable`) so UX continuity does not silently become truth confusion;
- preserve the rule that shell-visible state is always downstream of authoritative run detail + transcript data;
- avoid letting frozen-repo integration accidentally reintroduce duplicate shell-state composition in JS and route handlers.
