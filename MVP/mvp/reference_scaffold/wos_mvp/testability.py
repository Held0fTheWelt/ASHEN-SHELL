from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(slots=True)
class RuntimeBuilder:
    graph_factory: Callable[[], Any] | None = None

    def build_non_graph_seam(self) -> str:
        return "non_graph_ready"

    def build_graph_seam(self) -> Any:
        if self.graph_factory is None:
            raise RuntimeError("graph_factory required for graph seam")
        return self.graph_factory()
