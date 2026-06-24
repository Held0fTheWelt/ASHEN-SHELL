# frontend — Software Architecture (arc42)

**Component:** frontend · **Folder:** `frontend/` · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Player-facing web UI: home, auth, dashboard, community, play routes, block renderer, WebSocket bootstrap
via backend (not direct world-engine auth for primary path).

The frontend never becomes the enforcement layer for narrative authority. It renders what backend and
play bootstrap return, surfaces block streams from MVP5 rendering contracts, and keeps operator/debug
surfaces out of player routes unless explicitly scoped.

## 2. Constraints

Cannot be sole enforcement layer for backend/runtime rules ([service-boundaries](../../../technical/architecture/service-boundaries.md)).

## 3. Context & Scope

In scope: templates, static JS, play shell. Out of scope: admin, narrative commit.

## 4. Solution Strategy

Call backend APIs; use browser-reachable play URL from backend bootstrap for runtime connection.
Block rendering modules stay isolated from server route code so MVP5 presentation changes do not
require backend deploys. Play shells treat websocket bootstrap failures as user-visible errors with
retry guidance rather than silent fallback to stale state.

## 5. Building Block View

| Block | Path |
| --- | --- |
| App routes | `frontend/app/` |
| Block renderer | `frontend/static/`, `frontend/tests/test_block_renderer.js` |
| Player backend bridge | `frontend/app/player_backend.py` |

## 6. Runtime View

A1 free-input path documented in [`a1_free_input_primary_runtime_path.md`](../../../technical/runtime/a1_free_input_primary_runtime_path.md).

## 7. Deployment View

Separate process from backend; configured `FRONTEND_URL` for redirects.

## 8. Crosscutting Concepts

MVP5 modular block rendering ([ADR MVP5-001](../../../archive/adr-retired-2026/MVP_Live_Runtime_Completion/adr-mvp5-001-modular-block-rendering-architecture.md)).

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Player narrative shell contract | Accepted | ADR-0034 |
| D2 | Typewriter cinematic direction | Accepted | ADR-0046 |
| D3 | Modular block rendering | Accepted | MVP5-001 |

### D1: Player-Facing Narrative Shell Contract (MVP5)

**Status:** Accepted
**Origin:** ADR-0034 (retired 2026-06-23)

**Context.** MVP4 establishes truthful runtime, diagnostics, and canonical HTTP bundles for the play path. MVP5 adds modular block rendering and typewriter delivery in the player shell (`frontend/static/play_shell.js`, `play_blocks_orchestrator.js`, `play_typewriter_engine.js`, `play_block_renderer.js`).

Product feedback indicates a gap between **theatrical narrative goals** (narrator as literate scene-setter and subtle cueing; NPC speech carrying the play) and **current runtime output pacing** (narrator too “complete” in few lines, UI not yet supporting script-like reading).

Separately, ADR-0033 now requires **non-PII player-input correlation** on Backend Langfuse spans for canonical turns. This ADR covers **what the shell must prove** once narrative semantics stabilize.

**Decision.** 1. **Scope boundary:** ADR-0033 governs commit truth, Langfuse evidence gates, and player-input **hash correlation** on `backend.turn.execute`. **This ADR** governs the **player-visible shell contract**: block stream semantics, transcript vs. live-append rules, and acceptance tests that fail when the shell misrepresents committed runtime truth.

2. **Transcript vs. live delivery:** After each successful turn, the shell must not give the appearance that earlier committed story vanished. The HTTP contract already exposes `story_window.entries` and `visible_scene_output.blocks`; MVP5 orchestration must align with the **cumulative** block policy on the Backend bundle (see `backend/app/api/v1/game_routes.py` cumulative `scene_blocks` when entries carry `scene_blocks`).

3. **Narrator role (product, not only UI):** The narrator is a **literary scene presenter**: atmosphere, perception, and **light guidance** (what is noticeable, what the room offers). The shell must **not** prescribe crude player emotions (“you feel afraid”) or substitute for player agency. Narration density, “show vs tell”, and lane separation (narrator vs NPC vs stage direction) remain **content and graph policy** concerns; the shell **renders** committed lanes faithfully when the engine emits typed blocks and text. Specific literary rules live in narrative governance / prompt packs.

4. **Dramaturgical block types:** The contract assumes distinct block kinds (e.g. narrator, actor line, stage direction) when the API provides `block_type` / structure. The shell must preserve typographic and semantic distinction **when the bundle supplies it** — no collapsing lanes into an undifferentiated blob.

4a. **Narrator/actor speech composition boundary:** Visible lane separation is not the same as authorship separation. When a line is authored as narrated direct speech, the runtime SHALL keep it as one visible `narrator` card with `composition_kind="narrated_actor_speech"` and one or more `embedded_speech_spans`. Consumers must treat those spans as actor speech evidence for responder detection, voice validation, and authority diagnostics. They must not split the visible prose into a separate narrator card plus a separate actor card unless the source content is structurally separate. They must not reassign embedded speech to the human player because the card's visible `block_type` is `narrator`.

4b. **Extended player-facing block kinds (shell must render faithfully):**
   - **`player_input_outcome`:** Second card in the **always-two** human-bound player pair: echo (`player_input`) then diegetic shell line (`player_input_outcome`). The semantic block carries `speaker_label` / `actor_id` for attribution and cleaned `text` for the utterance (e.g. label `Annette`, text `Hallo Veronique`), not a localized `says`/`sagt` template and not a hardcoded greeting rewrite. Same cumulative rules as other blocks; **distinct** CSS lane from `player_input` (darker green bar / panel — presentation only).
   - **`narration_beat` (optional on `narrator` blocks):** Typewriter profile key and optional CSS accent. **Must reflect authored or operational metadata on that block** — see §**narration_beat semantics**. Unknown values fall back to the typewriter `default` profile; consumers must not treat unknown keys as errors.
   - **`visual_emphasis` (optional):** Separate from `narration_beat` — e.g. `dramatic_moment` drives card chrome via `scene-block--visual-emphasis-*`, not the legacy opening index hack.

4c. **NPC lane cardinality (engine projection):** For God of Carnage live projection, **distinct NPC speakers must appear as separate `actor_line` blocks** when the model merged them into one visible string. The World-Engine normalizes before finalize (see Implementation Status). **One jammed string → N blocks** (N emerges from content); **redundant `actor_action` tail already present in a prior `actor_line` → dropped**. This is **structural** truthfulness of the transcript, not a substitute for model-side dramaturgy. This rule does **not** override §4a: embedded direct speech inside a prose sentence is not a jammed speaker-prefix row and should remain a single narrated-speech card with structured spans.

5. **Single-active typewriter:** Exactly **one** block uses the typewriter at a time. On HTTP `loadTurn`, the shell delivers blocks sequentially according to **`typewriter_slice_start_index`** (see §7). On streamed `appendNarratorBlock`, any in-progress queue is **finalized** (`revealAll`) before starting delivery for the new block (each appended stream chunk is one block — it animates as the active slice). `TypewriterEngine` registers **one** `VirtualClock` tick handler for its lifetime (no duplicate `onTick` listeners per block).

6. **No debug surface in player UI:** Diagnostic or technical payloads must not appear as ordinary narrative blocks in the player shell. Debug belongs in operator tools, Langfuse, or explicit diagnostics endpoints — not mixed into the theatrical transcript.

7. **Cumulative blocks + typewriter slice (HTTP):** `visible_scene_output.blocks` remains the **full committed transcript** (cumulative across `story_window.entries` when each entry carries `scene_blocks`). To animate **only the newly committed blocks** for this response — while showing earlier blocks as stable transcript — the Backend adds **`typewriter_slice_start_index`**: an integer index into `blocks` such that indices `< index` render as **full text immediately**, and indices `>= index` through `len(blocks)-1` are delivered **one after another** via the typewriter (still only one block animating at a time). **Legacy clients:** if the field is absent, the shell may fall back to animating **only the last** block (`blocks.length - 1`), preserving pre-2026-05 behavior.

8. **Streamed narrator chunks:** Each WebSocket/appended narrator block is treated as **one** new block for presentation: finalize any in-flight typewriter (`revealAll`), then run typewriter for **that** block only (decision **5**). HTTP slice indices do not apply to incremental stream delivery.

9. **Progressive DOM mount for HTTP slice cards:** Applies to **every** turn where `visible_scene_output.blocks` includes **multiple** animated slice entries (same rule as opening multi-beat flows — not opening-specific). **`this.blocks` keeps the full committed list** while **DOM insertion** for slice cards is **one card at a time**: first slice block mounts on `loadTurn`; each subsequent slice block mounts **immediately before** its typewriter run (`render` → empty displayed cell → `startDelivery`) so **empty placeholder cards are not shown ahead of animation**. **`revealAll`** and **`setAccessibilityMode(true)`** must **`render` any not-yet-mounted blocks** and fill **`blockDisplayTextForShell`** so “show all” and reduced motion expose the **complete** transcript. **Diagnostics** blocks render when encountered (not queued in `sliceQueue`). **DOM ordering:** v1 appends in API order as deliveries advance; **anchor placement** (`render before/after`) is reserved for a future refinement if diagnostics or stable rows must interleave visually between deferred slice cards.

10. **Direct narrator-tail cleanup (presentation-only):** The player-facing card builder may remove a **directly adjacent** story-lane NPC card when a preceding narrator card already fully subsumes that NPC visible text under the redundancy guardrails; this affects only the rendered player-card projection (`visible_scene_output.blocks`) and does **not** modify committed semantic runtime `scene_blocks`.

11. **Runtime bootstrap is shell-owned, not narrative-owned:** On initial page bootstrap only, the shell may prepend a `system_boot` block before `visible_scene_output.blocks` and set the displayed payload's `typewriter_slice_start_index` to `0` so the boot and then the narrative slice type sequentially. The required command line is `C:\WOS> START DIRECTOR_TICK`; subsequent warmup lines report system readiness for manager/dispatcher/capability/content/session surfaces from the payload when present and fall back to explicit `STANDBY` / `PENDING` / `WAITING` states when not present. This boot block must not be persisted as a story-window entry and must not be injected for ordinary turn updates unless a caller explicitly requests a bootstrap mode.

### narration_beat semantics (normative)

`scene_blocks[].narration_beat` is **presentation and typewriter metadata** on a **specific block**. It is **not** a substitute for canonical mandatory-beat identity, literary opening structure, or Langfuse opening-shape vocabulary.

| Source | Valid `narration_beat` values | Consumer behaviour |
|--------|------------------------------|-------------------|
| **Canonical narrator path** (`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`) | Mandatory beat **id** from YAML (e.g. `park_edge_establishing_image`, `stick_strikes_face`) | Typewriter `default` profile unless id matches a named profile; **no** `scene-block--narrator-role-anchor` unless value is literally `role_anchor` |
| **Runtime bootstrap** (`play_runtime_bootstrap.js`) | `boot` | `boot` typewriter profile; operational UI only |
| **Explicit dramaturgic annotation** (rare; author/model) | `role_anchor`, `tension`, `dialogue`, `action`, `reflection` | Matching profile in `TYPEWRITER_BEAT_PROFILES`; `role_anchor` adds `scene-block--narrator-role-anchor` (sweep CSS — must not clip multi-line text; see ADR-0046 follow-up) |
| **Dramatic emphasis** | Use `visual_emphasis.kind` (e.g. `dramatic_moment`), **not** `narration_beat` | `scene-block--visual-emphasis-dramatic-moment` |

**Literary opening slots** (`premise`, `scene_setup`, `role_anchor` as *story structure*) apply to **`gm_narration` text**, not to shell block indices:

- `ai_stack/story_runtime/god_of_carnage/god_of_carnage_opening_transition.py` — validates/reorders the first three narrator **strings** before projection.
- `ai_stack/story_runtime/opening_shape_normalizer.py` — normalizes model `narration_summary` into beat strings.
- `_compute_opening_shape_subgates` in `world-engine/app/story_runtime/manager/` — Langfuse evidence; checks that indices 0–2 are `narrator` **block types** (subgate names `narrator_intro_present`, `role_anchor_present`, `scene_setup_present` are **historical labels**, not `narration_beat` values to write onto blocks).

**Do not conflate** “opening has three narrator cards” with “card 0 = premise, card 1 = scene_setup, card 2 = role_anchor”. With narrator-path openings there are **many** narrator blocks; the third visible card is ordinary canonical content.

### Removed patterns (do not restore)

| Removed | Was | Why removed |
|---------|-----|-------------|
| `_annotate_goc_opening_narration_beats` | Forced `premise` / `scene_setup` / `role_anchor` onto `blocks[0..2].narration_beat` after projection | Overwrote canonical beat ids; wrongly triggered `scene-block--narrator-role-anchor` + `overflow: hidden` on the third card; broke multi-line typewriter layout |
| Index-based opening UI tagging | Any post-projection pass that maps block index → literary slot name | Superseded by content-authored `narration_beat` + `visual_emphasis`; narrator-path uses mandatory beat ids |

**Guard test:** `world-engine/tests/test_trace_middleware.py::test_opening_scene_blocks_do_not_force_legacy_ui_narration_beat_tags` — first three projected opening blocks must not carry `premise`, `scene_setup`, or `role_anchor` as `narration_beat`.

**Internal label stripping:** Model leaks such as `role_anchor:` in **text** are removed by `visible_narrative_contract` — that is unrelated to the `narration_beat` field.

**Consequences.** ### Positive

- Clear split: **0033** = truth + observability, **0034** = presentation + shell acceptance.
- E2E and frontend unit tests can target a stable shell contract without overloading runtime ADRs.

### Negative / risks

- Without engine-side block typing and stable `scene_blocks` IDs, the shell cannot deliver theater-grade layout; UI work alone will not satisfy this ADR.
- **Split heuristics** build speaker-prefix alternation from the **runtime NPC roster** (`runtime_projection.npc_actor_ids`, canonical ids, alias expansion) plus display tokens; a static GoC display-name tuple remains a **fallback** only for colon-stutter dedupe when block context is missing. Novel modules/languages need their own roster/vocab, not silent extension of GoC literals in the engine core.
- **Prune rule** uses substring containment on normalized text; very short actions are kept; long duplicated stage tails are removed. False positives are unlikely but possible if an unrelated short clause repeats.
- **Embedded speech readers** must read both old `actor_line` blocks and new
  `narrator` + `embedded_speech_spans` blocks when checking whether an NPC
  visibly responded. Treating only `actor_line` as speech can create false
  "narrator-only" diagnostics and can wrongly make a later forced response look
  like it belongs to the player.

**Implementation status.** **Last reviewed:** 2026-05-20. **Core shell contract implemented; some test tiers pending.**

**Implemented:**
- `frontend/static/play_block_display_text.js`: shared `blockDisplayTextForShell(block)` — `player_display_text != null ? player_display_text : text` (same rule for renderer, orchestrator fill, and typewriter duration/DOM).
- `frontend/static/play_blocks_orchestrator.js`: HTTP `loadTurn()` builds **`sliceQueue`** (indices `>= typewriter_slice_start_index`, excluding diagnostics); indices below the slice render **full text immediately**; **`this.blocks` always holds every API block** for reveal/skip/accessibility even when slice cards are not yet mounted. **Progressive DOM mount:** only the **first** slice card is **`renderer.render`** on load; further slice cards mount **when their delivery starts** (`_mountBlockIfNeeded` → empty cell → `startDelivery`). The slice is delivered **sequentially** via `TypewriterEngine.startDelivery` + **`setOnDeliveryComplete`**. **`skipCurrentBlock`** completes the active block (full text) then continues the slice; **`revealAll`** mounts any deferred slice rows, fills **full** shell text for pending slice blocks, clears the queue, and detaches the completion hook. **`setAccessibilityMode(true)`** mounts all blocks in `this.blocks` and fills full transcript. **`appendNarratorBlock`** clears slice state and keeps **one block per stream chunk** (unchanged streaming semantics).
- `frontend/static/play_typewriter_engine.js`: single active block; single `VirtualClock` listener; **`setOnDeliveryComplete(blockId)`** fires after natural completion, skip, or empty display immediate resolve; display text uses `blockDisplayTextForShell`.
- `frontend/static/play_block_renderer.js`: block rendering with `block_type` semantic distinction; optional `narration_beat` on narrator blocks for typewriter pacing and **opt-in** presentation accents (see §**narration_beat semantics** — not index-forced opening tags).
- `frontend/static/style.css`: distinct lane chrome per `block_type` (including `player_input_outcome`); `scene-block--narrator-role-anchor` only when a block **explicitly** carries `narration_beat: "role_anchor"`.
- `frontend/static/play_shell.js`: orchestrates renderer + typewriter + controls.
- `frontend/static/play_runtime_bootstrap.js`: shell-owned DOS-style startup bootstrap. It can prepend a player-visible `system_boot` block with `narration_beat: "boot"` before the first Director-owned story slice, deriving readiness lines from the bootstrap payload (`runtime_session_ready`, `can_execute`, `session_loop`, `shell_state_view`, `visible_scene_output`, and optional scene/capability plan fields). This block is a runtime UI handoff, not committed narrative content.
- Legacy fallback: if `typewriter_slice_start_index` absent, last block is animated (pre-2026-05 behavior preserved).
- `appendNarratorBlock()` finalizes in-flight typewriter before starting delivery for streamed blocks.
- No debug surface in player UI (operator diagnostics stay in Langfuse / explicit diagnostic endpoints).
- Jest tests: `frontend/tests/test_blocks_orchestrator.js`, `frontend/tests/test_typewriter_engine.js`, `frontend/tests/test_block_renderer.js`, `frontend/tests/test_runtime_bootstrap.js`.

**World-Engine — committed visible block shaping (God of Carnage live path):**
- **Invariant (no fixed card count):** The number of NPC transcript cards per turn is **not** a product constant; it emerges from structured rows, split/merge policy, validation, and prune rules. Tests assert **invariants** (no megablock jam, no colon stutter, no redundant action lane), not a fixed DOM node count.
- **One NPC, one `actor_line` block:** If the model jams multiple speakers into a single `actor_line` string (e.g. `Veronique: … Alain: …`), `_expand_multi_speaker_actor_lines` in `world-engine/app/story_runtime/manager/` splits it into **separate** `actor_line` blocks (per `actor_id` / `speaker_label`). Speaker-prefix detection is **roster-driven** from `session.runtime_projection` via `ai_stack/story_runtime/npc_agency/god_of_carnage_npc_transcript_projection.py` (not a hardcoded name union in the engine). Consecutive spans for the **same** speaker may be merged depending on governed `story_runtime_experience` flags (`goc_transcript_merge_consecutive_same_actor`, optional `goc_transcript_split_speech_stage_same_actor` after dialogue-then-stage boundaries).
- **No duplicate lane rows:** `_prune_actor_actions_subsumed_by_prior_actor_lines` drops an `actor_action` when its visible text (length-gated, normalized) is already contained in an **earlier** `actor_line` in the same turn (typical `spoken_lines` + `action_lines` echo).
- **Finalize hook:** Split + prune run inside `_finalize_visible_blocks_with_goc_actor_split` immediately before / after `ai_stack.contracts.visible_narrative_contract.finalize_visible_scene_blocks` (both the pre-built `scene_blocks` path and the bundle-built path). Effective experience flags are passed from governed `story_runtime_experience` (see `ai_stack/story_runtime/story_runtime_experience.py`).
- **Regie lane mapping (policy):** When `goc_map_action_lines_to_actor_line_lane` is true, structured `action_lines` rows project as `actor_line` blocks (same shell lane as speech) so staging does not force a second colour lane; default remains `actor_action` for distinct stage-direction chrome.
- **Narrated actor speech (single-card embedded dialogue):** A visible `narrator` block may carry `composition_kind: "narrated_actor_speech"` and `embedded_speech_spans[]`. This is the required shape when prose and direct NPC speech are inseparable in natural narration, e.g. a sentence that frames an actor's gesture and contains the spoken words. The visible card stays one narrator/prose block; speaker authority is preserved in the embedded span (`actor_id`, `speaker_label`, `speech_text`, `speech_act`, canonical beat IDs). The narrator may frame or follow the speech, but must not summarize a scripted `npc_speak` beat instead of carrying the direct speech text.
- **Structured row diagnostics:** If a single `spoken_lines` dict row’s text contains multiple roster speaker prefixes, `ai_stack.story_runtime.turn.god_of_carnage_turn_seams.run_visible_render` adds marker `goc_multi_speaker_merged_into_single_spoken_line_row` (soft signal for operators / quality gates; projection still splits at commit when the jam appears in projected `actor_line` text).
- **PLAYER-SHELL-NARRATIVE-CARD-01:** HTTP `visible_scene_output.blocks` are **player-facing narrative cards** built by `ai_stack/story_runtime/player_narrative_cards.build_player_facing_narrative_cards` from semantic `scene_blocks` (semantic `block_type` preserved; `card_style` / `visible_lane` / `player_display_text` added). Adjacent same-actor `actor_action` folds into the prior `actor_line` card; subsumed duplicates are dropped from the shell list; diagnostics live under `player_shell_narrative_card_diagnostics`.
- **Human-bound player transcript (GoC live):** `_player_input_scene_blocks_for_story_window` **always** emits **two** blocks when `human_actor_id` is set: `player_input` (verbatim typing) then `player_input_outcome` (diegetic attributed line). Direct speech and unresolved greeting-like inputs use neutral script attribution, not localized phrase templates such as `Annette sagt: ...`; semantic greeting realization belongs to the governed runtime/model path, not to a hardcoded shell rewrite. Scene blocks carry attribution in `speaker_label` / `actor_id`, so their `text` may be the cleaned utterance without a duplicate `Annette:` prefix. The shell renders each as its own card (see §4b).
- **Thin-path movement fold (ADR-0062):** when the Director thin path realizes via `narrator.*` and the turn has no NPC lines, narrator realization text is folded into `player_input_outcome` and redundant `narrator` scene blocks are suppressed for that turn (`manager.py` thin-path fold).
- **Opening literary slots vs shell `narration_beat`:** See §**narration_beat semantics** and **Removed patterns**. `_annotate_goc_opening_narration_beats` was **removed** (2026-05); do not reintroduce index-based `premise` / `scene_setup` / `role_anchor` tagging on `scene_blocks`.
- Pytests: `world-engine/tests/test_goc_multi_speaker_actor_line_split.py`, `world-engine/tests/test_goc_player_input_greeting_imperative.py`, `ai_stack/tests/test_god_of_carnage_npc_transcript_projection.py`, `ai_stack/tests/test_wave3_multi_actor_vitality.py` (jammed-row marker).

**Not yet fully implemented:**
- Live Langfuse gate (`test_langfuse_live_c640_gate.py`) requires opt-in `RUN_LANGFUSE_LIVE=1` — not run in standard CI.
- Backend cumulative `scene_blocks` / `typewriter_slice_start_index` propagation from turn responses: partially implemented (verified in `tests/test_mvp4_contract_playability.py`).
- **Staging correctness** (e.g. which character may “welcome” guests) remains **model / prompt / content** responsibility; this ADR does not hard-code dialogue rewrites beyond structural de-duplication and lane split.

**Evidence.** `docs/architecture/components/frontend/architecture.md#d1-player-narrative-shell-contract` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Typewriter Cinematic Direction

**Status:** Accepted
**Origin:** ADR-0046 (retired 2026-06-23)

**Context.** **As of 2026-05-19** the player-shell typewriter is **no longer** a flat `textContent.substring` stream. `play_typewriter_engine.js` reveals per-character spans, drives a live `play-cursor`, and resolves tempo from `TYPEWRITER_BEAT_PROFILES` keyed by each block's `narration_beat` (unknown values → `default`). `play_blocks_orchestrator.js` applies profile-based gaps between slices; `play_cinematic.js` wires composing pulse, player-echo fade, and typing/stream surface classes.

**Historical problem (pre-implementation):** constant 44 cps, unused beat metadata, dead legacy `.block-typewriter::after` cursor CSS, and hard-cut slice transitions.

**Historical opening bug (removed 2026-05):** `_annotate_goc_opening_narration_beats` forced `premise` / `scene_setup` / `role_anchor` onto `blocks[0..2].narration_beat`, which wrongly applied `scene-block--narrator-role-anchor` (`overflow: hidden`) to the third opening card and broke multi-line layout. That pass is **deleted**; guard: `world-engine/tests/test_trace_middleware.py::test_opening_scene_blocks_do_not_force_legacy_ui_narration_beat_tags`. Full semantics: ADR-0034 §**narration_beat semantics**.

**Current opening behaviour:** GoC **narrator-path** sets `narration_beat` to each block's **canonical mandatory beat id** (`ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`). Dramatic emphasis uses `visual_emphasis` (e.g. `dramatic_moment`), not literary slot names on the field. The `role_anchor` typewriter/CSS sweep runs **only** when a block explicitly has `narration_beat: "role_anchor"`.

**Remaining gaps vs this ADR:** beat-change timing is profile-driven, not a fixed 250 ms decompression; matrix “coupling” is a light CSS glow, often inert on `/play` where `#matrix-layer` is absent; dedicated Jest tests for render-shape / beat-profile dispatch called out below are not all present yet.

The product goal remains: the typewriter should feel **live-directed** — punctuation breaths, beat-coded tempo, cursor presence, and composing/echo signals — not a uniform machine stream.

**Decision.** The typewriter pipeline (`play_typewriter_engine.js`, `play_blocks_orchestrator.js`, `play_block_renderer.js`, `play_shell.js`, `style.css`) will be modified so that each of the following bullets is true and verifiable:

1. **Per-character DOM model.** `play_typewriter_engine.js` reveals text by appending `<span class="char">…</span>` elements (one per code-point, whitespace preserved as visible spans), not by mutating `textContent.substring`. The block element's final `textContent` equals the source string. Each appended span receives a CSS reveal animation (`opacity` + `transform: translateY` + `filter: blur`) so each character resolves into place rather than popping.
2. **Live cursor.** A single `<span class="play-cursor" aria-hidden="true">` element is appended after the last revealed char-span on every tick. The cursor's variant (`data-cursor-variant`) is driven by the active block's beat profile. The cursor breathes (sinusoidal opacity + glow), and pulses sharply on each newly-revealed char. When a block completes the cursor performs a "settle" animation (pulse, shrink, fade) before the next slice begins.
3. **Punctuation-aware pauses.** After a char is revealed the engine schedules the next char's reveal at `now + base_interval + jitter + punctuation_pause(char)`, where `punctuation_pause` is sourced from a constant map (`. ! ?` → 280–420 ms; `, ;` → 110–160 ms; `—` → 180 ms; `…` → 650 ms cumulative; `\n` → 200 ms). This activates the "sentence breath" that today is absent.
4. **Micro-jitter.** Per-char interval is multiplied by `(1 + noise)` where `noise ∈ [-0.12, +0.12]` from a deterministic PRNG seeded with the block id (so the same block id produces the same rhythm on replay/debug). This removes the machine-cadence.
5. **`pause_after_ms` activated.** Block completion holds the slice queue for the next slice's `pause_before_ms` then starts; default profile values are tuned per beat (see §6). The orchestrator owns the gap (engine reports complete; orchestrator schedules next via the existing `setOnDeliveryComplete` callback).
6. **Beat profile map.** A single profile object in the engine maps every supported `narration_beat` to: `cps`, `jitter`, `cursor_variant`, `atmosphere_class`, `pause_before_ms`, `pause_after_ms`. Beats covered: `boot` (runtime shell bootstrap only), `role_anchor`, `tension`, `dialogue`, `action`, `reflection`, plus a `default` fallback. The orchestrator switches profile on block start and applies `atmosphere_class` to the scene-block element.
7. **Beat-change decompression.** When the next slice's beat differs from the current one, the orchestrator inserts a 250 ms gap during which the outgoing cursor fades and the incoming scene-block border pulses once with the incoming beat's atmosphere colour, before the first char of the new block is scheduled.
8. **Live-direction signals.** Between player-submit and the first scene block arriving, `play_shell.js` shows a `play-composing` indicator (three pulsing glyphs in mono, beat-coloured). The signal dissolves into the position of the first revealed char. Player-echo: the player's own most-recent input fades to 0.55 opacity while the engine is delivering. The story window border carries a 60-bpm heartbeat while a WebSocket narrator stream is open; the heartbeat goes matte when the stream closes.
9. **Spektakel layer.**
   - **Skip** becomes a speed-run: remaining chars reveal at 8× current beat cps with the cursor flattened to a line and a chromatic-aberration tint; no instant `textContent` swap.
   - **`role_anchor` sweep (opt-in):** When a block's `narration_beat` is **literally** `role_anchor` (author/model annotation, not index-forced opening tags), card-border glow sweeps left→right (800 ms) before the first char is scheduled. Canonical narrator-path openings use mandatory beat **ids** and `visual_emphasis` for dramatic moments — they do **not** get this sweep unless explicitly tagged.
   - **Matrix coupling**: while a typewriter slice is active the matrix-rain layer runs +12% speed and +8% density; otherwise it relaxes to baseline.
10. **Determinism guarantee for tests.** When `TypewriterEngine` is constructed with `test_mode === true`, jitter, punctuation pauses, beat-change decompression, and matrix coupling are bypassed. The existing `getQueueState()` shape (`current_block_id`, `current_visible_chars`, `queue_length`, `queue[]`) is preserved. `clock.advanceBy()` continues to drive deterministic time. The existing test suite (`frontend/tests/test_typewriter_engine.js`) must remain green without modification.
11. **Accessibility & reduced motion.** `prefers-reduced-motion: reduce` suppresses char-reveal animation, cursor breathing, sweeps, and matrix coupling — char-spans appear instantly and the cursor is static. The existing `accessibility_mode` toggle on `BlocksOrchestrator` continues to render every block in full immediately.
12. **No content/contract changes.** Block schema, `player_display_text`/`text` selection rules (ADR-0034 §7), `typewriter_slice_start_index` semantics, and diagnostics-block suppression rules are unchanged.
13. **Runtime boot delivery is a first-class profile, not a story beat.** `play_runtime_bootstrap.js` may create a `system_boot` block with `narration_beat: "boot"` and a per-block delivery cps override. The TypewriterEngine honours `block.delivery.characters_per_second` for such operational blocks while preserving the existing global default for ordinary unannotated narrative blocks. The `boot` profile exists to style shell startup text and must not be interpreted as canonical narrative pacing.

**Consequences.** **Positive:**

- Player perceives a directed performance: punctuation breaths, beat-coded tempo, and a cursor that reacts to the engine make every turn feel hand-paced.
- Beat metadata is now load-bearing — authoring beats on a block has visible runtime impact, encouraging dramaturgs to use it.
- Live signals (composing pulse, heartbeat, echo) make the runtime's *presence* visible to the player; loss of connectivity is felt, not just logged.
- Per-char span model unlocks future effects (highlight on player-mentioned entities, in-line tooltips, evidence-anchor underlines) without another rewrite.

**Negative / risks:**

- DOM cost rises from one `textContent` write per tick to one `<span>` append per char. Mitigated by short block sizes typical for narrative beats and by `documentFragment` batching where useful. Profiled budget: < 4 ms scripting cost per 100 chars on a mid-range laptop.
- Determinism: jitter + punctuation pauses change tick math. Mitigated by `test_mode` short-circuit (no jitter, no pauses) and by deriving block-level jitter from a seeded PRNG so the same id replays identically.
- Beat profile drift: if dramaturgs author beats inconsistently, players see incoherent tempo. Mitigated by collapsing unknown beats to the `default` profile and by logging unknown beat names once per session in dev mode.

**Follow-ups:**

- Profile-tune the beat map after first playtests (the values in §6 are first-pass estimates).
- **CSS:** `scene-block--narrator-role-anchor { overflow: hidden }` can clip multi-line typewriter text — if `role_anchor` styling is used, remove or relax overflow (ADR-0034 §**narration_beat semantics**).
- Consider an opt-in audio layer (subtle tipping ticks, beat-tinted; default off) — explicitly out of scope for this ADR.
- Consider an in-game "Director cadence" preset (slow/normal/fast) exposed in the play-controls bar, multiplying every beat's `cps` uniformly.

**Implementation status.** **Last reviewed:** 2026-05-19.

| ADR bullet | Status | Evidence |
|------------|--------|----------|
| §1 Per-char `<span class="char">` model | **Done** | `frontend/static/play_typewriter_engine.js` |
| §2 Live `play-cursor` + variants | **Done** | same; `style.css` `data-cursor-variant` |
| §3 Punctuation pauses | **Done** (live mode) | `PUNCTUATION_PAUSE_MS`; off in `test_mode` |
| §4 Micro-jitter (seeded PRNG) | **Done** (live mode) | `_mulberry32` / `_seedFromString` |
| §5 `pause_before` / `pause_after` between slices | **Done** | `play_blocks_orchestrator.js` profile gaps |
| §6 `TYPEWRITER_BEAT_PROFILES` map | **Done** | `DEFAULT_BEAT_PROFILES`; unknown → `default` |
| §7 Beat-change decompression | **Partial** | `scene-block--beat-decompress` + profile gap; not a fixed 250 ms orchestrator hold |
| §8 Composing / player-echo / typing pulse | **Done** | `frontend/static/play_cinematic.js` |
| §9 Skip speedrun | **Done** | `is-speedrun` on `.play-shell` |
| §9 `role_anchor` sweep | **Done (opt-in)** | CSS on `.scene-block--narrator-role-anchor` only when block has `narration_beat: "role_anchor"` |
| §9 Matrix +12% / +8% while typing | **Partial** | CSS glow on `body.is-typing .matrix-layer__glow`; play route often has no matrix layer |
| §10 `test_mode` determinism | **Done** | 37 Jest cases in `frontend/tests/test_typewriter_engine.js` |
| §11 `prefers-reduced-motion` | **Done** | `style.css` media query |
| §13 `boot` profile | **Done** | `play_runtime_bootstrap.js` |

**Opening `narration_beat` semantics** (normative, not typewriter-specific): [ADR-0034](../../../archive/adr-retired-2026/adr-0034-player-facing-narrative-shell-contract.md) §**narration_beat semantics**. Do **not** reintroduce `_annotate_goc_opening_narration_beats` or index-based `premise` / `scene_setup` / `role_anchor` on `scene_blocks`. Canonical narrator-path blocks use **mandatory beat ids** (e.g. `stick_strikes_face`); typewriter uses the `default` profile unless the id matches a named profile key.

**Testing.** How we **verify** this decision:

- **Unit suite (current):** `cd frontend && npm test -- --testPathPattern=test_typewriter_engine` — **37 passed** (2026-05-19). `test_mode === true` disables jitter/punctuation for determinism; public surface (`getQueueState`, `skipBlock`, `revealAll`, `setOnDeliveryComplete`) unchanged.
- **Render-shape contract test (follow-up):** assert post-delivery `.char` count equals display text length and `.play-cursor` is present — not yet a dedicated case.
- **Beat-profile dispatch test (follow-up):** block with `narration_beat: 'tension'` → tension `cps` / `data-cursor-variant` — not yet a dedicated case.
- **Runtime boot profile test (follow-up):** `boot` in `DEFAULT_BEAT_PROFILES` + `play_runtime_bootstrap.js` — covered indirectly; no isolated Jest case yet.
- **World-Engine opening guard:** `world-engine/tests/test_trace_middleware.py::test_opening_scene_blocks_do_not_force_legacy_ui_narration_beat_tags`.
- **Frontend pytest suite:** `cd frontend && python -m pytest tests/` must remain green when touching the shell.
- **Manual smoke**: open `/play/<session_id>` in Chrome and Firefox with a real backend + world-engine; confirm composing pulse → first char dissolve → punctuation breaths → cursor variant per beat → settle → next slice. Repeat with `prefers-reduced-motion: reduce` set.

**Failure modes that should trigger an ADR review:**

- Tests in `frontend/tests/test_typewriter_engine.js` need to be modified to pass — that means we broke the determinism guarantee in §10.
- Players report the new cadence "feels slower than reading" — beat profile values in §6 need re-tuning; that is a tuning patch, not an ADR change. An ADR change is required if a beat is *added* to the schema or *removed* from the profile map.
- Per-char rendering exceeds the 4 ms scripting budget on baseline hardware — implementation must batch via `DocumentFragment` or fall back to chunked reveal.

Gate and promotion-style tests must comply with **[ADR-0039](../../../archive/adr-retired-2026/adr-0039-gate-tests-no-hardcoded-oracle-bypass.md)** (no hardcoded primary oracles); the typewriter is a display surface and never an oracle — no compliance change required.

**Evidence.** `docs/architecture/components/frontend/architecture.md#d2-typewriter-cinematic-direction` (archived — see `docs/archive/adr-retired-2026/`)

### D3: Modular block rendering

**Status:** Accepted · **Origin:** MVP5-001

**Context.** Committed block types must map to isolated renderer modules so presentation evolves without backend deploys.

**Decision.** Block renderer modules map semantic `block_type` (and optional `narration_beat`) to UI components; orchestrator owns delivery sequencing, renderer owns DOM shape, typewriter owns reveal timing.

**Evidence.** [`frontend/static/play_block_renderer.js`](../../../../frontend/static/play_block_renderer.js), [`frontend/tests/test_block_renderer.js`](../../../../frontend/tests/test_block_renderer.js), [ADR MVP5-001](../../../archive/adr-retired-2026/MVP_Live_Runtime_Completion/adr-mvp5-001-modular-block-rendering-architecture.md).

 Quality Requirements

`frontend/tests/`, MVP5 gate evidence when present.

## 11. Risks & Technical Debt

ADR-0033 frontend readiness states partially implemented.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Play shell | UI surface executing turns via backend |
