# Player Shell Obligations and Quality Signals

## Player-Visible Quality Signals (Mandatory)

The MVP must convey these quality signals to every player:

### Signal 1: Scene State Clarity
**What it means:** The player understands what's happening and where they are.

**Requirements:**
- Scene description is concrete (locations, objects, spatial relationships are real)
- Characters present are named and their emotional/relational state is visible
- The dramatic pressure active in the scene is palpable (not generic)
- Scene identity is distinct (different scenes should feel like different places)

**Validation:** Turn output includes `scene_changes` describing what changed; previous scenes are retrievable.

**Test:** Player can close their eyes, listen to narration, and accurately describe where they are.

### Signal 2: Actionable Options
**What it means:** The player knows what they can do; actions have stakes.

**Requirements:**
- Available actions are shown (not just "say something"; specific options based on scene)
- Each action has visible consequences (what would happen if you do X)
- Options reflect the pressure (if scene is high blame, options show that)
- Invalid actions are rejected explicitly (not silently ignored)

**Validation:** Turn output includes suggested actions based on scene function and available responders.

**Test:** Player feels they have agency; they can predict roughly what will happen if they choose action A vs. action B.

### Signal 3: Turn Effects Visibility
**What it means:** The player sees what their action did.

**Requirements:**
- Immediate feedback is visible (character reacted, scene changed, pressure shifted)
- Character response is differentiated (Vanya responds differently than Annette)
- Effects match the action (if player escalates, pressure increases; if player repairs, pressure decreases)
- Feedback is concrete (not abstract; use dialogue and narrative beats, not labels)

**Validation:** `visible_output` includes dialogue and scene changes directly traceable to committed effects.

**Test:** Player can point to specific dialogue or scene change and say "that's what happened because I did X."

### Signal 4: Short-Term Memory
**What it means:** The player remembers why they're here; context carries forward.

**Requirements:**
- Last 3 turns are summarized in scene context (what led to this moment)
- Character relationships mentioned are based on actual turn history (not generic)
- Consequences from previous turns are referenced in narration
- Scene pressure builds on previous pressure (not random)

**Validation:** Turn output includes `recent_events` list; context mentions specific prior turns.

**Test:** If session paused at turn 20 and resumes at turn 21, player sees turns 18-20 summarized; context feels continuous.

### Signal 5: Consequence Carry-Forward
**What it means:** Actions have stakes that persist across multiple turns.

**Requirements:**
- A consequence established in turn N appears in turn N+1 narration
- Character behavior reflects prior consequences (injured character is slower, alliance-broken character doesn't help, etc.)
- Pressure vectors compound (each turn's pressure shapes next turn's options)
- Consequences can resolve (pressure can decrease; wounds can heal; alliances can reform)

**Validation:** Turn log shows `consequence_preview` in turn N and `consequence_feedback.carry_forward` in turn N+1+.

**Test:** Player's turn 1 action that "broke an alliance" is visible in turn 2-5 character behavior (character doesn't help, barely speaks, finally reconciles in turn 5).

---

## Character Response Bounds

### Voice Differentiation
Each character must have recognizable voice across turns:

**Vanya** (protagonist):
- Speech: Formal, literary, self-aware (uses long sentences, pauses)
- Pressure response: Inward (shame, denial, intellectual defensiveness)
- Goals: Maintain dignity and control; avoid humiliation
- Tone: Wounded pride, dark humor

**Annette** (ex-wife):
- Speech: Sharp, direct, often bitter (short sentences, pointed)
- Pressure response: Outward (attack, interrogation)
- Goals: Make Vanya face consequences; get answers
- Tone: Accusatory, demanding

**Other characters** should have distinct voices; differentiation makes game feel alive.

**Validation:** Operator can read dialogue in turn_trace and immediately identify who is speaking.

**Test:** Dialogue is anonymized; operator can guess speaker with 80%+ accuracy.

### Pressure Alignment
Character behavior must align with active pressure:

- **High blame:** Characters are angry, accusatory, escalating
- **Shame exposure:** Characters are defensive, hiding, avoiding eye contact
- **Alliance fracture:** Characters don't cooperate, speak coldly, may leave
- **Dignity injury:** Characters are withdrawn, less talkative, emotional

**Validation:** Scene assessment records active pressure; character dialogue reflects it.

**Test:** If pressure is "high blame", character dialogue is accusatory (not apologetic). If pressure is "shame exposure", character is defensive (not attacking).

### Response Boundaries (What Characters Won't Do)

Characters have role boundaries:

- **Vanya won't become antagonistic toward himself** (he may internalize blame, but won't self-harm narratively)
- **Annette won't forgive without acknowledgment of hurt** (she can reconcile, but not before Vanya owns consequences)
- **Characters won't contradict established facts** (if Annette said "I left because you were drunk every night," she won't later say "I never complained about drinking")
- **Characters honor their revealed injuries** (if Annette's dignity was wounded in turn 3, it must influence turn 4-6 behavior)

**Validation:** Operator audit checks if character behavior respects these bounds.

**Test:** Run session 10 times with different player actions; character response patterns are consistent (not random).

---

## Continuity Across Re-Entry

If player leaves mid-scene and returns later:

### Resumption Requirements
- Scene context is unchanged (same location, same characters, same objects)
- Character emotional state is preserved (if they were angry when player left, they're still angry on return)
- Pressure vectors are intact (scene pressure is where it was)
- Turn history is available (player can review what happened before they left)

### Re-Entry Narration
When player returns:

1. Scene is re-described (but briefly; player remembers it)
2. Character current state is shown (how they're standing/speaking now)
3. What changed while player was gone (did anything shift, or did characters just wait)
4. Available options are shown (usually same as before, but may change based on time elapsed)

**Test:** Player leaves at turn 5, returns 1 hour later; they can understand the situation without replaying.

---

## Graceful Degradation Rules

If validation fails or commit fails, player still sees something:

### Validation Failure
If proposed effects fail validation:

**Player sees:** "Your suggestion didn't land. [Character name] isn't ready for that kind of confrontation. What else?"

**Behind scenes:** Validation rejected the move; commit never happened; state is unchanged.

**Operator sees:** Full validation failure explanation (which rule was violated, why).

### Commit Failure
If committed effects can't be applied (data error):

**Player sees:** "Something went wrong applying that action. The system is recovering. Try again?"

**Behind scenes:** Commit detected data inconsistency; session is paused; operator is alerted.

**Operator sees:** Full error trace and recommended corrective action.

### Render Failure
If turn cannot be rendered to player-visible output:

**Player sees:** Generic fallback message ("The scene pauses for a moment. What do you do?") + indication that something unusual happened.

**Behind scenes:** Render detected inconsistency in committed state; fallback message is shown; session is marked `degraded`.

**Operator sees:** What the inconsistency was and how to fix it.

### All Degradation is Governed
- Fallback messages are explicit (player knows something unusual happened)
- Operators are alerted (issue is tracked)
- Session is marked (session status reflects degradation)
- Turn trace is preserved (diagnostics show exactly what went wrong)

No silent failures.

---

## Accessibility and Clarity Obligations

### Language & Vocabulary
- No jargon (no "pressure vector", "continuity impact", "scene function")
- Dialogue is natural (characters speak like people, not game systems)
- Consequences are named intuitively ("He's angry now", not "blame_pressure_magnitude=high")
- Scene descriptions are vivid but not purple prose

**Test:** Read narration to someone unfamiliar with the game; they understand what's happening.

### Sensory Richness
- Scenes are described with sensory detail (what characters see, hear, feel)
- Dialogue includes action beats (character's posture, tone, movement)
- Consequence feedback is concrete (what physically/emotionally changed)

**Test:** Player can imagine the scene vividly; feels like being there, not reading a log.

### Understandable Failure
When something goes wrong:

- Reason is explicit ("Annette isn't ready to hear that right now")
- Recovery path is clear ("Ask something else?" or "Wait for another moment?")
- Consequences are shown ("Her trust is lower now")

**Test:** When validation rejects a move, player understands why and what to try next.

### Pacing and Rhythm
- Turns take reasonable time (5-15 seconds of narration max)
- Dialogue is not overwhelming (3-5 spoken lines per turn typical)
- Silence is used strategically (brief pauses make moments land)

**Test:** Player never waits too long; dialogue never feels like a monologue.

---

## Support Obligations

### Help During Session
Player can:

- Ask "who is who?" and get character summary with relationship
- Ask "what happened?" and get brief turn summary
- Ask "what can I do?" and get action suggestions based on scene
- Request scene re-description (if they missed something)

**Implementation:** Chat sidebar provides these queries.

### Help Between Sessions
If player returns after break:

- Session summary is available (last 5 turns in brief form)
- Character relationship summary is available
- Pressure state is summarized
- Continue button is prominent

**Implementation:** Session dashboard shows this without requiring navigation.

### Help on Failure
When a move is rejected:

- Reason is explained in player-friendly terms
- Similar moves that might work are suggested
- Player isn't stuck (alternative actions always exist)

**Implementation:** Feedback message includes concrete suggestion.

---

## Acceptance Criteria

Player shell is correct when:

1. **All 5 quality signals are present** in every turn
2. **Character voices are distinct** (operator can identify speaker from dialogue)
3. **Pressure alignment is visible** (character behavior matches scene pressure)
4. **Consequences carry forward** (turn N consequences appear in turn N+1 narration)
5. **Degradation is graceful** (all failures show explicit fallback message)
6. **Language is clear** (no jargon; player understands what's happening)
7. **Pacing is smooth** (turns feel natural; no overwhelming text walls)
8. **Support is available** (player can ask for help and get it)

---

## Testing the Signals

### Test Protocol
Run 5 sessions with different player approaches:
1. **Escalation path** (player pushes conflict)
2. **Repair path** (player seeks reconciliation)
3. **Evasion path** (player avoids confrontation)
4. **Information path** (player asks questions)
5. **Mixed path** (player changes approaches mid-session)

### Signal Validation Checklist
For each session, verify:
- [ ] Scene clarity: Can observer describe scene accurately?
- [ ] Actionable options: Can player predict roughly what happens?
- [ ] Turn effects visible: Can player point to dialogue/change that shows their action worked?
- [ ] Short-term memory: Does context reference previous turns?
- [ ] Consequence carry-forward: Do turn N consequences appear in turn N+1?
- [ ] Character voice distinct: Can observer identify speaker?
- [ ] Pressure alignment visible: Does character behavior match pressure?
- [ ] Graceful degradation: Do failures show explicit message, not silent ignoring?

All checkmarks must be true for Phase 4 acceptance.

