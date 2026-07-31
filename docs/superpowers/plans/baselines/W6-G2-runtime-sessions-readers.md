# G2 — `runtime_sessions` reader audit + drop evidence (Wave 6)

**Status:** EXECUTED 2026-07-31 (Gate G2 approved in
`docs/superpowers/plans/DRIFT_SANIERUNG_GATE_ENTSCHEIDUNGEN.md`).

## Table / model (pre-drop)
- SQLAlchemy: `backend/app/models/world_engine/runtime_session.py` — **deleted**
- `__tablename__ = "runtime_sessions"`
- Was exported from `backend/app/models/__init__.py` as `RuntimeSessionRecord` — **removed**

## Static reader/writer scan (2026-07-31, pre-drop)
| Kind | Finding |
| --- | --- |
| ORM model definition | Present (removed after drop) |
| Python `query` / `session.add` / `RuntimeSessionRecord(` usage | **None** outside model definition + `__init__` export |
| String `runtime_sessions` in product code | Model file only |
| Docs / plans / drift catalog | Mentions only (plans, SAD, CHANGELOG, RAG corpus) |
| External SQL / BI / operator access | **None observed** during local up/down execution |

## Step 1 — row count (mandatory)

| Field | Value |
| --- | --- |
| Date | 2026-07-31 |
| Database | `backend/instance/wos.db` (SQLite; shared with `worldofshadows-backend-1`) |
| Command | `SELECT COUNT(*) FROM runtime_sessions;` |
| Result | **0** |

## Step 2 — archive

Skipped: COUNT was 0. No
`docs/superpowers/plans/baselines/W6-G2-runtime-sessions-archive.json` created.

## Step 3–4 — migration + model removal

- Alembic: `backend/migrations/versions/049_drop_runtime_sessions.py`
- Downgrade docstring states it restores **structure only**, not data.
- Model file deleted; export removed from `backend/app/models/__init__.py`.

## Step 5 — gate

- `tests/gates/test_runtime_sessions_table_absent.py`

## Step 6 — up/down evidence (local DB)

| Direction | Command | Result |
| --- | --- | --- |
| upgrade 048→049 | `docker exec worldofshadows-backend-1 bash -lc "cd /app && flask db upgrade"` | `Running upgrade 048 -> 049`; table absent; `alembic_version=049` |
| downgrade 049→048 | `docker exec worldofshadows-backend-1 bash -lc "cd /app && flask db downgrade 048"` | `Running downgrade 049 -> 048`; empty table restored; `alembic_version=048`; COUNT=0 |
| upgrade again | same upgrade command | table absent; `alembic_version=049` |

Final local state after evidence run: **table absent**, revision **049**.
