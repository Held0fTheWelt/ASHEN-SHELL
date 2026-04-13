# Agent notes (World of Shadows)

## Repository language

**Canonical wording:** [`docs/dev/contributing.md`](docs/dev/contributing.md) — heading **Repository language** (anchor `#repository-language`). Follow that section; do not treat this file as a second copy of the policy.

## Despaghettify hub

The Despaghettify hub (Python package **`despaghettify`**, task Markdown, **state/**) lives under **`'fy'-suites/despaghettify/`** alongside other repo-wide tool suites. Use **`pip install -e .`** at the repo root so `python -m despaghettify.tools …` resolves the package (see root **`pyproject.toml`**).

### Repo standard (Cursor)

1. **Router skills** live under `'fy'-suites/despaghettify/superpowers/<skill-name>/SKILL.md` (minimal; edit only to improve routing or descriptions). **Procedure** lives in the task Markdowns (`spaghetti-check-task.md`, `spaghetti-solve-task.md`, etc.); **numeric** trigger policy lives in `'fy'-suites/despaghettify/spaghetti-setup.md` — never duplicate those in a skill.
2. **Cursor discovery** uses **`.cursor/skills/<skill-name>/SKILL.md`** (committed). After changing any canonical skill file, run **`python "./'fy'-suites/despaghettify/tools/sync_despag_skills.py"`** from the repo root before commit/PR (same as human contributors; optional CI: `python "./'fy'-suites/despaghettify/tools/sync_despag_skills.py" --check`).
3. Do **not** hand-edit only `.cursor/skills/` — it will be overwritten on the next sync. **Windows / macOS / Linux:** use **`python "./'fy'-suites/despaghettify/tools/sync_despag_skills.py"`** (file copy) only — **no** symlinks, **no** `mklink`; committed `.cursor/skills/` is what Cursor auto-loads.
4. **Language:** Same canonical policy as [`docs/dev/contributing.md`](docs/dev/contributing.md#repository-language). Hub files add **procedure-only scope** in `'fy'-suites/despaghettify/README.md` (**Language** paragraph) and each task Markdown `**Language:**` line — **links upward**, no restated project policy.

### References

- **CLI:** `python -m despaghettify.tools check` (`--with-metrics` optional) | `open-ds` | `solve-preflight --ds DS-nnn` | `autonomous-init` / `autonomous-advance` / `autonomous-status` / `autonomous-verify` | `metrics-emit` | `trigger-eval` (optional `pip install -e .` → `despag-check` / `wos-despag`) — see `'fy'-suites/despaghettify/superpowers/references/CLI.md`.
- **Task docs:** `'fy'-suites/despaghettify/spaghetti-check-task.md`, `spaghetti-solve-task.md`, `spaghetti-add-task-to-meet-trigger.md`, `spaghetti-autonomous-agent-task.md`; numeric policy `'fy'-suites/despaghettify/spaghetti-setup.md`; input list `'fy'-suites/despaghettify/despaghettification_implementation_input.md`.

Human-oriented contributor wording also lives in **root `CONTRIBUTING.md`** and **`docs/dev/contributing.md`** (Despaghettify and Cursor agent skills).

**Skill path validation:** `python "./'fy'-suites/despaghettify/tools/validate_despag_skill_paths.py"` (see `'fy'-suites/despaghettify/superpowers/references/VALIDATION.md`; GitHub Actions runs on relevant diffs).

## Postmanify hub

1. **Router skill** lives under `'fy'-suites/postmanify/superpowers/postmanify-sync/SKILL.md`. **Procedure** lives in `'fy'-suites/postmanify/postmanify-sync-task.md`.
2. **Cursor discovery:** after editing that skill, run **`python "./'fy'-suites/postmanify/tools/sync_postmanify_skills.py"`** from the repo root (same copy-only rule as Despaghettify — no symlinks).
3. **CLI:** `python -m postmanify.tools plan` | `generate` (requires **`pip install -e .`**) — see `'fy'-suites/postmanify/superpowers/references/CLI.md`. Console script **`postmanify`** is equivalent.

## Docify hub

Docify lives under **`'fy'-suites/docify/`** with other **“fy”** meta-tool suites; see the suite catalog in **`'fy'-suites/Readme.md`**.

1. **Router skills** live under ``'fy'-suites/docify/superpowers/<skill-name>/SKILL.md`` (minimal). **Procedure** lives in task Markdowns in that folder (for example ``'fy'-suites/docify/documentation-audit-task.md``); do not duplicate repository language policy in skills.
2. **Cursor discovery** uses **`.cursor/skills/<skill-name>/SKILL.md`** (committed). After changing any canonical Docify skill file, run **`python "./'fy'-suites/docify/tools/sync_docify_skills.py"`** from the repo root before commit/PR (optional CI: `python "./'fy'-suites/docify/tools/sync_docify_skills.py" --check`).
3. Do **not** hand-edit only `.cursor/skills/` for Docify copies — the next sync overwrites them. Use **`python "./'fy'-suites/docify/tools/sync_docify_skills.py"`** (file copy only — **no** symlinks, **no** `mklink`).
4. **Language:** Same canonical policy as [`docs/dev/contributing.md`](docs/dev/contributing.md#repository-language). Hub overview: **`'fy'-suites/docify/README.md`**.

**Docify default docstring scan** (`python_documentation_audit.py` without `--root`): `backend`, `world-engine`, `ai_stack`, `frontend`, `administration-tool`, `story_runtime_core`, `'fy'-suites/despaghettify`, `'fy'-suites/postmanify`, `tools/mcp_server` — not the Docify tree itself; use ``--root 'fy'-suites/docify`` when you want that slice (see **`'fy'-suites/docify/README.md`**). **`python_docstring_synthesize.py`** does **not** scan the tree; it adds **PEP 8 inline `#` comments** or an optional Google docstring draft for a chosen `--file` (see **`'fy'-suites/docify/documentation-docstring-synthesize-task.md`**).

**Docify path validation:** `python "./'fy'-suites/docify/tools/validate_docify_skill_paths.py"` (GitHub Actions: `.github/workflows/docify-skills-validate.yml` on relevant diffs).
