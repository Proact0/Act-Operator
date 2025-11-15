# Graph Construction

## When to Use This Resource
Read when building the graph, understanding BaseGraph, or compiling with persistence.

---

## Core Pattern: BaseGraph

**ALL graphs must inherit from BaseGraph (Act requirement)**

```python
# File: casts/my_cast/graph.py

from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph, END, START
from casts.my_cast.state import MyState
from casts.my_cast.nodes import NodeA, NodeB

class MyCastGraph(BaseGraph):
    """Graph for MyCast."""

    def __init__(self):
        super().__init__()  # REQUIRED
        self.state = MyState  # Set state schema

    def build(self):
        """Build and return compiled graph."""
        builder = StateGraph(self.state)

        # Add nodes (as instances!)
        builder.add_node("node_a", NodeA())
        builder.add_node("node_b", NodeB())

        # Add edges
        builder.set_entry_point("node_a")
        builder.add_edge("node_a", "node_b")
        builder.add_edge("node_b", END)

        # Compile
        graph = builder.compile()
        graph.name = self.name  # From BaseGraph

        return graph

# Export instance
my_cast_graph = MyCastGraph()
```

**Key points:**
- Inherit from `BaseGraph`
- Implement `build()` method
- Return compiled graph
- Export instance at module level

---

## Building the Graph

### 1. Create StateGraph

```python
from langgraph.graph import StateGraph
from casts.my_cast.state import MyState

builder = StateGraph(MyState)
```

---

### 2. Add Nodes

```python
from casts.my_cast.nodes import ProcessNode, ChatNode

# Add as INSTANCES, not classes
builder.add_node("process", ProcessNode())
builder.add_node("chat", ChatNode(model=my_model))
```

**CRITICAL:** Pass instances `NodeA()`, not classes `NodeA`

---

### 3. Set Entry Point

```python
from langgraph.graph import START

# Option 1: Use START constant (recommended)
builder.add_edge(START, "first_node")

# Option 2: set_entry_point (legacy)
builder.set_entry_point("first_node")
```

---

### 4. Add Edges

**Static edges:**
```python
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
```

**Conditional edges:**
```python
from casts.my_cast.conditions import route_mode

builder.add_conditional_edges(
    "router_node",
    route_mode,  # Function: (state) -> str
    {
        "search": "search_node",
        "chat": "chat_node"
    }
)
```

**See:** `core/edge-patterns.md` for routing details

---

### 5. Compile

```python
# Basic compilation
graph = builder.compile()

# With persistence
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# With Store
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
```

---

## Complete Example

```python
from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from casts.my_cast.state import MyState
from casts.my_cast.nodes import RouterNode, SearchNode, ChatNode
from casts.my_cast.conditions import route_mode

class MyCastGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.state = MyState

    def build(self):
        builder = StateGraph(self.state)

        # Nodes
        builder.add_node("router", RouterNode())
        builder.add_node("search", SearchNode())
        builder.add_node("chat", ChatNode())

        # Flow
        builder.add_edge(START, "router")

        builder.add_conditional_edges(
            "router",
            route_mode,
            {"search": "search", "chat": "chat"}
        )

        builder.add_edge("search", END)
        builder.add_edge("chat", END)

        # Persistence
        graph = builder.compile(
            checkpointer=MemorySaver(),
            store=InMemoryStore()
        )

        return graph

my_cast_graph = MyCastGraph()
```

---

## Input/Output Schemas

```python
from casts.my_cast.state import InputState, OutputState, State

builder = StateGraph(
    State,  # Internal state
    input=InputState,  # What graph receives
    output=OutputState  # What graph returns
)
```

---

## Running the Graph

### Basic Invocation

```python
graph = my_cast_graph.build()

result = graph.invoke({"query": "hello"})
print(result)
```

---

### With Config (thread_id)

```python
config = {
    "configurable": {
        "thread_id": "user_123"
    }
}

result = graph.invoke(
    {"query": "hello"},
    config=config
)
```

---

### Async Invocation

```python
import asyncio

async def run():
    result = await graph.ainvoke(
        {"query": "hello"},
        config=config
    )
    return result

result = asyncio.run(run())
```

**CRITICAL:** If using async checkpointer or async nodes, MUST use `ainvoke()`, not `invoke()`

---

## Anti-Patterns

### ❌ Not Inheriting BaseGraph

```python
# ❌ WRONG
def create_graph():
    builder = StateGraph(MyState)
    return builder.compile()
```

```python
# ✓ CORRECT
class MyCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(self.state)
        return builder.compile()
```

---

### ❌ Adding Classes Instead of Instances

```python
# ❌ WRONG
builder.add_node("my_node", MyNode)  # Class
```

```python
# ✓ CORRECT
builder.add_node("my_node", MyNode())  # Instance
```

---

### ❌ Missing super().__init__()

```python
class MyCastGraph(BaseGraph):
    def __init__(self):
        # ❌ Missing super().__init__()
        self.state = MyState
```

```python
class MyCastGraph(BaseGraph):
    def __init__(self):
        super().__init__()  # ✓ REQUIRED
        self.state = MyState
```

---

## References
- patterns/act-conventions.md (BaseGraph requirements)
- core/node-patterns.md (creating nodes)
- core/edge-patterns.md (routing logic)
- memory/short-term-memory.md (checkpointers)
- memory/long-term-memory.md (Store initialization)
