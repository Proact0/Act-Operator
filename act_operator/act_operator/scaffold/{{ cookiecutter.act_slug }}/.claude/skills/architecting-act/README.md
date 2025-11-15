# Architect

ing Act Skill

**Version:** 1.0.0
**Purpose:** Design LangGraph architectures through strategic questioning - state schemas, nodes, edges, and workflow patterns

## Overview

This skill guides users through designing high-level LangGraph architectures using a 4-stage interactive process. It focuses on architectural decisions (WHAT and WHY) rather than implementation details (HOW).

## File Structure

```
architecting-act/
├── SKILL.md                          # Main skill guide (404 lines)
├── README.md                         # This file
├── resources/                        # Decision frameworks (NO CODE)
│   ├── workflow-patterns.md          # Pattern selection guide (358 lines, ~2.8k tokens)
│   ├── state-design-guide.md         # State schema design (555 lines, ~3.2k tokens)
│   ├── node-architecture-guide.md    # Node decomposition (701 lines, ~4.1k tokens)
│   ├── edge-routing-guide.md         # Routing strategies (719 lines, ~4.0k tokens)
│   ├── subgraph-decisions.md         # Subgraph framework (632 lines, ~3.5k tokens)
│   └── anti-patterns.md              # Common mistakes (211 lines, ~1.5k tokens)
├── scripts/                          # Executable tools
│   ├── generate_claude_md.py         # Generate CLAUDE.md (445 lines)
│   └── validate_architecture.py      # Validate architecture (559 lines)
└── templates/
    └── CLAUDE.md.template            # Architecture doc template (256 lines)
```

## Resource Organization

### Core Decision Frameworks (Navigate via SKILL.md)

1. **workflow-patterns.md** - Choose ReAct, Plan-Execute, Reflection, Map-Reduce, Multi-Agent
2. **state-design-guide.md** - Design state schema with reducers and channels
3. **node-architecture-guide.md** - Apply SOLID principles to node design
4. **edge-routing-guide.md** - Design conditional routing and control flow
5. **subgraph-decisions.md** - Determine when to use subgraphs
6. **anti-patterns.md** - Avoid common architectural mistakes

### Scripts

- **generate_claude_md.py** - Interactive or CLI-based CLAUDE.md generation
- **validate_architecture.py** - Check architecture against anti-patterns

## Usage Flow

```
User invokes skill → 4-Stage Interactive Process → CLAUDE.md Generated
                                                           ↓
                                              Handoff to developing-cast skill
```

### Stage 1: Understand the Problem
Strategic questions about purpose, inputs, outputs, challenges

### Stage 2: Technical Constraints
Latency requirements, platform constraints, integration needs

### Stage 3: Architecture Design
- Workflow pattern recommendation (consult workflow-patterns.md)
- State schema proposal (consult state-design-guide.md)
- Node breakdown (consult node-architecture-guide.md)
- Edge routing (consult edge-routing-guide.md)
- Subgraph decisions (consult subgraph-decisions.md)

### Stage 4: Finalization
- Run validate_architecture.py
- Generate CLAUDE.md using generate_claude_md.py
- Review with user
- Hand off to developing-cast

## Key Design Principles

### No Code in Resources
All resources focus on concepts, patterns, and decision frameworks. Implementation belongs in developing-cast skill.

### Token Efficiency
- SKILL.md: <5k tokens (currently ~3.2k)
- Resources: <4k tokens each
- Frequently accessed (workflow-patterns, anti-patterns): <2k tokens

### LangGraph 1.0 Focus
All patterns and examples verified against LangGraph 1.0 official documentation. No deprecated 0.x features.

### SOLID Principles
Node architecture emphasizes Single Responsibility, dependency injection, and testability.

## Integration with Other Skills

### Prerequisites
- User has run `act new` to create scaffold
- Project structure exists at correct location

### Outputs
- `CLAUDE.md` at project root (architecture blueprint)
- Validated architecture ready for implementation

### Handoff
```
/developing-cast  # Implements the architecture in CLAUDE.md
```

## Quality Criteria

✓ Interactive workflow is clear and guides user effectively
✓ Resources provide decision frameworks, not just information
✓ Scripts execute successfully and generate valid output
✓ CLAUDE.md template is comprehensive
✓ Validation catches common anti-patterns
✓ All LangGraph references verified against official docs
✓ Enables smooth handoff to developing-cast skill

## Token Budget Analysis

**Total Skill Size:** ~18.5k tokens

- SKILL.md: ~3.2k tokens
- Resources: ~17k tokens combined
- Scripts: Executable (loaded on demand)
- Template: Loaded on demand

**Optimization Notes:**
- Resources are comprehensive but could be condensed further if needed
- Most frequently accessed (workflow-patterns, anti-patterns) are under 2k tokens
- Larger guides (node, edge, state, subgraph) provide deep reference when needed

## Testing Validation

### Automated Validation
```bash
uv run python scripts/validate_architecture.py --input CLAUDE.md
```

Checks:
- Completeness (purpose, pattern, state, nodes, edges)
- State design (field count, reducers, metadata)
- Node design (count, naming, dependencies)
- Routing (loops, error handling, END conditions)
- Pattern selection (rationale, latency match)
- SOLID adherence

### Manual Validation
- Walk through 4-stage process with test scenario
- Generate CLAUDE.md interactively
- Verify all resources are accessible and helpful

## Development Notes

### Created
2025-11-15

### Research Sources
- LangGraph 1.0 official documentation
- ReAct, Plan-Execute, Reflection patterns
- Map-Reduce, Multi-Agent collaboration patterns
- SOLID principles for node architecture

### Design Decisions
1. **Interactive over declarative** - 4-stage questioning guides better than upfront specification
2. **Decision frameworks over examples** - Teach pattern selection vs showing examples
3. **Validation scripts** - Automate anti-pattern detection
4. **Template-based generation** - Consistent CLAUDE.md structure

## Future Enhancements

Potential improvements:
- Mermaid diagram auto-generation from architecture
- More sophisticated validation rules
- Interactive web UI for architecture design
- Integration with LangGraph Studio

## Contributing

This skill is part of the Act Operator project. Improvements welcome via:
- Enhanced validation rules
- Additional anti-pattern detection
- Better decision frameworks
- Token optimization

---

**Remember:** Perfect architecture enables perfect implementation. This skill ensures users invest time in thoughtful design before coding begins.
