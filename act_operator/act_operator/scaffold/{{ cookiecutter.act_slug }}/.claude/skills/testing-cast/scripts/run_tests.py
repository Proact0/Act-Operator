#!/usr/bin/env python3
"""Enhanced pytest runner with common options."""

import sys
import subprocess
from pathlib import Path


def run_tests(args):
    """Run pytest with enhanced options."""
    pytest_args = ["pytest"]

    # Add coverage by default if not explicitly disabled
    if "--no-cov" not in args:
        pytest_args.extend([
            "--cov=casts",
            "--cov-report=term-missing",
            "--cov-report=html",
        ])
        # Remove --no-cov if present
        args = [a for a in args if a != "--no-cov"]

    # Add color output
    pytest_args.append("--color=yes")

    # Add verbosity if requested
    if "-v" in args or "--verbose" in args:
        pytest_args.append("-v")

    # Add remaining args
    pytest_args.extend(args[1:])

    # Run pytest
    result = subprocess.run(pytest_args)
    return result.returncode


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("""Enhanced pytest runner for Act projects.

Usage:
  python run_tests.py [options] [paths]

Common options:
  -v, --verbose           Verbose output
  -k EXPRESSION          Run tests matching expression
  -m MARKER              Run tests with marker
  --no-cov               Disable coverage
  -x, --exitfirst        Exit on first failure
  --pdb                  Drop into debugger on failure
  --lf, --last-failed    Run only last failed tests
  --ff, --failed-first   Run failed tests first
  --sw, --stepwise       Run tests until one fails, then continue from there

Examples:
  python run_tests.py                          # Run all tests with coverage
  python run_tests.py tests/test_nodes.py      # Run specific file
  python run_tests.py -k test_my_function      # Run tests matching name
  python run_tests.py -m "not slow"            # Skip slow tests
  python run_tests.py --no-cov -v              # No coverage, verbose
  python run_tests.py --lf                     # Run last failed
""")
        sys.exit(0)

    returncode = run_tests(sys.argv)
    sys.exit(returncode)


if __name__ == "__main__":
    main()
