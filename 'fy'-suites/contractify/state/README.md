# Contractify `state/`

This folder is the tracked restart and review layer for Contractify governance work.

Use it for **human-visible state tracking** of bounded Contractify waves, while machine-generated audit payloads continue to live under `../reports/`.

## What is tracked here

- **Pass state documents** — bounded wave records, decisions, evidence links, and unresolved areas.
- **State index** — one visible entry point for the currently relevant Contractify passes.
- **Pre/post artifact paths** — optional tracked anchor directories for future pre/post evidence snapshots when a pass needs them.

## Canonical visibility model

1. `contract_governance_input.md` — backlog and follow-up items (`CG-*`).
2. `state/ATTACHMENT_PASS_INDEX.md` — visible index of major Contractify state passes.
3. Pass state files under `state/*.md` — tracked narrative of what was actually done.
4. `reports/*.md` and `investigations/**` — bounded generated summaries and maps.
5. `reports/contract_audit.json` — machine-readable current audit output for the local run.
6. `reports/committed/*.hermetic-fixture.json` — committed fixture-level evidence for stable report shapes.

## Current dedicated state surfaces

- Runtime / MVP spine: `RUNTIME_MVP_SPINE_ATTACHMENT.md`
- ADR governance / investigation: `ADR_GOVERNANCE_INVESTIGATION.md`
