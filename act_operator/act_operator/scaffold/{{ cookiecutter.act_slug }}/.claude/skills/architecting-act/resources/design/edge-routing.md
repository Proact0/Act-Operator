# Edge Routing Guide

## Edge Types

| Type | Use Case |
|------|----------|
| **Normal** | Always same next node |
| **Conditional** | Decision-based routing |
| **Loop** | Repeat until condition met |

## Design Process

1. Connect nodes based on selected pattern
2. Add conditional edges at decision points
3. Ensure all paths reach END
4. Add exit conditions for loops

## Output Format

**IMPORTANT: Describe routing logic only. Do NOT write implementation code (def functions, if/else, etc.).**

### Normal Edges Table
| Source | Target |
|--------|--------|
| START | FirstNode |
| NodeA | NodeB |
| LastNode | END |

### Conditional Edges Table
| Source | Condition | Target |
|--------|-----------|--------|
| DecisionNode | condition_a | TargetA |
| DecisionNode | condition_b | TargetB |
| DecisionNode | default | FallbackNode |

### Routing Logic (Description Only)
Describe the condition logic in plain text:
- "If message contains tool_calls, route to ToolNode"
- "If quality score > 0.8, route to END"
- "Otherwise, route back to RefineNode"

## Design Principles

**Normal:** Use when next node is always the same.

**Conditional:** ALWAYS include default case.

**Loop:** Must have exit condition AND iteration limit.

## Checklist

- [ ] START has outgoing edge
- [ ] Every node has outgoing edge(s)
- [ ] All conditional edges have default
- [ ] All paths reach END
- [ ] Loops have exit conditions
