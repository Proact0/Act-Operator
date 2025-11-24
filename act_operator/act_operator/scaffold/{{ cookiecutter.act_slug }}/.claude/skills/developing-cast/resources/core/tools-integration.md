# Tools Integration

## When to Use This Resource
Read this when creating tools, integrating ToolNode, binding tools to LLMs, or deciding where tools should live in your project.

## Key Concepts

**Tool** = A function that LLMs can call to perform actions (search, calculate, fetch data, etc.).

**@tool decorator** = Converts a Python function into a LangChain tool.

**ToolNode** = LangGraph component that automatically executes tool calls from LLMs.

**bind_tools** = Attaches tools to an LLM so it knows they're available.

## Creating Tools

### Basic Tool with @tool Decorator

```python
from langchain_core.tools import tool

@tool
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    return a + b
```

**Key points:**
- Docstring is CRITICAL—LLM uses it to understand the tool
- Type hints help LLM use correct argument types
- Function name should be descriptive

### Tool with Complex Return Types

```python
from typing import Annotated
from langchain_core.tools import tool

@tool
def search_database(
    query: Annotated[str, "The search query"],
    limit: Annotated[int, "Max results"] = 10
) -> dict:
    """Search the database for matching records.

    Returns a dict with 'results' list and 'count' integer.
    """
    results = perform_search(query, limit)
    return {"results": results, "count": len(results)}
```

**Annotated** provides extra context for the LLM about parameters.

### Accessing Runtime Context in Tools

```python
from langchain_core.tools import tool, InjectedToolRuntime
from typing import Annotated

@tool
def get_user_preference(
    preference_key: str,
    runtime: Annotated[InjectedToolRuntime, ...],
) -> str:
    """Get user preference from store.

    Args:
        preference_key: The preference to retrieve
        runtime: Auto-injected runtime context
    """
    if runtime and runtime.store:
        return runtime.store.get(
            namespace=("user_prefs",),
            key=preference_key
        )
    return None
```

**InjectedToolRuntime** gives access to:
- `store` - Cross-thread memory
- `stream_writer` - Custom streaming
- Configuration - Thread ID, etc.

## Using ToolNode

**ToolNode** automatically executes tools that the LLM requests.

### Pattern 1: Agent with ToolNode

```python
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

# Define tools
tools = [calculate_sum, search_database]

# Create LLM with bound tools
llm = ChatOpenAI(model="gpt-4").bind_tools(tools)

# Create ToolNode
tool_node = ToolNode(tools)

# In graph
builder.add_node("agent", lambda s: {"messages": [llm.invoke(s["messages"])]})
builder.add_node("tools", tool_node)

# Routing: if LLM wants to call tools, go to tool_node
def should_use_tools(state) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("agent", should_use_tools, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")  # Loop back after tool execution
```

**How it works:**
1. Agent node calls LLM
2. If LLM wants to use a tool, routing sends to tool_node
3. ToolNode executes the tool
4. Results flow back to agent
5. Agent can use results or call more tools

### Pattern 2: Custom Tool Execution

```python
from casts.base_node import BaseNode

class CustomToolNode(BaseNode):
    """Custom tool execution with error handling."""

    def __init__(self, tools: list, **kwargs):
        super().__init__(**kwargs)
        self.tools_by_name = {t.name: t for t in tools}

    def execute(self, state) -> dict:
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", [])

        results = []
        for tool_call in tool_calls:
            tool = self.tools_by_name.get(tool_call["name"])
            if tool:
                try:
                    result = tool.invoke(tool_call["args"])
                    results.append({"tool": tool_call["name"], "result": result})
                except Exception as e:
                    results.append({"tool": tool_call["name"], "error": str(e)})

        return {"tool_results": results}
```

**When to use custom:**
- Need special error handling
- Want to log tool executions
- Need to transform tool results

## Act Project Convention

⚠️ **Tools MUST live in:** `casts/[cast]/modules/tools.py`

```python
# casts/[cast]/modules/tools.pysearch_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    ...

@tool
def database_search(query: str, table: str) -> dict:
    """Search a specific database table."""
    ...

# Export for easy importing
__all__ = ["web_search", "database_search"]
```

**Then in nodes:**
```python
# casts/{ cast_name }/modules/nodes.py
from modules.tools.search_tools import web_search, database_search
from langgraph.prebuilt import ToolNode

tools = [web_search, database_search]
tool_node = ToolNode(tools)
```

## Decision Framework

```
Need LLM to call external functions?
└─ Yes → Create tools with @tool decorator

Tools location:
└─ ALWAYS → casts/[cast]/modules/tools.py[category]_tools.py

Execution approach:
├─ Standard agent pattern → Use ToolNode
├─ Need error handling/logging → Create custom tool execution node
└─ Simple one-off call → Call tool directly in node

Tool needs Store/Runtime access?
└─ Yes → Add InjectedToolRuntime parameter with Annotated
```

## Common Mistakes

❌ **Tools in wrong location**
```python
# ❌ Wrong - tools in cast directory
# casts/{ cast_name }/tools.py

# ✅ Right - tools in modules
# casts/[cast]/modules/tools.pymy_tools.py
```

❌ **Poor docstrings**
```python
@tool
def search(q: str) -> str:
    """Searches."""  # ❌ Vague, unhelpful
    ...

@tool
def search(query: str) -> str:
    """Search the web for current information about a topic.

    Useful when you need up-to-date information that may not be
    in your training data.
    """  # ✅ Clear, detailed
    ...
```

❌ **Forgetting to bind tools to LLM**
```python
llm = ChatOpenAI(model="gpt-4")
# ❌ LLM doesn't know about tools

llm = ChatOpenAI(model="gpt-4").bind_tools(tools)
# ✅ Now LLM can call tools
```

❌ **Not handling tool_calls in routing**
```python
# ❌ No check for tool_calls - tools never executed

# ✅ Check for tool_calls
def should_use_tools(state):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END
```

## References
- LangChain Tools: https://docs.langchain.com/oss/python/langchain/tools
- Related: `implementing-nodes.md` (custom tool execution nodes)
- Related: `../integration/external-apis.md` (tools calling APIs)
- Related: `../memory/cross-thread-memory.md` (InjectedToolRuntime)
