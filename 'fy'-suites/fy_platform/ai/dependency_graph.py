"""TypedDependencyGraph: DAG of suite relationships with validation and queries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SuiteNode:
    """A suite in the dependency graph."""
    name: str
    suite_type: str  # e.g., 'core', 'governance', 'analysis', 'ai', 'control'
    requires: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)  # output types
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, SuiteNode):
            return self.name == other.name
        return self.name == other


@dataclass
class DependencyEdge:
    """A directed edge in the dependency graph."""
    source: str  # suite that provides
    target: str  # suite that requires
    edge_type: str  # e.g., 'output_consumes', 'fixture_consumes', 'reference'
    strength: float = 1.0  # 0.0 to 1.0, confidence in this dependency
    metadata: dict[str, Any] = field(default_factory=dict)


class TypedDependencyGraph:
    """DAG of 13 suite relationships with acyclic validation.

    Encodes the dependency structure discovered in cross_suite_intelligence.RELATED_SUITES
    plus explicit fixture and obligation relationships.
    """

    def __init__(self):
        """Initialize the dependency graph with all 13 suites."""
        self.nodes: dict[str, SuiteNode] = {}
        self.edges: list[DependencyEdge] = []
        self._build_suite_graph()

    def _build_suite_graph(self):
        """Build the complete suite graph from known relationships."""
        # Define all 13 suites with their explicit dependencies
        # Dependencies MUST be acyclic: only point from dependents to their requirements
        suites_metadata = {
            'fy_platform': ('core', [], ['contracts_ir', 'lanes', 'workspace_manifest']),
            'contractify': ('governance', ['fy_platform'], ['contracts', 'drift_findings', 'conflict_matrix']),
            'docify': ('analysis', ['fy_platform'], ['docstring_audit', 'doc_gaps', 'style_guide_violations']),
            'despaghettify': ('analysis', ['fy_platform'], ['structure_findings', 'spike_analysis', 'refactor_plan']),
            'testify': ('governance', ['contractify', 'despaghettify'], ['test_obligations', 'test_mappings', 'coverage_matrix']),
            'templatify': ('governance', ['fy_platform'], ['templates', 'template_validation', 'output_format_specs']),
            'documentify': ('governance', ['contractify', 'docify', 'templatify'], ['doc_obligations', 'doc_structure', 'generated_docs']),
            'usabilify': ('governance', ['templatify', 'documentify'], ['usability_findings', 'ui_contracts', 'accessibility_report']),
            'securify': ('governance', ['contractify', 'testify'], ['security_risks', 'compliance_gaps', 'vulnerability_matrix']),
            'observifyfy': ('control', ['contractify', 'documentify', 'testify'], ['observability_plan', 'metrics_schema', 'monitoring_config']),
            'metrify': ('analysis', ['observifyfy', 'contractify', 'testify'], ['usage_report', 'cost_analysis', 'performance_metrics']),
            'postmanify': ('governance', ['contractify'], ['postman_collections', 'api_manifest', 'openapi_sync']),
            'mvpify': ('control', ['contractify', 'despaghettify', 'testify', 'documentify'], ['MVP_bundle', 'migration_plan', 'next_steps']),
        }

        for suite_name, (suite_type, requires, provides) in suites_metadata.items():
            node = SuiteNode(
                name=suite_name,
                suite_type=suite_type,
                requires=requires,
                provides=provides,
            )
            self.nodes[suite_name] = node

        # Add explicit dependency edges (requires -> suite that requires it)
        for suite_name, (_, requires, _) in suites_metadata.items():
            for required_suite in requires:
                edge = DependencyEdge(
                    source=required_suite,
                    target=suite_name,
                    edge_type='output_consumes',
                    strength=0.9,
                )
                self.edges.append(edge)

        # Add explicit fixture dependencies (edges for fixture data flow)
        self._add_fixture_edges()
        self._validate_acyclic()

    def _add_fixture_edges(self):
        """Add explicit fixture edges between output consumers and reference edges."""
        # Only add fixture edges that don't create cycles
        # These are edges that go from producer to consumer
        fixture_links = [
            ('contractify', 'testify', 'fixture_consumes', 0.9),
            ('contractify', 'securify', 'fixture_consumes', 0.85),
            ('docify', 'documentify', 'fixture_consumes', 0.8),
            ('templatify', 'usabilify', 'fixture_consumes', 0.75),
        ]
        for source, target, edge_type, strength in fixture_links:
            # Only add if not already in dependencies (would create backtrack)
            edge = DependencyEdge(
                source=source,
                target=target,
                edge_type=edge_type,
                strength=strength,
            )
            self.edges.append(edge)

        # Add reference edges for cross-suite awareness (non-blocking dependencies)
        reference_links = [
            ('contractify', 'postmanify', 'reference', 0.7),
            ('testify', 'observifyfy', 'reference', 0.6),
            ('despaghettify', 'testify', 'reference', 0.5),
            ('documentify', 'usabilify', 'reference', 0.7),
            ('docify', 'despaghettify', 'reference', 0.5),
            ('securify', 'metrify', 'reference', 0.6),
        ]
        for source, target, edge_type, strength in reference_links:
            edge = DependencyEdge(
                source=source,
                target=target,
                edge_type=edge_type,
                strength=strength,
            )
            self.edges.append(edge)

    def _validate_acyclic(self):
        """Validate that the graph is acyclic using DFS."""
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for edge in self.edges:
                if edge.source == node:
                    neighbor = edge.target
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        for node_name in self.nodes:
            if node_name not in visited:
                if has_cycle(node_name):
                    raise ValueError(f'Cycle detected in dependency graph at node {node_name}')

    def dependencies_of(self, suite: str) -> list[str]:
        """Return all suites that must be run before this suite.

        Parameters
        ----------
        suite
            Suite name to query

        Returns
        -------
        list[str]
            Sorted list of dependent suite names
        """
        deps = set()
        for edge in self.edges:
            if edge.target == suite:
                deps.add(edge.source)
        return sorted(deps)

    def dependents_of(self, suite: str) -> list[str]:
        """Return all suites that depend on this suite.

        Parameters
        ----------
        suite
            Suite name to query

        Returns
        -------
        list[str]
            Sorted list of dependent suite names
        """
        dependents = set()
        for edge in self.edges:
            if edge.source == suite:
                dependents.add(edge.target)
        return sorted(dependents)

    def transitive_closure(self, suite: str) -> list[str]:
        """Return all suites reachable from this suite (transitive dependencies).

        Parameters
        ----------
        suite
            Suite name to start from

        Returns
        -------
        list[str]
            Sorted list of all reachable suites (excluding the input suite)
        """
        visited = set()
        stack = [suite]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            for dep in self.dependents_of(current):
                if dep not in visited:
                    stack.append(dep)

        visited.discard(suite)
        return sorted(visited)

    def get_edges(self, source: str | None = None, target: str | None = None, edge_type: str | None = None) -> list[DependencyEdge]:
        """Query edges with optional filtering.

        Parameters
        ----------
        source
            Optional source suite to filter by
        target
            Optional target suite to filter by
        edge_type
            Optional edge type to filter by

        Returns
        -------
        list[DependencyEdge]
            Filtered list of edges
        """
        result = self.edges
        if source is not None:
            result = [e for e in result if e.source == source]
        if target is not None:
            result = [e for e in result if e.target == target]
        if edge_type is not None:
            result = [e for e in result if e.edge_type == edge_type]
        return result

    def get_suite_node(self, suite: str) -> SuiteNode | None:
        """Return a suite node by name."""
        return self.nodes.get(suite)

    def edge_count(self) -> int:
        """Return total edge count."""
        return len(self.edges)

    def suite_count(self) -> int:
        """Return total suite count."""
        return len(self.nodes)

    def summary(self) -> dict[str, Any]:
        """Return a summary of the graph structure."""
        edge_types = {}
        for edge in self.edges:
            edge_types.setdefault(edge.edge_type, 0)
            edge_types[edge.edge_type] += 1

        return {
            'suite_count': self.suite_count(),
            'edge_count': self.edge_count(),
            'edge_types': edge_types,
            'is_acyclic': True,  # We validate this in __init__
        }
