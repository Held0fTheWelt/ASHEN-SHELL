# Agent notes (World of Shadows)

## Despaghettify hub

### Repo standard (Cursor)

1. **Router skills** live under `despaghettify/superpowers/<skill-name>/SKILL.md` (minimal; edit only to improve routing or descriptions). **Procedure** lives in the task Markdowns (`spaghetti-check-task.md`, `spaghetti-solve-task.md`, etc.); **numeric** trigger policy lives in `despaghettify/spaghetti-setup.md` — never duplicate those in a skill.
2. **Cursor discovery** uses **`.cursor/skills/<skill-name>/SKILL.md`** (committed). After changing any canonical skill file, run **`python despaghettify/tools/sync_despag_skills.py`** from the repo root before commit/PR (same as human contributors; optional CI: `python despaghettify/tools/sync_despag_skills.py --check`).
3. Do **not** hand-edit only `.cursor/skills/` — it will be overwritten on the next sync. **Windows / macOS / Linux:** use **`python despaghettify/tools/sync_despag_skills.py`** (file copy) only — **no** symlinks, **no** `mklink`; committed `.cursor/skills/` is what Cursor auto-loads.

### References

- **CLI:** `python -m despaghettify.tools check` (`--with-metrics` optional) | `open-ds` | `solve-preflight --ds DS-nnn` | `autonomous-init` / `autonomous-advance` / `autonomous-status` / `autonomous-verify` | `metrics-emit` | `trigger-eval` (optional `pip install -e .` → `despag-check` / `wos-despag`) — see `despaghettify/superpowers/references/CLI.md`.
- **Task docs:** `despaghettify/spaghetti-check-task.md`, `spaghetti-solve-task.md`, `spaghetti-add-task-to-meet-trigger.md`, `spaghetti-autonomous-agent-task.md`; numeric policy `despaghettify/spaghetti-setup.md`; input list `despaghettify/despaghettification_implementation_input.md`.

Human-oriented contributor wording also lives in **root `CONTRIBUTING.md`** and **`docs/dev/contributing.md`** (§ Despaghettify and Cursor agent skills).

**Skill path validation:** `python despaghettify/tools/validate_despag_skill_paths.py` (see `despaghettify/superpowers/references/VALIDATION.md`; GitHub Actions runs on relevant diffs).
