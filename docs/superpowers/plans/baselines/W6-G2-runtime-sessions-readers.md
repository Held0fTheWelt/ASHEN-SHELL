# G2 — `runtime_sessions` reader audit (Wave 6)

**Status:** Awaiting human approval (**G2**). Do **not** drop the table until approved.

## Table / model
- SQLAlchemy: `backend/app/models/world_engine/runtime_session.py`
- `__tablename__ = "runtime_sessions"`
- Exported from `backend/app/models/__init__.py` as `RuntimeSessionRecord`

## Static reader/writer scan (2026-07-31)
| Kind | Finding |
| --- | --- |
| ORM model definition | Present |
| Python `query` / `session.add` / `RuntimeSessionRecord(` usage | **None** outside model definition + `__init__` export |
| String `runtime_sessions` in product code | Model file only |
| Docs / plans / drift catalog | Mentions only (plans, SAD, CHANGELOG, RAG corpus) |

## Conclusion
No live Python read/write path was found. The table appears **dormant schema residue** complementary to the deleted backend turn cluster. Dropping it is still a **data migration** (Human Gate G2): confirm no external SQL/BI/operator views depend on it, then remove model + Alembic migration with a reversible down-migration.

## Proposed next step (after approval)
1. Add Alembic migration `DROP TABLE runtime_sessions` (reversible `CREATE` in downgrade).
2. Remove `RuntimeSessionRecord` and package export.
3. Add `test_runtime_sessions_table_absent` as plan exit criterion.
