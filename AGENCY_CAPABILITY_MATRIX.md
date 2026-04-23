# Runtime Agency Capability Matrix — WS-1..5 Truth Surface

## Executive Summary

The World of Shadows runtime supports **actor-driven dramatic action** through five integrated workstreams (WS-1 through WS-5). This document describes what actors **actually do** vs. what the narrator-only fallback provides, and how operators can diagnose where behavior survives or degrades.

---

## Capability Levels

| Level | Status | What Actors Do | Telemetry | Requirements |
|---|---|---|---|---|
| **Full Actor Agency** | ✅ Active | Generation succeeded, validation approved, commit applied, output rendered | All telemetry fields populated | None — baseline |
| **Fallback Active** | ⚠️ Degraded | Generation fell back to fallback model; behavior less sophisticated | `fallback_used: true` | Primary model unavailable |
| **Validation Constrained** | ⚠️ Degraded | Validation restricted/corrected behavior; original intent was modified | `validation_approved: true` but constraints applied | Continuity or legality constraints |
| **Commit Blocked** | ⚠️ Degraded | Turn was not persisted; story state unchanged | `commit_applied: false` | Transaction or validation failure |
| **Narration Only** | ⚠️ Degraded | No spoken lines or action beats; narrator-only output | `spoken_lines_rendered: 0, action_lines_rendered: 0` | Actor was silent or suppressed |
| **Generation Failed** | ❌ Non-functional | No actor output available; fallback failed | `generation_attempted: false` | Model or provider failure |

---

## Actor Behavior Surface

When **Full Actor Agency** is active:

- **Responder Selection**: `selected_responder_set` is non-empty; primary responder identified
- **Scene Function**: `selected_scene_function` is active (e.g., `escalate_conflict`, `repair_or_stabilize`)
- **Spoken Lines**: Generated with `responder_id` attribution; rendered in `spoken_lines` output field
- **Action Beats**: Generated as `action_lines`; rendered in `action_pulses` output field
- **Initiative**: `initiative_summary` recorded (primary spoke, secondary reacted, interruption occurred, etc.)
- **Continuity**: Turn advances `beat_progression_speed` and `pressure_state`
- **Output Contract**: `visible_output_bundle` includes:
  - `spoken_lines`: list of attributed dialogue
  - `action_pulses`: short action beats
  - `responder_trace`: who spoke and when
  - `continuation_state`: whether scene continues

---

## Degradation Diagnosis

### Where Behavior Survives vs. Fails

**Telemetry tracks four seams:**

1. **Generation Seam** (`generation_phase`)
   - ✅ Survives: Model called, spoke, generated responder output
   - ⚠️ Degrades: Fallback model used (lower sophistication)
   - ❌ Fails: No model available

2. **Validation Seam** (`validation_phase`)
   - ✅ Survives: Output passed actor legality, speaker legality, continuity checks
   - ⚠️ Degrades: Validation approved but constraints were applied
   - ❌ Fails: Output rejected (speaker mute, action illegal, continuity broken)

3. **Commit Seam** (`commit_phase`)
   - ✅ Survives: State effects persisted, story state advanced
   - ⚠️ Degrades: Partial commit (some effects lost)
   - ❌ Fails: Commit rolled back (transaction conflict, guard rejected)

4. **Render Seam** (`render_phase`)
   - ✅ Survives: Spoken lines, action beats, responder trace all present in output
   - ⚠️ Degrades: Some lines rendered, some suppressed
   - ❌ Fails: All actor output flattened to narration-only

---

## Operator Diagnostics API

### Check Session Agency Health

```bash
GET /api/v1/operator/diagnostics/session/<session_id>
```

Returns:
- Turn-by-turn agency level (`full_actor_agency`, `fallback_active`, `validation_constrained`, etc.)
- Degradation summary: count of fallback/failed/constrained turns
- Suggestions for operators ("Generation failed on 3 turns; check provider health")
- Documented capabilities (what each level means)

### View Turn-History Dashboard

```bash
GET /api/v1/operator/diagnostics/session/<session_id>/turn-history
```

Returns:
- Responder, scene function, validation result per turn
- Spoken lines generated vs. rendered
- Fallback status, commit status, agency level
- Diagnostic hints for each degraded turn

---

## Honesty Guarantees

**WS-5 enforces these truth rules:**

1. **Fallback turns are explicitly marked**
   - `generation_phase.generation_fallback_used: true`
   - Agency level set to `fallback_active`, not `full_actor_agency`
   - Operator hints warn about lower sophistication

2. **Validation constraints are visible**
   - If validation approved but applied corrections, `validation_constrained` is the agency level
   - Original intent vs. approved output is preserved in telemetry

3. **Commit failures prevent story progression**
   - If `commit_applied: false`, story state was not updated
   - Agency level set to `commit_blocked`
   - Operator hints warn that state may be stale

4. **Narration-only turns are labeled**
   - If `spoken_lines_rendered: 0`, output is narrator voice, not actor voice
   - Agency level set to `narration_only`
   - Operator can see responder was silent or output was suppressed

5. **No false claims of agency**
   - Dashboard never shows `full_actor_agency` if any degradation occurred
   - Operator UI surfaces the actual agency level, not the aspiration
   - Docs match actual capability, not theoretical capability

---

## Documented Limits (What's Not Implemented)

These features are **roadmap**, not active:

- ❌ **Autonomous NPC-to-NPC exchange** without player action (bounded under `allow_scene_progress_without_player_action`)
- ❌ **Free-running scene motion** past `max_scene_pulses_per_response` limit
- ❌ **Player re-entry into moving scene** (each turn resets scene context)
- ❌ **Beat state persistence** independent of continuity impacts
- ❌ **Initiative carry-forward** across multiple turns

These are **in the Story Runtime Experience partial foundation** and will be added in future waves.

---

## How Operators Diagnose

**If players report "actor is too quiet":**
1. Check `/operator/diagnostics/session/<id>/turn-history`
2. Look for `spoken_lines_rendered: 0` rows
3. Check `validation_constrained` or `narration_only` levels
4. Read diagnostic hints: "No spoken lines in final output; responder may have been silent"
5. **Action:** Check continuity constraints, increase `npc_initiative`, or review scene function

**If players report "stories feel like fallback":**
1. Check `fallback_active` turn count in agency statistics
2. If >20%, model provider may be unavailable
3. **Action:** Check provider health in AI runtime governance

**If actors never speak in live mode:**
1. Check `agency_level: full_actor_agency` count
2. If all turns are `narration_only`, check `dialogue_priority` setting
3. Check `inter_npc_exchange_intensity` (may be `off`)
4. **Action:** Increase dialogue priority or exchange intensity in Story Runtime Experience settings

---

## Integration Points

- **Telemetry Source:** `ai_stack/actor_survival_telemetry.py`
- **Package Integration:** `ai_stack/langgraph_runtime_package_output.py`
- **Operator Service:** `backend/app/services/operator_turn_history_service.py`
- **API Routes:** `backend/app/api/v1/operator_diagnostics_routes.py`
- **Story Runtime Experience:** Tied to `experience_mode`, `delivery_profile`, and character behavior settings
