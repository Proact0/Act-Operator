#!/usr/bin/env python3
"""Test runner with reporting.

This script runs pytest with coverage reporting and generates test reports.
Provides proper exit codes for CI/CD integration.

Usage:
    python run_tests.py
    python run_tests.py --coverage
    python run_tests.py --verbose
    python run_tests.py --path tests/unit_tests
    python run_tests.py --markers "not slow"
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class TestRunner:
    """Runs tests with pytest and generates reports."""

    def __init__(
        self,
        test_path: str = "tests",
        coverage: bool = False,
        verbose: bool = False,
        markers: Optional[str] = None,
        html_report: bool = False,
    ):
        """Initialize the test runner.

        Args:
            test_path: Path to tests directory
            coverage: Enable coverage reporting
            verbose: Enable verbose output
            markers: Pytest marker expression (e.g., "not slow")
            html_report: Generate HTML coverage report
        """
        self.test_path = test_path
        self.coverage = coverage
        self.verbose = verbose
        self.markers = markers
        self.html_report = html_report

    def build_command(self) -> List[str]:
        """Build pytest command with options.

        Returns:
            Command as list of strings
        """
        cmd = ["python", "-m", "pytest", self.test_path]

        # Add verbosity
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")

        # Add coverage
        if self.coverage:
            cmd.extend(
                [
                    "--cov=casts",
                    "--cov-report=term-missing",
                ]
            )
            
            if self.html_report:
                cmd.append("--cov-report=html")

        # Add markers
        if self.markers:
            cmd.extend(["-m", self.markers])

        # Add color output
        cmd.append("--color=yes")

        # Show local variables on failure
        cmd.append("--showlocals")

        return cmd

    def run(self) -> int:
        """Run the tests.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        print(f"\n{Colors.BOLD}Running Tests{Colors.END}\n")
        print(f"{Colors.BLUE}Test Path:{Colors.END} {self.test_path}")

        if self.coverage:
            print(f"{Colors.BLUE}Coverage:{Colors.END} Enabled")
        if self.markers:
            print(f"{Colors.BLUE}Markers:{Colors.END} {self.markers}")

        print()

        # Build command
        cmd = self.build_command()
        
        if self.verbose:
            print(f"{Colors.BLUE}Command:{Colors.END} {' '.join(cmd)}\n")

        # Run tests
        try:
            result = subprocess.run(cmd, check=False)
            exit_code = result.returncode

            # Print summary
            print(f"\n{Colors.BOLD}Test Summary{Colors.END}")
            print("=" * 50)

            if exit_code == 0:
                print(f"{Colors.GREEN}✓ All tests passed{Colors.END}")
            elif exit_code == 1:
                print(f"{Colors.RED}✗ Some tests failed{Colors.END}")
            elif exit_code == 2:
                print(f"{Colors.RED}✗ Test execution was interrupted{Colors.END}")
            elif exit_code == 3:
                print(f"{Colors.RED}✗ Internal error occurred{Colors.END}")
            elif exit_code == 4:
                print(f"{Colors.RED}✗ pytest command line usage error{Colors.END}")
            elif exit_code == 5:
                print(f"{Colors.YELLOW}⚠ No tests were collected{Colors.END}")

            if self.coverage and self.html_report and exit_code in [0, 1]:
                print(
                    f"\n{Colors.GREEN}✓{Colors.END} HTML coverage report: htmlcov/index.html"
                )

            print("=" * 50)

            return exit_code

        except FileNotFoundError:
            print(
                f"{Colors.RED}✗{Colors.END} pytest not found. Install with: pip install pytest"
            )
            return 1
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠{Colors.END} Tests interrupted by user")
            return 130
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Error running tests: {str(e)}")
            return 1


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run tests with pytest and coverage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py
  python run_tests.py --coverage
  python run_tests.py --verbose
  python run_tests.py --path tests/unit_tests
  python run_tests.py --markers "not slow"
  python run_tests.py --coverage --html-report

Marker Examples:
  -m "not slow"              # Skip slow tests
  -m "integration"           # Only integration tests
  -m "unit and not slow"     # Unit tests that aren't slow
        """,
    )
    parser.add_argument(
        "-p",
        "--path",
        default="tests",
        help="Path to tests directory (default: tests)",
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Enable coverage reporting"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-m", "--markers", help="Pytest marker expression (e.g., 'not slow')"
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML coverage report (requires --coverage)",
    )

    args = parser.parse_args()

    runner = TestRunner(
        test_path=args.path,
        coverage=args.coverage,
        verbose=args.verbose,
        markers=args.markers,
        html_report=args.html_report,
    )

    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
