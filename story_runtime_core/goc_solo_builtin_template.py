"""God of Carnage solo builtin experience template (SSOT fragment).

Canonical dramatic YAML remains under content/modules/god_of_carnage/; this template
must stay title-aligned (VERTICAL_SLICE_CONTRACT_GOC).
"""

from __future__ import annotations

from .experience_template_models import (
    ExperienceKind,
    ExperienceTemplate,
    JoinPolicy,
)
from .goc_solo_builtin_roles_rooms import goc_solo_role_templates, goc_solo_room_templates


def build_god_of_carnage_solo() -> ExperienceTemplate:
    # MVP1-FIX-002: Runtime profile only — NO story truth here.
    # This profile is NOT a loadable content module.
    # Story truth (beats, props, actions) is DERIVED from canonical god_of_carnage content
    # module at runtime via runtime profile linking.
    # Roles and rooms are runtime structure required to bootstrap the run (FIX-002-B).
    # Selected player role maps to one of the two selectable human roles (annette/alain).
    # Unselected human guest roles are converted to NPC participants at bootstrap.
    # visitor must never appear as a role; canonical GoC characters are veronique and michel as NPCs.
    # (VERTICAL_SLICE_CONTRACT_GOC.md §6.1).
    return ExperienceTemplate(
        id="god_of_carnage_solo",
        title="God of Carnage",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        summary=(
            "Runtime profile for a tense apartment confrontation. One human player"
            " enters via runtime_profile_id=\"god_of_carnage_solo\" with selected_player_role=annette|alain."
            " Story structure is provided by canonical god_of_carnage module."
        ),
        max_humans=1,
        initial_beat_id="",  # Empty: story truth comes from canonical module at runtime
        tags=["authored", "single-adventure", "social-drama", "better-tomorrow"],
        roles=goc_solo_role_templates(),  # Runtime structure for bootstrap: annette/alain (human), veronique/michel (NPC)
        rooms=goc_solo_room_templates(),  # Runtime structure for bootstrap: hallway/living_room/bathroom
        props=[],
        actions=[],
        beats=[],
    )
