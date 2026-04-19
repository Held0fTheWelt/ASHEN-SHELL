# WorldOfShadows documentation

Audience-first documentation entrypoint.

## Start here (everyone)

- Plain-language orientation: [`docs/start-here/README.md`](start-here/README.md)
- Master index: [`docs/INDEX.md`](INDEX.md)
- Full glossary: [`docs/reference/glossary.md`](reference/glossary.md)
- Short glossary: [`docs/start-here/glossary.md`](start-here/glossary.md)
- Doc registry: [`docs/reference/documentation-registry.md`](reference/documentation-registry.md)

## Audience roots

- **Users:** [`docs/user/README.md`](user/README.md)
- **Administrators / operators:** [`docs/admin/README.md`](admin/README.md)
- **Developers:** [`docs/dev/README.md`](dev/README.md) — lean redirect layer retained for governance-stable paths
- **Technical system (architecture, AI, runtime):** [`docs/technical/README.md`](technical/README.md)
- **Stakeholder slides:** [`docs/presentations/`](presentations/)
- **ADRs:** [`docs/governance/README.md`](governance/README.md)

## Optional static site (MkDocs)

From repository root (after `pip install -r requirements-docs.txt`):

```bash
python -m mkdocs serve
```

Build output is gitignored at `/site/` (see `mkdocs.yml`). CI builds on changes to `docs/`, `mkdocs.yml`, and `requirements-docs.txt`.

## Legacy and evidence

- **Archived/tombstoned carry-forward surfaces:** [`docs/archive/`](archive/) — lean notes only, not the full historical archive
- **Audit tombstone:** [`docs/audit/`](audit/) — current governance evidence now lives primarily under `validation/` and `governance/`

## Consolidation and carry-forward record

See [`governance/V24_SOURCE_PRESERVATION_LEDGER.md`](../governance/V24_SOURCE_PRESERVATION_LEDGER.md) for the original-repository → v24 mapping and intentional exclusions.
