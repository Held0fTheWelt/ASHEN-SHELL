# 52 — Validation Runbook

Use these commands as the default validation spine after implementation work.
Adjust only when the owning component requires a narrower or broader run.

## MVP scaffold

```bash
cd reference_scaffold
pip install -e .[test]
pytest -q
```

## Backend

```bash
cd ../backend
pip install -r requirements.txt
PYTHONPATH=. pytest -q tests/test_session_routes.py
PYTHONPATH=. pytest -q tests/runtime/test_mcp_enrichment.py
```

## MCP server

```bash
cd ..
PYTHONPATH=backend:. pytest -q tools/mcp_server/tests/test_mcp_runtime_safe_session_surface.py
PYTHONPATH=backend:. pytest -q tools/mcp_server/tests/test_mcp_operational_parity_and_registry.py
```

## AI stack

```bash
cd ..
PYTHONPATH=. pytest -q ai_stack/tests/test_mcp_canonical_surface.py
PYTHONPATH=. pytest -q ai_stack/tests/test_langgraph_runtime.py
```

## Repository smoke

```bash
cd ..
PYTHONPATH=backend:. pytest -q tests/smoke
```

## Reporting rule

Always report:
- what was run,
- what passed,
- what failed,
- and what was not run.
