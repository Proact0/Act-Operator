# Architecture Diagram Guide

Guide for creating clear Mermaid diagrams that represent your Cast architecture.

## Design Process

1. Start with START node
2. Add nodes based on selected pattern
3. Connect nodes with edges (normal or conditional)
4. Ensure all paths reach END
5. Add exit conditions for loops

## Mermaid Syntax

### Basic Structure
```mermaid
graph TD
    START((START)) --> NodeName[NodeName]
    NodeName --> END((END))
```

### Conditional Routing
```mermaid
graph TD
    START((START)) --> DecisionNode{DecisionNode}
    DecisionNode -->|condition_a| NodeA[NodeA]
    DecisionNode -->|condition_b| NodeB[NodeB]
    DecisionNode -->|default| FallbackNode[FallbackNode]
    NodeA --> END((END))
    NodeB --> END((END))
    FallbackNode --> END((END))
```

### Loops
```mermaid
graph TD
    START((START)) --> ProcessNode[ProcessNode]
    ProcessNode --> EvaluateNode{EvaluateNode}
    EvaluateNode -->|pass| END((END))
    EvaluateNode -->|fail| RefineNode[RefineNode]
    RefineNode --> ProcessNode
```

## Node Shapes

- **START/END**: `((START))`, `((END))`
- **Normal Node**: `[NodeName]`
- **Decision Node**: `{DecisionNode}` (diamond shape for conditional routing)

## Design Principles

**Clarity:** Each node should be clearly labeled with CamelCase names

**Completeness:** All paths must reach END

**Loops:** Must show exit condition and loop path

**Conditionals:** Label edges with conditions (e.g., `|condition|`)

## Checklist

- [ ] START node present
- [ ] All nodes connected
- [ ] All paths reach END
- [ ] Conditional edges labeled with conditions
- [ ] Loop exit conditions shown
- [ ] Node names use CamelCase
