#!/usr/bin/env python3
"""Validate distributed architecture specification for completeness.

Usage:
    python scripts/validate_architecture.py

Validates that the distributed architecture specification (root CLAUDE.md + cast CLAUDE.md files) is complete and consistent.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of validation check."""

    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    """Complete validation report."""

    results: list[ValidationResult] = field(default_factory=list)

    def add(self, passed: bool, message: str, severity: str = "error"):
        """Add a validation result."""
        self.results.append(ValidationResult(passed, message, severity))

    @property
    def errors(self) -> list[ValidationResult]:
        """Get all errors."""
        return [r for r in self.results if not r.passed and r.severity == "error"]

    @property
    def warnings(self) -> list[ValidationResult]:
        """Get all warnings."""
        return [r for r in self.results if not r.passed and r.severity == "warning"]

    @property
    def passed(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    def print_report(self):
        """Print formatted report."""
        print("\n" + "=" * 60)
        print("ARCHITECTURE VALIDATION REPORT")
        print("=" * 60 + "\n")

        # Group by status
        passed = [r for r in self.results if r.passed]
        errors = self.errors
        warnings = self.warnings

        # Print passed
        if passed:
            print("PASSED:")
            for r in passed:
                print(f"  [OK] {r.message}")
            print()

        # Print warnings
        if warnings:
            print("WARNINGS:")
            for r in warnings:
                print(f"  [!] {r.message}")
            print()

        # Print errors
        if errors:
            print("ERRORS:")
            for r in errors:
                print(f"  [X] {r.message}")
            print()

        # Summary
        print("-" * 60)
        print(
            f"Total: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors"
        )
        print("-" * 60)

        if self.passed:
            print("\nValidation PASSED")
        else:
            print("\nValidation FAILED - Please fix errors before proceeding")


def get_project_root() -> Path:
    """Find project root by looking for pyproject.toml."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return current


def parse_act_claude_md(content: str) -> dict:
    """Parse root CLAUDE.md (Act-level) content into structured data."""
    data = {
        "has_act_overview": False,
        "has_casts_table": False,
        "casts_in_table": [],
    }

    # Check Act-level sections
    data["has_act_overview"] = "## Act Overview" in content
    data["has_casts_table"] = "## Casts" in content

    # Extract casts from table
    # Format: | CastName | purpose | [link](path) |
    cast_table_pattern = (
        r"\| ([A-Z][a-zA-Z0-9 ]+) \| .* \| \[.*?\]\((casts/[^/]+/CLAUDE\.md)\)"
    )
    matches = re.findall(cast_table_pattern, content)
    data["casts_in_table"] = [{"name": name, "path": path} for name, path in matches]

    return data


def parse_cast_claude_md(content: str, cast_name: str) -> dict:
    """Parse Cast-level CLAUDE.md content into structured data."""
    data = {
        "name": cast_name,
        "has_overview": False,
        "has_diagram": False,
        "has_input_state": False,
        "has_output_state": False,
        "has_overall_state": False,
        "has_nodes": False,
        "has_tech_stack": False,
        "has_parent_link": False,
        "nodes": [],
    }

    # Check required sections
    data["has_overview"] = "## Overview" in content
    data["has_diagram"] = "## Architecture Diagram" in content
    data["has_input_state"] = "### InputState" in content
    data["has_output_state"] = "### OutputState" in content
    data["has_overall_state"] = "### OverallState" in content
    data["has_nodes"] = "## Node Specifications" in content
    data["has_tech_stack"] = "## Technology Stack" in content
    data["has_parent_link"] = "**Parent Act:**" in content

    # Extract node names
    node_pattern = r"### (\w+)\s*\n\s*\| Attribute"
    data["nodes"] = re.findall(node_pattern, content)

    # Check mermaid diagram
    if "```mermaid" in content:
        mermaid_match = re.search(r"```mermaid\s*(.*?)\s*```", content, re.DOTALL)
        if mermaid_match:
            mermaid_content = mermaid_match.group(1)
            data["mermaid_has_start"] = "START" in mermaid_content
            data["mermaid_has_end"] = "END" in mermaid_content
            data["mermaid_node_count"] = len(re.findall(r"\[.*?\]", mermaid_content))

    return data


def validate_act_level(data: dict, report: ValidationReport):
    """Validate Act-level CLAUDE.md completeness."""

    report.add(
        data["has_act_overview"],
        "Root CLAUDE.md: Act Overview section present",
    )
    report.add(
        data["has_casts_table"],
        "Root CLAUDE.md: Casts table present",
    )

    # Check at least one cast in table
    cast_count = len(data["casts_in_table"])
    report.add(
        cast_count > 0,
        f"Root CLAUDE.md: At least one Cast in table (found {cast_count})",
    )


def validate_cast_level(data: dict, report: ValidationReport):
    """Validate Cast-level CLAUDE.md completeness."""

    cast_name = data["name"]

    report.add(
        data.get("has_parent_link", False),
        f"Cast {cast_name}: Parent Act link present",
    )
    report.add(
        data.get("has_overview", False),
        f"Cast {cast_name}: Overview section present",
    )
    report.add(
        data.get("has_diagram", False),
        f"Cast {cast_name}: Architecture diagram present",
    )
    report.add(
        data.get("has_input_state", False),
        f"Cast {cast_name}: InputState schema defined",
    )
    report.add(
        data.get("has_output_state", False),
        f"Cast {cast_name}: OutputState schema defined",
    )
    report.add(
        data.get("has_overall_state", False),
        f"Cast {cast_name}: OverallState schema defined",
    )
    report.add(
        data.get("has_nodes", False),
        f"Cast {cast_name}: Node specifications present",
    )
    report.add(
        data.get("has_tech_stack", False),
        f"Cast {cast_name}: Technology stack section present",
    )


def validate_cast_diagram(data: dict, report: ValidationReport):
    """Validate Cast-level mermaid diagram."""

    cast_name = data["name"]

    if not data.get("mermaid_has_start"):
        report.add(False, f"Cast {cast_name}: Diagram missing START node", "warning")
    else:
        report.add(True, f"Cast {cast_name}: Diagram has START node")

    if not data.get("mermaid_has_end"):
        report.add(False, f"Cast {cast_name}: Diagram missing END node", "warning")
    else:
        report.add(True, f"Cast {cast_name}: Diagram has END node")

    node_count = data.get("mermaid_node_count", 0)
    if node_count == 0:
        report.add(False, f"Cast {cast_name}: Diagram has no nodes defined")
    else:
        report.add(True, f"Cast {cast_name}: Diagram has {node_count} nodes")


def validate_cast_nodes(data: dict, report: ValidationReport):
    """Validate Cast-level node specifications."""

    cast_name = data["name"]
    nodes = data.get("nodes", [])

    if len(nodes) == 0:
        report.add(False, f"Cast {cast_name}: No node specifications found")
    else:
        report.add(True, f"Cast {cast_name}: Found {len(nodes)} node specifications")


def validate_cross_references(
    act_data: dict, cast_files: dict[str, Path], report: ValidationReport
):
    """Validate cross-references between Act and Cast CLAUDE.md files."""

    # Check that all casts in table have corresponding files
    for cast_info in act_data["casts_in_table"]:
        cast_name = cast_info["name"]
        expected_path = cast_info["path"]

        if cast_name not in cast_files:
            report.add(
                False,
                f"Cross-ref: Cast '{cast_name}' in table but CLAUDE.md not found at {expected_path}",
            )
        else:
            report.add(
                True,
                f"Cross-ref: Cast '{cast_name}' has corresponding CLAUDE.md file",
            )

    # Check for cast files not in table
    table_cast_names = {c["name"] for c in act_data["casts_in_table"]}
    for cast_name in cast_files.keys():
        if cast_name not in table_cast_names:
            report.add(
                False,
                f"Cross-ref: Cast '{cast_name}' has CLAUDE.md but not listed in root Casts table",
                "warning",
            )


def validate_distributed_architecture(project_root: Path) -> ValidationReport:
    """Validate distributed CLAUDE.md structure.

    Args:
        project_root: Project root directory

    Returns:
        ValidationReport with all results
    """
    report = ValidationReport()

    # 1. Validate root CLAUDE.md exists
    root_claude = project_root / "CLAUDE.md"
    if not root_claude.exists():
        report.add(False, "Root CLAUDE.md not found at project root")
        return report

    report.add(True, "Root CLAUDE.md exists")

    # 2. Parse root CLAUDE.md
    root_content = root_claude.read_text(encoding="utf-8")
    act_data = parse_act_claude_md(root_content)
    validate_act_level(act_data, report)

    # 3. Find all cast CLAUDE.md files
    casts_dir = project_root / "casts"
    cast_files = {}  # cast_name -> Path

    if casts_dir.exists():
        for cast_dir in casts_dir.iterdir():
            if cast_dir.is_dir():
                cast_claude = cast_dir / "CLAUDE.md"
                if cast_claude.exists():
                    # Extract cast name from file
                    cast_content = cast_claude.read_text(encoding="utf-8")
                    cast_name_match = re.search(
                        r"# Cast: ([A-Z][a-zA-Z0-9 ]+)", cast_content
                    )
                    if cast_name_match:
                        cast_name = cast_name_match.group(1).strip()
                        cast_files[cast_name] = cast_claude
    else:
        report.add(False, "Casts directory not found at project root", "warning")

    # 4. Validate each cast CLAUDE.md
    for cast_name, cast_path in cast_files.items():
        cast_content = cast_path.read_text(encoding="utf-8")
        cast_data = parse_cast_claude_md(cast_content, cast_name)

        validate_cast_level(cast_data, report)
        validate_cast_diagram(cast_data, report)
        validate_cast_nodes(cast_data, report)

    # 5. Cross-reference validation
    validate_cross_references(act_data, cast_files, report)

    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate distributed architecture specification completeness"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Only output errors")

    args = parser.parse_args()

    # Get project root
    project_root = get_project_root()

    # Validate
    report = validate_distributed_architecture(project_root)

    # Output
    if not args.quiet:
        report.print_report()
    else:
        if not report.passed:
            for error in report.errors:
                print(f"ERROR: {error.message}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
