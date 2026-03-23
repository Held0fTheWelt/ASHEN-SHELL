#!/usr/bin/env python3
"""
World of Shadows — Complete Test Suite Runner (Python)

Cross-platform test runner with multiple modes and detailed reporting.

Usage:
    python run_tests.py                # Full suite with coverage (default)
    python run_tests.py --quick        # Fast tests only
    python run_tests.py --coverage     # Detailed coverage report
    python run_tests.py --api          # API tests only
    python run_tests.py --security     # Security tests only
    python run_tests.py --verbose      # Full debug output
    python run_tests.py --help         # Show this help
"""

import sys
import subprocess
import os
from pathlib import Path
import argparse
from datetime import datetime

# Setup
BACKEND_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = BACKEND_DIR.parent
TEST_DIR = BACKEND_DIR / "tests"
COVERAGE_DIR = BACKEND_DIR / "htmlcov"

# ANSI colors
class Colors:
    HEADER = '\033[94m'
    OKBLUE = '\033[0;34m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    line = "━" * 70
    print(f"{Colors.OKBLUE}{line}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{line}{Colors.ENDC}")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print an info message."""
    print(f"{Colors.WARNING}ℹ {text}{Colors.ENDC}")

def check_environment():
    """Verify test environment is ready."""
    print_header("Environment Check")

    try:
        import pytest
        print_success(f"pytest: {pytest.__version__}")
    except ImportError:
        print_error("pytest not installed. Run: pip install -r requirements-dev.txt")
        return False

    try:
        import coverage
        print_success(f"coverage: {coverage.__version__}")
    except ImportError:
        print_info("coverage not installed (optional). Run: pip install coverage")

    print()
    return True

def show_test_stats():
    """Display test discovery statistics."""
    print_header("Test Suite Statistics")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", str(TEST_DIR)],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        # Extract test count from last line
        for line in output.split('\n'):
            if 'test' in line.lower() and any(c.isdigit() for c in line):
                print_info(f"Tests discovered: {line.strip()}")
                break
    except Exception as e:
        print_info(f"Could not get test count: {e}")

    test_files = len(list(TEST_DIR.glob("test_*.py")))
    print_info(f"Test files: {test_files}")
    print()

def run_pytest(args, description):
    """Run pytest with given arguments."""
    print_header(description)

    cmd = [sys.executable, "-m", "pytest"] + args

    try:
        result = subprocess.run(cmd, cwd=str(BACKEND_DIR))
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def run_full_tests():
    """Run full test suite with coverage."""
    args = [
        "-v", "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=85",
        str(TEST_DIR)
    ]

    success = run_pytest(args, "Running Full Test Suite with Coverage")

    if success:
        print_success("All tests passed!")
        print_info(f"Coverage report: {COVERAGE_DIR}/index.html")
    else:
        print_error("Tests failed")

    return success

def run_quick_tests():
    """Run quick test suite without coverage."""
    args = [
        "-v", "--tb=short",
        "--no-cov",
        "-x",  # Stop on first failure
        str(TEST_DIR)
    ]

    success = run_pytest(args, "Running Quick Test Suite (no coverage)")

    if success:
        print_success("Quick tests passed!")
    else:
        print_error("Tests failed")

    return success

def run_coverage_tests():
    """Run with detailed coverage reporting."""
    args = [
        "-v", "--tb=short",
        "--cov=app",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=html",
        "--cov-report=json",
        "--cov-fail-under=85",
        str(TEST_DIR)
    ]

    success = run_pytest(args, "Running Full Test Suite with Detailed Coverage")

    if success:
        print_success("All tests passed with coverage!")
        print_info(f"Coverage report: {COVERAGE_DIR}/index.html")
    else:
        print_error("Tests failed")

    return success

def run_api_tests():
    """Run API tests only."""
    args = [
        "-v", "--tb=short",
        "--no-cov",
        "-k", "api",
        str(TEST_DIR)
    ]

    success = run_pytest(args, "Running API Tests")

    if success:
        print_success("API tests passed!")
    else:
        print_error("API tests failed")

    return success

def run_security_tests():
    """Run security-related tests."""
    args = [
        "-v", "--tb=short",
        "--no-cov",
        "-k", "security or csrf or auth or injection or xss or privilege",
        str(TEST_DIR)
    ]

    success = run_pytest(args, "Running Security Tests")

    if success:
        print_success("Security tests passed!")
    else:
        print_error("Security tests failed")

    return success

def run_verbose_tests():
    """Run with full debug output."""
    args = [
        "-vv", "--tb=long",
        "-s",  # No capture
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-fail-under=85",
        str(TEST_DIR)
    ]

    success = run_pytest(args, "Running Full Test Suite (Verbose with Debug Output)")

    if success:
        print_success("All tests passed!")
    else:
        print_error("Tests failed")

    return success

def main():
    parser = argparse.ArgumentParser(
        description="World of Shadows — Complete Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py              # Full suite with coverage
  python run_tests.py --quick      # Fast tests only
  python run_tests.py --coverage   # Detailed coverage
  python run_tests.py --security   # Security tests only
        """
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests without coverage"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with detailed coverage report"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run API tests only"
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security tests only"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run with full debug output"
    )

    args = parser.parse_args()

    # Check environment
    if not check_environment():
        return 1

    # Show stats
    show_test_stats()

    # Run tests based on mode
    if args.quick:
        success = run_quick_tests()
    elif args.coverage:
        success = run_coverage_tests()
    elif args.api:
        success = run_api_tests()
    elif args.security:
        success = run_security_tests()
    elif args.verbose:
        success = run_verbose_tests()
    else:
        success = run_full_tests()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
