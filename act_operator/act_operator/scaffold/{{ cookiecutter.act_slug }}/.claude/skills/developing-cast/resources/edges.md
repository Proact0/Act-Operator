---
# Edges Resource
# LangGraph 1.0 Edge and Routing Patterns
---

# Edges and Routing

## Overview

Edges define graph flow. Linear edges connect nodes directly. Conditional edges route based on state.

## Linear Edges

Simple connections between nodes:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)

builder.add_node("node1", Node1())
builder.add_node("node2", Node2())

# Linear edges
builder.add_edge(START, "node1")  # Start → node1
builder.add_edge("node1", "node2")  # node1 → node2
builder.add_edge("node2", END)  # node2 → end
```

## Conditional Edges

Route based on state using routing functions.

### Basic Pattern

```python
# modules/conditions.py
def route_by_status(state) -> str:
    """Route based on status field.

    Args:
        state: Current graph state.

    Returns:
        Node name to route to.
    """
    status = state.get("status", "unknown")

    if status == "success":
        return "success_handler"
    elif status == "error":
        return "error_handler"
    else:
        return "default_handler"


# graph.py
builder.add_conditional_edges(
    "validator",  # Source node
    route_by_status,  # Routing function
    {
        "success_handler": "success_handler",
        "error_handler": "error_handler",
        "default_handler": "default_handler"
    }  # Mapping: function return → node name
)
```

### Routing to END

```python
from langgraph.graph import END

def route_to_end_or_retry(state) -> str:
    """Route to END or retry."""
    attempts = state.get("attempts", 0)

    if attempts >= 3:
        return "end"
    else:
        return "retry"

builder.add_conditional_edges(
    "processor",
    route_to_end_or_retry,
    {
        "end": END,  # Finish graph
        "retry": "processor"  # Loop back
    }
)
```

## Routing Function Patterns

### Boolean Routing

```python
def route_by_validation(state) -> str:
    """Simple boolean routing."""
    is_valid = state.get("is_valid", False)
    return "continue" if is_valid else "error"
```

### Multi-Way Routing

```python
def route_by_category(state) -> str:
    """Route to different handlers."""
    category = state.get("category", "general")

    if category == "technical":
        return "technical_team"
    elif category == "billing":
        return "billing_team"
    elif category == "sales":
        return "sales_team"
    else:
        return "general_support"
```

### Complex Logic Routing

```python
def route_by_priority(state) -> str:
    """Route based on multiple factors."""
    priority = state.get("priority", "low")
    errors = state.get("errors", [])
    attempts = state.get("attempts", 0)

    # High priority with errors → escalate
    if priority == "high" and errors:
        return "escalate"

    # Too many attempts → abort
    if attempts >= 5:
        return "abort"

    # Normal flow
    if errors:
        return "error_handler"
    else:
        return "continue"
```

## Location

**Routing functions:** `modules/conditions.py`

```python
# modules/conditions.py
"""Conditional routing functions for graph edges."""

def route_function_1(state) -> str:
    """Route description."""
    ...

def route_function_2(state) -> str:
    """Route description."""
    ...
```

## Routing with Type Hints

```python
from typing import Literal

def typed_route(state) -> Literal["success", "failure", "retry"]:
    """Type-safe routing function.

    Args:
        state: Graph state.

    Returns:
        One of: "success", "failure", "retry"
    """
    if state.get("status") == "ok":
        return "success"
    elif state.get("attempts", 0) < 3:
        return "retry"
    else:
        return "failure"
```

## Default Routes

Handle unexpected returns:

```python
def route_with_default(state) -> str:
    category = state.get("category")

    if category == "A":
        return "handler_a"
    elif category == "B":
        return "handler_b"
    else:
        return "default"  # Catch-all

# In graph
builder.add_conditional_edges(
    "router",
    route_with_default,
    {
        "handler_a": "node_a",
        "handler_b": "node_b",
        "default": "fallback_node"  # Default route
    }
)
```

## Looping Edges

Create loops for retries or iterations:

```python
def retry_or_finish(state) -> str:
    attempts = state.get("attempts", 0)
    success = state.get("success", False)

    if success:
        return "finish"
    elif attempts < 3:
        return "retry"
    else:
        return "give_up"

# Creates loop
builder.add_conditional_edges(
    "processor",
    retry_or_finish,
    {
        "retry": "processor",  # Loop back to self
        "finish": END,
        "give_up": "error_handler"
    }
)
```

**Prevent infinite loops:**
- Always have exit condition
- Limit attempts with counter
- Timeout mechanism

## Examples

### Simple Binary Route

```python
def is_valid_route(state) -> str:
    """Route valid vs invalid."""
    return "valid" if state.get("is_valid") else "invalid"

builder.add_conditional_edges(
    "validator",
    is_valid_route,
    {"valid": "processor", "invalid": "error"}
)
```

### Category-Based Routing

```python
def route_by_type(state) -> str:
    """Route by document type."""
    doc_type = state.get("document_type", "unknown")

    type_mapping = {
        "pdf": "pdf_processor",
        "image": "image_processor",
        "text": "text_processor",
    }

    return type_mapping.get(doc_type, "generic_processor")
```

### Priority Routing

```python
def prioritize_route(state) -> str:
    """Route by urgency."""
    priority = state.get("priority", 0)

    if priority >= 8:
        return "urgent"
    elif priority >= 5:
        return "normal"
    else:
        return "low"

builder.add_conditional_edges(
    "triage",
    prioritize_route,
    {
        "urgent": "fast_track",
        "normal": "standard_process",
        "low": "batch_process"
    }
)
```

### State-Based Completion

```python
def check_completion(state) -> str:
    """Route based on completion status."""
    steps_done = state.get("steps_completed", [])
    total_steps = state.get("total_steps", 0)

    if len(steps_done) >= total_steps:
        return "complete"
    else:
        return "continue"

builder.add_conditional_edges(
    "step_executor",
    check_completion,
    {
        "complete": END,
        "continue": "next_step"
    }
)
```

## Debugging Routes

Add logging to routing functions:

```python
def debug_route(state) -> str:
    """Route with logging."""
    status = state.get("status")
    print(f"[ROUTE] Status: {status}")  # Debug

    if status == "success":
        print("[ROUTE] Taking success path")
        return "success"
    else:
        print("[ROUTE] Taking failure path")
        return "failure"
```

## Testing Routes

```python
# test_conditions.py
from modules.conditions import route_by_status

def test_success_route():
    state = {"status": "success"}
    assert route_by_status(state) == "success_handler"

def test_error_route():
    state = {"status": "error"}
    assert route_by_status(state) == "error_handler"

def test_default_route():
    state = {"status": "unknown"}
    assert route_by_status(state) == "default_handler"
```

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Missing default case | Always handle unexpected values |
| Infinite loops | Add exit condition + counter |
| Complex logic in graph.py | Move to conditions.py |
| Not returning string | Return node name as string |
| Unmapped return value | Ensure all returns in mapping dict |
| Hardcoded in nodes | Use routing functions |

## Advanced Patterns

### Multi-Condition Routing

```python
def complex_route(state) -> str:
    """Route based on multiple conditions."""
    errors = state.get("errors", [])
    warnings = state.get("warnings", [])
    valid = state.get("is_valid", False)

    # Priority order
    if errors:
        return "handle_errors"
    elif warnings and not valid:
        return "review_warnings"
    elif valid:
        return "proceed"
    else:
        return "manual_review"
```

### Conditional Fan-Out

Route to multiple parallel nodes (requires LangGraph send API):

```python
# For parallel execution after routing
# See LangGraph docs on "send" for dynamic fan-out
```

## Graph Visualization

Visualize your routing logic:

```python
# graph.py
graph = builder.compile()

# Generate Mermaid diagram
print(graph.get_graph().draw_mermaid())

# Or save as PNG (requires graphviz)
# graph.get_graph().draw_png("graph.png")
```

## Next Steps

- **Implementing nodes:** See `resources/nodes.md`
- **State for routing:** See `resources/state.md`
- **Testing graphs:** See `testing-cast` skill
