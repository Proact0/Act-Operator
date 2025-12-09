# Cast-Level CLAUDE.md Template

Template for creating Cast-specific CLAUDE.md with detailed specifications.

## Full Template Structure

```markdown
# Cast: {{ cookiecutter.cast_name }}

> **Parent Act:** [{{ cookiecutter.act_name }}](../../CLAUDE.md)

## Overview
**Purpose:** {One sentence describing what this cast does}
**Pattern:** {Sequential | Branching | Cyclic | Multi-agent}
**Latency:** {Low | Medium | High}
**Dependencies:** {List of other casts this depends on, or "None"}

## Architecture Diagram

\```mermaid
graph TD
    START((START)) --> Node1[NodeName]
    Node1 --> Node2[NodeName]
    Node2 --> END((END))
\```

## State Schema

### InputState
| Field | Type | Description |
|-------|------|-------------|
| field_name | type | description |

### OutputState
| Field | Type | Description |
|-------|------|-------------|
| field_name | type | description |

### OverallState
| Field | Type | Category | Description |
|-------|------|----------|-------------|
| field_name | type | Input | description |
| field_name | type | Output | description |
| field_name | type | Internal | description |

## Node Specifications

### NodeName
| Attribute | Value |
|-----------|-------|
| Responsibility | {Single sentence describing what this node does} |
| Reads | {state fields this node reads} |
| Writes | {state fields this node writes} |

## Technology Stack

> Note: `langgraph`, `langchain` are already in template. List only **additional** dependencies for this Cast.

### Additional Dependencies
| Package | Purpose |
|---------|---------|
| package-name | purpose |

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| VAR_NAME | Yes/No | description |

## Implementation Notes

### Module Structure
```
casts/{{ cookiecutter.cast_slug }}/
  ├── graph.py           # Main graph assembly
  ├── modules/
  │   ├── state.py       # State definitions
  │   ├── nodes.py       # Node implementations
  │   ├── conditions.py  # Conditional routing (if needed)
  │   ├── agents.py      # Agent configurations (if needed)
  │   ├── tools.py       # Custom tools (if needed)
  │   └── middlewares.py # Middleware setup (if needed)
  └── tests/
      └── test_*.py      # Test files
```

### Next Steps
1. Create cast package: `uv run act cast -c "{{ cookiecutter.cast_name }}"`
2. Implement components in order: state → dependency modules → nodes → conditions → graph
3. Add dependencies: `uv add --package {{ cookiecutter.cast_slug }} package-name`
4. Write tests: Use `testing-cast` skill
5. Run LangGraph dev server: `uv run langgraph dev`
```

## Usage Notes

### Location
- **File path**: `PROJECT_ROOT/casts/{{ cookiecutter.cast_slug }}/CLAUDE.md`
- **Contains**: Complete Cast specifications and implementation guide
- **Links to**: Root CLAUDE.md for Act-level context

### When to Create

- **Initial Design (Mode 1)**: Create along with root CLAUDE.md
- **Add Cast (Mode 2)**: Create for each new cast
- **Extract Sub-Cast (Mode 3)**: Create for extracted sub-cast

### When to Update

- **Add nodes**: Update Node Specifications and Architecture Diagram
- **Modify state**: Update State Schema
- **Add dependencies**: Update Technology Stack
- **Change pattern**: Update Overview and possibly entire structure

### Pattern-Specific Guidance

#### Sequential Pattern
- Nodes execute in linear order
- Each node processes and passes to next
- Simple state flow (Input → Internal → Output)

#### Branching Pattern
- Router node determines path
- Multiple handler nodes for different cases
- State includes routing decision field

#### Cyclic Pattern
- Refinement loop with exit condition
- State tracks iteration count and quality metrics
- Condition node checks if refinement needed

#### Multi-agent Pattern
- Specialized agents for different roles
- Supervisor coordinates agent interactions
- State includes agent outputs and coordination info

## Cross-References

### Parent/Sub-Cast Relationships

If this is a sub-cast, document:
- **Parent Cast**: Link to parent cast CLAUDE.md
- **Integration Point**: Where/how parent calls this sub-cast
- **Input Contract**: What parent passes to this sub-cast
- **Output Contract**: What this sub-cast returns to parent

If this has sub-casts, document:
- **Sub-Casts**: List of sub-casts this calls
- **Why Sub-Cast**: Reason for extraction (complexity, reuse, etc.)
- **Integration**: How sub-casts are invoked

## Checklist

- [ ] Overview clearly states cast purpose
- [ ] Pattern is identified and appropriate
- [ ] Architecture diagram shows all nodes and edges
- [ ] Diagram has START and END nodes
- [ ] All three state schemas defined (InputState, OutputState, OverallState)
- [ ] Every node in diagram has a specification
- [ ] Node specifications include Responsibility, Reads, Writes
- [ ] Technology Stack lists additional dependencies
- [ ] Environment variables documented
- [ ] Links to parent Act CLAUDE.md work
