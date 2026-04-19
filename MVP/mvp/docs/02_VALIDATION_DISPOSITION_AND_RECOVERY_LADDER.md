# 02 — Validation Disposition and Recovery Ladder

## Required dispositions

- `ACCEPT_STRONG`
- `ACCEPT_WEAK`
- `REPAIRABLE_QUALITY_FAIL`
- `REPAIRABLE_LOGIC_FAIL`
- `PROVIDER_RETRY`
- `SAME_SCENE_REPLAN`
- `LOW_INTENSITY_CONTINUATION`
- `CONSTRAINT_RESPECTING_REDIRECT`
- `SYSTEM_DEGRADED_SAFE`
- `HARD_RULE_BLOCK`

## Recovery ladder

1. Retry provider if the provider failed but logic is still sound.
2. Replan inside the same scene if response quality is insufficient.
3. Redirect within constraints if the requested path is illegal but an adjacent lawful continuation exists.
4. Continue at low intensity if the story must move but high-complexity generation is unsafe.
5. Enter degraded safe mode if index, provider, or retrieval freshness is insufficient.
6. Hard block only when rules, safety, canon, or partition boundaries would otherwise be broken.

Every failure and recovery step must preserve failed node, reason, disposition, retry count, degraded state, and final visible outcome class.
