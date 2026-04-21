import pytest
from wos_mvp.testability import RuntimeBuilder
from wos_mvp.runtime_profiles import accept_degraded_safe


def test_non_graph_seam_executes_without_graph_factory():
    builder = RuntimeBuilder()
    assert builder.build_non_graph_seam() == "non_graph_ready"


def test_graph_seam_requires_explicit_factory():
    builder = RuntimeBuilder()
    with pytest.raises(RuntimeError):
        builder.build_graph_seam()


def test_degraded_safe_stays_explicit():
    outcome = accept_degraded_safe()
    assert outcome.code == "ACCEPT_DEGRADED_SAFE"
    assert outcome.player_safe_status == "committed_degraded_safe"
