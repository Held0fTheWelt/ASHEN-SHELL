"""Scene / ending legality helpers for story-runtime (Wave 4 / D26).

Operates on runtime_projection dicts (live authority), not backend ContentModule.
Missing transition cards do not imply impossibility — Wave 3 maps that to partial.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SceneLegalityDecision:
    allowed: bool
    reason: str = ""


class SceneTransitionLegality:
    """Projection-based legality for transitions and endings."""

    @staticmethod
    def check_transition_legal(
        *,
        from_scene: str,
        to_scene: str,
        runtime_projection: dict[str, Any],
    ) -> SceneLegalityDecision:
        scenes = _scene_ids(runtime_projection)
        if to_scene not in scenes:
            return SceneLegalityDecision(
                allowed=False,
                reason=f"Scene {to_scene!r} not in runtime projection",
            )
        if from_scene == to_scene:
            return SceneLegalityDecision(
                allowed=True,
                reason=f"Self-transition in {from_scene!r} is always allowed",
            )
        hints = runtime_projection.get("transition_hints")
        if not isinstance(hints, list) or not hints:
            # No card → not illegal here; commit layer treats as partial (E9).
            return SceneLegalityDecision(
                allowed=True,
                reason="No transition hints; legality deferred to partial commit semantics",
            )
        allowed_targets: set[str] = set()
        for row in hints:
            if not isinstance(row, dict):
                continue
            frm = str(row.get("from") or row.get("from_scene") or "").strip()
            to = str(row.get("to") or row.get("to_scene") or "").strip()
            if frm == from_scene and to:
                allowed_targets.add(to)
        if to_scene in allowed_targets:
            return SceneLegalityDecision(
                allowed=True,
                reason=f"Transition {from_scene!r} -> {to_scene!r} is on the transition card",
            )
        return SceneLegalityDecision(
            allowed=False,
            reason=f"Transition {from_scene!r} -> {to_scene!r} not on transition card",
        )

    @staticmethod
    def check_ending_legal(
        *,
        scene_id: str,
        ending_id: str | None,
        runtime_projection: dict[str, Any],
    ) -> SceneLegalityDecision:
        if not ending_id:
            return SceneLegalityDecision(allowed=False, reason="No ending proposed")
        terminals = _terminal_scene_ids(runtime_projection)
        if scene_id in terminals:
            return SceneLegalityDecision(
                allowed=True,
                reason=f"Scene {scene_id!r} is terminal; ending {ending_id!r} allowed",
            )
        endings = runtime_projection.get("endings")
        if isinstance(endings, list):
            for row in endings:
                if not isinstance(row, dict):
                    continue
                eid = str(row.get("id") or row.get("ending_id") or "").strip()
                if eid == ending_id:
                    return SceneLegalityDecision(
                        allowed=True,
                        reason=f"Ending {ending_id!r} is declared in projection",
                    )
        return SceneLegalityDecision(
            allowed=False,
            reason=f"Ending {ending_id!r} not legal for scene {scene_id!r}",
        )


def _scene_ids(runtime_projection: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    scenes = runtime_projection.get("scenes")
    if isinstance(scenes, list):
        for scene in scenes:
            if isinstance(scene, dict):
                for key in ("id", "scene_id"):
                    raw = scene.get(key)
                    if isinstance(raw, str) and raw.strip():
                        out.add(raw.strip())
                        break
    return out


def _terminal_scene_ids(runtime_projection: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    raw = runtime_projection.get("terminal_scene_ids")
    if isinstance(raw, list):
        for x in raw:
            if isinstance(x, str) and x.strip():
                ids.add(x.strip())
    scenes = runtime_projection.get("scenes")
    if isinstance(scenes, list):
        for scene in scenes:
            if isinstance(scene, dict) and scene.get("terminal") is True:
                for key in ("id", "scene_id"):
                    sid = scene.get(key)
                    if isinstance(sid, str) and sid.strip():
                        ids.add(sid.strip())
                        break
    return ids
