# Runtime Profile vs Content Module — Contract

**Status:** Active contract — 2026-04-26

---

## Definitions

### Content Module
A **content module** is canonical story truth. It lives under `content/modules/<module_id>/` and contains:
- Characters (who, with what properties)
- Relationships (formal axes and dynamics)
- Scenes (phase structure, exit conditions)
- Transitions, triggers, endings (story logic)
- Direction (LLM guidance, voice, scene constraints)

Content modules are **not runtime modules**. They are loaded by the engine at session start.
Content module data is the authoritative source for story facts.

### Runtime Profile
A **runtime profile** is session configuration. It provides:
- Session bootstrap structure (roles, rooms)
- Join policy and max_humans
- A reference to which content module to load

A runtime profile contains **NO story truth**: no beats, no actions, no props, no scene content.
Story truth is always sourced from the canonical content module at runtime.

---

## Current Instances

| Artifact | Type | Story Truth |
|---------|------|-------------|
| `content/modules/god_of_carnage/` | Content module | YES (canonical) |
| `god_of_carnage_solo` (in story_runtime_core) | Runtime profile | NONE |

---

## Separation Rules

1. A runtime profile MUST NOT contain beats, actions, or props.
2. A runtime profile MUST reference a valid canonical content module by module_id.
3. A content module MUST have `module_id` matching its directory name.
4. `god_of_carnage_solo` is a runtime profile; its `module_id` is `god_of_carnage_solo`, not `god_of_carnage`.
5. The canonical module's `module_id` is `god_of_carnage`.
6. Session start with `runtime_profile_id="god_of_carnage_solo"` loads `god_of_carnage` canonical module.

---

## Enforcement Contract

- The world-engine/play-service validates that the selected runtime profile exists.
- The play-service loads the content module referenced by the runtime profile.
- If the content module is absent or malformed, the session is rejected (not degraded silently).
- `selected_player_role` must be a valid human-playable role (annette or alain for GoC).
- Invalid role selection is rejected; the committed state is not created.

---

## ADR References

- ADR-mvp1-002: Runtime profile resolver
- ADR-mvp1-005: Canonical content authority
- ADR-0025: Canonical authored content model
