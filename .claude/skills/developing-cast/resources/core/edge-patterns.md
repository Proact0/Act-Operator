# Edge Patterns

## When to Use This Resource
Read when connecting nodes, implementing routing logic, or using conditional edges.

---

## Edge Types

### Static Edges (Sequential Flow)

```python
# Direct connection: node_a → node_b
builder.add_edge("node_a", "node_b")

# Multiple sequential edges
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_c")
builder.add_edge("node_c", END)
```

**Use when:** Flow is always the same, no decisions needed

---

### Conditional Edges (Branching)

```python
from casts.my_cast.conditions import route_mode

builder.add_conditional_edges(
    "router_node",  # Source node
    route_mode,  # Routing function
    {  # Mapping: return value → target node
        "search": "search_node",
        "chat": "chat_node",
        "help": "help_node"
    }
)
```

**Use when:** Flow depends on state (routing decisions)

---

## Routing Functions (conditions.py)

### Basic Router

```python
# File: casts/my_cast/conditions.py

def route_mode(state: dict) -> str:
    """Routes based on mode field.

    Args:
        state: Current graph state

    Returns:
        Next node name as string
    """
    mode = state.get("mode", "default")

    if mode == "search":
        return "search_node"
    elif mode == "chat":
        return "chat_node"
    else:
        return "default_node"  # Always have fallback
```

**Key points:**
- Function signature: `(state: dict) -> str`
- Returns next node name as string
- Always include fallback/default case

---

### Tool Routing Pattern

```python
from langgraph.prebuilt import tools_condition

def should_continue(state: dict) -> str:
    """Determines if tools should be called.

    Args:
        state: Graph state with messages

    Returns:
        "tools" or "end"
    """
    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    # Check if LLM wants to call tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"
```

**Usage:**
```python
builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tool_node", "end": END}
)
```

---

### Multi-Way Routing

```python
def classify_intent(state: dict) -> str:
    """Classifies user intent for routing.

    Returns: "search" | "synthesis" | "chat" | "help"
    """
    query = state.get("query", "").lower()

    # Keyword-based classification
    if any(word in query for word in ["search", "find", "look up"]):
        return "search"
    elif any(word in query for word in ["summarize", "synthesize"]):
        return "synthesis"
    elif any(word in query for word in ["help", "how to"]):
        return "help"
    else:
        return "chat"


# In graph:
builder.add_conditional_edges(
    "classifier",
    classify_intent,
    {
        "search": "search_node",
        "synthesis": "synthesis_node",
        "help": "help_node",
        "chat": "chat_node"
    }
)
```

---

### LLM-Based Routing

```python
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4")

def llm_route(state: dict) -> str:
    """Uses LLM to determine routing.

    Returns: Node name
    """
    query = state.get("query", "")

    prompt = f"""Classify this query into one category:
- "search" for information lookup
- "chat" for conversation
- "help" for assistance

Query: {query}

Respond with only the category name."""

    response = model.invoke([HumanMessage(content=prompt)])
    category = response.content.strip().lower()

    # Map to node names
    mapping = {
        "search": "search_node",
        "chat": "chat_node",
        "help": "help_node"
    }

    return mapping.get(category, "chat_node")  # Fallback
```

---

## Entry Points

### Using START Constant

```python
from langgraph.graph import START

# Recommended approach
builder.add_edge(START, "first_node")
```

---

### Using set_entry_point

```python
# Legacy approach (still works)
builder.set_entry_point("first_node")
```

---

## END Constant

### Ending Graph Execution

```python
from langgraph.graph import END

# Terminal edge
builder.add_edge("last_node", END)

# Conditional ending
builder.add_conditional_edges(
    "decision_node",
    should_end,
    {"continue": "next_node", "end": END}
)
```

---

## Common Patterns

### Linear Flow

```python
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_c")
builder.add_edge("node_c", END)

# START → node_a → node_b → node_c → END
```

---

### Branch and Merge

```python
# Branch
builder.add_conditional_edges(
    "router",
    route,
    {"path_a": "node_a", "path_b": "node_b"}
)

# Merge back
builder.add_edge("node_a", "merge")
builder.add_edge("node_b", "merge")
builder.add_edge("merge", END)
```

---

### Loop Pattern

```python
def should_continue(state: dict) -> str:
    """Decides to continue or end loop."""
    count = state.get("count", 0)
    return "continue" if count < 5 else "end"

builder.add_edge(START, "process")
builder.add_conditional_edges(
    "process",
    should_continue,
    {
        "continue": "process",  # Loop back
        "end": END
    }
)
```

---

### ReAct Agent Pattern

```python
from langgraph.prebuilt import ToolNode

# Agent node → Tools → Agent (loop until done)
tools = [web_search, calculator]
tool_node = ToolNode(tools)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,  # Checks for tool_calls
    {"tools": "tools", "end": END}
)
builder.add_edge("tools", "agent")  # Back to agent
```

---

## Anti-Patterns

### ❌ Router Without Fallback

```python
def route(state):
    mode = state.get("mode")  # Could be None!

    if mode == "search":
        return "search"
    elif mode == "chat":
        return "chat"
    # ❌ Missing else - what if mode is unexpected?
```

```python
def route(state):
    mode = state.get("mode", "default")  # ✓ Default value

    if mode == "search":
        return "search"
    elif mode == "chat":
        return "chat"
    else:
        return "default"  # ✓ Fallback
```

---

### ❌ Returning Wrong Type

```python
def route(state):
    return ["search", "chat"]  # ❌ List, should be string
```

```python
def route(state):
    return "search"  # ✓ String
```

---

### ❌ Missing Mapping Entry

```python
# Router can return "search", "chat", or "help"
builder.add_conditional_edges(
    "router",
    route,
    {
        "search": "search_node",
        "chat": "chat_node"
        # ❌ Missing "help" mapping!
    }
)
```

```python
builder.add_conditional_edges(
    "router",
    route,
    {
        "search": "search_node",
        "chat": "chat_node",
        "help": "help_node"  # ✓ Complete
    }
)
```

---

## Decision Framework

**Q: Static or conditional edge?**
- Always same flow → Static edge
- Depends on state → Conditional edge

**Q: Where to put routing logic?**
- In `conditions.py` file (Act convention)
- NOT in nodes or graph.py

**Q: How to decide routing logic?**
- Simple keywords → if/elif checks
- Complex classification → Use LLM
- Tool calling → Use tools_condition helper

---

## References
- patterns/act-conventions.md (conditions.py location)
- core/graph-construction.md (building graph)
- core/node-patterns.md (node implementation)
