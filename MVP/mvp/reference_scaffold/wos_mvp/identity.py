from __future__ import annotations

class EntityIdentityResolver:
    def __init__(self, alias_to_canonical: dict[str, str] | None = None) -> None:
        self.alias_to_canonical = {k.lower(): v for k, v in (alias_to_canonical or {}).items()}

    def canonicalize(self, raw: str) -> str:
        key = raw.strip().lower()
        return self.alias_to_canonical.get(key, key.replace(" ", "_"))

    def same_entity(self, left: str, right: str) -> bool:
        return self.canonicalize(left) == self.canonicalize(right)
