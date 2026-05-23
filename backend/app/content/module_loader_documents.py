"""Document loading helpers for content module YAML trees."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .module_exceptions import ModuleFileReadError

YamlLoader = Callable[[Path], dict[str, Any]]


def _yaml_files(directory: Path, *, recursive: bool, label: str) -> list[Path]:
    try:
        pattern = "*.yaml"
        return sorted(directory.rglob(pattern) if recursive else directory.glob(pattern))
    except (PermissionError, OSError) as exc:
        raise ModuleFileReadError(
            message=f"Failed to read module {label} directory",
            module_id="unknown",
            file_path=str(directory),
            errors=[str(exc)],
        ) from exc


def _top_level_yaml_files(module_root: Path) -> list[Path]:
    try:
        return sorted(module_root.glob("*.yaml"))
    except (PermissionError, OSError) as exc:
        raise ModuleFileReadError(
            message="Failed to read module directory",
            module_id="unknown",
            file_path=str(module_root),
            errors=[str(exc)],
        ) from exc


def _load_top_level_documents(load_file: YamlLoader, module_root: Path, result: dict[str, Any]) -> None:
    for yaml_file in _top_level_yaml_files(module_root):
        result[yaml_file.stem] = load_file(yaml_file)


def _load_knowledge_documents(load_file: YamlLoader, module_root: Path, result: dict[str, Any]) -> None:
    knowledge_dir = module_root / "knowledge"
    if not knowledge_dir.is_dir():
        return
    for yaml_file in _yaml_files(knowledge_dir, recursive=False, label="knowledge"):
        result[yaml_file.stem] = load_file(yaml_file)


def _load_character_documents(load_file: YamlLoader, module_root: Path, result: dict[str, Any]) -> None:
    character_dir = module_root / "characters"
    if not character_dir.is_dir():
        return
    character_documents: dict[str, Any] = {}
    for yaml_file in _yaml_files(character_dir, recursive=True, label="characters"):
        payload = load_file(yaml_file)
        if not isinstance(payload, dict):
            continue
        if "relationship_axes" in payload or yaml_file.stem == "relationships":
            result["relationships"] = payload
            continue
        if "actor_pressure_profiles" in payload:
            result["actor_pressure_profiles"] = payload
            continue
        if yaml_file.stem == "character_voice":
            continue
        if "characters" in payload:
            result["characters"] = payload
            continue
        if "characters_index" in payload:
            continue
        inner = payload.get("character_document") or payload.get("character")
        if isinstance(inner, dict):
            char_id = str(inner.get("id") or inner.get("canonical_id") or yaml_file.stem).strip()
            if char_id:
                character_documents[char_id] = inner
    if character_documents:
        result["character_documents"] = character_documents
        result["characters"] = _character_index(character_documents)


def _character_index(character_documents: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        char_id: {
            "id": str(doc.get("canonical_id") or doc.get("id") or char_id),
            "name": str(doc.get("name") or char_id),
            "role": str(doc.get("role") or doc.get("dramatic_role") or ""),
            "actor_id": str(doc.get("actor_id") or doc.get("runtime_actor_id") or ""),
            "runtime_actor_id": str(doc.get("runtime_actor_id") or doc.get("actor_id") or ""),
            "baseline_attitude": str(
                doc.get("baseline_attitude")
                or doc.get("baseline_posture")
                or doc.get("public_identity")
                or ""
            ),
            "extras": dict(doc),
        }
        for char_id, doc in character_documents.items()
        if isinstance(doc, dict)
    }


def _load_location_documents(load_file: YamlLoader, module_root: Path, result: dict[str, Any]) -> None:
    locations_dir = module_root / "locations"
    if not locations_dir.is_dir():
        return
    location_documents: dict[str, Any] = {}
    for yaml_file in _yaml_files(locations_dir, recursive=True, label="locations"):
        payload = load_file(yaml_file)
        if not isinstance(payload, dict):
            continue
        if yaml_file.parent == locations_dir and yaml_file.stem in {"index", "locations"}:
            result["locations"] = payload
            continue
        if yaml_file.stem == "apartment_layout":
            result["apartment_layout"] = payload
            continue
        inner = payload.get("location") or payload.get("place")
        if isinstance(inner, dict):
            place_id = str(inner.get("id") or yaml_file.stem).strip()
            if place_id:
                location_documents[place_id] = inner
    if location_documents:
        result["locations"] = {"locations": _merged_locations(result.get("locations"), location_documents)}


def _merged_locations(locations_payload: Any, location_documents: dict[str, Any]) -> dict[str, Any]:
    locations_payload = locations_payload if isinstance(locations_payload, dict) else {}
    locations_inner = (
        locations_payload.get("locations")
        if isinstance(locations_payload.get("locations"), dict)
        else locations_payload
    )
    locations_inner = dict(locations_inner) if isinstance(locations_inner, dict) else {}
    merged_places: dict[str, Any] = {}
    places = locations_inner.get("places") if isinstance(locations_inner.get("places"), list) else []
    for row in places:
        if not isinstance(row, dict):
            continue
        place_id = str(row.get("id") or "").strip()
        if place_id:
            merged_places[place_id] = row
    merged_places.update(location_documents)
    locations_inner["places"] = list(merged_places.values())
    return locations_inner


def _load_object_documents(load_file: YamlLoader, module_root: Path, result: dict[str, Any]) -> None:
    objects_dir = module_root / "objects"
    if not objects_dir.is_dir():
        return
    object_documents: dict[str, Any] = {}
    for yaml_file in _yaml_files(objects_dir, recursive=True, label="objects"):
        payload = load_file(yaml_file)
        if not isinstance(payload, dict):
            continue
        if yaml_file.parent == objects_dir and yaml_file.stem in {"index", "objects"}:
            result["objects"] = payload
            continue
        inner = payload.get("object") or payload.get("object_document")
        if isinstance(inner, dict):
            object_id = str(inner.get("id") or yaml_file.stem).strip()
            if object_id:
                object_doc = dict(inner)
                object_doc.setdefault("source_ref", yaml_file.relative_to(module_root).as_posix())
                object_documents[object_id] = object_doc
    if object_documents:
        objects_payload = result.get("objects") if isinstance(result.get("objects"), dict) else {}
        objects_inner = (
            objects_payload.get("objects") if isinstance(objects_payload.get("objects"), dict) else objects_payload
        )
        objects_inner = dict(objects_inner) if isinstance(objects_inner, dict) else {}
        objects_inner["object_documents"] = object_documents
        result["objects"] = {"objects": objects_inner}


def _load_canonical_path_documents(load_file: YamlLoader, module_root: Path, result: dict[str, Any]) -> None:
    canonical_path_dir = module_root / "canonical_path"
    if not canonical_path_dir.is_dir():
        return
    canonical_path_payload: dict[str, Any] = {}
    canonical_path_steps: list[dict[str, Any]] = []
    for yaml_file in _yaml_files(canonical_path_dir, recursive=False, label="canonical_path"):
        payload = load_file(yaml_file)
        if not isinstance(payload, dict):
            continue
        if yaml_file.stem == "index":
            canonical_path_payload = payload
            continue
        step = payload.get("canonical_path_step") or payload.get("step")
        if isinstance(step, dict):
            canonical_path_steps.append(step)
    if canonical_path_payload or canonical_path_steps:
        result["canonical_path"] = {"canonical_path": _canonical_path_inner(canonical_path_payload, canonical_path_steps)}


def _canonical_path_inner(payload: dict[str, Any], steps: list[dict[str, Any]]) -> dict[str, Any]:
    inner = payload.get("canonical_path") if isinstance(payload.get("canonical_path"), dict) else payload
    inner = dict(inner) if isinstance(inner, dict) else {}
    if steps:
        inner["steps"] = sorted(steps, key=lambda row: int(row.get("sequence") or 0))
    return inner


_UNWRAP_MAPPING = {
    "characters": "characters",
    "relationships": "relationship_axes",
    "scenes": "scene_phases",
    "triggers": "trigger_types",
    "endings": "ending_types",
    "transitions": "phase_transitions",
    "escalation_axes": "escalation_axes",
    "apartment_layout": "apartment_layout",
    "premise_and_backstory": "premise_and_backstory",
    "actor_pressure_profiles": "actor_pressure_profiles",
    "phase_beat_policy": "phase_beat_policy",
    "narrator_sensory_palette": "narrator_sensory_palette",
    "opening_scene_sequence": "opening_scene_sequence",
    "opening_quote_anchors": "opening_quote_anchors",
    "hard_forbidden_rules": "hard_forbidden_rules",
    "modularity_policy": "modularity_policy",
    "scene_graph": "scene_graph",
    "canonical_path": "canonical_path",
    "locations": "locations",
    "objects": "objects",
    "content_access_policy": "content_access_policy",
}


def _unwrap_documents(result: dict[str, Any]) -> None:
    for filename, content in list(result.items()):
        if filename == "module" or not isinstance(content, dict):
            continue
        if filename == "relationships" and "relationship_axes" in content:
            result[filename] = {
                "relationship_axes": content["relationship_axes"],
                "relationship_pair_definitions": content.get("relationships", {}),
                "stability_constraints": content.get("stability_constraints", {}),
            }
            continue
        if filename in _UNWRAP_MAPPING:
            wrapping_key = _UNWRAP_MAPPING[filename]
            if wrapping_key in content:
                result[filename] = content[wrapping_key]


def load_module_file_documents(load_file: YamlLoader, module_root: Path) -> dict[str, dict]:
    """Load all YAML document groups for one content module directory."""
    result: dict[str, Any] = {}
    _load_top_level_documents(load_file, module_root, result)
    _load_knowledge_documents(load_file, module_root, result)
    _load_character_documents(load_file, module_root, result)
    _load_location_documents(load_file, module_root, result)
    _load_object_documents(load_file, module_root, result)
    _load_canonical_path_documents(load_file, module_root, result)
    _unwrap_documents(result)
    return result
