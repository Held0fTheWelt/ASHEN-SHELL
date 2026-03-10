# World of Shadows — Prompt List

Cursor/AI prompts used for planning and executing the server foundation. Use in order when doing a staged rebuild.

| # | File | Purpose | Relates to |
|---|------|---------|------------|
| 00 | [00_start_prompt_cursor.txt](00_start_prompt_cursor.txt) | Planning only: audit, architecture, create /mvps milestone plan. No full rebuild. | MVP 01–10 (planning) |
| 01 | [01_mvp_execution_template.txt](01_mvp_execution_template.txt) | Generic rules for executing any single MVP from /mvps. | Any MVP |
| 02 | [02_mvp_01_execute.txt](02_mvp_01_execute.txt) | Execute MVP_01: audit and extraction plan (analysis only). | MVP_01 |
| 03 | [03_mvp_02_execute.txt](03_mvp_02_execute.txt) | Execute MVP_02: target architecture. | MVP_02 |
| 04 | [04_mvp_03_execute.txt](04_mvp_03_execute.txt) | Execute MVP_03: project bootstrap. | MVP_03 |
| 05 | [05_mvp_04_execute.txt](05_mvp_04_execute.txt) | Execute MVP_04: database and user model. | MVP_04 |
| 06 | [06_mvp_05_execute.txt](06_mvp_05_execute.txt) | Execute MVP_05: web blueprint and templates. | MVP_05 |
| 07 | [07_mvp_06_execute.txt](07_mvp_06_execute.txt) | Execute MVP_06: API v1 and JWT auth. | MVP_06 |
| 08 | [08_mvp_07_execute.txt](08_mvp_07_execute.txt) | Execute MVP_07: security baseline. | MVP_07 |
| 09 | [09_mvp_08_execute.txt](09_mvp_08_execute.txt) | Execute MVP_08: cleanup and domain purge. | MVP_08 |
| 10 | [10_mvp_09_execute.txt](10_mvp_09_execute.txt) | Execute MVP_09: smoke tests and runbook. | MVP_09 |
| 11 | [11_mvp_10_execute.txt](11_mvp_10_execute.txt) | Execute MVP_10: handover summary. | MVP_10 |
| — | [strict_mode_addendum.txt](strict_mode_addendum.txt) | Global rules: no domain naming, no legacy clutter, replace over adapt, honest MVP status. | All |

---

## Usage

1. **Planning:** Run `00_start_prompt_cursor.txt` once to produce the /mvps milestone set.
2. **Execution:** For each MVP, use the corresponding `0X_mvp_XX_execute.txt` (or the template `01_mvp_execution_template.txt` with the MVP file name).
3. **Strict mode:** Apply `strict_mode_addendum.txt` throughout (no movie/blog naming, clean base, accurate status).
