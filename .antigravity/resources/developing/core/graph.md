# Graph Implementation

Graphs are implemented in `casts/{cast_name}/graph.py` by extending `BaseGraph`.

## Contents

- Import
- Basic Pattern
- With Checkpointing (Persistence)
- With Store (Cross-Thread Memory)
- With Interrupts (Human-in-the-Loop)
- Decision Framework
- Common Mistakes

## Import

```python
# casts/{cast_name}/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph
```

## Basic Pattern

```python
# casts/{cast_name}/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from casts.{cast_name}.modules.state import State, InputState, OutputState
from casts.{cast_name}.modules.nodes import InputNode, ProcessNode, OutputNode
from casts.{cast_name}.modules.conditions import should_continue

class {CastName}Graph(BaseGraph):
    """Main graph for {CastName}."""

    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Build and compile the graph."""
        # 1. Create StateGraph with state schema
        builder = StateGraph(
            self.state,
            input_schema=self.input,
            output_schema=self.output
        )

        # 2. Add nodes (must be instances, not classes)
        builder.add_node("input", InputNode())
        builder.add_node("process", ProcessNode(verbose=True))
        builder.add_node("output", OutputNode())

        # 3. Add edges
        builder.add_edge(START, "input")
        builder.add_edge("input", "process")
        builder.add_conditional_edges(
            "process",
            should_continue,
            {"output": "output", "retry": "process", END: END}
        )
        builder.add_edge("output", END)

        # 4. Compile and return
        graph = builder.compile()
        graph.name = self.name
        return graph

# Create graph instance
{cast_name}_graph = {CastName}Graph()
```

**Key steps:**
1. Create `StateGraph(State, input_schema=..., output_schema=...)`
2. Add nodes as **instances** (not classes)
3. Define edges (static and conditional)
4. Compile and return

---

## With Checkpointing (Persistence)

**When to use:** Save state between runs, support interrupts, time-travel debugging.

```python
# casts/{cast_name}/graph.py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

class {CastName}Graph(BaseGraph):
    def __init__(self, checkpointer=None):
        super().__init__()
        self.checkpointer = checkpointer or MemorySaver()

    def build(self):
        builder = StateGraph(State)
        # ... add nodes and edges ...
        
        graph = builder.compile(checkpointer=self.checkpointer)
        graph.name = self.name
        return graph
```

## With Store (Cross-Thread Memory)

**When to use:** Need memory across different threads/conversations.

```python
# casts/{cast_name}/graph.py
from langgraph.store.memory import InMemoryStore

class MemoryEnabledGraph(BaseGraph):
    def __init__(self, store=None, checkpointer=None):
        super().__init__()
        self.store = store or InMemoryStore()
        self.checkpointer = checkpointer

    def build(self):
        builder = StateGraph(State)
        # ... add nodes and edges ...
        
        graph = builder.compile(
            checkpointer=self.checkpointer,
            store=self.store
        )
        graph.name = self.name
        return graph
```

## With Interrupts (Human-in-the-Loop)

**When to use:** Human approval steps, review workflows.

```python
# casts/{cast_name}/graph.py
from langgraph.checkpoint.memory import MemorySaver

class InterruptibleGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)
        # ... add nodes ...
        
        graph = builder.compile(
            checkpointer=MemorySaver(),  # Required for interrupts
            interrupt_before=["approval_node"],  # Pause before
            # OR
            interrupt_after=["data_fetch"]  # Pause after
        )
        graph.name = self.name
        return graph
```

---

## Decision Framework

```
Need state persistence between runs?
├─ Yes → Add checkpointer
│   ├─ Development → MemorySaver()
│   └─ Production → SqliteSaver / PostgresSaver
└─ No → compile() without checkpointer

Need memory across threads?
└─ Yes → Add store (InMemoryStore / PostgresStore)

Need human approval steps?
└─ Yes → Add interrupt_before/interrupt_after
         (Requires checkpointer)
```

---

## Common Mistakes

❌ **Not inheriting from BaseGraph**
```python
class MyGraph:  # ❌ Wrong
    def build(self): ...
```

✅ **Correct**
```python
class MyGraph(BaseGraph):  # ✅
    def build(self): ...
```

❌ **Using interrupts without checkpointer**
```python
builder.compile(interrupt_before=["node"])  # ❌ Needs checkpointer
```

✅ **Correct**
```python
builder.compile(checkpointer=MemorySaver(), interrupt_before=["node"])  # ✅
```

❌ **Wrong START/END usage**
```python
builder.add_edge("START", "first")  # ❌ String "START"
builder.add_edge(START, "first")    # ✅ Imported constant
```

❌ **Adding class instead of instance**
```python
builder.add_node("node", MyNode)    # ❌ Class
builder.add_node("node", MyNode())  # ✅ Instance
```
