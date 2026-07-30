# Better Tomorrow AKDB authority

Better Tomorrow owns its architecture assertions, source bindings, depth gate and
test set. ArchitecturalKnowledgeDB is a pinned, external tool dependency. It is
never a writable source subtree of this repository and is never an authority for
runtime behavior.

## Authority order

1. Runtime source and executable contracts are implementation truth.
2. The component and project SADs express intended architecture and decisions.
3. `architecture.bindings.json` binds declarations to discoverable source anchors.
4. Source-linked PlantUML views are derived projections, not independent claims.
5. `akdb-canon-manifest.json` pins the exact file projection exported to AKDB.

The Better Tomorrow audit rejects accepted claims without anchors, undisclosed
discovered units, shallow required views, file drift and canon drift. JSON, JUnit
and SARIF are equivalent renderings of the same audit result.

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
