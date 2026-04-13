---
name: docify-orchestrate
description: Routes agents to Docify documentation tasks — Python docstring backlog audit, inline source explain (PEP 8 comments), slice-based fixes, JSON reports. Triggers on docify, docify orchestrate, documentation audit, explain source block, python docstring backlog, doc audit, run docify.
---

# Docify orchestrate (router)

**Do not duplicate repository language policy here.** Pick **one** track and follow **only** that task file end-to-end:

| Intent | Open and follow (single source) |
|--------|----------------------------------|
| **Python docstrings / readability** — measure backlog, work in slices, re-verify | [`documentation-audit-task.md`](../../documentation-audit-task.md) |
| **Inline explain (PEP 8 `#` comments)** — dry-run a range, then `--apply` after review | [`documentation-docstring-synthesize-task.md`](../../documentation-docstring-synthesize-task.md) |

**Tools (helpers only, not policy):** ``'fy'-suites/docify/tools/python_documentation_audit.py`` — AST audit → text or JSON; optional `ruff` append. ``'fy'-suites/docify/tools/python_docstring_synthesize.py`` — block comments for a file/range; `--apply` writes source.

Hub orientation: [`README.md`](../../README.md).
