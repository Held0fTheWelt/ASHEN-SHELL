"""Better Tomorrow architecture assurance.

This package is deliberately owned by Better Tomorrow.  It implements the
same binding, representation, view-depth, and drift semantics as the TTD
architecture-depth standard without importing code from the TTD repository.
"""

from .audit import build_report, evaluate_gate

__all__ = ["build_report", "evaluate_gate"]
