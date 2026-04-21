# 07 — NPC Autonomy and World Simulation Specification

NPCs must not be purely reactive. Important NPCs plan, update beliefs, and create off-screen events.

## Simulation modes
- full simulation for major NPCs every turn
- periodic simulation for supporting NPCs
- event-driven simulation for background actors

## Turn integration
1. Consciousness chooses strategy
2. NPC simulation runs within budget
3. Narrative layer receives world events and changed relationship states
4. Semantic layer plans against updated world pressure

Default per-turn NPC budget: 500 ms.
