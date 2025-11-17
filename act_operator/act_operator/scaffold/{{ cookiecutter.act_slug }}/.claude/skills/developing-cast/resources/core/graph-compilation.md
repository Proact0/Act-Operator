# Graph Compilation

## When to Use This Resource
Read this when creating graph.py, compiling StateGraph, or using BaseGraph to build your complete graph.

## Key Concepts

**StateGraph** = LangGraph builder for creating state-based workflows.

**CompiledStateGraph** = Executable graph after calling `.compile()`.

**BaseGraph** = Act project base class that ALL graphs must inherit from.

## Basic Graph Pattern

### Using BaseGraph (Required in Act Projects)

```python
# casts/my_cast/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from .state import MyCastState
from .nodes import InputNode, ProcessNode, OutputNode
from .conditions import should_continue

class MyCastGraph(BaseGraph):
    """Main graph for MyCast."""

    def build(self) -> CompiledStateGraph:
        """Build and compile the graph."""
        # 1. Create StateGraph with state schema
        builder = StateGraph(MyCastState)

        # 2. Instantiate nodes
        input_node = InputNode()
        process_node = ProcessNode(verbose=True)
        output_node = OutputNode()

        # 3. Add nodes
        builder.add_node("input", input_node)
        builder.add_node("process", process_node)
        builder.add_node("output", output_node)

        # 4. Add edges
        builder.add_edge(START, "input")
        builder.add_edge("input", "process")
        builder.add_conditional_edges(
            "process",
            should_continue,
            {"output": "output", "retry": "process", END: END}
        )
        builder.add_edge("output", END)

        # 5. Compile and return
        return builder.compile()
```

**Key steps:**
1. Create `StateGraph(YourState)`
2. Instantiate node instances
3. Add nodes to graph
4. Define edges (static and conditional)
5. Compile and return

### Using the Graph

```python
# Somewhere else (e.g., main.py, API endpoint)
from casts.my_cast.graph import MyCastGraph

# Instantiate graph class
graph_builder = MyCastGraph()

# Build (compile) the graph
compiled_graph = graph_builder.build()  # or graph_builder()

# Invoke
result = compiled_graph.invoke({"input": "Hello"})
```

## Adding Checkpointing (Persistence)

**When to use:** Need to save state between runs, support interrupts, or enable time-travel debugging.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

class MyCastGraph(BaseGraph):
    def build(self, checkpointer=None) -> CompiledStateGraph:
        builder = StateGraph(MyCastState)

        # ... add nodes and edges ...

        # Compile with checkpointer
        return builder.compile(checkpointer=checkpointer)

# Usage
memory_saver = MemorySaver()  # In-memory (dev/testing)
# OR
sqlite_saver = SqliteSaver.from_conn_string("checkpoints.db")  # Persistent

graph = MyCastGraph().build(checkpointer=sqlite_saver)

# Now supports thread_id for separate conversations
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"input": "..."}, config=config)
```

**See:** `../memory/checkpoints-persistence.md` for details.

## Advanced Compilation Options

### Pattern: Graph with Store (Cross-Thread Memory)

```python
from langgraph.store.memory import InMemoryStore

class MemoryEnabledGraph(BaseGraph):
    def build(self, store=None, checkpointer=None):
        builder = StateGraph(GraphState)

        # ... add nodes and edges ...

        compiled = builder.compile(
            checkpointer=checkpointer,
            store=store  # Enable Store for cross-thread memory
        )

        return compiled

# Usage
store = InMemoryStore()
graph = MemoryEnabledGraph().build(store=store, checkpointer=MemorySaver())
```

**When to use:** Need memory across different threads/conversations.

**See:** `../memory/cross-thread-memory.md` for Store details.

### Pattern: Graph with Interrupts

```python
from langgraph.graph import StateGraph, START, END

class InterruptibleGraph(BaseGraph):
    def build(self):
        builder = StateGraph(GraphState)

        # ... add nodes ...

        # Compile with interrupt_before or interrupt_after
        return builder.compile(
            checkpointer=MemorySaver(),  # Required for interrupts
            interrupt_before=["approval_node"],  # Pause before this node
            # OR
            interrupt_after=["data_fetch"]  # Pause after this node
        )
```

**When to use:** Human-in-the-loop workflows, approval steps.

**See:** `../advanced/interrupts-hitl.md` for complete patterns.

## Act Project Structure

Complete graph.py example:

```python
# casts/my_cast/graph.py
"""Graph definition for MyCast."""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from casts.base_graph import BaseGraph

from .state import MyCastState
from .nodes import (
    InputNode,
    ProcessNode,
    OutputNode,
)
from .conditions import should_continue, route_by_intent

class MyCastGraph(BaseGraph):
    """MyCast main graph."""

    def __init__(self, checkpointer=None, **kwargs):
        super().__init__()
        self.checkpointer = checkpointer or SqliteSaver.from_conn_string(":memory:")

    def build(self):
        """Build the graph structure."""
        builder = StateGraph(MyCastState)

        # Initialize nodes
        input_node = InputNode()
        process_node = ProcessNode(verbose=True)
        output_node = OutputNode()

        # Add nodes
        builder.add_node("input", input_node)
        builder.add_node("process", process_node)
        builder.add_node("output", output_node)

        # Add edges
        builder.add_edge(START, "input")
        builder.add_conditional_edges("input", route_by_intent, [...])
        builder.add_edge("process", "output")
        builder.add_edge("output", END)

        # Compile
        return builder.compile(checkpointer=self.checkpointer)
```

## Decision Framework

```
Graph needs to persist state between runs?
├─ Yes → Add checkpointer parameter
│   ├─ Development/testing → MemorySaver()
│   └─ Production → SqliteSaver or PostgresSaver
└─ No → compile() without checkpointer

Need memory across threads/conversations?
└─ Yes → Add store parameter with InMemoryStore/PostgresStore

Need human approval steps?
└─ Yes → Add interrupt_before/interrupt_after
         (Requires checkpointer)

Multiple graphs in project?
└─ Each gets its own class in casts/[cast_name]/graph.py
```

## Common Mistakes

❌ **Not inheriting from BaseGraph**
```python
class MyGraph:  # ❌ Should inherit from BaseGraph
    def build(self):
        ...
```

❌ **Forgetting to compile**
```python
def build(self):
    builder = StateGraph(State)
    # ... add nodes/edges ...
    return builder  # ❌ Should be builder.compile()
```

❌ **Using interrupts without checkpointer**
```python
builder.compile(interrupt_before=["node"])  # ❌ Needs checkpointer
builder.compile(checkpointer=MemorySaver(), interrupt_before=["node"])  # ✅
```

❌ **Wrong START/END usage**
```python
builder.add_edge("START", "first")  # ❌ String "START"
builder.add_edge(START, "first")    # ✅ Imported START constant

from langgraph.graph import START, END  # Must import
```

## Invoking Compiled Graphs

### Simple Invocation
```python
result = graph.invoke({"input": "test"})
```

### With Thread Support
```python
config = {"configurable": {"thread_id": "conversation-1"}}
result = graph.invoke({"input": "test"}, config=config)
```

### Streaming Results
```python
for chunk in graph.stream({"input": "test"}, config=config):
    print(chunk)
```

**See:** `../advanced/streaming.md` for streaming patterns.

## References
- BaseGraph source: `casts/base_graph.py`
- Related: `state-management.md` (StateGraph state schema)
- Related: `implementing-nodes.md` (nodes to add to graph)
- Related: `edge-patterns.md` (edges to add to graph)
- Related: `../memory/checkpoints-persistence.md`
- Related: `../advanced/interrupts-hitl.md`
