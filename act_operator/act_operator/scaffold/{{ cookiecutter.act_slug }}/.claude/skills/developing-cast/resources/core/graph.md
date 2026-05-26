# Graph Implementation

Graphs are implemented in `casts/{cast_name}/graph.py` by extending `BaseGraph`.

## Contents

- Import
- Basic Pattern
- With Checkpointing (Persistence)
- With Store (Cross-Thread Memory)
- With Interrupts (Human-in-the-Loop)
- Event Streaming v3 (langgraph v1.2+)
- Typed Invoke v2 (langgraph v1.1+)
- Graceful Shutdown (langgraph v1.2+)
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

## Event Streaming v3 (langgraph v1.2+)

Pass `version="v3"` to `stream_events()`/`astream_events()` for a typed-projection event stream. The returned run object exposes `run.messages`, `run.values`, `run.subgraphs`, `run.tool_calls`, `run.output`, `run.interrupts`, and `run.extensions`.

```python
graph = my_graph.build()

stream = await graph.astream_events({"topic": "ice cream"}, version="v3")

# Token-by-token output
async for message in stream.messages:
    async for token in message.text:
        print(token, end="", flush=True)

# Final state
final_state = await stream.output
```

See the `streaming-cast` skill for projections, custom transformers, subgraph/subagent filtering, and transport integration.

## Typed Invoke v2 (langgraph v1.1+)

Pass `version="v2"` to `invoke()`/`ainvoke()` to get a `GraphOutput` with `.value` and `.interrupts`:

```python
from langgraph.types import GraphOutput

result = graph.invoke({"query": "hello"}, version="v2")
result.value       # dict, Pydantic model, or dataclass (auto-coerced)
result.interrupts  # tuple of Interrupt objects (replaces v1's __interrupt__ key)
```

`version="v2"` is opt-in. `GraphOutput` supports dict-style access for gradual migration.

## Graceful Shutdown (langgraph v1.2+)

Stop an in-flight graph run cooperatively after the current superstep completes, saving a resumable checkpoint. Useful for handling SIGTERM signals or external supervisors that need to reclaim resources without losing work.

Create a `RunControl` and pass it as `control=` to `invoke()` / `stream_events()` / `astream_events()`. Call `request_drain()` from any thread to signal that the run should stop:

```python
import signal
from langgraph.types import Command, RunControl
from langgraph.errors import GraphDrained

control = RunControl()

def on_sigterm(signum, frame):
    control.request_drain(reason="SIGTERM received")

signal.signal(signal.SIGTERM, on_sigterm)

config = {"configurable": {"thread_id": "session-1"}}

try:
    stream = await graph.astream_events(
        inputs,
        config=config,
        version="v3",
        control=control,
    )
    async for message in stream.messages:
        async for token in message.text:
            print(token, end="", flush=True)
except GraphDrained:
    # Run paused after the current superstep, checkpoint saved
    pass

# Resume later with the same config
stream = await graph.astream_events(Command(resume=None), config=config, version="v3")
final_state = await stream.output
```

> **Requirements:** A checkpointer must be attached at compile time for the drained run to be resumable.

Inside nodes, read `runtime.drain_requested` to skip expensive work before the next superstep boundary — see node.md § "Graceful Drain Inside Nodes".

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
