# Edge Patterns

## When to Use This Resource
Read this when defining graph flow, implementing conditional routing, or creating routing functions for conditional edges.

## Key Concepts

**Edge** = Connection between nodes defining execution flow.

**Static Edge** = Always goes to the same next node.

**Conditional Edge** = Routes to different nodes based on state.

**Dynamic Routing** = Routes determined at runtime by routing function.

## Pattern 1: Static Edges

**When to use:** Flow is always the same—no branching logic needed.

```python
from langgraph.graph import StateGraph

builder = StateGraph(GraphState)
builder.add_node("node_a", node_a_instance)
builder.add_node("node_b", node_b_instance)

# Static: always go from node_a to node_b
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)  # END is special terminal node
```

**Use when:**
- Sequential processing (A → B → C)
- No decisions needed
- Deterministic flow

## Pattern 2: Conditional Edges

**When to use:** Need to route to different nodes based on state values.

### Simple Conditional (2-way branch)

```python
def route_by_intent(state: dict) -> str:
    """Routes based on intent field."""
    if state.get("intent") == "search":
        return "search_node"
    else:
        return "default_node"

# Add conditional edge
builder.add_conditional_edges(
    "intent_detector",           # Source node
    route_by_intent,             # Routing function
    ["search_node", "default_node"]  # Possible destinations
)
```

### Multi-way Conditional (3+ branches)

```python
def route_by_complexity(state: dict) -> str:
    """Routes based on query complexity."""
    complexity = state.get("complexity_score", 0)

    if complexity > 0.8:
        return "deep_research"
    elif complexity > 0.4:
        return "standard_search"
    else:
        return "quick_lookup"

builder.add_conditional_edges(
    "analyzer",
    route_by_complexity,
    ["deep_research", "standard_search", "quick_lookup"]
)
```

## Pattern 3: Conditional with Fallback/END

**When to use:** Some branches should end the graph.

```python
from langgraph.graph import END

def should_continue(state: dict) -> str:
    """Decides whether to continue or end."""
    if state.get("complete"):
        return END
    elif state.get("error"):
        return "error_handler"
    else:
        return "next_step"

builder.add_conditional_edges(
    "checker",
    should_continue,
    {
        END: END,                    # Graph terminates
        "error_handler": "error_handler",
        "next_step": "next_step"
    }
)
```

## Pattern 4: Loops and Cycles

**When to use:** Need to repeat nodes until a condition is met.

```python
def should_retry(state: dict) -> str:
    """Loops back or continues based on validation."""
    if not state.get("validated"):
        attempts = state.get("attempts", 0)
        if attempts < 3:
            return "retry"  # Loop back
        else:
            return "give_up"
    else:
        return "success"

# Creates a loop: validator -> should_retry -> validator (if retry)
builder.add_conditional_edges(
    "validator",
    should_retry,
    {
        "retry": "validator",      # Loops back
        "give_up": "error_handler",
        "success": "finalizer"
    }
)
```

**⚠️ Warning:** Always have an exit condition to prevent infinite loops!

## Act Project Conventions

⚠️ **Routing Function Location:** `casts/[cast_name]/conditions.py`

```python
# casts/my_cast/conditions.py
"""Routing functions for conditional edges."""
from langgraph.graph import END

def route_by_intent(state: dict) -> str:
    """Routes based on detected intent."""
    intent = state.get("intent", "unknown")

    if intent == "search":
        return "search_handler"
    elif intent == "summarize":
        return "summarizer"
    else:
        return "fallback"

def should_continue_research(state: dict) -> str:
    """Determines if research loop should continue."""
    if state.get("research_complete"):
        return END
    elif state.get("max_iterations_reached"):
        return "timeout_handler"
    else:
        return "next_research_step"
```

Then in `graph.py`:
```python
from .conditions import route_by_intent, should_continue_research

builder.add_conditional_edges("detector", route_by_intent, [...])
builder.add_conditional_edges("research", should_continue_research, [...])
```

## Decision Framework

```
Flow always goes to same next node?
├─ Yes → Use add_edge(source, target)
└─ No  → Continue...

Need to branch based on state?
├─ Yes → Use add_conditional_edges(source, routing_func, targets)
    ├─ 2-3 branches → Simple if/elif/else in routing function
    ├─ 4+ branches → Consider pattern matching or dict lookup
    └─ One branch is END → Include END in targets

Need to loop back to previous node?
└─ Yes → Conditional edge that returns previous node name
         ⚠️ Must have exit condition!
```

## Routing Function Best Practices

### ✅ Do: Clear, Explicit Logic
```python
def route_by_status(state: dict) -> str:
    """Clear routing based on status."""
    status = state.get("status", "unknown")

    if status == "ready":
        return "processor"
    elif status == "pending":
        return "waiter"
    else:
        return "error_handler"
```

### ✅ Do: Handle Missing State
```python
def safe_router(state: dict) -> str:
    """Handles missing keys gracefully."""
    value = state.get("key", default_value)  # Safe access
    return "next_node" if value else "fallback"
```

### ❌ Don't: Complex Logic in Router
```python
def bad_router(state: dict) -> str:
    # ❌ Too much business logic in router
    result = complex_calculation(state)
    processed = transform(result)
    validated = check(processed)
    return "next" if validated else "error"

# ✅ Better: Do complex logic in a node, simple routing
def good_router(state: dict) -> str:
    # State already processed by previous node
    return state.get("next_node", "default")
```

## Common Mistakes

❌ **Returning node not in targets list**
```python
builder.add_conditional_edges(
    "router",
    lambda s: "node_x",  # ❌ node_x not in list below
    ["node_a", "node_b"]
)
```

❌ **Forgetting END import**
```python
def router(state):
    return END  # ❌ NameError: END not defined

# ✅ Import it
from langgraph.graph import END
```

❌ **Infinite loops without exit**
```python
# ❌ Dangerous - can loop forever
def router(state):
    return "same_node"  # Always loops back

# ✅ Safe - has exit condition
def safe_router(state):
    if state.get("done"):
        return END
    return "same_node"
```

## References
- Related: `implementing-nodes.md` (what nodes return affects routing)
- Related: `graph-compilation.md` (how edges fit in graph building)
- Related: `../advanced/error-handling-retry.md` (error routing patterns)
