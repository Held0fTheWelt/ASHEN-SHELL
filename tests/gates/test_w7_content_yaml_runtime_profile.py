"""Wave 7: YAML-backed GoC runtime profile and no product Python content overrides."""

from __future__ import annotations

from pathlib import Path

from story_runtime_core.builtin_experience_templates import build_god_of_carnage_solo, load_builtin_templates
from story_runtime_core.runtime_profile_loader import runtime_profile_path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_goc_solo_profile_loads_from_authored_yaml() -> None:
    path = runtime_profile_path("god_of_carnage", "god_of_carnage_solo")
    assert path.is_file()
    assert "content/modules/god_of_carnage/runtime_profiles" in path.as_posix()
    template = build_god_of_carnage_solo()
    assert template.id == "god_of_carnage_solo"
    assert template.props == []
    assert template.actions == []
    assert template.beats == []
    assert {role.id for role in template.roles} == {"annette", "alain", "veronique", "michel"}
    assert {room.id for room in template.rooms} == {"hallway", "living_room", "bathroom"}


def test_no_goc_solo_builtin_python_modules() -> None:
    src = REPO_ROOT / "story_runtime_core"
    leftovers = sorted(src.glob("goc_solo_builtin_*.py"))
    assert leftovers == [], f"hand-maintained GoC builtins must be removed: {leftovers}"


def test_no_product_python_overrides_authored_fact() -> None:
    """Product Python must not redefine GoC character/room facts outside the YAML profile."""
    forbidden_stems = {
        "goc_solo_builtin_catalog",
        "goc_solo_builtin_catalog_actions",
        "goc_solo_builtin_roles_rooms",
        "goc_solo_builtin_template",
    }
    hits: list[str] = []
    for root_name in ("story_runtime_core", "backend/app", "world-engine/world_engine", "ai_stack"):
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if path.stem in forbidden_stems:
                hits.append(path.as_posix())
    assert hits == [], f"product Python still ships hand-authored GoC builtin modules: {hits}"

    templates = load_builtin_templates()
    goc = templates["god_of_carnage_solo"]
    # Runtime profile may bootstrap structure, but must not carry competing story catalogs.
    assert goc.props == [] and goc.actions == [] and goc.beats == []
