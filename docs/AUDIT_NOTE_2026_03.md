# Audit note – documentation and verification (2026-03)

Internal audit. Scope: documentation cleanup, changelog truth, verification hardening, consistency of completion claims. No feature work.

## Confirmed truths from codebase

- **administration-tool/frontend_app.py:** `BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "https://held0fthewelt.pythonanywhere.com").rstrip("/")` — default is remote PythonAnywhere; local is override only.
- **Paths:** Repository structure uses `backend/` and `administration-tool/` (README already updated in prior pass). On case-sensitive filesystems the actual directory may be `backend` or `Backend`; docs should consistently use `backend/` and `administration-tool/` as the canonical names.
- **backend/pytest.ini:** `addopts = -v --tb=short --cov=app --cov-report=term-missing --cov-fail-under=85` — 85% coverage gate is configured; full verification requires `pytest` from `backend/` with coverage.
- **Test counts:** `backend/tests/test_forum_api.py` has 30 test functions (including subscribe, notifications). Total backend tests are 236 (from last full run). Changelog 0.0.22 "27 passing tests" referred to forum at that time; 0.0.23 added 3 forum tests. Changelog 0.0.18 "203 tests" is historical (at that release).
- **No dedicated verification doc** that states: exact commands, run-from directory, expected pass count, coverage gate, and what is manual.

## Contradictions in docs/changelog

1. **README.md**
   - Line 31: "running from `Backend/`" — contradicts canonical path `backend/`. Fix to `backend/`.
   - Line 157 (env table): "Default SQLite in `Backend/instance/wos.db`" — fix to `backend/instance/wos.db`.
   - Line 35: "Frontend default 5001" — ambiguous; prefer "administration-tool default 5001" or "Frontend (administration-tool) default 5001" for clarity.

2. **docs/development/LocalDevelopment.md**
   - Title and body use "Frontend" and "Backend" as service names; body uses "Backend/" in commands. Fix command paths to `backend/`; clarify that "Frontend" means administration-tool app.
   - Line 17: "From repo root or `Backend/`" — fix to `backend/`.
   - Line 76: "cd Backend" — fix to `cd backend`.

3. **docs/runbook.md**
   - Commands use `Backend` (e.g. `cd Backend`, Working directory `Backend`). Fix to `backend` for consistency with README and repo convention.
   - Line 216: "File: `Backend/content/wiki.md`" — fix to `backend/content/wiki.md` (or note path is under backend).

4. **docs/architecture/ServerArchitecture.md**
   - Uses "Backend/" in text and commands. Fix to `backend/` for current workflow.

5. **CHANGELOG.md**
   - Older entries reference `Backend/`, `Frontend/`, "203 tests", "27 tests". Historical entries can stay as-is with a short clarification where they would mislead (e.g. "Current test count and paths: see README and backend/tests."). 0.0.23 and 0.0.22 are already consistent with backend/ and administration-tool/.

6. **backend/tests/README.md**
   - Layout section does not list test_forum_api.py, test_wiki_public.py, test_data_api.py, etc. Outdated; update in verification phase.

## Stale references — harmless vs misleading

- **Harmless (optional clarification only):** CHANGELOG entries that mention `Backend/docs/...` or `Frontend/` as past state; architecture doc FrontendBackendRestructure.md describes historical split — add one-line note that current folder names are backend/ and administration-tool/.
- **Misleading (must fix):** README and runbook/LocalDevelopment/ServerArchitecture that tell users to "cd Backend" or "from Backend/" — these are setup/run instructions and must use `backend/` so they match the rest of the doc and the repo.

## Exact files to change

| File | Change |
|------|--------|
| README.md | Line 31: Backend/ → backend/. Line 157: Backend/instance → backend/instance. Line 35: clarify Frontend → administration-tool (or leave "Frontend" with short clarification). |
| docs/development/LocalDevelopment.md | Backend/ → backend/ in commands and paths; clarify Frontend = administration-tool. |
| docs/runbook.md | Backend → backend in all commands and paths. |
| docs/architecture/ServerArchitecture.md | Backend/ → backend/ in text and commands. |
| CHANGELOG.md | No mandatory rewrite of old entries; add clarification only where a current default or path would be wrong (e.g. if any entry implies localhost is default for BACKEND_API_URL). Review 0.0.18 "203 tests" and 0.0.20 "85% coverage" — state that 85% is the configured gate and full suite must be run to verify. |
| docs/ (new or update) | Add or update a concise verification doc: commands (targeted + full), run-from directory, expected success, coverage gate, manual verification. |
| backend/tests/README.md | Update layout to include test_forum_api, test_wiki_public, test_data_api, etc.; add "Run from backend/". |

## Verification story

- **Currently missing:** One place that states: (1) run `cd backend && pytest tests/ -v --no-cov` for full suite; (2) run `cd backend && pytest` for coverage-gated run (85%); (3) targeted commands for forum, news, wiki; (4) what "success" means (exit 0, counts); (5) that 85% is not asserted as "currently met" without a recent coverage run.
- **Required:** Add or update `docs/verification.md` (or similar) with the above, and reference it from README Tests section.
