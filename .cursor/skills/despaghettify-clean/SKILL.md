---
name: despaghettify-clean
description: Routes agents to the Despaghettify workstream artefact wipe — all pre/post session files under state/artifacts/workstreams, optional ephemeral cleanup. Triggers on spaghetti clean, wipe despaghettify artefacts, clear workstream pre post, hub clean before reset.
---

# Despaghettify clean (router)

**Do not duplicate danger notices or PowerShell steps here.** The **only** specification for irreversibility, slug list, wipe/recreate layout, and optional ephemeral cleanup is:

`despaghettify/spaghetti-clean-task.md`

Read that file **in full** and execute it. This task **deletes governance evidence** under `artifacts/workstreams/**`; do not run if those files are the sole copy of required closure proof.

Binding index: `despaghettify/state/WORKSTREAM_INDEX.md`.
