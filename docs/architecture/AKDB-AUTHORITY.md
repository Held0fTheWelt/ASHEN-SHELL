# Better Tomorrow AKDB authority

Better Tomorrow owns its architecture assertions, source bindings, depth gate and
test set. ArchitecturalKnowledgeDB is a pinned, external tool dependency. It is
never a writable source subtree of this repository and is never an authority for
runtime behavior.

## Authority order

1. Runtime source and executable contracts are implementation truth.
2. The component and project SADs express intended architecture and decisions.
3. Git history and reconciled historical artifacts expose drift; they do not
   silently override current source or accepted decisions.
4. `architecture.bindings.json` binds declarations to discoverable source anchors.
5. `model_catalog.json` defines the individualized semantic viewpoints required
   to analyze each subsystem's own structure, behavior, data, state and deployment
   concerns.
6. Source-linked PlantUML views are deterministic projections, not independent claims.
7. `akdb-canon-manifest.json` pins the exact file projection exported to AKDB.

The Better Tomorrow audit rejects accepted claims without anchors, undisclosed
discovered units, shallow or generic required views, missing relationship
contracts, invalid source anchors, file drift and canon drift. It also rejects a
single fixed viewpoint profile applied to every subsystem. JSON, JUnit and SARIF
are equivalent renderings of the same audit result.
Source anchors are restricted to files visible to Git (tracked or non-ignored
new files), so local secrets, databases, caches and nested worktrees cannot
become architectural evidence.

## External AKDB contract

The permitted AKDB revision is pinned in
`tools/architecture_assurance/akdb.lock.json`. CI checks it out separately and
tests it only against a temporary source fixture and temporary data roots.
Production databases, developer databases and an installed AKDB checkout are
never mutated by integration tests.

## Reproducible operations

```bash
python -m tools.architecture_assurance generate --dry-run
python -m tools.architecture_assurance generate
python -m tools.architecture_assurance drift-evidence \
  --archive-root "<read-only historical artifact root>" --dry-run
python -m tools.architecture_assurance reconcile-drift --dry-run
python -m tools.architecture_assurance canon-manifest
python -m tools.architecture_assurance audit \
  --json reports/architecture.json \
  --junit reports/architecture.junit.xml \
  --sarif reports/architecture.sarif
python -m tools.architecture_assurance canon-export \
  --destination reports/akdb-canon
```

Repeating `generate`, `canon-manifest`, report emission or `canon-export` with
unchanged inputs produces byte-identical output and reports `unchanged`.
Text fingerprints normalize CRLF and LF before hashing, so the same Git content
has one canon on Windows and Linux. `--dry-run` computes the same action plan
but does not write.

The archive root is an optional, read-only archaeology input. Durable evidence
stores hashes, headings and repository-relative comparisons, never an operational
dependency on that external folder.
