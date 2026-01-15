#!/usr/bin/env python3
"""Validate distributed architecture specification for completeness.

Usage:
    python scripts/validate_architecture.py

Validates that the distributed architecture specification (root CLAUDE.md + cast CLAUDE.md files)
is complete and consistent. All validation checks from validation-checklist.md are implemented here.

Success Criteria:
- Root CLAUDE.md exists with Act Overview and Casts table
- All casts in table have corresponding CLAUDE.md files
- All Cast CLAUDE.md files have complete sections
- Diagrams show START -> nodes -> END
- State schemas are complete
- Dependencies are documented
- Cross-references between files work
- No placeholder text
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    fix_hint: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report."""

    results: list[ValidationResult] = field(default_factory=list)

    def add(
        self,
        passed: bool,
        message: str,
        severity: str = "error",
        fix_hint: Optional[str] = None,
    ):
        """Add a validation result."""
        self.results.append(ValidationResult(passed, message, severity, fix_hint))

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
        print("\n" + "=" * 70)
        print("ARCHITECTURE VALIDATION REPORT")
        print("=" * 70 + "\n")

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
                if r.fix_hint:
                    print(f"      Fix: {r.fix_hint}")
            print()

        # Print errors
        if errors:
            print("ERRORS:")
            for r in errors:
                print(f"  [X] {r.message}")
                if r.fix_hint:
                    print(f"      Fix: {r.fix_hint}")
            print()

        # Summary
        print("-" * 70)
        print(
            f"Total: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors"
        )
        print("-" * 70)

        if self.passed:
            print("\n[SUCCESS] Validation PASSED - Ready for implementation")
            print("\nNext steps:")
            print("  1. engineering-act (scaffold casts)")
            print("  2. developing-cast (implement)")
            print("  3. testing-cast (test)")
        else:
            print("\n[FAILED] Validation FAILED - Please fix errors before proceeding")


def get_project_root() -> Path:
    """Find project root by looking for pyproject.toml."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return current


# =============================================================================
# PARSING FUNCTIONS
# =============================================================================


def parse_act_claude_md(content: str) -> dict:
    """Parse root CLAUDE.md (Act-level) content into structured data."""
    data = {
        "has_act_overview": False,
        "has_purpose": False,
        "has_domain": False,
        "has_casts_table": False,
        "has_project_structure": False,
        "casts_in_table": [],
        "has_placeholders": False,
        "placeholder_locations": [],
    }

    # Check Act-level sections
    data["has_act_overview"] = "## Act Overview" in content
    data["has_purpose"] = "**Purpose:**" in content and not content.count(
        "**Purpose:** {"
    )
    data["has_domain"] = "**Domain:**" in content and not content.count("**Domain:** {")
    data["has_casts_table"] = "## Casts" in content
    data["has_project_structure"] = "## Project Structure" in content

    # Check for placeholder patterns
    placeholder_patterns = [
        r"\{[A-Za-z_]+\}",  # {placeholder}
        r"\[TODO\]",  # [TODO]
        r"\[TBD\]",  # [TBD]
        r"{{[A-Z_]+}}",  # {{PLACEHOLDER}} - template markers
    ]

    for pattern in placeholder_patterns:
        matches = re.findall(pattern, content)
        if matches:
            data["has_placeholders"] = True
            data["placeholder_locations"].extend(matches)

    # Extract casts from table
    # Format: | CastName | purpose | [link](path) |
    cast_table_pattern = (
        r"\| ([A-Z][a-zA-Z0-9 ]+) \| .* \| \[.*?\]\((casts/[^/]+/CLAUDE\.md)\)"
    )
    matches = re.findall(cast_table_pattern, content)
    data["casts_in_table"] = [{"name": name.strip(), "path": path} for name, path in matches]

    return data


def parse_cast_claude_md(content: str, cast_name: str) -> dict:
    """Parse Cast-level CLAUDE.md content into structured data."""
    data = {
        "name": cast_name,
        # Required sections
        "has_parent_link": False,
        "has_overview": False,
        "has_purpose": False,
        "has_pattern": False,
        "has_latency": False,
        "has_diagram": False,
        "has_input_state": False,
        "has_output_state": False,
        "has_overall_state": False,
        "has_nodes": False,
        "has_tech_stack": False,
        "has_cast_structure": False,
        # Mermaid validation
        "mermaid_has_start": False,
        "mermaid_has_end": False,
        "mermaid_node_count": 0,
        "mermaid_nodes": [],
        "mermaid_orphan_nodes": [],
        # Node validation
        "nodes": [],
        "nodes_in_diagram": [],
        # State validation
        "input_state_fields": [],
        "output_state_fields": [],
        "overall_state_fields": [],
        # Placeholder detection
        "has_placeholders": False,
        "placeholder_locations": [],
    }

    # Check required sections
    data["has_parent_link"] = "**Parent Act:**" in content or "[../../CLAUDE.md]" in content
    data["has_overview"] = "## Overview" in content
    data["has_purpose"] = "**Purpose:**" in content
    data["has_pattern"] = "**Pattern:**" in content
    data["has_latency"] = "**Latency:**" in content
    data["has_diagram"] = "## Architecture Diagram" in content
    data["has_input_state"] = "### InputState" in content
    data["has_output_state"] = "### OutputState" in content
    data["has_overall_state"] = "### OverallState" in content
    data["has_nodes"] = "## Node Specifications" in content
    data["has_tech_stack"] = "## Technology Stack" in content
    data["has_cast_structure"] = "## Cast Structure" in content

    # Check for placeholder patterns
    placeholder_patterns = [
        r"\{[A-Za-z_]+\}",  # {placeholder}
        r"\[TODO\]",  # [TODO]
        r"\[TBD\]",  # [TBD]
        r"{{[A-Z_]+}}",  # {{PLACEHOLDER}} - template markers
    ]

    for pattern in placeholder_patterns:
        matches = re.findall(pattern, content)
        if matches:
            data["has_placeholders"] = True
            data["placeholder_locations"].extend(matches)

    # Parse mermaid diagram
    if "```mermaid" in content:
        mermaid_match = re.search(r"```mermaid\s*(.*?)\s*```", content, re.DOTALL)
        if mermaid_match:
            mermaid_content = mermaid_match.group(1)
            data["mermaid_has_start"] = "START" in mermaid_content
            data["mermaid_has_end"] = "END" in mermaid_content

            # Extract nodes from mermaid
            node_pattern = r"\[([A-Za-z0-9_]+)\]"
            nodes = re.findall(node_pattern, mermaid_content)
            data["mermaid_nodes"] = nodes
            data["mermaid_node_count"] = len(nodes)
            data["nodes_in_diagram"] = nodes

            # Check for orphan nodes (defined but not connected)
            # A node is connected if it appears in an edge (-->)
            edge_pattern = r"(\w+)\s*-->"
            edge_targets = r"-->\s*(\w+)"
            sources = set(re.findall(edge_pattern, mermaid_content))
            targets = set(re.findall(edge_targets, mermaid_content))
            connected_nodes = sources | targets

            for node in nodes:
                if node not in connected_nodes and node not in ["START", "END"]:
                    data["mermaid_orphan_nodes"].append(node)

    # Extract node specifications
    node_spec_pattern = r"### (\w+)\s*\n\s*\| Attribute"
    data["nodes"] = re.findall(node_spec_pattern, content)

    # Extract state fields
    # InputState fields
    input_state_match = re.search(
        r"### InputState\s*\n\s*\|.*?\n\s*\|[-|]+\n((?:\|.*\n)*)",
        content,
    )
    if input_state_match:
        field_pattern = r"\| (\w+) \|"
        data["input_state_fields"] = re.findall(field_pattern, input_state_match.group(1))

    # OutputState fields
    output_state_match = re.search(
        r"### OutputState\s*\n\s*\|.*?\n\s*\|[-|]+\n((?:\|.*\n)*)",
        content,
    )
    if output_state_match:
        field_pattern = r"\| (\w+) \|"
        data["output_state_fields"] = re.findall(field_pattern, output_state_match.group(1))

    # OverallState fields
    overall_state_match = re.search(
        r"### OverallState\s*\n\s*\|.*?\n\s*\|[-|]+\n((?:\|.*\n)*)",
        content,
    )
    if overall_state_match:
        field_pattern = r"\| (\w+) \|"
        data["overall_state_fields"] = re.findall(field_pattern, overall_state_match.group(1))

    return data


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_act_level(data: dict, report: ValidationReport):
    """Validate Act-level CLAUDE.md completeness."""

    # Act Overview section
    report.add(
        data["has_act_overview"],
        "Root CLAUDE.md: Act Overview section present",
        fix_hint="Add '## Act Overview' section with Purpose and Domain",
    )

    report.add(
        data["has_purpose"],
        "Root CLAUDE.md: Purpose is defined",
        fix_hint="Add '**Purpose:** <description>' under Act Overview",
    )

    report.add(
        data["has_domain"],
        "Root CLAUDE.md: Domain is specified",
        fix_hint="Add '**Domain:** <domain>' under Act Overview",
    )

    # Casts table
    report.add(
        data["has_casts_table"],
        "Root CLAUDE.md: Casts table present",
        fix_hint="Add '## Casts' section with table of casts",
    )

    # Check at least one cast in table
    cast_count = len(data["casts_in_table"])
    report.add(
        cast_count > 0,
        f"Root CLAUDE.md: At least one Cast in table (found {cast_count})",
        fix_hint="Add at least one cast to the Casts table",
    )

    # Project structure
    report.add(
        data["has_project_structure"],
        "Root CLAUDE.md: Project Structure section present",
        severity="warning",
        fix_hint="Add '## Project Structure' section with directory tree",
    )

    # Placeholder detection
    if data["has_placeholders"]:
        unique_placeholders = list(set(data["placeholder_locations"]))[:5]
        report.add(
            False,
            f"Root CLAUDE.md: Contains placeholder text: {unique_placeholders}",
            fix_hint="Replace all placeholder text with actual content",
        )
    else:
        report.add(True, "Root CLAUDE.md: No placeholder text found")


def validate_cast_level(data: dict, report: ValidationReport):
    """Validate Cast-level CLAUDE.md completeness."""

    cast_name = data["name"]

    # Parent link
    report.add(
        data["has_parent_link"],
        f"Cast {cast_name}: Parent Act link present",
        fix_hint="Add '**Parent Act:** [../../CLAUDE.md](../../CLAUDE.md)' at top",
    )

    # Overview section
    report.add(
        data["has_overview"],
        f"Cast {cast_name}: Overview section present",
        fix_hint="Add '## Overview' section",
    )

    report.add(
        data["has_purpose"],
        f"Cast {cast_name}: Purpose defined",
        fix_hint="Add '**Purpose:** <description>' under Overview",
    )

    report.add(
        data["has_pattern"],
        f"Cast {cast_name}: Pattern specified",
        fix_hint="Add '**Pattern:** <Sequential|Branching|Cyclic|Agentic>' under Overview",
    )

    report.add(
        data["has_latency"],
        f"Cast {cast_name}: Latency specified",
        severity="warning",
        fix_hint="Add '**Latency:** <Low|Medium|High>' under Overview",
    )

    # Architecture diagram
    report.add(
        data["has_diagram"],
        f"Cast {cast_name}: Architecture diagram present",
        fix_hint="Add '## Architecture Diagram' with mermaid diagram",
    )

    # State schemas
    report.add(
        data["has_input_state"],
        f"Cast {cast_name}: InputState schema defined",
        fix_hint="Add '### InputState' with field table",
    )

    report.add(
        data["has_output_state"],
        f"Cast {cast_name}: OutputState schema defined",
        fix_hint="Add '### OutputState' with field table",
    )

    report.add(
        data["has_overall_state"],
        f"Cast {cast_name}: OverallState schema defined",
        fix_hint="Add '### OverallState' with field table",
    )

    # Node specifications
    report.add(
        data["has_nodes"],
        f"Cast {cast_name}: Node specifications present",
        fix_hint="Add '## Node Specifications' with node details",
    )

    # Technology stack
    report.add(
        data["has_tech_stack"],
        f"Cast {cast_name}: Technology stack section present",
        fix_hint="Add '## Technology Stack' with dependencies",
    )

    # Placeholder detection
    if data["has_placeholders"]:
        unique_placeholders = list(set(data["placeholder_locations"]))[:5]
        report.add(
            False,
            f"Cast {cast_name}: Contains placeholder text: {unique_placeholders}",
            fix_hint="Replace all placeholder text with actual content",
        )
    else:
        report.add(True, f"Cast {cast_name}: No placeholder text found")


def validate_cast_diagram(data: dict, report: ValidationReport):
    """Validate Cast-level mermaid diagram."""

    cast_name = data["name"]

    # START node
    if not data.get("mermaid_has_start"):
        report.add(
            False,
            f"Cast {cast_name}: Diagram missing START node",
            fix_hint="Add 'START((START))' node to mermaid diagram",
        )
    else:
        report.add(True, f"Cast {cast_name}: Diagram has START node")

    # END node
    if not data.get("mermaid_has_end"):
        report.add(
            False,
            f"Cast {cast_name}: Diagram missing END node",
            fix_hint="Add 'END((END))' node and ensure all paths reach it",
        )
    else:
        report.add(True, f"Cast {cast_name}: Diagram has END node")

    # Node count
    node_count = data.get("mermaid_node_count", 0)
    if node_count == 0:
        report.add(
            False,
            f"Cast {cast_name}: Diagram has no nodes defined",
            fix_hint="Add nodes to mermaid diagram using [NodeName] syntax",
        )
    else:
        report.add(True, f"Cast {cast_name}: Diagram has {node_count} nodes")

    # Orphan nodes
    orphan_nodes = data.get("mermaid_orphan_nodes", [])
    if orphan_nodes:
        report.add(
            False,
            f"Cast {cast_name}: Diagram has orphan nodes: {orphan_nodes}",
            severity="warning",
            fix_hint="Connect orphan nodes to the flow or remove them",
        )


def validate_cast_nodes(data: dict, report: ValidationReport):
    """Validate Cast-level node specifications match diagram."""

    cast_name = data["name"]
    nodes_specified = data.get("nodes", [])
    nodes_in_diagram = data.get("nodes_in_diagram", [])

    if len(nodes_specified) == 0:
        report.add(
            False,
            f"Cast {cast_name}: No node specifications found",
            fix_hint="Add '### NodeName' sections under Node Specifications",
        )
    else:
        report.add(
            True,
            f"Cast {cast_name}: Found {len(nodes_specified)} node specifications",
        )

    # Check nodes in diagram have specifications
    if nodes_in_diagram:
        for node in nodes_in_diagram:
            if node not in nodes_specified:
                report.add(
                    False,
                    f"Cast {cast_name}: Node '{node}' in diagram has no specification",
                    severity="warning",
                    fix_hint=f"Add '### {node}' section with Responsibility, Reads, Writes",
                )


def validate_cast_state_completeness(data: dict, report: ValidationReport):
    """Validate state schema completeness."""

    cast_name = data["name"]

    input_fields = data.get("input_state_fields", [])
    output_fields = data.get("output_state_fields", [])
    overall_fields = data.get("overall_state_fields", [])

    # Check OverallState includes Input and Output fields
    if input_fields and overall_fields:
        missing_input = [f for f in input_fields if f not in overall_fields and f != "field_name"]
        if missing_input:
            report.add(
                False,
                f"Cast {cast_name}: OverallState missing InputState fields: {missing_input}",
                severity="warning",
                fix_hint="Add InputState fields to OverallState with Category='Input'",
            )

    if output_fields and overall_fields:
        missing_output = [f for f in output_fields if f not in overall_fields and f != "field_name"]
        if missing_output:
            report.add(
                False,
                f"Cast {cast_name}: OverallState missing OutputState fields: {missing_output}",
                severity="warning",
                fix_hint="Add OutputState fields to OverallState with Category='Output'",
            )


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
                fix_hint=f"Create /casts/{expected_path.split('/')[1]}/CLAUDE.md with cast specifications",
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
                severity="warning",
                fix_hint=f"Add '{cast_name}' to the Casts table in root CLAUDE.md",
            )


# =============================================================================
# MAIN VALIDATION
# =============================================================================


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
        report.add(
            False,
            "Root CLAUDE.md not found at project root",
            fix_hint="Create CLAUDE.md at project root using act-template",
        )
        return report

    report.add(True, "Root CLAUDE.md exists")

    # 2. Parse and validate root CLAUDE.md
    root_content = root_claude.read_text(encoding="utf-8")
    act_data = parse_act_claude_md(root_content)
    validate_act_level(act_data, report)

    # 3. Find all cast CLAUDE.md files
    casts_dir = project_root / "casts"
    cast_files: dict[str, Path] = {}

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
        report.add(
            False,
            "Casts directory not found at project root",
            severity="warning",
            fix_hint="Create 'casts/' directory and add cast packages",
        )

    # 4. Validate each cast CLAUDE.md
    for cast_name, cast_path in cast_files.items():
        cast_content = cast_path.read_text(encoding="utf-8")
        cast_data = parse_cast_claude_md(cast_content, cast_name)

        validate_cast_level(cast_data, report)
        validate_cast_diagram(cast_data, report)
        validate_cast_nodes(cast_data, report)
        validate_cast_state_completeness(cast_data, report)

    # 5. Cross-reference validation
    validate_cross_references(act_data, cast_files, report)

    return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate distributed architecture specification completeness"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Only output errors"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()

    # Get project root
    project_root = get_project_root()

    # Validate
    report = validate_distributed_architecture(project_root)

    # Output
    if args.json:
        import json
        output = {
            "passed": report.passed,
            "error_count": len(report.errors),
            "warning_count": len(report.warnings),
            "results": [
                {
                    "passed": r.passed,
                    "message": r.message,
                    "severity": r.severity,
                    "fix_hint": r.fix_hint,
                }
                for r in report.results
            ],
        }
        print(json.dumps(output, indent=2))
    elif args.quiet:
        if not report.passed:
            for error in report.errors:
                print(f"ERROR: {error.message}")
                if error.fix_hint:
                    print(f"  Fix: {error.fix_hint}")
    else:
        report.print_report()

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
