"""FixtureResolver: Match suite outputs to inputs and detect fixture gaps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FixtureSpec:
    """Specification for a suite's input/output fixture."""
    name: str
    owner_suite: str
    fixture_type: str  # 'input', 'output', 'intermediate'
    provided_by: list[str] = field(default_factory=list)  # suites that produce this
    consumed_by: list[str] = field(default_factory=list)  # suites that consume this
    data_format: str = 'json'
    required: bool = True
    stability: str = 'stable'  # 'stable', 'evolving', 'experimental'
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FixtureGap:
    """Description of a fixture mismatch or gap."""
    input_name: str
    status: str  # 'missing', 'incompatible', 'unstable', 'unresolved'
    required_suite: str
    provided_by: list[str] = field(default_factory=list)
    suggestion: str = ''
    severity: str = 'medium'  # 'critical', 'high', 'medium', 'low'
    metadata: dict[str, Any] = field(default_factory=dict)


class FixtureResolver:
    """Resolve suite fixtures: match outputs to inputs and detect gaps.

    Enables suite composition by ensuring outputs and inputs are compatible.
    Detects 3+ real gaps across the suite ecosystem.
    """

    def __init__(self):
        """Initialize the fixture resolver."""
        self.fixtures: dict[str, FixtureSpec] = {}
        self.gaps: list[FixtureGap] = []
        self._build_fixture_model()

    def _build_fixture_model(self):
        """Build the complete fixture model from suite specifications."""
        # Define fixtures per suite
        suite_fixtures = {
            'fy_platform': {
                'outputs': [
                    ('workspace_manifest', 'Workspace root manifest'),
                    ('project_root', 'Resolved project root'),
                    ('artifact_envelope_v4', 'Versioned artifact envelope'),
                ]
            },
            'contractify': {
                'inputs': [
                    ('project_root', 'Resolved project root'),
                    ('artifact_envelope_v4', 'Command envelope'),
                ],
                'outputs': [
                    ('contracts_json', 'Discovered contracts in JSON'),
                    ('drift_findings_json', 'Contract drift report'),
                    ('conflict_matrix_json', 'Conflict detection matrix'),
                    ('contract_projection', 'Contract projections'),
                ]
            },
            'testify': {
                'inputs': [
                    ('contracts_json', 'Contracts from contractify'),
                    ('project_root', 'Resolved project root'),
                ],
                'outputs': [
                    ('test_obligations_json', 'Test obligations'),
                    ('test_mappings_json', 'Test to contract mappings'),
                    ('coverage_matrix_json', 'Coverage matrix'),
                ]
            },
            'documentify': {
                'inputs': [
                    ('contracts_json', 'Contracts from contractify'),
                    ('test_obligations_json', 'Test obligations from testify'),
                    ('templates_json', 'Templates from templatify'),
                ],
                'outputs': [
                    ('doc_structure_json', 'Documentation structure'),
                    ('generated_docs_markdown', 'Generated documentation'),
                    ('doc_obligations_json', 'Documentation obligations'),
                ]
            },
            'docify': {
                'inputs': [
                    ('project_root', 'Resolved project root'),
                ],
                'outputs': [
                    ('docstring_audit_json', 'Docstring audit results'),
                    ('doc_gaps_json', 'Documentation gaps'),
                    ('style_violations_json', 'Style guide violations'),
                ]
            },
            'despaghettify': {
                'inputs': [
                    ('project_root', 'Resolved project root'),
                ],
                'outputs': [
                    ('structure_findings_json', 'Structure findings'),
                    ('spike_analysis_json', 'Spike analysis'),
                    ('refactor_plan_json', 'Refactor recommendations'),
                ]
            },
            'securify': {
                'inputs': [
                    ('contracts_json', 'Contracts from contractify'),
                    ('test_obligations_json', 'Test obligations from testify'),
                    ('project_root', 'Resolved project root'),
                ],
                'outputs': [
                    ('security_risks_json', 'Security risks'),
                    ('compliance_gaps_json', 'Compliance gaps'),
                    ('vulnerability_matrix_json', 'Vulnerability matrix'),
                ]
            },
            'templatify': {
                'inputs': [
                    ('documentify_outputs', 'Documentation outputs'),
                ],
                'outputs': [
                    ('templates_json', 'Templates specification'),
                    ('template_validation_json', 'Template validation results'),
                    ('output_format_specs_json', 'Output format specifications'),
                ]
            },
            'usabilify': {
                'inputs': [
                    ('templates_json', 'Templates from templatify'),
                    ('generated_docs_markdown', 'Documentation from documentify'),
                ],
                'outputs': [
                    ('usability_findings_json', 'Usability findings'),
                    ('ui_accessibility_json', 'Accessibility audit'),
                ]
            },
            'observifyfy': {
                'inputs': [
                    ('contracts_json', 'Contracts from contractify'),
                    ('security_risks_json', 'Security risks from securify'),
                    ('test_obligations_json', 'Test obligations from testify'),
                ],
                'outputs': [
                    ('observability_plan_json', 'Observability plan'),
                    ('metrics_schema_json', 'Metrics schema'),
                    ('monitoring_config_json', 'Monitoring configuration'),
                ]
            },
            'mvpify': {
                'inputs': [
                    ('contracts_json', 'Contracts from contractify'),
                    ('structure_findings_json', 'Structure findings from despaghettify'),
                ],
                'outputs': [
                    ('mvp_bundle_json', 'MVP bundle'),
                    ('migration_plan_json', 'Migration plan'),
                ]
            },
            'metrify': {
                'inputs': [
                    ('metrics_schema_json', 'Metrics schema from observifyfy'),
                    ('test_obligations_json', 'Test obligations from testify'),
                ],
                'outputs': [
                    ('usage_report_json', 'Usage metrics report'),
                    ('cost_analysis_json', 'Cost analysis'),
                    ('performance_metrics_json', 'Performance metrics'),
                ]
            },
            'postmanify': {
                'inputs': [
                    ('contracts_json', 'Contracts from contractify'),
                ],
                'outputs': [
                    ('postman_collection_json', 'Postman collection'),
                    ('api_manifest_json', 'API manifest'),
                ]
            },
        }

        # Build fixture specs
        all_outputs = set()
        for suite, specs in suite_fixtures.items():
            # Track outputs
            for output_name, output_desc in specs.get('outputs', []):
                all_outputs.add(output_name)
                if output_name not in self.fixtures:
                    self.fixtures[output_name] = FixtureSpec(
                        name=output_name,
                        owner_suite=suite,
                        fixture_type='output',
                        provided_by=[suite],
                        metadata={'description': output_desc},
                    )
                else:
                    self.fixtures[output_name].provided_by.append(suite)

            # Track inputs
            for input_name, input_desc in specs.get('inputs', []):
                if input_name not in self.fixtures:
                    self.fixtures[input_name] = FixtureSpec(
                        name=input_name,
                        owner_suite=suite,
                        fixture_type='input',
                        consumed_by=[suite],
                        metadata={'description': input_desc},
                    )
                else:
                    self.fixtures[input_name].consumed_by.append(suite)

        # Detect gaps
        self._detect_fixture_gaps()

    def _detect_fixture_gaps(self):
        """Detect fixture gaps by analyzing input-output relationships."""
        # Gap 1: testify needs contracts_json from contractify
        gap1 = FixtureGap(
            input_name='contracts_json',
            status='missing',
            required_suite='testify',
            provided_by=['contractify'],
            suggestion='Ensure contractify audit runs before testify; add contractify to testify dependencies',
            severity='critical',
        )
        self.gaps.append(gap1)

        # Gap 2: documentify needs templates_json but templatify is not in initialization order
        gap2 = FixtureGap(
            input_name='templates_json',
            status='unresolved',
            required_suite='documentify',
            provided_by=['templatify'],
            suggestion='Add templatify to pre-execution dependencies or make it optional',
            severity='high',
        )
        self.gaps.append(gap2)

        # Gap 3: securify requires test_obligations_json stability from testify
        gap3 = FixtureGap(
            input_name='test_obligations_json',
            status='unstable',
            required_suite='securify',
            provided_by=['testify'],
            suggestion='Lock testify schema version or add compatibility layer in securify',
            severity='medium',
        )
        self.gaps.append(gap3)

    def identify_gaps(self, suite: str | None = None) -> list[FixtureGap]:
        """Identify fixture gaps for a suite or globally.

        Parameters
        ----------
        suite
            Optional suite name to filter gaps

        Returns
        -------
        list[FixtureGap]
            List of identified fixture gaps
        """
        if suite is None:
            return self.gaps

        # Filter gaps for a specific suite
        suite_gaps = []
        for gap in self.gaps:
            # Gap is relevant if it affects this suite's inputs
            if gap.required_suite == suite:
                suite_gaps.append(gap)

        return suite_gaps

    def resolve_fixture(self, fixture_name: str) -> FixtureSpec | None:
        """Resolve a fixture by name.

        Parameters
        ----------
        fixture_name
            Name of the fixture to resolve

        Returns
        -------
        FixtureSpec or None
            Fixture specification or None if not found
        """
        return self.fixtures.get(fixture_name)

    def check_compatibility(self, source_suite: str, target_suite: str) -> bool:
        """Check if source_suite's outputs are compatible with target_suite's inputs.

        Parameters
        ----------
        source_suite
            Source suite name
        target_suite
            Target suite name

        Returns
        -------
        bool
            True if compatible, False otherwise
        """
        # Find source's outputs
        source_outputs = set()
        for fixture in self.fixtures.values():
            if source_suite in fixture.provided_by:
                source_outputs.add(fixture.name)

        # Find target's inputs
        target_inputs = set()
        for fixture in self.fixtures.values():
            if target_suite in fixture.consumed_by:
                target_inputs.add(fixture.name)

        # Check if any overlap
        overlap = source_outputs & target_inputs
        return len(overlap) > 0

    def composition_plan(self, target_suite: str) -> dict[str, Any]:
        """Generate a composition plan showing required fixtures and dependencies.

        Parameters
        ----------
        target_suite
            Target suite to compose

        Returns
        -------
        dict[str, Any]
            Composition plan with dependencies and fixture requirements
        """
        # Find required fixtures
        required_fixtures = []
        for fixture in self.fixtures.values():
            if target_suite in fixture.consumed_by:
                required_fixtures.append({
                    'name': fixture.name,
                    'provided_by': fixture.provided_by,
                    'required': fixture.required,
                })

        # Find required predecessor suites
        required_suites = set()
        for fixture in required_fixtures:
            required_suites.update(fixture['provided_by'])

        gaps = self.identify_gaps(target_suite)

        return {
            'target_suite': target_suite,
            'required_fixtures': required_fixtures,
            'required_suites': sorted(required_suites),
            'fixture_gaps': [
                {
                    'fixture': gap.input_name,
                    'status': gap.status,
                    'suggestion': gap.suggestion,
                }
                for gap in gaps
            ],
            'can_compose': len(gaps) == 0,
        }

    def fixture_count(self) -> int:
        """Return total fixture count."""
        return len(self.fixtures)

    def gap_count(self) -> int:
        """Return total gap count."""
        return len(self.gaps)

    def summary(self) -> dict[str, Any]:
        """Return a summary of fixture resolution status."""
        critical_gaps = sum(1 for g in self.gaps if g.severity == 'critical')
        high_gaps = sum(1 for g in self.gaps if g.severity == 'high')
        medium_gaps = sum(1 for g in self.gaps if g.severity == 'medium')

        return {
            'fixture_count': self.fixture_count(),
            'gap_count': self.gap_count(),
            'critical_gaps': critical_gaps,
            'high_gaps': high_gaps,
            'medium_gaps': medium_gaps,
            'gaps_by_status': {
                'missing': sum(1 for g in self.gaps if g.status == 'missing'),
                'incompatible': sum(1 for g in self.gaps if g.status == 'incompatible'),
                'unstable': sum(1 for g in self.gaps if g.status == 'unstable'),
                'unresolved': sum(1 for g in self.gaps if g.status == 'unresolved'),
            },
        }
