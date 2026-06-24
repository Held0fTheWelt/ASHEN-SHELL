# ADR-0003: Git Provenance and Code Evolution Layer

## Status

Proposed

## Context

Coding agents often see only the current contents of files. This is insufficient for complex architecture work because it hides why code was introduced, which decisions shaped it, which alternatives were rejected, and how files evolved together.

ArchitecturalKnowledgeDB already stores ADRs, UML, rules, definitions, and source-area knowledge. To make code more explainable in its origin and evolution, ArchitecturalKnowledgeDB needs linked Git provenance.

However, Git history must not become a second source of normative architecture truth. ADRs, rules, and definitions remain authoritative. Git metadata provides evidence and context.

## Decision

ArchitecturalKnowledgeDB will add a Git Provenance and Code Evolution Layer.

The layer registers repositories and reads selected Git metadata through Git CLI or a library such as pygit2/libgit2. The `.git` directory is not copied into the database. ArchitecturalKnowledgeDB stores selected metadata and references back to the local repository.

The layer tracks:

- repository identity
- commit hashes
- commit timestamps
- commit messages
- changed file paths
- file change type
- optional anonymized author identity
- file history summaries
- knowledge-to-commit links
- knowledge-to-file links
- staleness and drift reports

## Consequences

ArchitecturalKnowledgeDB can answer:

- Why does this code area exist?
- Which ADR or rule is historically linked to this file?
- Which files changed together with this ADR?
- Has this UML diagram fallen behind related source changes?
- Which code areas are affected by a knowledge item?

## Authority model

Git provenance is evidence. It may suggest links, stale state, and origin trails. It must not override accepted ADRs, active rules, or canonical definitions.

Authority order:

1. hard guardrail
2. accepted ADR
3. active rule
4. canonical definition
5. current UML model
6. source-area model
7. explicit knowledge links
8. Git provenance evidence
9. inferred correlation
10. historical or superseded context

## Privacy and safety

By default, ArchitecturalKnowledgeDB must not store raw author emails. It may store hashed author emails if enabled. Remote URLs must be sanitized. Secrets and credentials must never be persisted.

Full diffs are out of scope for the MVP. Optional later diff storage may be restricted to ADR/UML/rule files and must be explicitly enabled.

## Non-goals

This ADR does not permit ArchitecturalKnowledgeDB to:

- mutate repositories
- run Git writes
- rewrite history
- create commits
- infer authoritative rules solely from Git correlations
- store `.git` internals inside the database
