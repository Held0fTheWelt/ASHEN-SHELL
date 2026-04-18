# Usabilify hub

`usabilify` is the UI/UX and usability governance suite for World of Shadows.
It inventories views and reusable UI surfaces, attaches relevant UI contracts and
design guidance, and evaluates the repository for friction, accessibility, and
consistency risks.

## What it does

- scans HTML/Jinja template trees for views, blocks, and interactive elements
- links UI surfaces to relevant contracts and technical guidance from `docs/`
- consumes `templatify` reports when present to inherit area/block context
- evaluates view and area usability with stable heuristics
- emits machine-readable JSON, markdown reports, and a Mermaid map of UI surfaces

## Main commands

```bash
usabilify inspect
usabilify evaluate
usabilify full
```

## Output model

- `reports/usabilify_inventory.json` — machine-readable UI inventory
- `reports/usabilify_evaluation.json` — findings, scores, and contract links
- `reports/usabilify_view_map.mmd` — Mermaid graph for areas and views
- `state/USABILITY_STATE.md` — restartable state summary

## Evaluation themes

The suite scores repository surfaces against research-backed usability and
accessibility themes such as feedback visibility, consistency, error prevention,
recognition over recall, and accessible interaction affordances. These are
expressed as stable suite rules rather than ad-hoc opinions.
