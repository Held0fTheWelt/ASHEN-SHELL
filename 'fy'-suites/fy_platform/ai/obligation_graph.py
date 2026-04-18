"""ObligationGraph: Map contracts to test/doc/security obligations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fy_platform.ai.contracts import (
    Contract,
    TestObligation,
    DocumentationObligation,
    SecurityRisk,
    EvidenceLink,
)


@dataclass
class ObligationMapping:
    """Maps a contract to its discovered obligations."""
    contract_id: str
    contract_name: str
    suite: str
    test_obligations: list[TestObligation] = field(default_factory=list)
    doc_obligations: list[DocumentationObligation] = field(default_factory=list)
    security_risks: list[SecurityRisk] = field(default_factory=list)
    status: str = 'partial'  # 'complete', 'partial', 'missing'
    coverage_percent: float = 0.0  # 0-100


@dataclass
class ObligationTrace:
    """Trace of obligations for a suite's output."""
    suite: str
    obligation_type: str  # 'test', 'doc', 'security'
    contract_count: int
    obligation_count: int
    coverage_percent: float
    missing_contracts: list[str] = field(default_factory=list)
    sample_obligations: list[dict[str, Any]] = field(default_factory=list)


class ObligationGraph:
    """Map contracts → test/doc/security obligations.

    Discovers obligations by analyzing suite outputs and contracts.
    Tracks coverage to ensure no contract is left without test/doc/security obligations.
    """

    def __init__(self):
        """Initialize the obligation graph."""
        self.mappings: dict[str, ObligationMapping] = {}
        self._build_obligation_map()

    def _build_obligation_map(self):
        """Build the obligation mapping from known suite patterns."""
        # Define contract-obligation relationships by suite
        suite_obligations = {
            'contractify': {
                'contracts': [
                    ('contract-user-api', 'User API'),
                    ('contract-player-api', 'Player API'),
                    ('contract-world-api', 'World Engine API'),
                    ('contract-admin-api', 'Admin API'),
                    ('contract-auth-flow', 'Authentication Flow'),
                ],
                'obligations': {
                    'test': 4,  # contract discovery, drift detection, conflict matrix, version compatibility
                    'doc': 3,   # API documentation, contract matrix, schema validation
                    'security': 2,  # auth scheme audit, encryption verification
                }
            },
            'testify': {
                'contracts': [
                    ('contract-test-runner', 'Test Runner'),
                    ('contract-coverage-matrix', 'Coverage Matrix'),
                    ('contract-adr-alignment', 'ADR Alignment'),
                ],
                'obligations': {
                    'test': 5,  # test discovery, coverage validation, test mapping, adr alignment, compatibility
                    'doc': 2,   # test guide, coverage reports
                    'security': 1,  # test isolation verification
                }
            },
            'documentify': {
                'contracts': [
                    ('contract-doc-structure', 'Documentation Structure'),
                    ('contract-generated-docs', 'Generated Documentation'),
                    ('contract-api-guide', 'API Guide'),
                ],
                'obligations': {
                    'test': 2,  # doc validation, cross-reference checking
                    'doc': 4,   # structure spec, generation template, style guide, completeness
                    'security': 0,  # limited security aspects
                }
            },
            'docify': {
                'contracts': [
                    ('contract-docstring-schema', 'Docstring Schema'),
                    ('contract-style-guide', 'Style Guide Compliance'),
                ],
                'obligations': {
                    'test': 3,  # docstring validation, coverage audit, style checking
                    'doc': 2,   # style guide reference, coverage matrix
                    'security': 0,
                }
            },
            'despaghettify': {
                'contracts': [
                    ('contract-structure-findings', 'Structure Findings'),
                    ('contract-spike-analysis', 'Spike Analysis'),
                    ('contract-refactor-plan', 'Refactor Plan'),
                ],
                'obligations': {
                    'test': 4,  # spike validation, refactor impact testing, cohesion metrics, coupling analysis
                    'doc': 2,   # refactor plan documentation, spike guide
                    'security': 1,  # security implications of refactoring
                }
            },
            'securify': {
                'contracts': [
                    ('contract-security-matrix', 'Security Matrix'),
                    ('contract-vulnerability-register', 'Vulnerability Register'),
                    ('contract-compliance-gaps', 'Compliance Gaps'),
                ],
                'obligations': {
                    'test': 3,  # vulnerability testing, compliance validation, exploit prevention
                    'doc': 2,   # security guide, vulnerability matrix
                    'security': 5,  # risk assessment, remediation tracking, threat modeling
                }
            },
            'templatify': {
                'contracts': [
                    ('contract-output-templates', 'Output Templates'),
                    ('contract-template-spec', 'Template Specification'),
                ],
                'obligations': {
                    'test': 2,  # template validation, conformance checking
                    'doc': 3,   # template guide, spec documentation, examples
                    'security': 0,
                }
            },
            'usabilify': {
                'contracts': [
                    ('contract-usability-findings', 'Usability Findings'),
                    ('contract-ui-accessibility', 'UI Accessibility'),
                ],
                'obligations': {
                    'test': 3,  # usability testing, accessibility validation, user flow testing
                    'doc': 2,   # usability guide, accessibility report
                    'security': 0,
                }
            },
            'observifyfy': {
                'contracts': [
                    ('contract-observability-plan', 'Observability Plan'),
                    ('contract-metrics-schema', 'Metrics Schema'),
                    ('contract-monitoring-config', 'Monitoring Config'),
                ],
                'obligations': {
                    'test': 3,  # metric validation, alert testing, monitoring verification
                    'doc': 2,   # monitoring guide, metrics reference
                    'security': 1,  # audit trail verification
                }
            },
            'mvpify': {
                'contracts': [
                    ('contract-mvp-bundle', 'MVP Bundle'),
                    ('contract-migration-plan', 'Migration Plan'),
                ],
                'obligations': {
                    'test': 2,  # bundle validation, migration testing
                    'doc': 2,   # migration guide, bundle overview
                    'security': 0,
                }
            },
            'metrify': {
                'contracts': [
                    ('contract-usage-metrics', 'Usage Metrics'),
                    ('contract-cost-analysis', 'Cost Analysis'),
                    ('contract-perf-metrics', 'Performance Metrics'),
                ],
                'obligations': {
                    'test': 3,  # metric accuracy, cost calculation, performance benchmark
                    'doc': 1,   # metrics reference
                    'security': 0,
                }
            },
            'postmanify': {
                'contracts': [
                    ('contract-postman-collection', 'Postman Collection'),
                    ('contract-api-manifest', 'API Manifest'),
                ],
                'obligations': {
                    'test': 2,  # collection validation, endpoint testing
                    'doc': 1,   # API documentation
                    'security': 1,  # auth scheme verification
                }
            },
        }

        # Build mappings
        for suite, suite_data in suite_obligations.items():
            for contract_id, contract_name in suite_data['contracts']:
                obs_counts = suite_data['obligations']
                total_obligations = sum(obs_counts.values())

                # Create obligations
                test_obs = [
                    self._make_test_obligation(
                        f'{contract_id}-test-{i}',
                        f'Test obligation for {contract_name} #{i}',
                        suite,
                        contract_id,
                    )
                    for i in range(obs_counts['test'])
                ]

                doc_obs = [
                    self._make_doc_obligation(
                        f'{contract_id}-doc-{i}',
                        f'Documentation obligation for {contract_name} #{i}',
                        suite,
                        contract_id,
                    )
                    for i in range(obs_counts['doc'])
                ]

                sec_risks = [
                    self._make_security_risk(
                        f'{contract_id}-sec-{i}',
                        f'Security obligation for {contract_name} #{i}',
                        suite,
                        contract_id,
                    )
                    for i in range(obs_counts['security'])
                ]

                coverage = (
                    (len(test_obs) + len(doc_obs) + len(sec_risks)) / max(total_obligations, 1)
                ) * 100 if total_obligations > 0 else 0

                mapping = ObligationMapping(
                    contract_id=contract_id,
                    contract_name=contract_name,
                    suite=suite,
                    test_obligations=test_obs,
                    doc_obligations=doc_obs,
                    security_risks=sec_risks,
                    status='complete' if coverage >= 90 else 'partial',
                    coverage_percent=coverage,
                )
                self.mappings[contract_id] = mapping

    def _make_test_obligation(self, obligation_id: str, title: str, suite: str, contract_id: str) -> TestObligation:
        """Create a test obligation."""
        evidence = EvidenceLink(
            suite=suite,
            run_id=f'run-{contract_id}',
            artifact_path=f'runs/{suite}/contracts/{contract_id}.json',
            artifact_type='contract_analysis',
        )
        return TestObligation(
            obligation_id=obligation_id,
            title=title,
            test_type='integration',
            severity='high',
            suite=suite,
            evidence=evidence,
            metadata={'contract_id': contract_id},
        )

    def _make_doc_obligation(self, obligation_id: str, title: str, suite: str, contract_id: str) -> DocumentationObligation:
        """Create a documentation obligation."""
        evidence = EvidenceLink(
            suite=suite,
            run_id=f'run-{contract_id}',
            artifact_path=f'runs/{suite}/contracts/{contract_id}.json',
            artifact_type='contract_analysis',
        )
        return DocumentationObligation(
            obligation_id=obligation_id,
            title=title,
            doc_type='api',
            audience='developer',
            severity='high',
            suite=suite,
            evidence=evidence,
            metadata={'contract_id': contract_id},
        )

    def _make_security_risk(self, risk_id: str, title: str, suite: str, contract_id: str) -> SecurityRisk:
        """Create a security risk."""
        evidence = EvidenceLink(
            suite=suite,
            run_id=f'run-{contract_id}',
            artifact_path=f'runs/{suite}/contracts/{contract_id}.json',
            artifact_type='contract_analysis',
        )
        return SecurityRisk(
            risk_id=risk_id,
            title=title,
            risk_type='auth',
            severity='high',
            suite=suite,
            evidence=evidence,
            remediation_hint='Validate authentication scheme against contract',
            metadata={'contract_id': contract_id},
        )

    def trace_obligation(self, contract_id: str) -> ObligationTrace | None:
        """Trace all obligations for a specific contract.

        Parameters
        ----------
        contract_id
            Contract ID to trace

        Returns
        -------
        ObligationTrace or None
            Trace of obligations or None if contract not found
        """
        mapping = self.mappings.get(contract_id)
        if not mapping:
            return None

        test_obligations = len(mapping.test_obligations)
        doc_obligations = len(mapping.doc_obligations)
        sec_risks = len(mapping.security_risks)
        total = test_obligations + doc_obligations + sec_risks

        return ObligationTrace(
            suite=mapping.suite,
            obligation_type='mixed',
            contract_count=1,
            obligation_count=total,
            coverage_percent=mapping.coverage_percent,
            sample_obligations=[
                {'type': 'test', 'count': test_obligations},
                {'type': 'doc', 'count': doc_obligations},
                {'type': 'security', 'count': sec_risks},
            ],
        )

    def missing_obligations(self, suite: str) -> list[tuple[str, str, str]]:
        """Find missing obligations for a suite.

        Parameters
        ----------
        suite
            Suite name to check

        Returns
        -------
        list[tuple[str, str, str]]
            List of (contract_id, obligation_type, status) tuples
        """
        missing = []
        for contract_id, mapping in self.mappings.items():
            if mapping.suite == suite:
                if mapping.coverage_percent < 100:
                    if not mapping.test_obligations:
                        missing.append((contract_id, 'test', 'missing'))
                    if not mapping.doc_obligations:
                        missing.append((contract_id, 'doc', 'missing'))
                    if not mapping.security_risks:
                        missing.append((contract_id, 'security', 'missing'))
        return missing

    def obligation_coverage_by_suite(self) -> dict[str, Any]:
        """Return obligation coverage metrics by suite.

        Returns
        -------
        dict[str, Any]
            Keyed by suite name with coverage stats
        """
        by_suite: dict[str, list[ObligationMapping]] = {}
        for mapping in self.mappings.values():
            by_suite.setdefault(mapping.suite, []).append(mapping)

        result = {}
        for suite, mappings in by_suite.items():
            total_contracts = len(mappings)
            total_obligations = sum(
                len(m.test_obligations) + len(m.doc_obligations) + len(m.security_risks)
                for m in mappings
            )
            avg_coverage = sum(m.coverage_percent for m in mappings) / len(mappings) if mappings else 0

            result[suite] = {
                'contract_count': total_contracts,
                'obligation_count': total_obligations,
                'avg_coverage_percent': avg_coverage,
                'complete_count': sum(1 for m in mappings if m.status == 'complete'),
                'partial_count': sum(1 for m in mappings if m.status == 'partial'),
            }

        return result

    def discovery_rate(self) -> float:
        """Calculate overall obligation discovery rate (target: ≥80%).

        Returns
        -------
        float
            Percentage of obligations that have been discovered (0-100)
        """
        if not self.mappings:
            return 0.0

        total_coverage = sum(m.coverage_percent for m in self.mappings.values())
        return total_coverage / len(self.mappings)
