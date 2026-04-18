from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecipeStep:
    name: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecipeResult:
    recipe: str
    ok: bool
    steps: list[RecipeStep]
    output: dict[str, Any]
