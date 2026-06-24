# SPEC 01 — ADR Vertical Slice: Round-Trip and DB-First Authoring

Status: Proposed
Date: 2026-06-16
Depends on: base ArchitecturalKnowledgeDB spec, ADR-0004 (multi-project)

## 1. Purpose

Deliver a thin end-to-end column that proves the DB-first co-authoring loop on the ADR corpus:

> Import the existing ADR markdown files losslessly → edit one ADR in the database through MCP
> tools (with the agent) → export back to the ADR folder → the resulting Git diff is small and
> stable, and a second round-trip changes nothing (idempotent).

This slice deliberately covers ADRs only. UML, Git provenance, staleness, context packs, semantic
retrieval, HTTP/FastAPI, and the admin UI are handled by later specs. The point is to prove the
spine (DB ↔ files ↔ MCP) on the easier artifact before structured UML lands on it.

## 2. Scope

In scope:

- Multi-project SQLite schema foundation (migration runner, connection manager, config loader).
- ADR import pipeline: ADR folder → DB records, lossless.
- ADR export pipeline: DB records → ADR folder, deterministic.
- Round-trip conformance gate (idempotency + no content loss) over the real ADR corpus.
- MCP stdio server exposing ADR read and authoring tools.
- Typer CLI for import/export/list/get.
- Minimal consistency checks needed while editing: supersede chains and broken supersedes links.
- FTS5 indexing of ADR text for `akdb_search_adrs`.

Out of scope (later specs): UML, Git provenance/staleness, context-pack builder, semantic
retrieval, FastAPI/HTTP surface, admin UI, folder→project mapping per plugin.

## 3. Success criteria

1. All existing ADR files import without loss; each DB record can reproduce its original bytes.
2. `import → export → import` yields an identical DB record (idempotent). The first export may
   normalize formatting once; every subsequent round-trip is byte-stable.
3. The agent can, via MCP: list ADRs, read one, propose a new ADR, edit a section, set status with
   `supersedes`, and export — and the change appears as a clean, reviewable Git diff in the ADR
   folder.
4. A query without a `project_id` is rejected (no silent global search).

## 4. Architecture and stack

Stack is fixed by the base design: Python 3.11+, SQLite (WAL + FTS5), Pydantic models, Typer CLI,
pytest, MCP stdio server. **No HTTP/FastAPI in this slice** — only CLI + MCP. FastAPI arrives with
the retrieval/admin specs.

```
architectural_knowledge_db/
  config.py          # data root, ADR folder path, active project id
  db/
    connection.py    # SQLite (WAL) connection manager
    migrations.py    # ordered migration runner
    schema/          # versioned .sql migrations
  model/
    adr.py           # Pydantic: AdrDocument, AdrSection, Project, KnowledgeItem
  adr/
    parser.py        # Markdown -> AdrDocument (lossless)
    renderer.py      # AdrDocument -> Markdown (deterministic)
    roundtrip.py     # import/export orchestration + conformance check
  consistency/
    supersede.py     # supersede chains + broken-link checks (minimal)
  search/
    fts.py           # FTS5 index maintenance + query
  mcp/
    server.py        # stdio MCP server
    tools.py         # tool definitions + dispatch
  cli.py             # typer entrypoint
```

Each module has one responsibility and a narrow interface: `parser`/`renderer` are pure functions
over text and `AdrDocument`; `roundtrip` orchestrates persistence; `mcp` only translates tool calls
into core operations. None of them reach into another's internals.

## 5. Data model (lossless extension)

Reuse the base `projects`, `knowledge_spaces`, `project_imports`, `knowledge_items`, and `adrs`
tables. Two additions to `adrs` guarantee the lossless invariant:

- `raw_source TEXT` — the exact original file bytes. Ultimate safety net; lets export reproduce the
  original verbatim and lets tests assert no content loss.
- `sections_json TEXT` — an **ordered** list of document parts:

  ```json
  [
    {"kind": "preamble", "text": "..."},
    {"kind": "heading",  "level": 1, "title": "ADR-0003: Git Provenance ...", "role": "title"},
    {"kind": "section",  "level": 2, "title": "Status",       "role": "status",       "body_md": "Proposed"},
    {"kind": "section",  "level": 2, "title": "Context",      "role": "context",      "body_md": "..."},
    {"kind": "section",  "level": 2, "title": "Decision",     "role": "decision",     "body_md": "..."},
    {"kind": "section",  "level": 2, "title": "Consequences", "role": "consequences", "body_md": "..."},
    {"kind": "section",  "level": 2, "title": "Authority model", "role": "other",     "body_md": "..."}
  ]
  ```

Rules:

- Known H2 roles (`status`, `context`, `decision`, `consequences`) are also mapped into the typed
  columns (`status`, `context_md`, `decision_md`, `consequences_md`) for querying and editing.
- Unknown sections (e.g. "Authority model", "Privacy", "Non-goals") and any embedded fenced blocks
  (including ` ```mermaid ` diagrams) ride along verbatim as `role: other`.
- Any content before the first heading is preserved as a `preamble` part.
- `supersedes_json` / `superseded_by_json` are parsed from the recognized fields when present.

The schema stays multi-project (ADR-0004). This slice imports into **one configurable project id**;
mapping folders to per-plugin projects is a later refinement.

## 6. Round-trip pipeline

- **Import** (`roundtrip.import_adrs(folder, project_id)`): for each `*.md`, `parser` builds an
  `AdrDocument`; persist the typed fields + `sections_json` + `raw_source`. Nothing is discarded —
  whatever the parser does not recognize becomes `preamble`/`other`. Re-importing an unchanged
  folder is a no-op at the record level.
- **Export** (`roundtrip.export_adrs(folder, project_id)`): `renderer` rebuilds markdown from
  `sections_json` in original order; edited typed fields replace the body of their mapped section.
  Files are written into the configured ADR folder.
- **Conformance gate** (`roundtrip.check(folder)`): the invariant test. For every file:
  `parse → render → parse` must produce an equal `AdrDocument`. A one-time normalization on first
  export is allowed; the second round-trip must be byte-stable. Run across the entire real ADR
  corpus in CI.

## 7. MCP server and authoring tools

A stdio MCP server registered in the agent session. Tools:

Read:
- `akdb_list_adrs(project_id, status?, limit?)`
- `akdb_get_adr(project_id, adr_id)` → typed fields + ordered sections
- `akdb_search_adrs(project_id, query, limit?)` → FTS5

Write (DB-first; never touch files except via export):
- `akdb_propose_adr(project_id, adr_id, title, context_md, decision_md, consequences_md, status="Proposed")`
- `akdb_update_adr_section(project_id, adr_id, role, body_md)` — `role ∈ {status, context, decision, consequences}` or a named `other` section
- `akdb_set_adr_status(project_id, adr_id, status, supersedes?[])` — maintains supersede links
- `akdb_export_adrs(project_id, folder?)` — DB → folder
- `akdb_import_adrs(project_id, folder?)` — folder → DB

Gating model: write tools mutate **only the database**. The ADR folder changes solely through the
explicit `akdb_export_adrs` call, so Git review/commit stays with the author. Claude Code's own
permission prompts add a second gate on any file write the agent performs.

## 8. Minimal consistency

Only what is needed during editing (the full engine is SPEC_03):

- **Supersede chains:** when `A supersedes B`, set `B.superseded_by ⊇ {A}`; detect and warn on
  cycles.
- **Broken-link check:** a `supersedes` entry pointing to a non-existent ADR id raises a warning.

Both are advisory (warnings in tool output / CLI), never blocking.

## 9. CLI

```bash
akdb project add --id <id> --name <name>
akdb adr import --project <id> --folder <path>
akdb adr export --project <id> --folder <path>
akdb adr list   --project <id>
akdb adr get    --project <id> --adr <ADR-0003>
akdb roundtrip check --folder <path>
```

## 10. Testing

- **Round-trip property test** over the entire real ADR corpus: idempotency and no content loss
  versus `raw_source`.
- **Golden-file tests** for parser/renderer, including embedded mermaid and extra/unknown sections.
- **Project isolation:** a data-access call without `project_id` is rejected.
- **MCP tool tests:** `propose`/`update`/`set_status`/`export` produce the expected DB and file
  results; supersede and broken-link warnings fire correctly.

## 11. Open decisions

- ADR id derivation on import (from filename vs. from the H1 title) when they disagree — proposed
  default: trust the H1 title, record the filename in metadata, warn on mismatch.
- Export filename policy for newly proposed ADRs (slug from title vs. caller-provided).

These are resolved during the implementation plan, not blockers for this design.
