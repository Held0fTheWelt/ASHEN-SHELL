from __future__ import annotations
from collections import defaultdict

class LineageGraph:
    def __init__(self) -> None:
        self.forward: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self.reverse: dict[str, list[tuple[str, str]]] = defaultdict(list)

    def add_edge(self, source: str, edge_type: str, target: str) -> None:
        self.forward[source].append((edge_type, target))
        self.reverse[target].append((edge_type, source))

    def successors(self, record_id: str) -> list[tuple[str, str]]:
        return list(self.forward.get(record_id, []))

    def predecessors(self, record_id: str) -> list[tuple[str, str]]:
        return list(self.reverse.get(record_id, []))

    def trace_upstream(self, record_id: str) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []

        def visit(node: str) -> None:
            for _, parent in self.predecessors(node):
                if parent not in seen:
                    seen.add(parent)
                    ordered.append(parent)
                    visit(parent)

        visit(record_id)
        return ordered

    def trace_downstream(self, record_id: str) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []

        def visit(node: str) -> None:
            for _, child in self.successors(node):
                if child not in seen:
                    seen.add(child)
                    ordered.append(child)
                    visit(child)

        visit(record_id)
        return ordered
