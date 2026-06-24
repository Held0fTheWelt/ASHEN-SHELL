# Operations Runbook

This runbook is for maintaining a local AKDB checkout and database.

## Start The Service

```powershell
akdb serve --host 127.0.0.1 --port 8787
```

Health check:

```text
http://127.0.0.1:8787/health
```

## Use A Specific Database

```powershell
akdb --db .akdb\architectural_knowledge_db.sqlite serve
```

Or set:

```powershell
$env:AKDB_DATABASE_PATH = "D:\TinyToolDevelopment\Tools\ArchitecturalKnowledgeDB\.akdb\architectural_knowledge_db.sqlite"
```

## Refresh Knowledge After Document Changes

For a standard starter layout:

```powershell
akdb adr import --project my-project --folder docs/architecture/adr
akdb document import --project my-project --folder docs/architecture --exclude "adr/**"
akdb uml import --project my-project --folder docs/architecture/uml
akdb git scan --project my-project
akdb stale run --project my-project
```

For MCP clients, `akdb_reingest_project` can perform a similar refresh from the configured source folders. It writes to the database, so use it only against a database the client owns or while the HTTP service is stopped.

## Swap A Local Database

The repo-local helper has a safe status mode:

```powershell
scripts\refresh_akdb_db.bat
```

Apply mode stops the local service on port `8787`, backs up the live database, copies the selected source database, and restarts the service:

```powershell
scripts\refresh_akdb_db.bat apply
scripts\refresh_akdb_db.bat apply D:\path\to\source.sqlite
```

Restart MCP clients after a DB swap so their stdio servers reopen the database.

## Keep The Repository Clean

- `.akdb/`, `Temp/`, and `exports/` are runtime output.
- Do not commit generated exports from external projects.
- Do not copy Tiny Tools SAD/UML packages into AKDB.
- Keep public showcase/user scripts in `D:\TinyToolDevelopment\Git\Tools`, not in this repository.

## Validate

```powershell
python -m pytest
```
