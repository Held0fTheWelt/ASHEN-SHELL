#!/usr/bin/env python3
"""
World of Shadows — multi-component test runner.

Runs pytest in each component tree (backend, frontend, administration-tool, world-engine,
Writers-Room, improvement, ai_stack, story_runtime_core) with a separate working directory
per suite (repo root where sibling-package imports are required). Optional scope filters
apply only to the backend suite (pytest markers).

Usage:
    python run_tests.py
    python run_tests.py --suite backend
    python run_tests.py --suite backend --scope contracts
    python run_tests.py --suite all --quick
    python run_tests.py --help
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
TESTS_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = TESTS_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
ADMIN_TOOL_DIR = PROJECT_ROOT / "administration-tool"
WORLD_ENGINE_DIR = PROJECT_ROOT / "world-engine"
REPORTS_DIR = TESTS_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Human-readable titles for each component (English)
SUITE_DISPLAY_NAMES: dict[str, str] = {
    "backend": "Backend (Flask API and services)",
    "frontend": "Frontend (player/public UI)",
    "administration": "Administration tool (proxy and UI)",
    "engine": "World engine (runtime and HTTP/WS)",
    "writers_room": "Writers-Room workflow (human-in-the-loop production)",
    "improvement": "Improvement loop (mutation / evaluation / recommendation)",
    "ai_stack": "WOS AI stack (LangGraph runtime, RAG, Writers-Room / improvement seed graphs)",
    "story_runtime_core": "Story runtime core (shared models, adapters, interpretation contracts)",
}

# Optional backend-only filter: CLI value -> pytest -m marker name
BACKEND_SCOPE_MARKERS: dict[str, str] = {
    "contracts": "contract",
    "integration": "integration",
    "e2e": "e2e",
    "security": "security",
}

# Matches backend/pytest.ini coverage gate when running backend tests
BACKEND_COV_FAIL_UNDER = "85"
FRONTEND_COV_FAIL_UNDER = "92"
DEFAULT_COV_FAIL_UNDER = "80"
# writers_room and improvement suites test only their own modules within the larger app package
# Overall app coverage will be low when these suites run alone (expected—untested modules drag average down)
# Instead, we check that the measured coverage (whatever modules ran) meets a minimal gate
WRITERS_ROOM_COV_FAIL_UNDER = "50"  # Realistic: only 3 modules tested out of ~30+ in app
IMPROVEMENT_COV_FAIL_UNDER = "50"   # Realistic: only 3 modules tested out of ~30+ in app

# Suite -> (pytest cwd, path argument to pytest, relative to cwd)
SUITE_PYTEST_TARGETS: dict[str, tuple[Path, str]] = {
    "backend": (BACKEND_DIR, "tests"),
    "frontend": (FRONTEND_DIR, "tests"),
    "administration": (ADMIN_TOOL_DIR, "tests"),
    "engine": (WORLD_ENGINE_DIR, "tests"),
    "writers_room": (BACKEND_DIR, "tests/writers_room"),
    "improvement": (BACKEND_DIR, "tests/improvement"),
    # Writers-Room / improvement seed graphs and runtime turn graph; imports require repo root on PYTHONPATH.
    "ai_stack": (PROJECT_ROOT, "ai_stack/tests"),
    # Shared-core tests also import the package from repo root.
    "story_runtime_core": (PROJECT_ROOT, "story_runtime_core/tests"),
}


class Colors:
    OKBLUE = "\033[0;34m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    line = "=" * 70
    print(f"{Colors.OKBLUE}{line}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{line}{Colors.ENDC}")


def print_success(text: str) -> None:
    print(f"{Colors.OKGREEN}[OK] {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    print(f"{Colors.FAIL}[FAIL] {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    print(f"{Colors.WARNING}[INFO] {text}{Colors.ENDC}")


def check_environment() -> bool:
    print_header("Environment check")
    try:
        import pytest

        print_success(f"pytest: {pytest.__version__}")
    except ImportError:
        print_error("pytest is not installed. Install dev dependencies (e.g. backend/requirements-dev.txt).")
        return False
    try:
        import coverage

        print_success(f"coverage: {coverage.__version__}")
    except ImportError:
        print_info("coverage not installed (optional).")
    print()
    return True


def _subprocess_env_for_suite(suite_name: str) -> dict[str, str] | None:
    """Suites that import sibling packages from repo root need PROJECT_ROOT on PYTHONPATH."""
    if suite_name not in {"ai_stack", "story_runtime_core", "engine"}:
        return None
    env = dict(os.environ)
    root = str(PROJECT_ROOT)
    sep = os.pathsep
    existing = env.get("PYTHONPATH", "")
    parts = [p for p in existing.split(sep) if p]
    if root not in parts:
        parts.insert(0, root)
    env["PYTHONPATH"] = sep.join(parts)
    return env


def _engine_story_runtime_preflight_message(detail: str) -> str:
    script_hint = "./setup-test-environment.sh"
    if os.name == "nt":
        script_hint = "setup-test-environment.bat"
    return (
        "Engine suite preflight failed before pytest collection.\n"
        "The world-engine story-runtime tests require the heavy story-runtime stack "
        "(langchain, langchain_core, langgraph, fastembed) plus editable local packages "
        "story_runtime_core and ai_stack[test].\n\n"
        f"Detected issue: {detail}\n\n"
        "Use the package-contained setup/bootstrap path from the repository root, then rerun the suite:\n"
        f"  {script_hint}\n"
        "  cd tests && python run_tests.py --suite engine --quick\n\n"
        "If you prefer manual setup, install backend/requirements-test.txt, then:\n"
        '  python -m pip install -e "./story_runtime_core"\n'
        '  python -m pip install -e "./ai_stack[test]"\n'
    )


def _preflight_suite_failure(suite_name: str) -> str | None:
    if suite_name != "engine":
        return None
    env = _subprocess_env_for_suite("engine") or dict(os.environ)
    script = """
import importlib
missing = []
checks = [
    ('langchain', 'langchain'),
    ('langchain_core', 'langchain_core'),
    ('langgraph', 'langgraph'),
    ('fastembed', 'fastembed'),
    ('yaml', 'pyyaml'),
]
for module_name, label in checks:
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        missing.append(label)
if missing:
    raise SystemExit('missing third-party dependencies: ' + ', '.join(missing))
try:
    import ai_stack
    if not getattr(ai_stack, 'LANGGRAPH_RUNTIME_EXPORT_AVAILABLE', False):
        raise SystemExit('ai_stack imported without RuntimeTurnGraphExecutor export; verify ai_stack[test] and story_runtime_core are installed')
    from ai_stack import RuntimeTurnGraphExecutor  # noqa: F401
except ModuleNotFoundError as exc:
    raise SystemExit(f'missing module while importing ai_stack story-runtime exports: {exc.name}')
except ImportError as exc:
    raise SystemExit(str(exc))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=str(WORLD_ENGINE_DIR),
        env=env,
    )
    if result.returncode == 0:
        return None
    detail = (result.stdout or result.stderr or "preflight failed").strip().splitlines()[-1]
    return _engine_story_runtime_preflight_message(detail)


def show_test_stats(suites: dict[str, tuple[Path, str]], preflight_failures: dict[str, str] | None = None) -> None:
    print_header("Test collection (collect-only)")
    preflight_failures = preflight_failures or {}
    for suite_name, (suite_cwd, test_path) in suites.items():
        if suite_name in preflight_failures:
            print_info(f"{suite_name}: collection skipped — preflight failed before pytest startup")
            continue
        test_root = suite_cwd / test_path
        if not (test_root.is_dir() or test_root.is_file()):
            print_info(f"{suite_name}: no tests directory or file ({test_root})")
            continue
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q", test_path],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(suite_cwd),
                env=_subprocess_env_for_suite(suite_name) or os.environ,
            )
            out = (result.stdout or "") + (result.stderr or "")
            collected_line = None
            for line in out.split("\n"):
                if "collected" in line.lower() and any(c.isdigit() for c in line):
                    collected_line = line.strip()
                    break
            if collected_line:
                print_info(f"{suite_name}: {collected_line}")
            else:
                print_info(f"{suite_name}: (could not parse collection output)")
        except Exception as exc:
            print_info(f"{suite_name}: collect-only failed ({exc})")
    print()


def get_suite_configs(suite_names: list[str]) -> dict[str, tuple[Path, str]]:
    all_suites = dict(SUITE_PYTEST_TARGETS)
    if "all" in suite_names:
        return dict(all_suites)
    result: dict[str, tuple[Path, str]] = {}
    for name in suite_names:
        if name in all_suites:
            result[name] = all_suites[name]
        else:
            print_error(f"Unknown suite: {name}")
    return result if result else dict(all_suites)


def _cov_fail_under_for_suite(suite_name: str) -> str:
    if suite_name == "backend":
        return BACKEND_COV_FAIL_UNDER
    if suite_name == "frontend":
        return FRONTEND_COV_FAIL_UNDER
    if suite_name == "writers_room":
        return WRITERS_ROOM_COV_FAIL_UNDER
    if suite_name == "improvement":
        return IMPROVEMENT_COV_FAIL_UNDER
    return DEFAULT_COV_FAIL_UNDER


def _cov_target_for_suite(suite_name: str) -> str:
    """Return coverage target (package/module) for a suite."""
    if suite_name in ("backend", "frontend"):
        return "app"
    if suite_name == "ai_stack":
        return "ai_stack"
    # writers_room and improvement measure app coverage, but only their tests run
    if suite_name == "writers_room":
        return "app"
    if suite_name == "improvement":
        return "app"
    return "."


def build_pytest_argv(
    *,
    suite_name: str,
    test_path: str,
    quick: bool,
    coverage_mode: bool,
    verbose: bool,
    scope: str,
) -> list[str]:
    """Build pytest arguments for one component run (cwd = suite working directory)."""
    cov_target = _cov_target_for_suite(suite_name)
    cov_under = _cov_fail_under_for_suite(suite_name)

    if quick:
        argv = ["-v", "--tb=short", "--no-cov", "-x"]
        if suite_name == "backend" and scope in BACKEND_SCOPE_MARKERS:
            argv.extend(["-m", BACKEND_SCOPE_MARKERS[scope]])
        argv.append(test_path)
        return argv

    if coverage_mode:
        argv = [
            "-v",
            "--tb=short",
            f"--cov={cov_target}",
            "--cov-report=term-missing:skip-covered",
            "--cov-report=html",
            f"--cov-fail-under={cov_under}",
        ]
    elif verbose:
        argv = [
            "-vv",
            "--tb=long",
            "-s",
            f"--cov={cov_target}",
            "--cov-report=term-missing",
            f"--cov-fail-under={cov_under}",
        ]
    else:
        argv = [
            "-v",
            "--tb=short",
            f"--cov={cov_target}",
            "--cov-report=term-missing",
            f"--cov-fail-under={cov_under}",
        ]

    # Backend-only marker filter (optional)
    if suite_name == "backend" and scope in BACKEND_SCOPE_MARKERS:
        marker = BACKEND_SCOPE_MARKERS[scope]
        argv.extend(["-m", marker])

    argv.append(test_path)
    return argv


def run_pytest(
    suite_name: str,
    suite_cwd: Path,
    test_path: str,
    pytest_argv: list[str],
    run_title: str,
) -> bool:
    print_header(run_title)
    tests_dir = suite_cwd / test_path
    if not (tests_dir.is_dir() or tests_dir.is_file()):
        print_error(f"Tests directory or file not found: {tests_dir}")
        return False

    junit_report = REPORTS_DIR / f"pytest_{suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    cmd = [sys.executable, "-m", "pytest", *pytest_argv, f"--junit-xml={junit_report}"]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(suite_cwd),
            env=_subprocess_env_for_suite(suite_name) or os.environ,
        )
        return result.returncode == 0
    except OSError as exc:
        print_error(f"Failed to run pytest: {exc}")
        return False


def run_tests_for_suites(
    suites: dict[str, tuple[Path, str]],
    *,
    quick: bool,
    coverage_mode: bool,
    verbose: bool,
    scope: str,
    preflight_failures: dict[str, str] | None = None,
) -> tuple[bool, dict[str, bool]]:
    all_passed = True
    results: dict[str, bool] = {}
    preflight_failures = preflight_failures or {}

    for suite_name, (suite_cwd, test_path) in suites.items():
        if suite_name in preflight_failures:
            display = SUITE_DISPLAY_NAMES.get(suite_name, suite_name)
            print_header(f"Running: {display} (preflight)")
            print_error(preflight_failures[suite_name])
            results[suite_name] = False
            all_passed = False
            print()
            continue

        display = SUITE_DISPLAY_NAMES.get(suite_name, suite_name)
        if scope in BACKEND_SCOPE_MARKERS:
            if suite_name == "backend":
                marker = BACKEND_SCOPE_MARKERS[scope]
                title = f"{display} — marker '{marker}'"
            else:
                print_info(
                    f"Scope '{scope}' applies only to backend; running full tests for '{suite_name}'."
                )
                title = f"{display} (full)"
        else:
            title = f"{display} (full)"

        argv = build_pytest_argv(
            suite_name=suite_name,
            test_path=test_path,
            quick=quick,
            coverage_mode=coverage_mode,
            verbose=verbose,
            scope=scope if suite_name == "backend" else "all",
        )
        ok = run_pytest(suite_name, suite_cwd, test_path, argv, f"Running: {title}")
        results[suite_name] = ok
        all_passed = all_passed and ok
        if not ok:
            print_error(f"{suite_name} tests failed")
        else:
            print_success(f"{suite_name} tests passed")
        print()

    return all_passed, results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run pytest per suite (backend, frontend, administration-tool, world-engine, "
            "writers-room, improvement, ai_stack, story_runtime_core)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py
  python run_tests.py --suite backend
  python run_tests.py --suite writers_room
  python run_tests.py --suite improvement
  python run_tests.py --suite frontend
  python run_tests.py --suite story_runtime_core
  python run_tests.py --suite backend --scope contracts
  python run_tests.py --suite writers_room improvement --quick
  python run_tests.py --suite ai_stack story_runtime_core --quick
  python run_tests.py --suite all --coverage
        """,
    )
    parser.add_argument(
        "--suite",
        nargs="+",
        default=["all"],
        choices=["backend", "frontend", "administration", "engine", "writers_room", "improvement", "ai_stack", "story_runtime_core", "all"],
        help="Suite to run (default: all)",
    )
    parser.add_argument(
        "--scope",
        default="all",
        choices=["all", "contracts", "integration", "e2e", "security"],
        help=(
            "Backend only: filter tests by pytest marker (contract, integration, e2e, security). "
            "Other components still run their full suite."
        ),
    )
    parser.add_argument("--quick", action="store_true", help="No coverage; stop on first failure")
    parser.add_argument("--coverage", action="store_true", help="Coverage with HTML report")
    parser.add_argument("--verbose", action="store_true", help="Verbose pytest and long tracebacks")

    args = parser.parse_args()

    if not check_environment():
        return 1

    suites = get_suite_configs(args.suite)
    if not suites:
        print_error("No valid suites specified")
        return 1

    preflight_failures = {name: msg for name in suites if (msg := _preflight_suite_failure(name))}

    show_test_stats(suites, preflight_failures)

    all_passed, results = run_tests_for_suites(
        suites,
        quick=args.quick,
        coverage_mode=args.coverage,
        verbose=args.verbose,
        scope=args.scope,
        preflight_failures=preflight_failures,
    )

    print_header("Summary")
    for suite, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        symbol = Colors.OKGREEN if passed else Colors.FAIL
        print(f"{symbol}{status}{Colors.ENDC} - {suite}")

    print()
    if all_passed:
        print_success("All selected suites passed.")
        return 0
    print_error("One or more suites failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
