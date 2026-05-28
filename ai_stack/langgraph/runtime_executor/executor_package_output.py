"""Output packaging.

Packages the final runtime turn output and returns the public graph result surface.
"""
SOURCE_LINES = [
    '    def _package_output(self, state: RuntimeTurnState) -> RuntimeTurnState:\n',
    '        """``_package_output`` — see implementation for behaviour and contracts.\n',
    '        \n',
    '        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.\n',
    '        \n',
    '        Args:\n',
    '            state: ``state`` (RuntimeTurnState); meaning follows the type and call sites.\n',
    '        \n',
    '        Returns:\n',
    '            RuntimeTurnState:\n',
    '                Returns a value of type ``RuntimeTurnState``; see the function body for structure, error paths, and sentinels.\n',
    '        """\n',
    '        from ai_stack.langgraph.langgraph_runtime_package_output import package_runtime_graph_output\n',
    '\n',
    '        return package_runtime_graph_output(\n',
    '            state, graph_name=self.graph_name, graph_version=self.graph_version\n',
    '        )\n',
]
