# Graph Building and Compilation

## When to Use This Resource

Read this when creating StateGraph, compiling graphs, or fixing graph execution issues.

## Key Concepts

**StateGraph:** Graph that maintains state passed between nodes.

**Compilation:** Converts graph definition into executable form.

**BaseGraph:** Act project base class for all graphs.

**Config:** Runtime configuration (thread_id, checkpointer, etc.).

**Checkpointer:** Persistence layer for state snapshots.

## Graph Pattern (Required in Act)

### Pattern 1: Basic Graph (Inherits BaseGraph)

**When to use:** All Act projects

```python
# File: casts/my_agent/graph.py
from langgraph.graph import StateGraph, END
from casts.base_graph import BaseGraph
from casts.my_agent.state import MyAgentState
from casts.my_agent.nodes import StartNode, ProcessNode

class MyAgentGraph(BaseGraph):
    """Main graph for MyAgent cast."""

    def build(self) -> StateGraph:
        """Build and compile the graph.

        Returns:
            Compiled StateGraph
        """
        # Create StateGraph with state schema
        builder = StateGraph(MyAgentState)

        # Instantiate nodes
        start = StartNode()
        process = ProcessNode()

        # Add nodes
        builder.add_node("start", start)
        builder.add_node("process", process)

        # Add edges
        builder.set_entry_point("start")
        builder.add_edge("start", "process")
        builder.add_edge("process", END)

        # Compile and return
        return builder.compile()
```

**Key points:**
- Inherit from `BaseGraph`
- Implement `build()` method
- Return compiled graph
- Create StateGraph with state schema

### Pattern 2: Graph with Checkpointer (Persistence)

**When to use:** Need to save state between runs, support interrupts

```python
from langgraph.checkpoint.memory import MemorySaver
from casts.base_graph import BaseGraph

class PersistentGraph(BaseGraph):
    """Graph with state persistence."""

    def __init__(self, checkpointer=None):
        super().__init__()
        self.checkpointer = checkpointer or MemorySaver()

    def build(self):
        builder = StateGraph(MyAgentState)

        # Add nodes and edges...
        builder.add_node("start", StartNode())
        builder.set_entry_point("start")
        builder.add_edge("start", END)

        # Compile with checkpointer
        return builder.compile(checkpointer=self.checkpointer)
```

**Usage:**
```python
# With default MemorySaver
graph = PersistentGraph()

# With production checkpointer
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
graph = PersistentGraph(checkpointer=checkpointer)
```

### Pattern 3: Graph with Dependencies

**When to use:** Nodes need LLM, tools, external clients

```python
from langchain_anthropic import ChatAnthropic
from modules.tools import search_tool, calculator_tool

class AgentGraph(BaseGraph):
    """Graph with LLM and tools."""

    def __init__(self, model_name: str = "claude-sonnet-4"):
        super().__init__()
        self.model = ChatAnthropic(model=model_name)
        self.tools = [search_tool, calculator_tool]

    def build(self):
        builder = StateGraph(AgentState)

        # Create nodes with dependencies
        from casts.my_agent.nodes import AgentNode
        agent = AgentNode(self.model, self.tools)

        builder.add_node("agent", agent)
        # ... rest of graph

        return builder.compile()
```

## Compiling Graphs

### Compile Options

```python
# Basic compilation
graph = builder.compile()

# With checkpointer
graph = builder.compile(checkpointer=MemorySaver())

# With interrupt before nodes
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human_review"],  # Pause before this node
)

# With interrupt after nodes
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_after=["sensitive_operation"],  # Pause after this node
)
```

**When to use interrupts:** Human-in-the-loop workflows, approval gates

## Executing Graphs

### Pattern: Basic Invocation

```python
# Instantiate graph
graph_instance = MyAgentGraph()
graph = graph_instance.build()

# Invoke (synchronous)
result = graph.invoke({
    "messages": [],
    "current_task": "Process this",
})

# Access results
print(result["results"])
```

### Pattern: With Config (thread_id)

```python
from langgraph.checkpoint.memory import MemorySaver

# Graph with checkpointer
graph_instance = PersistentGraph(checkpointer=MemorySaver())
graph = graph_instance.build()

# Config with thread_id
config = {"configurable": {"thread_id": "user-123"}}

# First invocation
result1 = graph.invoke(
    {"messages": [], "task": "First task"},
    config=config
)

# Second invocation (resumes from checkpoint)
result2 = graph.invoke(
    {"messages": result1["messages"], "task": "Second task"},
    config=config
)
```

### Pattern: Async Execution

```python
# For AsyncBaseNode graphs
async def run_graph():
    graph = MyAgentGraph().build()

    result = await graph.ainvoke({
        "messages": [],
        "task": "Async task",
    })

    return result

# Run
import asyncio
result = asyncio.run(run_graph())
```

### Pattern: Streaming

```python
# Stream state updates
for chunk in graph.stream({"messages": [], "task": "Stream task"}):
    print(chunk)  # Each node's output

# Stream with config
config = {"configurable": {"thread_id": "123"}}
for chunk in graph.stream({"task": "Task"}, config=config):
    print(chunk)
```

### Pattern: Stream Mode Options

```python
# Stream updates only (default)
for chunk in graph.stream(input, stream_mode="updates"):
    print(chunk)  # {"node_name": {"key": "value"}}

# Stream full state after each node
for chunk in graph.stream(input, stream_mode="values"):
    print(chunk)  # Complete state after each node

# Stream both
for chunk in graph.stream(input, stream_mode=["updates", "values"]):
    print(chunk)
```

## Act Project Structure

### Typical Graph File

**File:** `casts/my_agent/graph.py`
```python
"""Graph definition for MyAgent cast."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from casts.base_graph import BaseGraph
from casts.my_agent.state import MyAgentState
from casts.my_agent.nodes import StartNode, ProcessNode, DecisionNode
from casts.my_agent.conditions import should_continue

class MyAgentGraph(BaseGraph):
    """MyAgent implementation graph."""

    def __init__(self, checkpointer=None):
        super().__init__()
        self.checkpointer = checkpointer

    def build(self):
        """Build graph structure.

        Returns:
            Compiled StateGraph
        """
        builder = StateGraph(MyAgentState)

        # Instantiate nodes
        start = StartNode()
        process = ProcessNode()
        decision = DecisionNode()

        # Add nodes
        builder.add_node("start", start)
        builder.add_node("process", process)
        builder.add_node("decision", decision)

        # Add edges
        builder.set_entry_point("start")
        builder.add_edge("start", "process")

        builder.add_conditional_edges(
            "process",
            should_continue,
            {
                "continue": "decision",
                "end": END,
            }
        )

        builder.add_edge("decision", END)

        # Compile
        if self.checkpointer:
            return builder.compile(checkpointer=self.checkpointer)
        else:
            return builder.compile()
```

### Usage in Application

```python
# In main application code
from casts.my_agent.graph import MyAgentGraph
from langgraph.checkpoint.memory import MemorySaver

# Create graph
graph_instance = MyAgentGraph(checkpointer=MemorySaver())
graph = graph_instance.build()

# Execute
config = {"configurable": {"thread_id": "session-1"}}
result = graph.invoke(
    {"messages": [], "task": "Do something"},
    config=config
)
```

## Common Patterns

### Pattern: ReAct Agent Graph

```python
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from modules.tools import tool_list

class ReactGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.model = ChatAnthropic(model="claude-sonnet-4")
        self.tools = tool_list

    def build(self):
        builder = StateGraph(AgentState)

        # Create agent node with bound tools
        from casts.my_agent.nodes import AgentNode
        agent = AgentNode(self.model.bind_tools(self.tools))

        # Add nodes
        builder.add_node("agent", agent)
        builder.add_node("tools", ToolNode(self.tools))

        # Edges
        builder.set_entry_point("agent")

        builder.add_conditional_edges(
            "agent",
            should_continue,
            {"continue": "tools", "end": END}
        )

        builder.add_edge("tools", "agent")

        return builder.compile(checkpointer=MemorySaver())
```

### Pattern: Multi-Step Pipeline

```python
class PipelineGraph(BaseGraph):
    def build(self):
        builder = StateGraph(PipelineState)

        # Sequential nodes
        nodes = [
            ("fetch", FetchNode()),
            ("validate", ValidateNode()),
            ("process", ProcessNode()),
            ("save", SaveNode()),
        ]

        for name, node in nodes:
            builder.add_node(name, node)

        # Linear flow
        builder.set_entry_point("fetch")
        builder.add_edge("fetch", "validate")
        builder.add_edge("validate", "process")
        builder.add_edge("process", "save")
        builder.add_edge("save", END)

        return builder.compile()
```

### Pattern: Branching Workflow

```python
class BranchingGraph(BaseGraph):
    def build(self):
        builder = StateGraph(WorkflowState)

        builder.add_node("start", StartNode())
        builder.add_node("route", RouteNode())
        builder.add_node("path_a", PathANode())
        builder.add_node("path_b", PathBNode())
        builder.add_node("merge", MergeNode())

        builder.set_entry_point("start")
        builder.add_edge("start", "route")

        builder.add_conditional_edges(
            "route",
            route_decision,
            {"a": "path_a", "b": "path_b"}
        )

        builder.add_edge("path_a", "merge")
        builder.add_edge("path_b", "merge")
        builder.add_edge("merge", END)

        return builder.compile()
```

## Common Mistakes

### ❌ Not Returning Compiled Graph

```python
# BAD
def build(self):
    builder = StateGraph(MyState)
    # ... add nodes/edges
    builder.compile()  # Not returned!
```

**Fix:**
```python
# GOOD
def build(self):
    builder = StateGraph(MyState)
    # ... add nodes/edges
    return builder.compile()  # Return it
```

### ❌ Calling build() Multiple Times

```python
# BAD: build() creates new graph each time
graph_instance = MyGraph()
result1 = graph_instance.build().invoke(input1)
result2 = graph_instance.build().invoke(input2)  # Different graph!
```

**Fix:**
```python
# GOOD: build once, invoke multiple times
graph_instance = MyGraph()
graph = graph_instance.build()
result1 = graph.invoke(input1)
result2 = graph.invoke(input2, config)  # Same graph
```

### ❌ Wrong State Type

```python
# BAD
builder = StateGraph(dict)  # Generic dict
```

**Fix:**
```python
# GOOD
from casts.my_agent.state import MyAgentState
builder = StateGraph(MyAgentState)  # Typed state
```

### ❌ Compiling Before Adding Edges

```python
# BAD
builder = StateGraph(MyState)
builder.add_node("start", StartNode())
graph = builder.compile()  # Compiled too early
builder.add_edge("start", END)  # Error!
```

**Fix:**
```python
# GOOD
builder = StateGraph(MyState)
builder.add_node("start", StartNode())
builder.add_edge("start", END)  # All structure first
graph = builder.compile()  # Then compile
```

### ❌ No Entry Point

```python
# BAD
builder.add_node("node1", Node1())
builder.add_edge("node1", END)
graph = builder.compile()  # Where to start?
```

**Fix:**
```python
# GOOD
builder.add_node("node1", Node1())
builder.set_entry_point("node1")  # Or add_edge(START, "node1")
builder.add_edge("node1", END)
graph = builder.compile()
```

## Decision Framework

```
Need state persistence?
  → Compile with checkpointer=MemorySaver()

Need human approval steps?
  → Use interrupt_before or interrupt_after

Need to resume from checkpoint?
  → Pass config with thread_id

All nodes are async?
  → Use ainvoke() or astream()

Need real-time updates?
  → Use stream() instead of invoke()

Want node outputs only?
  → stream_mode="updates"

Want full state after each node?
  → stream_mode="values"
```

## Config Options

### Thread ID (Session Management)

```python
config = {
    "configurable": {
        "thread_id": "user-123",  # Unique session ID
    }
}

result = graph.invoke(input, config=config)
```

### Tags (Filtering/Logging)

```python
config = {
    "tags": ["production", "user-action"],
}

result = graph.invoke(input, config=config)
```

### Recursion Limit

```python
config = {
    "recursion_limit": 50,  # Max iterations (default: 25)
}

result = graph.invoke(input, config=config)
```

### Combined Config

```python
config = {
    "configurable": {"thread_id": "123"},
    "tags": ["important"],
    "recursion_limit": 100,
}
```

## Act Project Conventions

⚠️ **Required:**
- ALL graphs inherit from BaseGraph
- Implement `build()` returning CompiledStateGraph
- Define in: `casts/[cast_name]/graph.py`
- Class name: `[CastName]Graph`

⚠️ **Build method:**
```python
def build(self) -> CompiledStateGraph:
    """Build and return compiled graph."""
    builder = StateGraph(YourState)
    # ... add nodes and edges
    return builder.compile()
```

⚠️ **Instantiation:**
```python
# Create instance
graph_instance = MyGraph()

# Build once
graph = graph_instance.build()

# Invoke multiple times
result1 = graph.invoke(input1, config1)
result2 = graph.invoke(input2, config2)
```

## Anti-Patterns

- ❌ **Building graph in __init__** → Build in build() method only
- ❌ **Global graph instance** → Create instance per use or manage lifecycle
- ❌ **Hardcoded dependencies in build()** → Pass via __init__
- ❌ **No checkpointer for interactive apps** → Use checkpointer for session management
- ❌ **Ignoring config** → Always accept and pass config

## References

- BaseGraph source: `casts/base_graph.py`
- Related: `01-core/state.md`, `01-core/nodes.md`, `01-core/edges.md`
- Checkpointers: `03-memory/checkpointers.md`
- Interrupts: `04-advanced/interrupts.md`
