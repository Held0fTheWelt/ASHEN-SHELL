# Usability State

- Status: active
- Last edited: 2026-04-17
- Scope: repository UI surfaces, UI contracts, and templatify alignment
- Latest machine inventory: ../reports/usabilify_inventory.json
- Latest machine evaluation: ../reports/usabilify_evaluation.json
- Latest human report: ../reports/usabilify_evaluation_report.md

## Current focus

- inventory current UI views and template inheritance surfaces
- attach UI/UX and accessibility-relevant contracts from docs
- expose area-specific findings and improvement suggestions
- consume templatify block/area information where available

## Latest repository snapshot

- frontend average score: `93.2`
- administration-tool average score: `96.7`
- administration-manage average score: `96.6`
- backend info average score: `94.4`
- writers-room average score: `93.3`

## Current visible risks

- auth/player-facing frontend forms commonly lack visible status or error signaling surfaces in template markup
- some partial/admin helper views rely on inherited structure and should still be reviewed for explicit headings or title overrides
- backend info partial `info_sections.html` looks like a reusable fragment and scores lower because it intentionally lacks standalone heading/title affordances
- templatify context is optional; when present, its unmapped base blocks should be treated as open UX integration seams
