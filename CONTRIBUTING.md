# Contributing

Full workflow, layout, and conventions: **[docs/dev/contributing.md](docs/dev/contributing.md)**.

## Despaghettify · Cursor skills (repo standard)

- **Author** agent skills only under **`despaghettify/superpowers/<skill-name>/SKILL.md`**.
- **Mirror** them into **`.cursor/skills/`** for Cursor project discovery by running **`python despaghettify/tools/sync_despag_skills.py`** from the repo root after any skill change (before commit/PR).
- **Validate** links in skill markdown: **`python despaghettify/tools/validate_despag_skill_paths.py`** (see `despaghettify/superpowers/references/VALIDATION.md`; CI runs on hub edits).
- **Do not** rely on manual symlinks or one-off copies; the sync script is the supported path. Root **`AGENTS.md`** repeats this for AI agents.
