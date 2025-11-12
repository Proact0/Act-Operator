# Conditional Routing Guide for LangGraph

Comprehensive guide to implementing routing functions, conditional edges, and decision logic in LangGraph applications.

## Table of Contents

1. [Introduction](#introduction)
2. [Routing Function Basics](#routing-function-basics)
   - [What is a Routing Function](#what-is-a-routing-function)
   - [Function Signature](#function-signature)
   - [Return Values](#return-values)
3. [Simple Conditional Logic](#simple-conditional-logic)
   - [Binary Decisions](#binary-decisions)
   - [State-Based Routing](#state-based-routing)
   - [Message-Based Routing](#message-based-routing)
4. [Multi-Path Routing Patterns](#multi-path-routing-patterns)
   - [Multiple Destinations](#multiple-destinations)
   - [Routing Maps](#routing-maps)
   - [Default Routes](#default-routes)
5. [State-Based Routing](#state-based-routing-1)
   - [Field Checks](#field-checks)
   - [Iteration Limits](#iteration-limits)
   - [Error States](#error-states)
6. [Complex Routing Logic](#complex-routing-logic)
   - [Nested Conditions](#nested-conditions)
   - [Priority-Based Routing](#priority-based-routing)
   - [Dynamic Route Selection](#dynamic-route-selection)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Troubleshooting](#troubleshooting)
10. [References](#references)

---

## Introduction

Conditional routing in LangGraph enables dynamic graph execution based on state. Routing functions determine which node to execute next.

**Key concepts:**
- **Routing function**: Returns next node name
- **Conditional edges**: Edges with routing functions
- **State-based**: Route based on current state
- **Multi-path**: Multiple possible destinations

---

## Routing Function Basics

### What is a Routing Function

**Definition:**
```python
def routing_function(state):
    \"\"\"
    Determines which node to execute next.

    Args:
        state: Current graph state

    Returns:
        str: Name of next node to execute
    \"\"\"
    if some_condition(state):
        return "node_a"
    else:
        return "node_b"
```

**Usage in graph:**
```python
from langgraph.graph import StateGraph, END

builder = StateGraph(State)

# Add nodes
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

# Add conditional edge
builder.add_conditional_edges(
    "agent",
    routing_function,  # Function that returns next node
)
```

### Function Signature

**Basic signature:**
```python
def router(state):
    # Return node name
    return "next_node"
```

**With config (optional):**
```python
def router(state, config):
    # Can access config
    thread_id = config.get("configurable", {}).get("thread_id")
    # Return node name
    return "next_node"
```

**Type hints:**
```python
from typing import Literal

def router(state: State) -> Literal["tools", "end"]:
    \"\"\"Route to tools or end.\"\"\"
    if state.should_continue:
        return "tools"
    return "end"
```

### Return Values

**Must return:**
- Node name (string)
- Or END constant
- Matches edge mapping

**Examples:**
```python
from langgraph.graph import END

def route_agent(state):
    # Return node name
    if state.tool_calls:
        return "tools"

    # Return END to stop
    return END

# With mapping
def route_with_map(state):
    if state.iteration < 5:
        return "continue"
    return "finish"

builder.add_conditional_edges(
    "agent",
    route_with_map,
    {
        "continue": "agent",  # Loop back
        "finish": END
    }
)
```

---

## Simple Conditional Logic

### Binary Decisions

**Yes/No routing:**
```python
def should_continue(state):
    \"\"\"Simple binary decision.\"\"\"
    last_message = state.messages[-1]

    # Check if agent wants to use tools
    if last_message.tool_calls:
        return "tools"

    # No tools, we're done
    return END

# In graph
builder.add_conditional_edges("agent", should_continue)
```

**With mapping:**
```python
def route_binary(state):
    if state.approved:
        return "approved"
    return "rejected"

builder.add_conditional_edges(
    "review",
    route_binary,
    {
        "approved": "process",
        "rejected": "reject_handler"
    }
)
```

### State-Based Routing

**Check state fields:**
```python
def route_by_state(state):
    \"\"\"Route based on state fields.\"\"\"

    # Check error
    if state.error:
        return "error_handler"

    # Check completion
    if state.result:
        return END

    # Continue processing
    return "process"

builder.add_conditional_edges(
    "agent",
    route_by_state,
    {
        "error_handler": "handle_error",
        "process": "process_node"
    }
)
```

### Message-Based Routing

**Route based on messages:**
```python
def route_by_message(state):
    \"\"\"Route based on last message.\"\"\"
    last_message = state.messages[-1]

    # Check message type
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Check content
    content = last_message.content.lower()
    if "error" in content:
        return "error"
    if "done" in content or "finished" in content:
        return END

    # Default
    return "agent"
```

---

## Multi-Path Routing Patterns

### Multiple Destinations

**Three or more paths:**
```python
def route_multiple(state):
    \"\"\"Route to multiple possible destinations.\"\"\"

    # Check various conditions
    if state.needs_human_review:
        return "human"

    if state.iteration > 10:
        return "max_iterations"

    if state.error:
        return "error"

    if state.tool_calls:
        return "tools"

    if state.complete:
        return END

    # Default: continue
    return "agent"

builder.add_conditional_edges(
    "agent",
    route_multiple,
    {
        "human": "human_review",
        "max_iterations": "finish_early",
        "error": "error_handler",
        "tools": "tool_node",
        "agent": "agent"
    }
)
```

### Routing Maps

**Explicit mapping:**
```python
def classify_query(state):
    \"\"\"Classify and route query.\"\"\"
    query = state.query.lower()

    if "weather" in query:
        return "weather"
    elif "stock" in query or "price" in query:
        return "finance"
    elif "news" in query:
        return "news"
    else:
        return "general"

# Map to specialist nodes
builder.add_conditional_edges(
    "classifier",
    classify_query,
    {
        "weather": "weather_agent",
        "finance": "finance_agent",
        "news": "news_agent",
        "general": "general_agent"
    }
)
```

### Default Routes

**Fallback routing:**
```python
def route_with_default(state):
    \"\"\"Route with default fallback.\"\"\"
    query_type = state.get("query_type")

    # Known types
    if query_type == "search":
        return "search"
    elif query_type == "calculate":
        return "calculator"
    elif query_type == "fetch":
        return "api"

    # Default for unknown
    return "default"

builder.add_conditional_edges(
    "router",
    route_with_default,
    {
        "search": "search_node",
        "calculator": "calc_node",
        "api": "api_node",
        "default": "general_handler"  # Fallback
    }
)
```

---

## State-Based Routing (Advanced)

### Field Checks

**Robust field checking:**
```python
def safe_route(state):
    \"\"\"Route with safe field access.\"\"\"

    # Check if field exists and has value
    if hasattr(state, "result") and state.result:
        return "complete"

    # Check optional field
    if getattr(state, "error", None):
        return "error"

    # Check nested field
    metadata = getattr(state, "metadata", {})
    if metadata.get("priority") == "high":
        return "priority"

    # Default
    return "continue"
```

### Iteration Limits

**Prevent infinite loops:**
```python
def route_with_limit(state):
    \"\"\"Route with iteration limit.\"\"\"
    max_iterations = getattr(state, "max_iterations", 10)
    current = getattr(state, "iteration", 0)

    # Check limit
    if current >= max_iterations:
        return "max_reached"

    # Check completion
    if state.get("complete"):
        return END

    # Continue
    return "continue"

builder.add_conditional_edges(
    "agent",
    route_with_limit,
    {
        "max_reached": "finish_incomplete",
        "continue": "agent"
    }
)
```

### Error States

**Error handling routing:**
```python
def route_errors(state):
    \"\"\"Route based on error state.\"\"\"

    # No error, normal flow
    if not state.get("error"):
        if state.get("complete"):
            return END
        return "continue"

    # Categorize errors
    error = state.error

    if "timeout" in error.lower():
        return "retry"
    elif "unauthorized" in error.lower():
        return "auth_error"
    elif "not found" in error.lower():
        return "not_found"
    else:
        return "general_error"

builder.add_conditional_edges(
    "process",
    route_errors,
    {
        "continue": "next_step",
        "retry": "retry_node",
        "auth_error": "handle_auth",
        "not_found": "handle_not_found",
        "general_error": "error_handler"
    }
)
```

---

## Complex Routing Logic

### Nested Conditions

**Multiple condition levels:**
```python
def complex_router(state):
    \"\"\"Complex routing with nested conditions.\"\"\"

    # First level: Check mode
    if state.mode == "development":
        # Development mode logic
        if state.debug:
            return "debug_node"
        return "dev_node"

    elif state.mode == "production":
        # Production mode logic
        if state.error:
            return "error_handler"

        # Further nesting
        if state.priority == "high":
            if state.approved:
                return "high_priority_approved"
            return "high_priority_review"
        else:
            return "normal_priority"

    # Unknown mode
    return "error"
```

### Priority-Based Routing

**Route by priority:**
```python
def priority_router(state):
    \"\"\"Route based on priority levels.\"\"\"

    # Get priority (default to normal)
    priority = getattr(state, "priority", "normal")

    # Urgent: Immediate processing
    if priority == "urgent":
        return "urgent_handler"

    # High: Fast processing
    elif priority == "high":
        return "high_priority_handler"

    # Normal: Standard processing
    elif priority == "normal":
        return "normal_handler"

    # Low: Batch processing
    elif priority == "low":
        return "batch_handler"

    # Unknown priority
    else:
        return "normal_handler"  # Default to normal
```

### Dynamic Route Selection

**Compute route dynamically:**
```python
def dynamic_router(state):
    \"\"\"Dynamically select route.\"\"\"

    # Score different options
    scores = {
        "option_a": calculate_score_a(state),
        "option_b": calculate_score_b(state),
        "option_c": calculate_score_c(state)
    }

    # Select highest scoring route
    best_option = max(scores.items(), key=lambda x: x[1])

    return best_option[0]

def calculate_score_a(state):
    score = 0
    if state.query_length < 50:
        score += 10
    if "simple" in state.query:
        score += 5
    return score

def calculate_score_b(state):
    score = 0
    if state.iteration < 3:
        score += 10
    if state.complexity == "medium":
        score += 5
    return score

def calculate_score_c(state):
    score = 0
    if state.requires_tools:
        score += 10
    return score
```

---

## Best Practices

1. **Keep routing simple** - Easy to understand and debug
2. **Use type hints** - Document possible return values
3. **Handle all cases** - Always have a default/fallback
4. **Log routing decisions** - Track which path was taken
5. **Avoid side effects** - Pure function, no state mutation
6. **Test edge cases** - Verify all routing paths
7. **Document logic** - Explain routing criteria
8. **Use meaningful names** - Clear route identifiers
9. **Check for None** - Validate state fields exist
10. **Limit nesting** - Too complex = hard to maintain

**Example of good routing:**
```python
def route_agent(state: State) -> Literal["tools", "human", "end"]:
    \"\"\"
    Route agent to next node.

    Returns:
        - "tools": If tool calls present
        - "human": If human review needed
        - "end": If complete
    \"\"\"
    # Log for debugging
    logger.debug(f"Routing from agent, iteration: {state.iteration}")

    # Check tool calls
    last_message = state.messages[-1]
    if last_message.tool_calls:
        logger.debug("Routing to tools")
        return "tools"

    # Check human review
    if state.get("requires_human"):
        logger.debug("Routing to human review")
        return "human"

    # Default: done
    logger.debug("Routing to end")
    return "end"
```

---

## Common Pitfalls

### 1. Missing return statement

```python
# ❌ Bad - might not return
def bad_router(state):
    if state.condition:
        return "node_a"
    # What if condition is False? Error!

# ✅ Good - always returns
def good_router(state):
    if state.condition:
        return "node_a"
    return "node_b"  # Default
```

### 2. Returning wrong type

```python
# ❌ Bad - returns bool
def bad_router(state):
    return state.condition  # True/False not node name!

# ✅ Good - returns node name
def good_router(state):
    if state.condition:
        return "node_a"
    return "node_b"
```

### 3. Not in edge mapping

```python
# ❌ Bad - "unknown" not in mapping
def bad_router(state):
    return "unknown"

builder.add_conditional_edges(
    "node",
    bad_router,
    {"tools": "tools_node"}  # "unknown" not here!
)

# ✅ Good - all returns mapped
def good_router(state):
    if state.tool_calls:
        return "tools"
    return "end"

builder.add_conditional_edges(
    "node",
    good_router,
    {
        "tools": "tools_node",
        "end": END
    }
)
```

### 4. Modifying state

```python
# ❌ Bad - modifies state
def bad_router(state):
    state.count += 1  # Don't do this!
    return "next"

# ✅ Good - pure function
def good_router(state):
    # Read only
    if state.count > 5:
        return "end"
    return "next"
```

### 5. Complex nested logic

```python
# ❌ Bad - too complex
def bad_router(state):
    if state.a:
        if state.b:
            if state.c:
                if state.d:
                    return "node1"
                return "node2"
            return "node3"
        return "node4"
    return "node5"

# ✅ Good - simplified
def good_router(state):
    # Early returns
    if state.a and state.b and state.c and state.d:
        return "node1"

    if state.a and state.b and state.c:
        return "node2"

    if state.a and state.b:
        return "node3"

    if state.a:
        return "node4"

    return "node5"
```

---

## Troubleshooting

### Route not working

**Check:**
1. Router function returns correct type (string)
2. Returned value in edge mapping
3. State fields exist and have expected values
4. No exceptions in router function

**Debug:**
```python
def debug_router(state):
    print(f"State: {state}")

    result = "tools" if state.tool_calls else "end"
    print(f"Routing to: {result}")

    return result
```

### Wrong path taken

**Verify conditions:**
```python
def verify_router(state):
    # Check each condition explicitly
    has_tools = bool(state.messages[-1].tool_calls)
    print(f"Has tool calls: {has_tools}")

    if has_tools:
        print("Taking tools path")
        return "tools"

    print("Taking end path")
    return "end"
```

### Infinite loops

**Add iteration limit:**
```python
def safe_router(state):
    # Prevent infinite loops
    if state.iteration >= 10:
        return END

    # Your routing logic
    if state.should_continue:
        return "agent"
    return END
```

### KeyError in routing

**Safe field access:**
```python
def safe_router(state):
    # Use getattr with default
    error = getattr(state, "error", None)

    if error:
        return "error_handler"

    # Use get() for dicts
    priority = state.metadata.get("priority", "normal")

    return "process"
```

---

## References

- LangGraph Routing: https://langchain-ai.github.io/langgraph/how-tos/branching/
- Conditional Edges: https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.StateGraph.add_conditional_edges
- State Management: `state_patterns.md`
- Edge Types: `edge_types.md`
