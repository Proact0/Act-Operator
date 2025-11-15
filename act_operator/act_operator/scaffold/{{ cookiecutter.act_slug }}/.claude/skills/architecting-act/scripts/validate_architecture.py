#!/usr/bin/env python3
"""
Validate LangGraph architecture design against best practices and anti-patterns.

This script analyzes a CLAUDE.md architecture document or interactive inputs
to detect common anti-patterns, violations of SOLID principles, and potential
issues. It provides warnings and suggestions for improvement.

Usage:
    # Validate existing CLAUDE.md
    uv run python validate_architecture.py --input CLAUDE.md

    # Interactive validation (during architecture design)
    uv run python validate_architecture.py --interactive

    # JSON output for tooling
    uv run python validate_architecture.py --input CLAUDE.md --json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    """A validation issue found in the architecture."""
    severity: Severity
    category: str
    message: str
    suggestion: str = ""
    line_number: int | None = None


@dataclass
class ValidationResult:
    """Results of architecture validation."""
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings_count: int = 0
    errors_count: int = 0
    info_count: int = 0

    def add_issue(self, severity: Severity, category: str, message: str, suggestion: str = ""):
        """Add a validation issue."""
        issue = ValidationIssue(severity, category, message, suggestion)
        self.issues.append(issue)

        if severity == Severity.ERROR:
            self.errors_count += 1
        elif severity == Severity.WARNING:
            self.warnings_count += 1
        else:
            self.info_count += 1

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return self.errors_count > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return self.warnings_count > 0


def parse_claude_md(file_path: Path) -> dict[str, Any]:
    """Parse CLAUDE.md file and extract architecture information."""
    content = file_path.read_text()

    arch = {
        "raw_content": content,
        "has_purpose": False,
        "has_workflow_pattern": False,
        "has_state_schema": False,
        "has_nodes": False,
        "has_edges": False,
        "state_fields": [],
        "nodes": [],
        "edges_description": "",
    }

    # Extract sections (simple parsing)
    if "## Purpose" in content or "## purpose" in content:
        arch["has_purpose"] = True

    if "workflow pattern" in content.lower():
        arch["has_workflow_pattern"] = True

    if "state schema" in content.lower() or "## State" in content:
        arch["has_state_schema"] = True

    if "## Node" in content:
        arch["has_nodes"] = True

    if "## Edge" in content or "routing" in content.lower():
        arch["has_edges"] = True

    # Count state fields (look for markdown tables in state section)
    state_section = re.search(r"## State Schema.*?(?=##|$)", content, re.DOTALL | re.IGNORECASE)
    if state_section:
        # Count table rows (simple heuristic)
        table_rows = [line for line in state_section.group().split("\n") if line.strip().startswith("|")]
        # Subtract header rows (usually 2)
        arch["state_fields"] = [row for row in table_rows if not row.strip().startswith("|---")]
        # Filter out header row
        if arch["state_fields"]:
            arch["state_fields"] = arch["state_fields"][1:]  # Skip first header row

    # Count nodes
    node_section = re.search(r"## Node.*?(?=##|$)", content, re.DOTALL | re.IGNORECASE)
    if node_section:
        # Count table rows or bullet points
        table_rows = [line for line in node_section.group().split("\n") if line.strip().startswith("|")]
        if table_rows:
            arch["nodes"] = [row for row in table_rows if not row.strip().startswith("|---")]
            if arch["nodes"]:
                arch["nodes"] = arch["nodes"][1:]  # Skip header

    # Extract edge description
    edge_section = re.search(r"## Edge.*?(?=##|$)", content, re.DOTALL | re.IGNORECASE)
    if edge_section:
        arch["edges_description"] = edge_section.group()

    return arch


def validate_completeness(arch: dict[str, Any]) -> ValidationResult:
    """Validate that architecture document is complete."""
    result = ValidationResult()

    if not arch.get("has_purpose"):
        result.add_issue(
            Severity.ERROR,
            "completeness",
            "Missing purpose section",
            "Add a clear purpose statement describing what this graph accomplishes"
        )

    if not arch.get("has_workflow_pattern"):
        result.add_issue(
            Severity.ERROR,
            "completeness",
            "Missing workflow pattern selection",
            "Specify which workflow pattern (ReAct, Plan-Execute, etc.) and why"
        )

    if not arch.get("has_state_schema"):
        result.add_issue(
            Severity.ERROR,
            "completeness",
            "Missing state schema",
            "Define state schema with input, working, and output fields"
        )

    if not arch.get("has_nodes"):
        result.add_issue(
            Severity.ERROR,
            "completeness",
            "Missing node architecture",
            "Define nodes with their responsibilities and state dependencies"
        )

    if not arch.get("has_edges"):
        result.add_issue(
            Severity.WARNING,
            "completeness",
            "Missing or unclear edge/routing design",
            "Describe edge flow and routing logic clearly"
        )

    return result


def validate_state_design(arch: dict[str, Any]) -> ValidationResult:
    """Validate state schema design."""
    result = ValidationResult()

    state_fields = arch.get("state_fields", [])
    num_fields = len(state_fields)

    # Check for kitchen sink state
    if num_fields > 15:
        result.add_issue(
            Severity.WARNING,
            "state",
            f"Large state schema ({num_fields} fields detected)",
            "Consider if all fields are necessary. Kitchen sink state anti-pattern. See resources/anti-patterns.md"
        )

    if num_fields == 0 and arch.get("has_state_schema"):
        result.add_issue(
            Severity.WARNING,
            "state",
            "No state fields detected in state schema section",
            "Ensure state fields are documented in table format"
        )

    # Check for common missing fields
    content_lower = arch.get("raw_content", "").lower()

    has_metadata = any(word in content_lower for word in ["iteration", "count", "timestamp", "error", "metadata"])
    if not has_metadata:
        result.add_issue(
            Severity.INFO,
            "state",
            "No metadata fields detected",
            "Consider adding iteration counters, timestamps, or error tracking fields"
        )

    # Check for reducer mentions
    has_reducers = "reducer" in content_lower
    if not has_reducers and num_fields > 5:
        result.add_issue(
            Severity.WARNING,
            "state",
            "No reducers mentioned in state schema",
            "If using accumulating fields (lists, dicts), specify reducers. See resources/state-design-guide.md"
        )

    return result


def validate_node_design(arch: dict[str, Any]) -> ValidationResult:
    """Validate node architecture."""
    result = ValidationResult()

    nodes = arch.get("nodes", [])
    num_nodes = len(nodes)

    # Check for god node / chatty nodes
    if num_nodes == 1:
        result.add_issue(
            Severity.WARNING,
            "nodes",
            "Only one node detected - possible god node anti-pattern",
            "Consider if this node should be decomposed into multiple focused nodes. See resources/node-architecture-guide.md"
        )

    if num_nodes > 20:
        result.add_issue(
            Severity.WARNING,
            "nodes",
            f"Many nodes detected ({num_nodes}) - possible chatty nodes anti-pattern",
            "Consider if some trivial nodes should be merged. See resources/node-architecture-guide.md"
        )

    # Check for node naming patterns
    content = arch.get("raw_content", "")

    # Look for nodes with "and" in name (doing too much)
    and_nodes = re.findall(r'\*\*(\w+_and_\w+)\*\*|\b(\w+_and_\w+)\s*node', content, re.IGNORECASE)
    if and_nodes:
        result.add_issue(
            Severity.WARNING,
            "nodes",
            f"Node names contain 'and' - possibly doing too much",
            "Nodes should have single responsibility. Split nodes with 'and' in name. See resources/node-architecture-guide.md"
        )

    # Check for generic names
    generic_names = ["process", "handle", "manage", "do", "run", "execute"]
    for generic in generic_names:
        if re.search(rf'\b{generic}_node\b|\*\*{generic}\*\*', content, re.IGNORECASE):
            result.add_issue(
                Severity.INFO,
                "nodes",
                f"Generic node name detected: '{generic}'",
                "Use specific, descriptive node names (e.g., 'extract_key_info' not 'process')"
            )
            break  # Only warn once

    return result


def validate_routing(arch: dict[str, Any]) -> ValidationResult:
    """Validate edge and routing design."""
    result = ValidationResult()

    edges = arch.get("edges_description", "").lower()

    # Check for loop detection
    has_loop = any(word in edges for word in ["loop", "iterate", "repeat", "cycle"])
    if has_loop:
        has_max_iterations = any(word in edges for word in ["max", "limit", "maximum iteration"])
        if not has_max_iterations:
            result.add_issue(
                Severity.ERROR,
                "routing",
                "Loop detected without max iteration limit",
                "All loops must have max iteration limit to prevent infinite loops. See resources/edge-routing-guide.md"
            )

    # Check for error handling
    has_error_handling = any(word in edges for word in ["error", "failure", "exception", "fallback"])
    if not has_error_handling:
        result.add_issue(
            Severity.WARNING,
            "routing",
            "No error handling paths mentioned",
            "Consider error routing paths for robustness. See resources/edge-routing-guide.md"
        )

    # Check for END conditions
    content = arch.get("raw_content", "")
    has_end = "END" in content or "end" in edges
    if not has_end:
        result.add_issue(
            Severity.WARNING,
            "routing",
            "No END/completion conditions mentioned",
            "Explicitly document when and how execution completes"
        )

    return result


def validate_pattern_selection(arch: dict[str, Any]) -> ValidationResult:
    """Validate workflow pattern selection."""
    result = ValidationResult()

    content = arch.get("raw_content", "").lower()

    # Check if pattern is mentioned with rationale
    has_pattern = arch.get("has_workflow_pattern", False)
    if has_pattern:
        has_rationale = any(word in content for word in ["rationale", "because", "reason", "why"])
        if not has_rationale:
            result.add_issue(
                Severity.WARNING,
                "pattern",
                "Workflow pattern mentioned but no rationale provided",
                "Explain why this pattern was chosen. See resources/workflow-patterns.md"
            )

    # Check for pattern/complexity mismatch (heuristic)
    if "react" in content and any(word in content for word in ["complex", "multi-step", "planning"]):
        result.add_issue(
            Severity.INFO,
            "pattern",
            "ReAct pattern with complex/multi-step task mentioned",
            "Consider if Plan-Execute pattern would be more appropriate. See resources/workflow-patterns.md"
        )

    if any(pattern in content for pattern in ["multi-agent", "reflection"]) and "latency" in content:
        if any(word in content for word in ["low latency", "fast", "real-time", "quick"]):
            result.add_issue(
                Severity.WARNING,
                "pattern",
                "Complex pattern (multi-agent/reflection) with low latency requirements",
                "Complex patterns increase latency. Verify this matches requirements. See resources/workflow-patterns.md"
            )

    return result


def validate_subgraph_usage(arch: dict[str, Any]) -> ValidationResult:
    """Validate subgraph decisions."""
    result = ValidationResult()

    content = arch.get("raw_content", "").lower()

    has_subgraph = "subgraph" in content or "sub-graph" in content
    if has_subgraph:
        # Check if rationale provided
        subgraph_section = re.search(r"subgraph.*?(?=##|$)", content, re.DOTALL)
        if subgraph_section:
            section_text = subgraph_section.group()
            has_rationale = any(word in section_text for word in ["purpose", "because", "rationale", "why"])
            if not has_rationale:
                result.add_issue(
                    Severity.WARNING,
                    "subgraph",
                    "Subgraphs mentioned but purpose/rationale unclear",
                    "Document why each subgraph is separate. See resources/subgraph-decisions.md"
                )

    return result


def validate_solid_principles(arch: dict[str, Any]) -> ValidationResult:
    """Validate adherence to SOLID principles."""
    result = ValidationResult()

    # This is more of a reminder check
    content = arch.get("raw_content", "").lower()

    # Check if dependencies are documented
    has_dependencies = any(word in content for word in ["reads", "writes", "depends", "requires"])
    if not has_dependencies:
        result.add_issue(
            Severity.INFO,
            "solid",
            "Node dependencies not clearly documented",
            "Document which state fields each node reads and writes. See resources/node-architecture-guide.md"
        )

    return result


def run_all_validations(arch: dict[str, Any]) -> ValidationResult:
    """Run all validation checks."""
    combined = ValidationResult()

    validators = [
        validate_completeness,
        validate_state_design,
        validate_node_design,
        validate_routing,
        validate_pattern_selection,
        validate_subgraph_usage,
        validate_solid_principles,
    ]

    for validator in validators:
        result = validator(arch)
        combined.issues.extend(result.issues)
        combined.errors_count += result.errors_count
        combined.warnings_count += result.warnings_count
        combined.info_count += result.info_count

    return combined


def print_results(result: ValidationResult, verbose: bool = True):
    """Print validation results to console."""
    print("\n=== Architecture Validation Results ===\n")

    if not result.issues:
        print("✓ No issues found! Architecture looks good.\n")
        return

    # Group by severity
    errors = [i for i in result.issues if i.severity == Severity.ERROR]
    warnings = [i for i in result.issues if i.severity == Severity.WARNING]
    infos = [i for i in result.issues if i.severity == Severity.INFO]

    # Print summary
    print(f"Summary: {result.errors_count} errors, {result.warnings_count} warnings, {result.info_count} info\n")

    # Print errors
    if errors:
        print("❌ ERRORS (must fix):\n")
        for issue in errors:
            print(f"  [{issue.category}] {issue.message}")
            if issue.suggestion:
                print(f"    → {issue.suggestion}")
            print()

    # Print warnings
    if warnings:
        print("⚠️  WARNINGS (should review):\n")
        for issue in warnings:
            print(f"  [{issue.category}] {issue.message}")
            if issue.suggestion:
                print(f"    → {issue.suggestion}")
            print()

    # Print info (only if verbose)
    if infos and verbose:
        print("ℹ️  INFO (suggestions):\n")
        for issue in infos:
            print(f"  [{issue.category}] {issue.message}")
            if issue.suggestion:
                print(f"    → {issue.suggestion}")
            print()

    # Final recommendation
    print("\n" + "="*50)
    if result.has_errors():
        print("❌ Architecture has ERRORS - please fix before proceeding")
    elif result.has_warnings():
        print("⚠️  Architecture has WARNINGS - review recommended")
    else:
        print("✓ Architecture looks good - only minor suggestions")
    print("="*50 + "\n")


def output_json(result: ValidationResult) -> str:
    """Output validation results as JSON."""
    return json.dumps({
        "summary": {
            "errors": result.errors_count,
            "warnings": result.warnings_count,
            "info": result.info_count,
        },
        "issues": [
            {
                "severity": issue.severity.value,
                "category": issue.category,
                "message": issue.message,
                "suggestion": issue.suggestion,
            }
            for issue in result.issues
        ]
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Validate LangGraph architecture design",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="CLAUDE.md file to validate"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show errors and warnings, not info"
    )

    args = parser.parse_args()

    if not args.input:
        parser.error("--input is required (or use --interactive in future version)")

    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    # Parse architecture
    arch = parse_claude_md(args.input)

    # Validate
    result = run_all_validations(arch)

    # Output
    if args.json:
        print(output_json(result))
    else:
        print_results(result, verbose=not args.quiet)

    # Exit code
    sys.exit(1 if result.has_errors() else 0)


if __name__ == "__main__":
    main()
