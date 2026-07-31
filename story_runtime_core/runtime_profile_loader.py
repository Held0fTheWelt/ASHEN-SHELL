"""Load runtime ExperienceTemplate profiles from authored YAML (Wave 7).

Story facts remain in ``content/modules/<module>/``. Runtime profiles under
``runtime_profiles/`` supply bootstrap roles/rooms only — not competing content truth.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .experience_template_models import (
    ExperienceKind,
    ExperienceTemplate,
    ExitTemplate,
    JoinPolicy,
    ParticipantMode,
    RoleTemplate,
    RoomTemplate,
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "content" / "modules").is_dir():
            return parent
    return here.parents[1]


def runtime_profile_path(content_module_id: str, profile_id: str) -> Path:
    return (
        _repo_root()
        / "content"
        / "modules"
        / content_module_id
        / "runtime_profiles"
        / f"{profile_id}.yaml"
    )


def _as_mode(value: Any) -> ParticipantMode:
    raw = str(value or "").strip().lower()
    if raw == ParticipantMode.HUMAN.value:
        return ParticipantMode.HUMAN
    if raw == ParticipantMode.NPC.value:
        return ParticipantMode.NPC
    raise ValueError(f"Unsupported participant mode: {value!r}")


def _role_from_dict(row: dict[str, Any]) -> RoleTemplate:
    return RoleTemplate(
        id=str(row["id"]),
        display_name=str(row["display_name"]),
        description=str(row.get("description") or ""),
        mode=_as_mode(row.get("mode")),
        initial_room_id=str(row["initial_room_id"]),
        can_join=bool(row.get("can_join", row.get("mode") == "human")),
        npc_voice=str(row["npc_voice"]) if row.get("npc_voice") is not None else None,
    )


def _room_from_dict(row: dict[str, Any]) -> RoomTemplate:
    exits: list[ExitTemplate] = []
    for exit_row in row.get("exits") or []:
        if not isinstance(exit_row, dict):
            continue
        exits.append(
            ExitTemplate(
                direction=str(exit_row["direction"]),
                target_room_id=str(exit_row["target_room_id"]),
                label=str(exit_row.get("label") or exit_row["direction"]),
            )
        )
    return RoomTemplate(
        id=str(row["id"]),
        name=str(row["name"]),
        description=str(row.get("description") or ""),
        exits=exits,
        prop_ids=list(row.get("prop_ids") or []),
        action_ids=list(row.get("action_ids") or []),
        artwork_prompt=str(row["artwork_prompt"]) if row.get("artwork_prompt") is not None else None,
    )


@lru_cache(maxsize=8)
def load_runtime_profile_template(
    content_module_id: str,
    profile_id: str,
) -> ExperienceTemplate:
    """Build an ExperienceTemplate from ``runtime_profiles/<profile_id>.yaml``."""
    path = runtime_profile_path(content_module_id, profile_id)
    if not path.is_file():
        raise FileNotFoundError(f"Runtime profile YAML missing: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Runtime profile must be a mapping: {path}")

    kind_raw = str(payload.get("kind") or "solo_story").strip().lower()
    kind = ExperienceKind.SOLO_STORY if kind_raw == "solo_story" else ExperienceKind(kind_raw)
    join_raw = str(payload.get("join_policy") or "owner_only").strip().lower()
    join_policy = JoinPolicy.OWNER_ONLY if join_raw == "owner_only" else JoinPolicy(join_raw)

    roles = [_role_from_dict(row) for row in payload.get("roles") or [] if isinstance(row, dict)]
    rooms = [_room_from_dict(row) for row in payload.get("rooms") or [] if isinstance(row, dict)]
    return ExperienceTemplate(
        id=str(payload.get("profile_id") or profile_id),
        title=str(payload.get("title") or profile_id),
        kind=kind,
        join_policy=join_policy,
        summary=str(payload.get("summary") or ""),
        max_humans=int(payload.get("max_humans") or 1),
        initial_beat_id=str(payload.get("initial_beat_id") or ""),
        tags=list(payload.get("tags") or []),
        roles=roles,
        rooms=rooms,
        props=[],
        actions=[],
        beats=[],
    )


def goc_solo_role_templates() -> list[RoleTemplate]:
    """Compatibility helper for gates: roles from the YAML runtime profile."""
    return list(load_runtime_profile_template("god_of_carnage", "god_of_carnage_solo").roles)
