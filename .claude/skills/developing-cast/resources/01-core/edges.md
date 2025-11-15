# Edge Implementation

## When to Use This Resource

Read this when adding routing logic, implementing conditional branches, or troubleshooting edge flow issues.

## Key Concepts

**Edge:** Connection between nodes defining execution flow.

**Static Edge:** Fixed connection (A → B always).

**Conditional Edge:** Decision point (A → B or C based on condition).

**Dynamic Routing:** Runtime-determined destinations.

**Entry Point:** First node executed when graph starts.

## Edge Types

### Type 1: Static Edge (Fixed Flow)

**When to use:** Flow always goes A → B

```python
# In graph.py
builder.add_edge("node_a", "node_b")  # Always A → B
builder.add_edge("node_b", END)  # B → END (terminal)
```

**Example use cases:**
- Sequential processing steps
- Setup → Process → Cleanup
- Start → Validate → Execute

**Visual:**
```
START → node_a → node_b → END
```

### Type 2: Conditional Edge (Decision Point)

**When to use:** Flow depends on state (A → B or C or D)

```python
# In graph.py
from casts.my_agent.conditions import route_decision

builder.add_conditional_edges(
    source="decision_node",
    path=route_decision,  # Function that returns next node name
)
```

**Condition function in conditions.py:**
```python
# File: casts/my_agent/conditions.py
from casts.my_agent.state import MyAgentState

def route_decision(state: MyAgentState) -> str:
    """Route based on action in state.

    Args:
        state: Current graph state

    Returns:
        Name of next node
    """
    action = state.get("action", "default")

    if action == "approve":
        return "approve_node"
    elif action == "review":
        return "review_node"
    else:
        return "reject_node"
```

**Visual:**
```
              ┌──> approve_node
decision_node ├──> review_node
              └──> reject_node
```

### Type 3: Conditional Edge with Path Map

**When to use:** Need clearer routing logic, want to rename routes

```python
# In graph.py
from casts.my_agent.conditions import decide_route

builder.add_conditional_edges(
    source="decision_node",
    path=decide_route,
    path_map={
        "approve": "approve_node",
        "review": "review_node",
        "reject": "reject_node",
        "default": END,
    }
)
```

**Condition function returns key from path_map:**
```python
# File: casts/my_agent/conditions.py
def decide_route(state: MyAgentState) -> str:
    """Decide which route to take.

    Returns:
        Key from path_map ('approve', 'review', 'reject', 'default')
    """
    score = state.get("score", 0)

    if score > 0.8:
        return "approve"  # Maps to "approve_node"
    elif score > 0.5:
        return "review"  # Maps to "review_node"
    else:
        return "reject"  # Maps to "reject_node"
```

**Benefits:**
- Clearer intent (return "approve" vs "approve_node")
- Easier refactoring (change node names without touching conditions)
- Can map to END directly

### Type 4: Tool Calling Edge (ReAct Pattern)

**When to use:** Agent decides whether to call tools or finish

```python
from langgraph.prebuilt import ToolNode
from casts.my_agent.conditions import should_continue

# Add tool node
builder.add_node("tools", ToolNode(tools))

# Conditional edge from agent
builder.add_conditional_edges(
    source="agent",
    path=should_continue,
    path_map={
        "continue": "tools",  # Call tools
        "end": END,  # Finish
    }
)

# Static edge back to agent after tools
builder.add_edge("tools", "agent")
```

**Condition checks for tool calls:**
```python
# File: casts/my_agent/conditions.py
from langchain_core.messages import AIMessage

def should_continue(state: MyAgentState) -> str:
    """Check if agent wants to call tools.

    Returns:
        'continue' if tool calls exist, 'end' otherwise
    """
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "continue"  # Has tool calls
    else:
        return "end"  # No tool calls, done
```

**Visual:**
```
        ┌──────────────┐
        │              │
agent ──┤              ├──> END
        │              │
        └──> tools ────┘
```

## Condition Functions

### Location

**File:** `casts/[cast_name]/conditions.py`

### Pattern

```python
"""Conditional routing functions for [CastName]."""

from casts.my_agent.state import MyAgentState
from langgraph.graph import END

def condition_name(state: MyAgentState) -> str:
    """Describe what this condition checks.

    Args:
        state: Current graph state

    Returns:
        Node name or key for path_map
    """
    # Decision logic
    if some_condition:
        return "node_a"
    else:
        return "node_b"
```

### Common Condition Patterns

#### Check Field Value

```python
def route_by_action(state: MyAgentState) -> str:
    """Route based on action field."""
    action = state.get("action", "default")
    return action  # Returns node name directly
```

#### Check Message Type

```python
from langchain_core.messages import AIMessage, ToolMessage

def route_by_message(state: MyAgentState) -> str:
    """Route based on last message type."""
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):
        return "process_ai"
    elif isinstance(last_message, ToolMessage):
        return "process_tool"
    else:
        return "process_other"
```

#### Check Threshold

```python
def route_by_score(state: MyAgentState) -> str:
    """Route based on score threshold."""
    score = state.get("score", 0)

    if score >= 0.8:
        return "high_confidence"
    elif score >= 0.5:
        return "medium_confidence"
    else:
        return "low_confidence"
```

#### Check Counter (Max Iterations)

```python
def check_iterations(state: MyAgentState) -> str:
    """Stop after max iterations."""
    max_iterations = 10
    current = state.get("step_count", 0)

    if current >= max_iterations:
        return END  # Stop graph
    else:
        return "continue_processing"
```

#### Tool Calls Check

```python
from langchain_core.messages import AIMessage

def should_continue(state: MyAgentState) -> str:
    """Check if agent made tool calls."""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    else:
        return "end"
```

## Entry Point

### Set Entry Point

```python
# In graph.py
builder.set_entry_point("start_node")
# Or
builder.add_edge(START, "start_node")
```

**First node executed when graph invoked.**

## Complete Edge Patterns

### Pattern: Linear Flow

```python
# Sequential execution
builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")
builder.add_edge("step3", END)
```

### Pattern: Branch and Merge

```python
# Branch on condition, merge back
builder.add_conditional_edges(
    "decision",
    path=decide_route,
    path_map={
        "path_a": "process_a",
        "path_b": "process_b",
    }
)
builder.add_edge("process_a", "merge")
builder.add_edge("process_b", "merge")
builder.add_edge("merge", END)
```

### Pattern: Loop Until Condition

```python
# Loop until done
builder.add_conditional_edges(
    "check",
    path=check_done,
    path_map={
        "continue": "process",
        "done": END,
    }
)
builder.add_edge("process", "check")  # Loop back
```

**Visual:**
```
check ──> process ──┐
  │                 │
  │←────────────────┘
  ↓
 END
```

### Pattern: ReAct Agent Loop

```python
# Agent → Tools → Agent loop
from langgraph.prebuilt import ToolNode

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    }
)
builder.add_edge("tools", "agent")  # Loop
```

## Act Project Structure

### File Organization

**File:** `casts/my_agent/conditions.py`
```python
"""Routing conditions for MyAgent."""

from casts.my_agent.state import MyAgentState
from langgraph.graph import END

def route_main(state: MyAgentState) -> str:
    """Main routing decision."""
    # Logic
    return "next_node"

def should_continue(state: MyAgentState) -> str:
    """Check continuation condition."""
    # Logic
    return "continue" or "end"
```

**Import in graph:**
```python
# File: casts/my_agent/graph.py
from casts.my_agent.conditions import route_main, should_continue

builder.add_conditional_edges("decision", route_main)
```

## Common Mistakes

### ❌ Condition Returns Node Object

```python
# BAD
def bad_condition(state):
    return ProcessNode()  # Returns object!
```

**Fix:**
```python
# GOOD
def good_condition(state) -> str:
    return "process_node"  # Returns name as string
```

### ❌ Forgetting to Return String

```python
# BAD
def bad_condition(state):
    if state["score"] > 0.5:
        "high"  # Not returned!
    else:
        "low"
```

**Fix:**
```python
# GOOD
def good_condition(state) -> str:
    if state["score"] > 0.5:
        return "high"
    else:
        return "low"
```

### ❌ Condition Returns Invalid Node Name

```python
# BAD
def bad_condition(state):
    return "nonexistent_node"  # Node doesn't exist!
```

**Fix:**
```python
# GOOD
def good_condition(state) -> str:
    return "existing_node"  # Must match add_node() name
```

### ❌ Missing Path in path_map

```python
# BAD
builder.add_conditional_edges(
    "decision",
    route_func,
    path_map={
        "approve": "approve_node",
        # Missing "reject" mapping!
    }
)

def route_func(state):
    return "reject"  # KeyError!
```

**Fix:**
```python
# GOOD
builder.add_conditional_edges(
    "decision",
    route_func,
    path_map={
        "approve": "approve_node",
        "reject": "reject_node",  # Include all paths
    }
)
```

### ❌ Circular Loop Without Exit

```python
# BAD: Infinite loop
builder.add_edge("a", "b")
builder.add_edge("b", "a")  # Loops forever
```

**Fix:**
```python
# GOOD: Conditional exit
builder.add_conditional_edges(
    "b",
    check_done,
    {"continue": "a", "done": END}  # Can exit
)
```

## Decision Framework

```
Flow always A → B?
  → builder.add_edge("a", "b")

Flow depends on state?
  → builder.add_conditional_edges("a", condition_func)

Need clear route names?
  → Use path_map with condition returning keys

Agent calling tools?
  → Use should_continue pattern with ToolNode

Need loop until condition met?
  → Conditional edge back to start with exit path

Multiple nodes merge to one?
  → Static edges from each to merge node
```

## Act Project Conventions

⚠️ **Conditions:**
- Define in: `casts/[cast_name]/conditions.py`
- Return: `str` (node name or path_map key)
- Type hint state parameter
- Add docstring

⚠️ **Edge definitions:**
- All in graph.py `build()` method
- After all add_node() calls
- Before compile()

⚠️ **Node names:**
- Match exactly between add_node() and edges
- Use lowercase with underscores: `process_input`
- Descriptive: `check_score` not `node1`

## Anti-Patterns

- ❌ **Complex logic in conditions** → Extract to node, condition just checks result
- ❌ **Side effects in conditions** → Conditions should be pure functions
- ❌ **Multiple conditions for same source** → Combine into single condition
- ❌ **Returning node instance** → Return string name only
- ❌ **No default path** → Always handle all cases

## References

- Related: `01-core/nodes.md`, `01-core/graph.md`, `04-advanced/subgraphs.md`
- LangGraph docs: https://docs.langchain.com/oss/python/langgraph/use-graph-api
