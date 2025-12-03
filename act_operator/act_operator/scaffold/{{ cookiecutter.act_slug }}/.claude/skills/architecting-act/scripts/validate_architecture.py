#!/usr/bin/env python3
"""Validate architecture specification for completeness.

Usage:
    python scripts/validate_architecture.py [CLAUDE.md]

Validates that the architecture specification is complete and consistent.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


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
        print(f"Total: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")
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


def parse_claude_md(content: str) -> dict:
    """Parse CLAUDE.md content into structured data."""
    data = {
        "has_overview": False,
        "has_diagram": False,
        "has_input_state": False,
        "has_output_state": False,
        "has_overall_state": False,
        "has_nodes": False,
        "has_edges": False,
        "has_tech_stack": False,
        "has_next_steps": False,
        "nodes": [],
    }
    
    # Check sections
    data["has_overview"] = "## Overview" in content
    data["has_diagram"] = "## Architecture Diagram" in content
    data["has_input_state"] = "### InputState" in content
    data["has_output_state"] = "### OutputState" in content
    data["has_overall_state"] = "### OverallState" in content
    data["has_nodes"] = "## Node Specifications" in content
    data["has_edges"] = "## Edge Definitions" in content
    data["has_tech_stack"] = "## Technology Stack" in content
    data["has_next_steps"] = "## Next Steps" in content
    
    # Extract node names
    node_pattern = r"### (\w+)\s*\n\s*\| Attribute"
    data["nodes"] = re.findall(node_pattern, content)
    
    # Check for placeholder text
    data["has_placeholders"] = "[" in content and "]" in content
    
    # Check mermaid diagram
    if "```mermaid" in content:
        mermaid_match = re.search(r"```mermaid\s*(.*?)\s*```", content, re.DOTALL)
        if mermaid_match:
            mermaid_content = mermaid_match.group(1)
            data["mermaid_has_start"] = "START" in mermaid_content
            data["mermaid_has_end"] = "END" in mermaid_content
            data["mermaid_node_count"] = len(re.findall(r"\[.*?\]", mermaid_content))
    
    return data


def validate_completeness(data: dict, report: ValidationReport):
    """Validate that all required sections exist."""
    
    # Required sections
    report.add(
        data["has_overview"],
        "Overview section present",
    )
    report.add(
        data["has_diagram"],
        "Architecture diagram present",
    )
    report.add(
        data["has_input_state"],
        "InputState schema defined",
    )
    report.add(
        data["has_output_state"],
        "OutputState schema defined",
    )
    report.add(
        data["has_overall_state"],
        "OverallState schema defined",
    )
    report.add(
        data["has_nodes"],
        "Node specifications present",
    )
    report.add(
        data["has_edges"],
        "Edge definitions present",
    )
    report.add(
        data["has_tech_stack"],
        "Technology stack section present",
    )
    report.add(
        data["has_next_steps"],
        "Next steps section present",
    )


def validate_diagram(data: dict, report: ValidationReport):
    """Validate the mermaid diagram."""
    
    if not data.get("mermaid_has_start"):
        report.add(False, "Diagram missing START node", "warning")
    else:
        report.add(True, "Diagram has START node")
    
    if not data.get("mermaid_has_end"):
        report.add(False, "Diagram missing END node", "warning")
    else:
        report.add(True, "Diagram has END node")
    
    node_count = data.get("mermaid_node_count", 0)
    if node_count == 0:
        report.add(False, "Diagram has no nodes defined")
    else:
        report.add(True, f"Diagram has {node_count} nodes")


def validate_nodes(data: dict, report: ValidationReport):
    """Validate node specifications."""
    
    if len(data["nodes"]) == 0:
        report.add(False, "No node specifications found")
    else:
        report.add(True, f"Found {len(data['nodes'])} node specifications")


def validate_placeholders(data: dict, report: ValidationReport):
    """Check for unfilled placeholders."""
    
    if data.get("has_placeholders"):
        report.add(
            False,
            "Document contains placeholder text (text in [brackets])",
            "warning"
        )
    else:
        report.add(True, "No placeholder text found")


def validate_architecture(content: str) -> ValidationReport:
    """Run all validation checks on CLAUDE.md content.
    
    Args:
        content: CLAUDE.md file content
        
    Returns:
        ValidationReport with all results
    """
    report = ValidationReport()
    data = parse_claude_md(content)
    
    validate_completeness(data, report)
    validate_diagram(data, report)
    validate_nodes(data, report)
    validate_placeholders(data, report)
    
    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate architecture specification completeness"
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=None,
        help="Path to CLAUDE.md (default: PROJECT_ROOT/CLAUDE.md)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output errors"
    )
    
    args = parser.parse_args()
    
    # Determine file path
    file_path = args.path
    if file_path is None:
        file_path = get_project_root() / "CLAUDE.md"
    
    # Check file exists
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        print("\nCreate CLAUDE.md first using the architecting-act skill.")
        return 1
    
    # Read and validate
    content = file_path.read_text(encoding="utf-8")
    report = validate_architecture(content)
    
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

