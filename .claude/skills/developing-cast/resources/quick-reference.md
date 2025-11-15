# Quick Reference

## One-Page Cheatsheet for LangGraph Implementation

### State Schema

```python
from typing import TypedDict, Annotated
from operator import add

class MyState(TypedDict):
    messages: Annotated[list, add]  # Accumulates
    data: dict  # Replaces
```

### Node Class

```python
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state: MyState) -> dict:
        return {"result": "value"}
```

### Graph Class

```python
from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph, END

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MyState)
        builder.add_node("node1", MyNode())
        builder.set_entry_point("node1")
        builder.add_edge("node1", END)
        return builder.compile()
```

### Edges

```python
# Static
builder.add_edge("a", "b")

# Conditional
builder.add_conditional_edges("a", condition_func, path_map)

# Condition function (in conditions.py)
def condition_func(state: MyState) -> str:
    return "next_node_name"
```

### Tools

```python
# File: modules/tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description for LLM."""
    return result
```

### Tool Integration

```python
from langgraph.prebuilt import ToolNode
from modules.tools import my_tool

tools = [my_tool]
model_with_tools = model.bind_tools(tools)

builder.add_node("agent", AgentNode(model_with_tools))
builder.add_node("tools", ToolNode(tools))

builder.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
builder.add_edge("tools", "agent")
```

### Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "123"}}
result = graph.invoke(input, config)
```

### Runtime Access

```python
from langgraph.runtime import Runtime

class MyNode(BaseNode):
    def execute(
        self,
        state: MyState,
        runtime: Runtime = None,
        **kwargs
    ) -> dict:
        if runtime and runtime.store:
            data = runtime.store.get(("user", user_id), "key")
        return {"data": data}
```

### Interrupts

```python
from langgraph.types import interrupt

class ReviewNode(BaseNode):
    def execute(self, state) -> dict:
        approval = interrupt("Review needed")
        return {"approved": approval}
```

### Common Patterns

**ReAct Agent:**
```python
builder.add_node("agent", AgentNode(model.bind_tools(tools)))
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
builder.add_edge("tools", "agent")
```

**Iteration Limit:**
```python
def should_continue(state) -> str:
    if state.get("iteration_count", 0) >= 10:
        return "end"
    # ... check other conditions
```

**Error Handling:**
```python
try:
    result = operation()
    return {"result": result, "error": None}
except Exception as e:
    return {"error": str(e)}
```

### File Locations (Act Project)

```
casts/[cast_name]/
  state.py         - State schema
  nodes.py         - Node classes
  conditions.py    - Routing functions
  graph.py         - Graph class

modules/tools/     - ALL tools here
```

### Execution

```python
# Sync
result = graph.invoke(input, config)

# Async
result = await graph.ainvoke(input, config)

# Streaming
for chunk in graph.stream(input, config):
    print(chunk)
```

### Key Principles

1. **All nodes inherit BaseNode**
2. **All graphs inherit BaseGraph**
3. **Tools ONLY in modules/tools**
4. **execute() returns dict of updates**
5. **Use reducers for accumulation**
6. **Config with thread_id for persistence**

### Common Mistakes

- ❌ Tools not in modules/tools
- ❌ Node doesn't inherit BaseNode
- ❌ Forgetting reducer for lists
- ❌ No thread_id with checkpointer
- ❌ Returning None from execute()

### Next Steps

- Implementing from architecture? → `from-architecture.md`
- Need details on specific topic? → Navigate to resource in SKILL.md
