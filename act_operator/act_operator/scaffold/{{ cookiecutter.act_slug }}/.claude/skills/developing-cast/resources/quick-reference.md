# Quick Reference

## Most Common Patterns

### Basic Node
```python
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state) -> dict:
        return {"result": "value"}
```

### Async Node
```python
from casts.base_node import AsyncBaseNode

class MyAsyncNode(AsyncBaseNode):
    async def execute(self, state) -> dict:
        result = await async_operation()
        return {"result": result}
```

### Node with Config/Runtime
```python
class AdvancedNode(BaseNode):
    def execute(self, state, config=None, runtime=None) -> dict:
        thread_id = self.get_thread_id(config)

        if runtime and runtime.store:
            data = runtime.store.get(namespace=("ns",), key="key")

        return {"data": data}
```

### State Schema
```python
from typing import TypedDict, Annotated
from langgraph.graph import add

class MyState(TypedDict):
    input: str                              # Simple field
    messages: Annotated[list[dict], add]   # List with append
    result: str | None                      # Optional field
```

### Graph
```python
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MyState)

        builder.add_node("node1", Node1())
        builder.add_node("node2", Node2())

        builder.add_edge(START, "node1")
        builder.add_edge("node1", "node2")
        builder.add_edge("node2", END)

        return builder.compile()
```

### Conditional Routing
```python
def route(state: dict) -> str:
    if state.get("condition"):
        return "node_a"
    else:
        return "node_b"

builder.add_conditional_edges(
    "source",
    route,
    ["node_a", "node_b"]
)
```

### Tool
```python
from langchain_core.tools import tool

@tool
def my_tool(arg: str) -> str:
    """Tool description for LLM.

    Args:
        arg: Argument description
    """
    return f"Result: {arg}"
```

### Tool with Runtime
```python
from langchain_core.tools import tool, InjectedToolRuntime
from typing import Annotated

@tool
def memory_tool(
    key: str,
    runtime: Annotated[InjectedToolRuntime, ...]
) -> str:
    """Tool with Store access."""
    if runtime and runtime.store:
        return runtime.store.get(namespace=("ns",), key=key)
    return None
```

### Checkpointer
```python
from langgraph.checkpoint.sqlite import SqliteSaver

graph = builder.compile(
    checkpointer=SqliteSaver.from_conn_string("memory.db")
)

# Invoke with thread_id
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"input": "..."}, config=config)
```

### Store (Cross-Thread Memory)
```python
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(conn_string)

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)

# In node
def execute(self, state, runtime=None, **kwargs):
    if runtime and runtime.store:
        runtime.store.put(
            namespace=("user", "123"),
            key="prefs",
            value={"theme": "dark"}
        )
```

### Interrupts
```python
# Compile with interrupt
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["approval_node"]
)

# Invoke - will pause
graph.invoke({"input": "..."}, config=config)

# Resume
graph.invoke(None, config=config)
```

### Or use interrupt() function
```python
from langgraph.graph import interrupt

class ApprovalNode(BaseNode):
    def execute(self, state) -> dict:
        approval = interrupt({"message": "Approve?"})

        if approval.get("approved"):
            return {"status": "approved"}
        return {"status": "rejected"}
```

### Streaming
```python
# Stream updates
for chunk in graph.stream({"input": "..."}, stream_mode="updates"):
    print(chunk)

# Stream full state
for chunk in graph.stream({"input": "..."}, stream_mode="values"):
    print(chunk)

# Async stream
async for chunk in graph.astream({"input": "..."}, stream_mode="values"):
    await process(chunk)
```

### Error Handling
```python
class RobustNode(BaseNode):
    def execute(self, state) -> dict:
        try:
            result = risky_operation(state)
            return {"result": result, "error": None}
        except Exception as e:
            self.log(f"Error: {e}")
            return {"result": None, "error": str(e)}
```

### Retry Loop
```python
def should_retry(state: dict) -> str:
    if state.get("error") and state.get("retries", 0) < 3:
        return "retry_node"
    elif state.get("error"):
        return "give_up"
    return "success"

builder.add_conditional_edges(
    "attempt",
    should_retry,
    {"retry_node": "attempt", "give_up": END, "success": "next"}
)
```

### Subgraph
```python
# Build subgraph
sub_builder = StateGraph(SubState)
# ... add nodes/edges ...
subgraph = sub_builder.compile()

# Use as node in parent
parent_builder.add_node("subgraph_step", subgraph)
```

### MCP Integration
```python
from langchain_mcp_adapters import MultiServerMCPClient

mcp_config = {
    "server": {
        "transport": "stdio",
        "command": "mcp-server",
        "args": []
    }
}

mcp_client = MultiServerMCPClient(mcp_config)
tools = mcp_client.get_tools()

# Use tools in graph
tool_node = ToolNode(tools)
builder.add_node("tools", tool_node)
```

## File Locations Cheatsheet

| What | Where |
|------|-------|
| State schema | `casts/[cast]/modules/state.py` |
| Nodes | `casts/[cast]/modules/nodes.py` |
| Graph | `casts/[cast]/graph.py` |
| Routing functions | `casts/[cast]/modules/conditions.py` |
| Tools | `casts/[cast]/modules/tools.py` |
| Prompts | `casts/[cast]/modules/prompts.py` |
| Base classes | `casts/base_node.py`, `casts/base_graph.py` |

## Common Imports

```python
# Base classes
from casts.base_node import BaseNode, AsyncBaseNode
from casts.base_graph import BaseGraph

# State
from typing import TypedDict, Annotated
from langgraph.graph import add

# Graph building
from langgraph.graph import StateGraph, START, END

# Checkpointers
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver

# Store
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

# Tools
from langchain_core.tools import tool, InjectedToolRuntime
from langgraph.prebuilt import ToolNode

# Interrupts
from langgraph.graph import interrupt

# LLMs
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
```

## Decision Trees

### Choose Node Type
```
Async operations (API calls, I/O)?
├─ Yes → AsyncBaseNode
└─ No  → BaseNode
```

### Choose State Type
```
Need validation/defaults?
├─ Yes → Pydantic BaseModel
└─ No  → TypedDict
```

### Choose Memory
```
Need to remember...
├─ During this run only → State
├─ Across conversation → Checkpointer
└─ Across all conversations → Store
```

### Choose Implementation Location
```
LLM should call it?
├─ Yes → Tool in modules/tools.py
└─ No  → Node in modules/nodes.py
```

## References
See detailed resources in `resources/` for comprehensive patterns and best practices.
