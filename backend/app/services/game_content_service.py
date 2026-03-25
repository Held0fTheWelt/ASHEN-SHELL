from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.extensions import db
from app.models import GameExperienceTemplate

_ALLOWED_TYPES = {
    GameExperienceTemplate.TYPE_SOLO,
    GameExperienceTemplate.TYPE_GROUP,
    GameExperienceTemplate.TYPE_OPEN_WORLD,
}
_ALLOWED_STATUSES = {
    GameExperienceTemplate.STATUS_DRAFT,
    GameExperienceTemplate.STATUS_REVIEW,
    GameExperienceTemplate.STATUS_PUBLISHED,
    GameExperienceTemplate.STATUS_ARCHIVED,
}
_REQUIRED_PAYLOAD_KEYS = {
    "id",
    "title",
    "kind",
    "join_policy",
    "summary",
    "max_humans",
    "initial_beat_id",
    "roles",
    "rooms",
    "props",
    "actions",
    "beats",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_tags(tags: Any) -> list[str]:
    if tags is None:
        return []
    if isinstance(tags, str):
        raw = tags.split(",")
    elif isinstance(tags, list):
        raw = tags
    else:
        raise ValueError("tags must be a list of strings or a comma-separated string")
    out: list[str] = []
    for item in raw:
        value = str(item or "").strip()
        if value:
            out.append(value)
    return out


def validate_experience_payload(payload: Any, *, expected_template_key: str | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("draft_payload must be a JSON object")
    missing = sorted(_REQUIRED_PAYLOAD_KEYS - set(payload.keys()))
    if missing:
        raise ValueError(f"draft_payload is missing required keys: {', '.join(missing)}")
    template_id = str(payload.get("id") or "").strip()
    if not template_id:
        raise ValueError("draft_payload.id is required")
    if expected_template_key and template_id != expected_template_key:
        raise ValueError("draft_payload.id must match the template key")
    kind = str(payload.get("kind") or "").strip()
    if kind not in _ALLOWED_TYPES:
        raise ValueError("draft_payload.kind must be one of: solo_story, group_story, open_world")
    join_policy = str(payload.get("join_policy") or "").strip()
    if join_policy not in {"owner_only", "invited_party", "public"}:
        raise ValueError("draft_payload.join_policy must be one of: owner_only, invited_party, public")
    for key in ("roles", "rooms", "props", "actions", "beats"):
        if not isinstance(payload.get(key), list):
            raise ValueError(f"draft_payload.{key} must be a list")
    try:
        max_humans = int(payload.get("max_humans"))
    except (TypeError, ValueError) as exc:
        raise ValueError("draft_payload.max_humans must be an integer") from exc
    if max_humans < 1:
        raise ValueError("draft_payload.max_humans must be at least 1")
    normalized = dict(payload)
    normalized["id"] = template_id
    normalized["kind"] = kind
    normalized["join_policy"] = join_policy
    normalized["max_humans"] = max_humans
    normalized["title"] = str(payload.get("title") or "").strip()
    normalized["summary"] = str(payload.get("summary") or "").strip()
    normalized["initial_beat_id"] = str(payload.get("initial_beat_id") or "").strip()
    normalized.setdefault("tags", [])
    normalized.setdefault("style_profile", "retro_pulp")
    return normalized


def _base_query(q: str | None = None):
    query = GameExperienceTemplate.query
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            db.or_(
                GameExperienceTemplate.key.ilike(pattern),
                GameExperienceTemplate.title.ilike(pattern),
                GameExperienceTemplate.summary.ilike(pattern),
            )
        )
    return query


def list_experiences(*, q: str | None = None, status: str | None = None, include_payload: bool = False) -> list[dict[str, Any]]:
    query = _base_query(q)
    if status:
        query = query.filter(GameExperienceTemplate.status == status)
    items = query.order_by(GameExperienceTemplate.updated_at.desc(), GameExperienceTemplate.id.desc()).all()
    return [item.to_dict(include_payload=include_payload) for item in items]


def get_experience(template_id: int) -> GameExperienceTemplate | None:
    return db.session.get(GameExperienceTemplate, template_id)


def create_experience(*, key: str, title: str, experience_type: str, summary: str | None, tags: Any, style_profile: str | None, draft_payload: Any, actor_id: int | None) -> tuple[GameExperienceTemplate | None, str | None]:
    key = (key or "").strip()
    title = (title or "").strip()
    experience_type = (experience_type or "").strip()
    if not key:
        return None, "key is required"
    if not title:
        return None, "title is required"
    if experience_type not in _ALLOWED_TYPES:
        return None, "experience_type must be one of: solo_story, group_story, open_world"
    if GameExperienceTemplate.query.filter_by(key=key).first():
        return None, "Experience key already exists"
    try:
        tags_value = _normalize_tags(tags)
        payload = validate_experience_payload(draft_payload, expected_template_key=key)
    except ValueError as exc:
        return None, str(exc)

    item = GameExperienceTemplate(
        key=key,
        title=title,
        experience_type=experience_type,
        summary=(summary or "").strip() or None,
        tags=tags_value,
        style_profile=(style_profile or "retro_pulp").strip() or "retro_pulp",
        status=GameExperienceTemplate.STATUS_DRAFT,
        current_version=1,
        draft_payload=payload,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.session.add(item)
    db.session.commit()
    return item, None


def update_experience(template_id: int, *, title: str | None = None, experience_type: str | None = None, summary: str | None = None, tags: Any = None, style_profile: str | None = None, draft_payload: Any = None, status: str | None = None, actor_id: int | None = None) -> tuple[GameExperienceTemplate | None, str | None]:
    item = get_experience(template_id)
    if not item:
        return None, "Experience not found"
    changed = False
    if title is not None:
        title = (title or "").strip()
        if not title:
            return None, "title cannot be empty"
        item.title = title
        changed = True
    if experience_type is not None:
        experience_type = (experience_type or "").strip()
        if experience_type not in _ALLOWED_TYPES:
            return None, "experience_type must be one of: solo_story, group_story, open_world"
        item.experience_type = experience_type
        changed = True
    if summary is not None:
        item.summary = (summary or "").strip() or None
        changed = True
    if tags is not None:
        try:
            item.tags = _normalize_tags(tags)
        except ValueError as exc:
            return None, str(exc)
        changed = True
    if style_profile is not None:
        item.style_profile = (style_profile or "retro_pulp").strip() or "retro_pulp"
        changed = True
    if status is not None:
        status = (status or "").strip()
        if status not in _ALLOWED_STATUSES:
            return None, "status must be one of: draft, review, published, archived"
        item.status = status
        changed = True
    if draft_payload is not None:
        try:
            item.draft_payload = validate_experience_payload(draft_payload, expected_template_key=item.key)
        except ValueError as exc:
            return None, str(exc)
        item.current_version = int(item.current_version or 1) + 1
        changed = True
    if not changed:
        return item, None
    item.updated_by = actor_id
    item.updated_at = _now()
    db.session.commit()
    return item, None


def publish_experience(template_id: int, *, actor_id: int | None = None) -> tuple[GameExperienceTemplate | None, str | None]:
    item = get_experience(template_id)
    if not item:
        return None, "Experience not found"
    try:
        payload = validate_experience_payload(item.draft_payload, expected_template_key=item.key)
    except ValueError as exc:
        return None, str(exc)
    item.published_payload = payload
    item.published_version = item.current_version
    item.status = GameExperienceTemplate.STATUS_PUBLISHED
    item.published_by = actor_id
    item.published_at = _now()
    item.updated_by = actor_id
    item.updated_at = _now()
    db.session.commit()
    return item, None


def list_published_experiences() -> list[dict[str, Any]]:
    items = (
        GameExperienceTemplate.query
        .filter(GameExperienceTemplate.status == GameExperienceTemplate.STATUS_PUBLISHED)
        .order_by(GameExperienceTemplate.published_at.desc(), GameExperienceTemplate.id.desc())
        .all()
    )
    out = []
    for item in items:
        if not item.published_payload:
            continue
        out.append(
            {
                "template_id": item.key,
                "version": item.published_version,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "payload": item.published_payload,
            }
        )
    return out
