# AKDB Documentation

This folder documents ArchitecturalKnowledgeDB itself: how to run it, how to operate it, how the local data model works, and how the implementation is planned. It should not contain copied documentation, SADs, UML packages, exports, or generated corpora from other repositories.

## Where To Start

| Need | Read |
| --- | --- |
| Understand the repository quickly | [Repository README](../README.md) |
| Run AKDB for the first time | [user/QUICKSTART.md](user/QUICKSTART.md) |
| Use the CLI/API/MCP workflows | [user/USER_MANUAL.md](user/USER_MANUAL.md) |
| Configure database paths and runtime settings | [user/SETTINGS_REFERENCE.md](user/SETTINGS_REFERENCE.md) |
| Fix a local run or MCP setup | [user/TROUBLESHOOTING.md](user/TROUBLESHOOTING.md) |
| Connect an MCP client | [operations/MCP.md](operations/MCP.md) |
| Maintain a local AKDB instance | [operations/RUNBOOK.md](operations/RUNBOOK.md) |
| Read the product architecture specs | [architecture/README.md](architecture/README.md) |
| Inspect implementation slices | [specs/README.md](specs/README.md) |

## Folder Map

| Folder | Contains |
| --- | --- |
| `user/` | Practical user documentation: quick start, manual, settings, troubleshooting, FAQ, third-party notes. |
| `operations/` | MCP setup, DB refresh notes, runtime ownership, and local maintenance runbook. |
| `architecture/` | AKDB product architecture specs, Git provenance model, multi-project model, and AKDB-owned diagrams. |
| `decisions/` | AKDB-local ADRs that explain product decisions. |
| `specs/` | Implementation-slice specifications used to build and verify the tool. |
| `contracts/` | API and MCP contract documents. |
| `schema/` | SQLite schema reference. |
| `examples/` | Registry, compose, and standalone sample inputs. |
| `planning/` | Roadmap, backlog, and implementation prompt material. |

## Documentation Boundary

AKDB may index other repositories at runtime, but this `docs/` tree only documents AKDB. Generated exports and imported project corpora belong in ignored runtime folders or outside the repository.

In the Tiny Tool workspace, public showcase/user scripts and cross-project architecture authority are maintained in `D:\TinyToolDevelopment\Git`, not copied into AKDB.

## Maintenance Rules

- Keep the root `README.md` as the GitHub-facing entry point.
- Keep this file as the documentation map.
- Add new user-facing docs under `user/`.
- Add new operational procedures under `operations/`.
- Add AKDB-local design decisions under `decisions/`.
- Update [architecture/README.md](architecture/README.md) and the central Tiny Tools SAD/UML in `D:\TinyToolDevelopment\Git` when an architectural contract changes.
- Do not commit `.akdb/`, `Temp/`, `exports/`, imported third-party repositories, or generated project corpora.
