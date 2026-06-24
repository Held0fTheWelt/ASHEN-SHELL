"""Compatibility import for the AI-stack language I/O adapter.

.. deprecated::
    Import from ``ai_stack.language_io.language_adapter`` (or ``ai_stack.language_io``)
    in new code. This module is a narrow re-export shim for the W5 migration window.

The implementation lives in ``ai_stack.language_io.language_adapter``. Importing this
module requires ``ai_stack`` on ``PYTHONPATH`` (optional ``[language]`` extra in
``pyproject.toml`` documents that runtime peer dependency).
"""

from ai_stack.language_io.language_adapter import *  # noqa: F401,F403
