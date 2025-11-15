#!/usr/bin/env python3
"""
Generate CLAUDE.md architecture document from user inputs.

This script generates a comprehensive architecture document that serves as the
blueprint for LangGraph implementation. It uses the CLAUDE.md.template and fills
it with architecture decisions made during the architecting-act skill workflow.

Usage:
    # Interactive mode (recommended)
    uv run python generate_claude_md.py --interactive

    # Direct mode (provide all arguments)
    uv run python generate_claude_md.py \
        --output CLAUDE.md \
        --cast-name "MyCast" \
        --workflow-pattern "ReAct" \
        --purpose "Answer questions using search tools"

    # Load from JSON config
    uv run python generate_claude_md.py --config architecture.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def prompt_user(message: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        response = input(f"{message} [{default}]: ").strip()
        return response if response else default
    return input(f"{message}: ").strip()


def prompt_multiline(message: str) -> str:
    """Prompt for multiline input (end with empty line)."""
    print(f"{message} (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)


def prompt_list(message: str) -> list[str]:
    """Prompt for list items (one per line, end with empty line)."""
    print(f"{message} (one per line, press Enter twice to finish):")
    items = []
    while True:
        item = input("  - ").strip()
        if not item:
            break
        items.append(item)
    return items


def interactive_mode() -> dict[str, Any]:
    """Collect architecture information interactively."""
    print("\n=== CLAUDE.md Architecture Generator ===\n")
    print("This will guide you through documenting your LangGraph architecture.\n")

    arch = {}

    # Basic Information
    print("--- Basic Information ---")
    arch["cast_name"] = prompt_user("Cast/Graph name", "MyCast")
    arch["purpose"] = prompt_user("Purpose (one-line description)")
    arch["created_date"] = datetime.now().strftime("%Y-%m-%d")

    # Workflow Pattern
    print("\n--- Workflow Pattern ---")
    print("Common patterns: ReAct, Plan-Execute, Reflection, Map-Reduce, Multi-Agent, Custom")
    arch["workflow_pattern"] = prompt_user("Workflow pattern", "ReAct")
    arch["pattern_rationale"] = prompt_multiline("Why this pattern?")

    # State Schema
    print("\n--- State Schema ---")
    print("\nInput State (what comes in):")
    arch["input_state"] = []
    while True:
        field = prompt_user("Field name (or Enter to finish)")
        if not field:
            break
        field_type = prompt_user(f"  Type for '{field}'", "str")
        description = prompt_user(f"  Description for '{field}'")
        arch["input_state"].append({
            "name": field,
            "type": field_type,
            "description": description
        })

    print("\nWorking State (intermediate data):")
    arch["working_state"] = []
    while True:
        field = prompt_user("Field name (or Enter to finish)")
        if not field:
            break
        field_type = prompt_user(f"  Type for '{field}'", "str")
        reducer = prompt_user(f"  Reducer for '{field}' (or Enter for default)", "")
        description = prompt_user(f"  Description for '{field}'")
        arch["working_state"].append({
            "name": field,
            "type": field_type,
            "reducer": reducer,
            "description": description
        })

    print("\nOutput State (what comes out):")
    arch["output_state"] = []
    while True:
        field = prompt_user("Field name (or Enter to finish)")
        if not field:
            break
        field_type = prompt_user(f"  Type for '{field}'", "str")
        description = prompt_user(f"  Description for '{field}'")
        arch["output_state"].append({
            "name": field,
            "type": field_type,
            "description": description
        })

    # Nodes
    print("\n--- Nodes ---")
    arch["nodes"] = []
    while True:
        print()
        node_name = prompt_user("Node name (or Enter to finish)")
        if not node_name:
            break
        purpose = prompt_user(f"  Purpose of '{node_name}'")
        reads = prompt_user(f"  State fields READ by '{node_name}' (comma-separated)", "").split(",")
        reads = [r.strip() for r in reads if r.strip()]
        writes = prompt_user(f"  State fields WRITTEN by '{node_name}' (comma-separated)", "").split(",")
        writes = [w.strip() for w in writes if w.strip()]
        arch["nodes"].append({
            "name": node_name,
            "purpose": purpose,
            "reads": reads,
            "writes": writes
        })

    # Edges
    print("\n--- Edges & Routing ---")
    arch["edges"] = prompt_multiline("Describe edge flow (e.g., 'START → node1 → router → ...')")
    arch["routing_logic"] = prompt_multiline("Describe routing/conditional logic")

    # Subgraphs
    print("\n--- Subgraphs (Optional) ---")
    use_subgraphs = prompt_user("Use subgraphs? (y/n)", "n").lower() == "y"
    arch["subgraphs"] = []
    if use_subgraphs:
        while True:
            subgraph_name = prompt_user("Subgraph name (or Enter to finish)")
            if not subgraph_name:
                break
            purpose = prompt_user(f"  Purpose of '{subgraph_name}'")
            arch["subgraphs"].append({
                "name": subgraph_name,
                "purpose": purpose
            })

    # Additional Notes
    print("\n--- Additional Notes ---")
    arch["implementation_notes"] = prompt_multiline("Implementation notes/guidance (optional)")
    arch["error_handling"] = prompt_multiline("Error handling strategy (optional)")

    return arch


def load_from_config(config_path: Path) -> dict[str, Any]:
    """Load architecture from JSON config file."""
    with open(config_path) as f:
        return json.load(f)


def generate_mermaid_diagram(arch: dict[str, Any]) -> str:
    """Generate Mermaid flowchart from architecture."""
    lines = ["```mermaid", "graph TD"]

    # Add start node
    lines.append("    START([START])")

    # Add nodes
    for node in arch.get("nodes", []):
        node_id = node["name"].replace(" ", "_")
        lines.append(f'    {node_id}["{node["name"]}"]')

    # Add edges (simplified - parse edge description)
    # This is a simple version; real implementation might be more sophisticated
    if arch.get("edges"):
        lines.append("")
        lines.append("    %% Edge flow")
        # Just include as comment for now, manual diagram creation recommended
        for line in arch["edges"].split("\n"):
            if line.strip():
                lines.append(f"    %% {line}")

    # Add end node
    lines.append("    END([END])")

    lines.append("```")
    return "\n".join(lines)


def format_state_table(state_fields: list[dict], include_reducer: bool = False) -> str:
    """Format state fields as markdown table."""
    if not state_fields:
        return "_None defined_"

    lines = []
    if include_reducer:
        lines.append("| Field | Type | Reducer | Description |")
        lines.append("|-------|------|---------|-------------|")
        for field in state_fields:
            reducer = field.get("reducer", "default (override)")
            lines.append(f'| `{field["name"]}` | `{field["type"]}` | {reducer} | {field["description"]} |')
    else:
        lines.append("| Field | Type | Description |")
        lines.append("|-------|------|-------------|")
        for field in state_fields:
            lines.append(f'| `{field["name"]}` | `{field["type"]}` | {field["description"]} |')

    return "\n".join(lines)


def format_nodes_table(nodes: list[dict]) -> str:
    """Format nodes as markdown table."""
    if not nodes:
        return "_None defined_"

    lines = [
        "| Node | Purpose | Reads | Writes |",
        "|------|---------|-------|--------|"
    ]

    for node in nodes:
        reads = ", ".join(f"`{r}`" for r in node.get("reads", []))
        writes = ", ".join(f"`{w}`" for w in node.get("writes", []))
        if not reads:
            reads = "_none_"
        if not writes:
            writes = "_none_"
        lines.append(f'| **{node["name"]}** | {node["purpose"]} | {reads} | {writes} |')

    return "\n".join(lines)


def generate_claude_md(arch: dict[str, Any], template_path: Path) -> str:
    """Generate CLAUDE.md content from architecture and template."""
    # Load template
    if template_path.exists():
        with open(template_path) as f:
            template = f.read()
    else:
        # Use embedded template if file doesn't exist
        template = get_default_template()

    # Replace placeholders
    replacements = {
        "{{CAST_NAME}}": arch.get("cast_name", "MyCast"),
        "{{PURPOSE}}": arch.get("purpose", ""),
        "{{DATE}}": arch.get("created_date", datetime.now().strftime("%Y-%m-%d")),
        "{{WORKFLOW_PATTERN}}": arch.get("workflow_pattern", ""),
        "{{PATTERN_RATIONALE}}": arch.get("pattern_rationale", ""),
        "{{INPUT_STATE_TABLE}}": format_state_table(arch.get("input_state", [])),
        "{{WORKING_STATE_TABLE}}": format_state_table(arch.get("working_state", []), include_reducer=True),
        "{{OUTPUT_STATE_TABLE}}": format_state_table(arch.get("output_state", [])),
        "{{NODES_TABLE}}": format_nodes_table(arch.get("nodes", [])),
        "{{EDGE_FLOW}}": arch.get("edges", ""),
        "{{ROUTING_LOGIC}}": arch.get("routing_logic", ""),
        "{{MERMAID_DIAGRAM}}": generate_mermaid_diagram(arch),
        "{{IMPLEMENTATION_NOTES}}": arch.get("implementation_notes", "_None_"),
        "{{ERROR_HANDLING}}": arch.get("error_handling", "_None_"),
    }

    content = template
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Handle subgraphs (optional section)
    if arch.get("subgraphs"):
        subgraph_section = "\n## Subgraphs\n\n"
        for sg in arch["subgraphs"]:
            subgraph_section += f'### {sg["name"]}\n\n'
            subgraph_section += f'**Purpose:** {sg["purpose"]}\n\n'
        content = content.replace("{{SUBGRAPHS_SECTION}}", subgraph_section)
    else:
        content = content.replace("{{SUBGRAPHS_SECTION}}", "")

    return content


def get_default_template() -> str:
    """Return default template if template file doesn't exist."""
    return """# {{CAST_NAME}} Architecture

**Created:** {{DATE}}

## Purpose

{{PURPOSE}}

## Workflow Pattern

**Pattern:** {{WORKFLOW_PATTERN}}

**Rationale:**
{{PATTERN_RATIONALE}}

## State Schema

### Input State

{{INPUT_STATE_TABLE}}

### Working State

{{WORKING_STATE_TABLE}}

### Output State

{{OUTPUT_STATE_TABLE}}

## Node Architecture

{{NODES_TABLE}}

## Edge & Routing Design

### Edge Flow

{{EDGE_FLOW}}

### Routing Logic

{{ROUTING_LOGIC}}

{{SUBGRAPHS_SECTION}}

## Architecture Diagram

{{MERMAID_DIAGRAM}}

## Implementation Guidance

### Implementation Notes

{{IMPLEMENTATION_NOTES}}

### Error Handling

{{ERROR_HANDLING}}

---

**Next Steps:**
Use the `developing-cast` skill to implement this architecture.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate CLAUDE.md architecture document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode (recommended)"
    )

    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Load architecture from JSON config file"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("CLAUDE.md"),
        help="Output file path (default: CLAUDE.md)"
    )

    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).parent.parent / "templates" / "CLAUDE.md.template",
        help="Template file path"
    )

    # Quick mode arguments
    parser.add_argument("--cast-name", help="Cast name")
    parser.add_argument("--purpose", help="Purpose description")
    parser.add_argument("--workflow-pattern", help="Workflow pattern")

    args = parser.parse_args()

    # Determine mode
    if args.interactive:
        arch = interactive_mode()
    elif args.config:
        arch = load_from_config(args.config)
    elif args.cast_name and args.purpose and args.workflow_pattern:
        # Quick mode with minimal info
        arch = {
            "cast_name": args.cast_name,
            "purpose": args.purpose,
            "workflow_pattern": args.workflow_pattern,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "pattern_rationale": "",
            "input_state": [],
            "working_state": [],
            "output_state": [],
            "nodes": [],
            "edges": "",
            "routing_logic": "",
        }
    else:
        parser.error("Must use --interactive, --config, or provide --cast-name, --purpose, and --workflow-pattern")

    # Generate CLAUDE.md
    content = generate_claude_md(arch, args.template)

    # Write output
    args.output.write_text(content)

    print(f"\n✓ Generated {args.output}")
    print(f"\nNext steps:")
    print(f"1. Review {args.output}")
    print(f"2. Make any manual adjustments")
    print(f"3. Use /developing-cast to implement")


if __name__ == "__main__":
    main()
