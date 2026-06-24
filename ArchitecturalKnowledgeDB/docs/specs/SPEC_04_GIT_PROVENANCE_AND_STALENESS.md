# SPEC 04 — Git Provenance & Staleness

Status: Proposed
Date: 2026-06-16
Depends on: SPEC_01 (DB foundation, project/repo scoping)
Implements: ADR-0003 (Git Provenance and Code Evolution Layer)

## 1. Purpose

Add the linked, read-only Git provenance layer described in ADR-0003 and the base spec, and turn it
into staleness/drift signals that surface during authoring: *which ADR or diagram has fallen behind
the code it describes?* Git is evidence, never authority.

## 2. Scope

In scope:

- Repository registry per project (path, sanitized remote, default branch, scan policy,
  include/exclude patterns).
- Read-only Git scanner (Git CLI or pygit2) for commit metadata and changed file paths. The `.git`
  directory is never copied into the database.
- File history summaries (first seen, last changed, change count).
- Origin trail for a source path or knowledge item (explicit links + inferred co-change links with
  confidence).
- Staleness/drift levels (`current|watch|review_recommended|likely_stale|unknown`) computed from
  related source changes after a knowledge item's last update.
- Provenance + staleness surfaced through MCP and folded into the SPEC_03 impact summary.

Out of scope (per ADR-0003): repository mutation, Git writes, full diffs by default, raw author
emails by default, treating Git correlation as authoritative.

## 3. Success criteria

1. A repository registers under one project; a scan stores commit hashes and changed paths and never
   writes to the repo or stores `.git` internals (asserted by test).
2. File history reports first-seen, last-changed, and change count; author email is not stored by
   default; remote URLs are sanitized.
3. `explain_origin(source_path)` returns related ADRs/rules/UML, first/last commits, and co-changed
   files, clearly labeled as evidence, not authority.
4. A diagram whose related source changed after its last update is reported `review_recommended`.

## 4. Data model

Reuse the base schema: `repositories`, `git_commits`, `git_commit_files`, `git_file_history`,
`staleness_reports`, and `knowledge_links` (for inferred `git_cochange_inferred` links with a
confidence label). No new tables required.

## 5. Module layout

```
architectural_knowledge_db/provenance/
  registry.py     # repository registration + scan policy
  scanner.py      # read-only git metadata scan (commits, changed files)
  sanitize.py     # remote-url sanitization, author-email hashing/omission
  history.py      # file history summaries
  origin.py       # origin-trail assembly (explicit + inferred links)
  staleness.py    # staleness/drift level computation
```

## 6. MCP tools

- `akdb_get_git_provenance(project_id, target, limit_commits?)`
- `akdb_explain_origin(project_id, target, target_type?)`
- `akdb_get_staleness_report(project_id, target?, status_filter?)`
- `akdb_scan_repo(project_id, repository_id?)` — explicit, manual scan trigger

## 7. Safety requirements (from ADR-0003)

- All Git operations are read-only; Docker source mounts are read-only.
- No credentials persisted; remote URLs sanitized before storage.
- Author email storage disabled by default (hashed only if explicitly enabled).
- Full diffs out of scope; optional later diff storage restricted to ADR/UML/rule files and
  explicitly enabled.

## 8. Testing

- Scan stores expected metadata; a test asserts no repo writes and no `.git` internals persisted.
- Sanitization test (remote URLs, omitted/hashed emails).
- File-history correctness on a fixture repo.
- Origin-trail output includes explicit + inferred links with confidence labels.
- Staleness levels computed correctly from related-source change timing.

## 9. Open decisions

- Git CLI vs. pygit2 for the scanner — proposed default: Git CLI first (zero build deps), with the
  adapter interface allowing a pygit2 backend later.
- Co-change inference window and confidence thresholds — tuned during planning.
