# Edges

Edges define routing logic between nodes.

## Contents

- Edge Types
- Normal Edge
- Conditional Edge
- Entry Point
- Conditional Entry Point
- Parallel Execution
- Complete Example

## Edge Types

| Type | Description |
|------|-------------|
| Normal Edge | Always go from A to B |
| Conditional Edge | Route based on function result |
| Entry Point | First node from START |
| Conditional Entry | Dynamic first node |

---

## Normal Edge

```python
# casts/{cast_name}/graph.py
builder.add_edge("node_a", "node_b")
```

## Conditional Edge

```python
# casts/{cast_name}/modules/conditions.py
def route_by_result(state) -> str:
    if state.get("success"):
        return "next_node"
    return "error_node"
```

```python
# casts/{cast_name}/graph.py
from casts.{cast_name}.modules.conditions import route_by_result

# Option 1: Direct return value as node name
builder.add_conditional_edges("process", route_by_result)

# Option 2: Map return values to node names
builder.add_conditional_edges(
    "process",
    route_by_result,
    {"next_node": "success_handler", "error_node": "error_handler"}
)
```

## Entry Point

```python
# casts/{cast_name}/graph.py
from langgraph.graph import START

builder.add_edge(START, "first_node")
```

## Conditional Entry Point

```python
# casts/{cast_name}/graph.py
from langgraph.graph import START

builder.add_conditional_edges(
    START,
    route_by_input,
    {"type_a": "handler_a", "type_b": "handler_b"}
)
```

---

## Parallel Execution

If a node has multiple outgoing edges, all destination nodes execute **in parallel**.

```python
# casts/{cast_name}/graph.py
# Both "analyze" and "summarize" run in parallel after "fetch"
builder.add_edge("fetch", "analyze")
builder.add_edge("fetch", "summarize")
```

---

## Complete Example

```python
# casts/{cast_name}/modules/conditions.py
from langgraph.graph import END

def should_continue(state) -> str:
    if state.get("done"):
        return END
    if state.get("error"):
        return "error_handler"
    return "next_step"
```

```python
# casts/{cast_name}/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph
from casts.{cast_name}.modules.conditions import should_continue

class WorkflowGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)
        
        builder.add_node("input", InputNode())
        builder.add_node("process", ProcessNode())
        builder.add_node("next_step", NextNode())
        builder.add_node("error_handler", ErrorNode())
        
        builder.add_edge(START, "input")
        builder.add_edge("input", "process")
        builder.add_conditional_edges(
            "process",
            should_continue,
            {
                "next_step": "next_step",
                "error_handler": "error_handler",
                END: END
            }
        )
        builder.add_edge("next_step", END)
        builder.add_edge("error_handler", END)
        
        graph = builder.compile()
        graph.name = self.name
        return graph
```
