---
name: graph-composition
description: Compose LangGraph workflows with BaseGraph. Use when building graphs, connecting nodes, adding edges, implementing routing, or defining graph topology in Act projects.
---

# Graph Composition

## Overview

Graph composition in LangGraph defines workflow by connecting nodes with edges. This skill provides patterns for building effective graph structures using the StateGraph API.

## When to Use This Skill

- Creating new graph classes
- Connecting nodes with edges
- Implementing conditional routing
- Understanding graph patterns
- Troubleshooting graph structure

## Build Workflow

### 1. Initialize Graph

```python
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)
        # Add nodes and edges...
        return builder.compile()
```

### 2. Add Nodes

```python
# Add nodes (always use instances!)
builder.add_node("process", ProcessNode())
builder.add_node("format", FormatNode())
```

### 3. Connect with Edges

**Simple edges**:
```python
builder.add_edge(START, "process")
builder.add_edge("process", "format")
builder.add_edge("format", END)
```

**Conditional edges**:
```python
def route(state):
    if state.category == "A":
        return "node_a"
    return "node_b"

builder.add_conditional_edges(
    "classifier",
    route,
    {"node_a": "node_a", "node_b": "node_b"}
)
```

### 4. Compile Graph

```python
graph = builder.compile()
graph.name = self.name
return graph
```

## Edge Types Quick Reference

**add_edge(from, to)**:
- Unconditional connection
- Example: `builder.add_edge("process", "save")`

**add_conditional_edges(source, router, mapping)**:
- Dynamic routing based on state
- Router function returns key from mapping
- Example: See conditional edges above

## Common Patterns

See `examples/` for:
- `linear_graph.py` - Sequential processing
- `conditional_graph.py` - Branch based on conditions
- `parallel_graph.py` - Fan-out/fan-in
- `complex_routing.py` - Multi-way routing

## Debugging Checklist

- [ ] All node names in edges match `add_node()` calls
- [ ] Node instances used (not classes)
- [ ] All paths eventually reach END
- [ ] Conditional edges have path for all possible returns
- [ ] Graph is compiled before returning

## Quick Reference

```python
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)
        
        # Nodes
        builder.add_node("node1", Node1())
        builder.add_node("node2", Node2())
        
        # Edges
        builder.add_edge(START, "node1")
        builder.add_edge("node1", "node2")
        builder.add_edge("node2", END)
        
        # Compile
        return builder.compile()
```

## Resources

### References
- `references/edge_types.md` - Detailed edge types and usage
- `references/routing_patterns.md` - Routing pattern catalog
- `references/compilation.md` - Graph compilation details

### Examples
- `examples/linear_graph.py` - Sequential workflow
- `examples/conditional_graph.py` - Conditional branching
- `examples/parallel_graph.py` - Parallel processing
- `examples/complex_routing.py` - Multi-way routing

### Scripts
- `scripts/visualize_graph.py` - Generate graph visualizations (mermaid)

### Official Documentation
- Graph API: https://docs.langchain.com/oss/python/langgraph/graph-api
- StateGraph: https://docs.langchain.com/oss/python/langgraph/graph-api#stategraph
- Edges: https://docs.langchain.com/oss/python/langgraph/graph-api#edges
