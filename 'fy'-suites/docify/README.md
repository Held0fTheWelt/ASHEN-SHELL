# Docify hub

**Language:** Same canonical policy as [`docs/dev/contributing.md`](../../docs/dev/contributing.md#repository-language). This suite holds **documentation-assist** tooling and **agent router skills**; procedure lives in task Markdowns here, not in skill files.

## Layout

| Path | Role |
|------|------|
| [`superpowers/`](superpowers/) | Minimal Cursor **router** `SKILL.md` files → task docs |
| [`tools/`](tools/) | Docify CLI helpers (AST docstring audit, synthesizer) |
| [`documentation-audit-task.md`](documentation-audit-task.md) | End-to-end procedure for backlog → slice → fix → re-audit |
| [`documentation-docstring-synthesize-task.md`](documentation-docstring-synthesize-task.md) | PEP 8 inline `#` comments for a source range → review → `--apply` |

## Cursor skills

Canonical skills: ``'fy'-suites/docify/superpowers/<skill-name>/SKILL.md``. **Committed** copies for auto-discovery: `.cursor/skills/<skill-name>/SKILL.md`.

After editing any canonical Docify skill, run from repository root:

```bash
python "./'fy'-suites/docify/tools/sync_docify_skills.py"
```

Optional drift check (exit 1 if copies differ):

```bash
python "./'fy'-suites/docify/tools/sync_docify_skills.py" --check
```

Do **not** hand-edit only `.cursor/skills/` for Docify — sync overwrites those files.

## Path validation

```bash
python "./'fy'-suites/docify/tools/validate_docify_skill_paths.py"
```

See root [`AGENTS.md`](../../AGENTS.md) for how Docify relates to the rest of the monorepo.

## Docify CLIs (``'fy'-suites/docify/tools/``)

Both are **Docify hub** entry points (run from repo root with ``python "./'fy'-suites/docify/tools/…"``):

| Script | Role |
|--------|------|
| [`tools/python_documentation_audit.py`](tools/python_documentation_audit.py) | AST audit — missing or empty docstrings; JSON/text |
| [`tools/python_docstring_synthesize.py`](tools/python_docstring_synthesize.py) | Inline block-comment assist for a `--file` line range (PEP 8 `#`); optional `--apply` |

**Default scan roots** (no `--root`): `backend`, `world-engine`, `ai_stack`, `frontend`, `administration-tool`, `story_runtime_core`, `'fy'-suites/despaghettify`, `'fy'-suites/postmanify`, `tools/mcp_server` — full tree each, excluding `**/migrations/**`, `**/site-packages/**`, `world-engine/source/**`, and (unless `--include-tests`) paths whose relative path contains a `tests` segment. The Docify suite itself is **not** in this list (pass ``--root 'fy'-suites/docify`` to audit it). Override with one or more `--root` paths.

Skills and task procedures link here from [`superpowers/`](superpowers/).
