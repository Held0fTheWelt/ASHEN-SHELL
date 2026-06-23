# Project SAD frontmatter convention

Every project-wide SAD carries YAML frontmatter:

| Key | Meaning |
| --- | --- |
| `id` | Stable id, e.g. `SAD-PROJECT-GOVERNANCE` |
| `status` | `accepted`, `draft`, `deprecated` |
| `type` | `project-sad` |
| `owns-adrs` | ADR ids absorbed into §9 |
| `uml-package` | Path under `UML/Project/<system>/` |
| `components` | Optional affected component slugs |
| `supersedes` | Superseded ids (not deleted paths) |
| `links` | Important routes to contracts, gates, evidence |

Component SADs use visible metadata lines instead:

```markdown
**Component:** world-engine · **Scope:** play service · **Status:** internal
**Last reconciled to code:** YYYY-MM-DD
```
