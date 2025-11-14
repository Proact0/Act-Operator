#!/usr/bin/env python3
"""
Generate claude.md template for Act graph architecture documentation.

Usage:
    python .claude/skills/architecting-act/scripts/generate-claude-md.py [--cast-name NAME]
"""

import argparse
from pathlib import Path


TEMPLATE = """# {cast_name} Graph Architecture

## Overview

[One paragraph describing the purpose and high-level workflow of this graph]

## Requirements

### Inputs
- **Field 1**: Description
- **Field 2**: Description

### Outputs
- **Field 1**: Description
- **Field 2**: Description

### Constraints
- **Latency**: [Low/Medium/High - X seconds]
- **Integration Points**: [External systems, APIs, databases]
- **Human-in-the-Loop**: [Yes/No - where in flow]
- **Scale**: [Expected volume/usage]

## State Schema

### InputState
```python
class InputState(TypedDict):
    field1: str  # Description
    field2: int  # Description
```

### OutputState
```python
class OutputState(TypedDict):
    result1: str  # Description
    result2: bool  # Description
```

### Internal State (extends InputState + OutputState)
```python
class State(MessagesState):
    # Inherits InputState and OutputState fields
    intermediate_field1: str  # Description
    intermediate_field2: list[str]  # Description
```

## Nodes

### Node1Name
**Responsibility**: [Single clear responsibility]

**Input**: [What it needs from state]

**Output**: [What it updates in state]

**Implementation**: [Key logic/approach]

### Node2Name
**Responsibility**: [Single clear responsibility]

**Input**: [What it needs from state]

**Output**: [What it updates in state]

**Implementation**: [Key logic/approach]

[Continue for all nodes...]

## Edges

### Linear Edges
- START → Node1
- Node1 → Node2
- NodeN → END

### Conditional Edges
- **From**: NodeX
- **Condition**: `route_by_category(state)`
- **Routes**:
  - "category_a" → NodeA
  - "category_b" → NodeB
  - "default" → NodeDefault

## Design Decisions

### Why Node Granularity?
[Explain why nodes were split to follow SRP]

### Why This Flow?
[Explain edge logic and routing decisions]

### Why No Subgraphs? (or Why Subgraph Used?)
[Explain complexity management decisions]

### Error Handling Strategy
[How errors are caught and handled in the graph]

## Implementation Notes

- **Tools location**: `modules/tools/` (if needed)
- **Memory patterns**: [Session state only / long-term integration]
- **External dependencies**: [List any external services/APIs]
- **Testing approach**: [How to test this graph]

## Future Enhancements

- [Potential improvement 1]
- [Potential improvement 2]
"""


def generate_claude_md(cast_name: str = "YourCast", output_path: Path = None):
    """Generate claude.md template with given cast name."""

    if output_path is None:
        output_path = Path.cwd() / "claude.md"

    content = TEMPLATE.format(cast_name=cast_name)

    output_path.write_text(content)
    print(f"✓ Created {output_path}")
    print(f"\nNext steps:")
    print(f"1. Fill in the template with your architecture design")
    print(f"2. Review with team/stakeholders")
    print(f"3. Use as reference during implementation with developing-cast skill")


def main():
    parser = argparse.ArgumentParser(
        description="Generate claude.md architecture template"
    )
    parser.add_argument(
        "--cast-name",
        default="YourCast",
        help="Name of the cast/graph being documented"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output path (default: ./claude.md)"
    )

    args = parser.parse_args()
    generate_claude_md(args.cast_name, args.output)


if __name__ == "__main__":
    main()
