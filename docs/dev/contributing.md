# Contributing and repository layout

Orientation for **developers** working across World of Shadows services. For plain-language system context, read [Start here](../start-here/README.md) first.

## Top-level layout

| Path | Responsibility |
|------|----------------|
| `frontend/` | Player/public Flask app |
| `administration-tool/` | Admin Flask app |
| `backend/` | API, auth, migrations, content compiler, integration |
| `world-engine/` | Play service (FastAPI): authoritative runtime |
| `ai_stack/` | LangGraph executor, RAG, GoC seams, LangChain bridges, capabilities |
| `story_runtime_core/` | Shared interpretation, model registry, adapters |
| `content/modules/` | Canonical YAML modules (`god_of_carnage/`, …) |
| `writers-room/` | Optional demo UI → backend Writers Room API |
| `tools/mcp_server/` | MCP server for operator/developer tooling |
| `schemas/` | JSON schemas shared across services |
| `tests/` | Repo-root smoke and gate helpers |
| `docs/` | Documentation (audience-first + architecture + audit) |

## Path hazards

- **Two “world-engine” paths:** canonical play service code lives in **root** `world-engine/`. A nested `backend/world-engine/` tree has been flagged as **confusing** in audit baselines—verify before editing or documenting paths.
- **Gitignored evidence:** `tests/reports/` is largely ignored; do not cite it as clone-guaranteed in user/admin docs.

## Package READMEs

Each major service maintains its own README with install and test hints:

- `backend/README.md`
- `world-engine/README.md`
- `frontend/README.md`
- `ai_stack/README.md` (if present) / `world-engine/requirements-dev.txt` for graph tests

## Development workflow

1. Follow [Local development and test workflow](local-development-and-test-workflow.md) for URLs and env vars.
2. Run the **smallest** relevant pytest package before wide suites (see [Test pyramid and suite map](testing/test-pyramid-and-suite-map.md)).
3. When touching GoC behavior, read the [normative contracts index](contracts/normative-contracts-index.md).

## AI and runtime changes

Cross-stack edits often touch `ai_stack/`, `world-engine/`, and `content/modules/` together. Review `docs/audit/TASK_1B_CROSS_STACK_COHESION_BASELINE.md` for seam vocabulary before large refactors.

## Despaghettify and Cursor agent skills

**Repo standard:** Despaghettify **agent skills** under **`despaghettify/superpowers/`** are **thin routers** (they point at task Markdown only — **no** duplicated M7 thresholds or checklists). **Trigger values** and the full analysis procedure are **only** in `despaghettify/spaghetti-check-task.md`. Cursor loads **project** skills from **`.cursor/skills/`**; this repository **commits** mirrored copies so every clone gets the same skills.

After **any** edit to `despaghettify/superpowers/*/SKILL.md`, run from the repository root:

```bash
python despaghettify/tools/sync_despag_skills.py
```

Optional drift check (e.g. in CI): `python despaghettify/tools/sync_despag_skills.py --check` (exit **1** if `.cursor/skills` is out of date). Do not edit `.cursor/skills/` in isolation — sync will overwrite it.

**Skill markdown links:** run `python despaghettify/tools/validate_despag_skill_paths.py` after changing paths under `despaghettify/superpowers/` (CI: `.github/workflows/despaghettify-skills-validate.yml`). See [`despaghettify/superpowers/references/VALIDATION.md`](../../despaghettify/superpowers/references/VALIDATION.md).

See also root **`AGENTS.md`**, [`despaghettify/superpowers/README.md`](../../despaghettify/superpowers/README.md), and [`despaghettify/README.md`](../../despaghettify/README.md).

## Related

- [Architecture README](../architecture/README.md)
- [Documentation registry](../reference/documentation-registry.md)
