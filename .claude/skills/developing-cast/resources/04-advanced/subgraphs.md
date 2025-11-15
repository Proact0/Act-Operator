# Subgraphs

## When to Use This Resource

Read this for multi-agent teams, nested workflows, or composing graphs from smaller graphs.

## Key Concept

**Subgraph:** A compiled graph used as a node in another graph. Enables modular, hierarchical agent systems.

## Pattern 1: Shared State Keys

**When to use:** Subgraph uses same state schema as parent

```python
# Subgraph definition
class SubAgentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(SharedState)
        builder.add_node("sub_task", SubTaskNode())
        builder.set_entry_point("sub_task")
        builder.add_edge("sub_task", END)
        return builder.compile()

# Parent graph uses compiled subgraph as node
class MainGraph(BaseGraph):
    def build(self):
        builder = StateGraph(SharedState)

        # Compile subgraph
        sub_graph = SubAgentGraph().build()

        # Add as node
        builder.add_node("sub_agent", sub_graph)

        builder.add_node("main_task", MainTaskNode())
        builder.add_edge("main_task", "sub_agent")
        builder.add_edge("sub_agent", END)

        return builder.compile()
```

## Pattern 2: Different State Schemas

**When to use:** Subgraph has its own state structure

```python
from casts.base_node import BaseNode

class SubGraphNode(BaseNode):
    """Wrapper node that invokes subgraph with transformation."""

    def __init__(self, subgraph, **kwargs):
        super().__init__(**kwargs)
        self.subgraph = subgraph

    def execute(self, state: ParentState) -> dict:
        # Transform parent state to subgraph state
        sub_input = {
            "task": state["current_task"],
            "context": state["context"],
        }

        # Invoke subgraph
        sub_result = self.subgraph.invoke(sub_input)

        # Transform subgraph result back to parent state
        return {
            "sub_results": sub_result["output"],
            "status": "completed",
        }
```

**In parent graph:**
```python
# Create subgraph
sub_graph = SubGraph().build()

# Wrap in node
sub_node = SubGraphNode(sub_graph)

# Add to parent
builder.add_node("sub_workflow", sub_node)
```

## Multi-Agent Team Pattern

```python
# Research agent subgraph
class ResearchAgent(BaseGraph):
    def build(self):
        builder = StateGraph(ResearchState)
        # ... research workflow
        return builder.compile()

# Analysis agent subgraph
class AnalysisAgent(BaseGraph):
    def build(self):
        builder = StateGraph(AnalysisState)
        # ... analysis workflow
        return builder.compile()

# Supervisor graph
class SupervisorGraph(BaseGraph):
    def build(self):
        builder = StateGraph(SupervisorState)

        # Add specialist agents as nodes
        researcher = ResearchAgent().build()
        analyzer = AnalysisAgent().build()

        builder.add_node("research", ResearchWrapper(researcher))
        builder.add_node("analyze", AnalysisWrapper(analyzer))
        builder.add_node("coordinate", CoordinatorNode())

        # Coordinator routes to specialists
        builder.set_entry_point("coordinate")
        builder.add_conditional_edges(
            "coordinate",
            route_to_specialist,
            {"research": "research", "analyze": "analyze", "end": END}
        )

        return builder.compile()
```

## Common Patterns

### Sequential Subgraphs

```python
builder.add_node("stage1", Stage1Graph().build())
builder.add_node("stage2", Stage2Graph().build())
builder.add_node("stage3", Stage3Graph().build())

builder.add_edge("stage1", "stage2")
builder.add_edge("stage2", "stage3")
```

### Parallel Subgraphs

```python
# Multiple subgraphs running independently
builder.add_conditional_edges(
    "router",
    route_tasks,
    {
        "task_a": "agent_a",  # Subgraph A
        "task_b": "agent_b",  # Subgraph B
        "task_c": "agent_c",  # Subgraph C
    }
)
```

## Decision Framework

```
Need separate workflows combined?
  → Use subgraphs

Same state schema?
  → Pattern 1 (direct subgraph as node)

Different state schemas?
  → Pattern 2 (wrapper node with transformation)

Multi-agent team?
  → Supervisor pattern with specialist subgraphs

Reusable workflow?
  → Extract to subgraph, use in multiple places
```

## Common Mistakes

### ❌ Forgetting State Transformation

```python
# BAD: Different states, no transformation
builder.add_node("sub", subgraph)  # State mismatch!
```

**Fix:**
```python
# GOOD: Wrapper transforms state
builder.add_node("sub", SubGraphWrapper(subgraph))
```

## References

- Graph building: `01-core/graph.md`
- Nodes: `01-core/nodes.md`
