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

```
Normal Edges:
- START → [first_node]
- [node_a] → [node_b]
- [last_node] → END

Conditional Edges:
- [decision_node] → {
    "[condition]": [target],
    "default": [fallback]
  }
```

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
