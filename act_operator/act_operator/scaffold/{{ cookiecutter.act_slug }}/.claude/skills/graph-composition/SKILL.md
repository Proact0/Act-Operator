---
name: graph-composition
description: Compose LangGraph workflows with BaseGraph - use when building graphs, connecting nodes, adding edges, implementing routing, or defining graph topology.
---

# Graph Composition

**Use this skill when:**
- Creating new graph classes
- Connecting nodes with edges
- Implementing conditional routing
- Building graph workflows
- Understanding graph patterns
- Troubleshooting graph structure

## Overview

Graphs define the workflow by connecting nodes with edges. Act provides `BaseGraph` as a base class that requires implementing a `build()` method where you construct your graph using LangGraph's StateGraph API.

**Key concepts:**
- **Graph**: Workflow definition connecting nodes
- **StateGraph**: LangGraph's graph builder
- **Nodes**: Processing units (added with `add_node`)
- **Edges**: Connections between nodes
- **START**: Entry point (built-in)
- **END**: Exit point (built-in)
- **Conditional edges**: Dynamic routing based on state

## Quick Start

### Simple Linear Graph

Most basic pattern:

```python
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from casts.my_cast.modules.state import State
from casts.my_cast.modules.nodes import ProcessNode, FormatNode

class MyGraph(BaseGraph):
    """Simple linear workflow."""

    def build(self):
        builder = StateGraph(State)

        # Add nodes (use instances!)
        builder.add_node("process", ProcessNode())
        builder.add_node("format", FormatNode())

        # Connect nodes
        builder.add_edge(START, "process")
        builder.add_edge("process", "format")
        builder.add_edge("format", END)

        # Compile and return
        graph = builder.compile()
        graph.name = self.name
        return graph

# Create instance
my_graph = MyGraph()
```

## BaseGraph Pattern

### Graph Template

Standard Act graph structure:

```python
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from casts.my_cast.modules.state import InputState, OutputState, State
from casts.my_cast.modules.nodes import Node1, Node2

class MyGraph(BaseGraph):
    """Graph definition.

    Attributes:
        input: Input schema for API
        output: Output schema for API
        state: Internal state schema
    """

    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Build and compile graph.

        Returns:
            CompiledStateGraph: Ready for execution
        """
        # Create builder with schemas
        builder = StateGraph(
            self.state,
            input_schema=self.input,
            output_schema=self.output
        )

        # Add nodes
        builder.add_node("node1", Node1())
        builder.add_node("node2", Node2())

        # Add edges
        builder.add_edge(START, "node1")
        builder.add_edge("node1", "node2")
        builder.add_edge("node2", END)

        # Compile
        graph = builder.compile()
        graph.name = self.name
        return graph
```

### Why Schemas Matter

```python
# Input/Output schemas define external API
builder = StateGraph(
    State,                  # Internal state (can have extra fields)
    input_schema=InputState,   # What users provide
    output_schema=OutputState  # What users receive
)

# Benefits:
# - Clear API contract
# - Hide internal fields from users
# - Type safety for inputs/outputs
# - Better error messages
```

## Adding Nodes

### Basic add_node

```python
# Always use INSTANCES, not classes!
builder.add_node("node_name", NodeClass())

# ✅ Good
builder.add_node("process", ProcessNode())

# ❌ Bad
builder.add_node("process", ProcessNode)  # Missing ()
```

### Multiple Nodes

```python
def build(self):
    builder = StateGraph(State)

    # Add multiple nodes
    builder.add_node("validate", ValidateNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("format", FormatNode())
    builder.add_node("save", SaveNode())

    # Connect them...
```

### Node with Configuration

```python
class MyGraph(BaseGraph):
    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose

    def build(self):
        builder = StateGraph(State)

        # Pass config to nodes
        builder.add_node("process", ProcessNode(verbose=self.verbose))
        builder.add_node("format", FormatNode(verbose=self.verbose))

        # ...
```

## Adding Edges

### Simple Edges

```python
# START → node
builder.add_edge(START, "first_node")

# node → node
builder.add_edge("node_a", "node_b")

# node → END
builder.add_edge("last_node", END)
```

### Chain of Edges

```python
# Linear flow: START → A → B → C → END
builder.add_node("a", NodeA())
builder.add_node("b", NodeB())
builder.add_node("c", NodeC())

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", END)
```

### Parallel Paths

```python
# Split: START → process → (format_a, format_b) → END
builder.add_node("process", ProcessNode())
builder.add_node("format_a", FormatANode())
builder.add_node("format_b", FormatBNode())

builder.add_edge(START, "process")
builder.add_edge("process", "format_a")
builder.add_edge("process", "format_b")
builder.add_edge("format_a", END)
builder.add_edge("format_b", END)
```

## Conditional Edges

### Basic Conditional

```python
def route_by_type(state):
    """Routing function."""
    if state.type == "A":
        return "process_a"
    elif state.type == "B":
        return "process_b"
    else:
        return "process_default"

def build(self):
    builder = StateGraph(State)

    builder.add_node("classify", ClassifyNode())
    builder.add_node("process_a", ProcessANode())
    builder.add_node("process_b", ProcessBNode())
    builder.add_node("process_default", ProcessDefaultNode())

    builder.add_edge(START, "classify")

    # Add conditional edge
    builder.add_conditional_edges(
        "classify",           # Source node
        route_by_type,        # Routing function
        {                     # Path mapping
            "process_a": "process_a",
            "process_b": "process_b",
            "process_default": "process_default"
        }
    )

    builder.add_edge("process_a", END)
    builder.add_edge("process_b", END)
    builder.add_edge("process_default", END)

    return builder.compile()
```

### Conditional with END

```python
def should_continue(state):
    """Decide if loop should continue."""
    if state.iterations >= state.max_iterations:
        return END
    if state.complete:
        return END
    return "process"

def build(self):
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())

    builder.add_edge(START, "process")

    # Loop or exit
    builder.add_conditional_edges(
        "process",
        should_continue,
        {
            "process": "process",  # Loop back
            END: END               # Exit
        }
    )

    return builder.compile()
```

### Method-Based Routing

```python
class MyGraph(BaseGraph):
    def route_query(self, state):
        """Routing method with access to self."""
        query = state.query.lower()

        if "math" in query:
            return "math_node"
        if "search" in query:
            return "search_node"
        return "general_node"

    def build(self):
        builder = StateGraph(State)

        builder.add_node("router", RouterNode())
        builder.add_node("math_node", MathNode())
        builder.add_node("search_node", SearchNode())
        builder.add_node("general_node", GeneralNode())

        builder.add_edge(START, "router")
        builder.add_conditional_edges(
            "router",
            self.route_query,  # Use method
            {
                "math_node": "math_node",
                "search_node": "search_node",
                "general_node": "general_node"
            }
        )

        # All paths lead to END
        builder.add_edge("math_node", END)
        builder.add_edge("search_node", END)
        builder.add_edge("general_node", END)

        return builder.compile()
```

## Graph Patterns

### Pattern 1: Linear Pipeline

Simple A → B → C flow:

```python
def build(self):
    builder = StateGraph(State)

    builder.add_node("fetch", FetchNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("save", SaveNode())

    builder.add_edge(START, "fetch")
    builder.add_edge("fetch", "process")
    builder.add_edge("process", "save")
    builder.add_edge("save", END)

    return builder.compile()
```

### Pattern 2: Branching

Conditional routing:

```python
def route_by_category(state):
    return state.category  # Returns "cat_a", "cat_b", or "cat_c"

def build(self):
    builder = StateGraph(State)

    builder.add_node("classify", ClassifyNode())
    builder.add_node("cat_a", ProcessCatANode())
    builder.add_node("cat_b", ProcessCatBNode())
    builder.add_node("cat_c", ProcessCatCNode())

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_by_category,
        {
            "cat_a": "cat_a",
            "cat_b": "cat_b",
            "cat_c": "cat_c"
        }
    )

    builder.add_edge("cat_a", END)
    builder.add_edge("cat_b", END)
    builder.add_edge("cat_c", END)

    return builder.compile()
```

### Pattern 3: Loop

Repeat until condition met:

```python
def should_retry(state):
    if state.success:
        return END
    if state.retry_count >= 3:
        return END
    return "process"

def build(self):
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())

    builder.add_edge(START, "process")
    builder.add_conditional_edges(
        "process",
        should_retry,
        {
            "process": "process",
            END: END
        }
    )

    return builder.compile()
```

### Pattern 4: Agent Loop

LLM agent with tools:

```python
def should_continue(state):
    last_message = state.messages[-1]

    # Check if LLM made tool calls
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"

    # No tool calls = done
    return END

def build(self):
    builder = StateGraph(State)

    builder.add_node("agent", AgentNode())
    builder.add_node("tools", ToolNode())

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    builder.add_edge("tools", "agent")  # Tools → agent (loop)

    return builder.compile()
```

### Pattern 5: Parallel Processing

Fan-out then fan-in:

```python
def build(self):
    builder = StateGraph(State)

    builder.add_node("split", SplitNode())
    builder.add_node("process_a", ProcessANode())
    builder.add_node("process_b", ProcessBNode())
    builder.add_node("process_c", ProcessCNode())
    builder.add_node("merge", MergeNode())

    # Fan-out
    builder.add_edge(START, "split")
    builder.add_edge("split", "process_a")
    builder.add_edge("split", "process_b")
    builder.add_edge("split", "process_c")

    # Fan-in
    builder.add_edge("process_a", "merge")
    builder.add_edge("process_b", "merge")
    builder.add_edge("process_c", "merge")

    builder.add_edge("merge", END)

    return builder.compile()
```

### Pattern 6: Retry with Fallback

Try, retry, fallback:

```python
def route_after_attempt(state):
    if state.success:
        return END

    if state.retry_count < 3:
        return "retry"

    # Max retries reached
    return "fallback"

def build(self):
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("retry", RetryNode())
    builder.add_node("fallback", FallbackNode())

    builder.add_edge(START, "process")
    builder.add_conditional_edges(
        "process",
        route_after_attempt,
        {
            "retry": "retry",
            "fallback": "fallback",
            END: END
        }
    )
    builder.add_edge("retry", "process")  # Try again
    builder.add_edge("fallback", END)

    return builder.compile()
```

## Compiling Graphs

### Basic Compilation

```python
def build(self):
    builder = StateGraph(State)

    # Add nodes and edges...

    # Compile (REQUIRED!)
    graph = builder.compile()

    # Set name for debugging
    graph.name = self.name

    return graph
```

### With Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

def build(self):
    builder = StateGraph(State)

    # Add nodes and edges...

    # Compile with checkpointer for persistence
    graph = builder.compile(
        checkpointer=MemorySaver()
    )

    graph.name = self.name
    return graph
```

### With Interrupts

```python
def build(self):
    builder = StateGraph(State)

    # Add nodes and edges...

    # Compile with interrupt points
    graph = builder.compile(
        interrupt_before=["human_review"],  # Pause before this node
        interrupt_after=["critical_step"]   # Pause after this node
    )

    graph.name = self.name
    return graph
```

## Best Practices

### 1. Always Use Node Instances

```python
# ✅ Good: Pass instance
builder.add_node("process", ProcessNode())

# ❌ Bad: Pass class
builder.add_node("process", ProcessNode)
```

### 2. Name Nodes Descriptively

```python
# ✅ Good: Clear names
builder.add_node("validate_input", ValidateNode())
builder.add_node("fetch_data", FetchNode())
builder.add_node("process_results", ProcessNode())

# ❌ Bad: Vague names
builder.add_node("node1", Node1())
builder.add_node("step", StepNode())
builder.add_node("do_stuff", DoStuffNode())
```

### 3. Document Graph Structure

```python
def build(self):
    """Build query processing graph.

    Flow:
        START → validate → classify → [route] → END
                                     ├─ math_solver
                                     ├─ web_search
                                     └─ general_qa

    Returns:
        CompiledStateGraph
    """
    # ...
```

### 4. Keep Routing Functions Simple

```python
# ✅ Good: Simple routing logic
def route(state):
    if state.type == "A":
        return "node_a"
    return "node_b"

# ❌ Bad: Complex logic in routing
def route(state):
    # 50 lines of complex logic...
    # Better to do this in a node
```

### 5. Always Compile Before Returning

```python
# ✅ Good: Compile then return
def build(self):
    builder = StateGraph(State)
    # ... add nodes and edges
    graph = builder.compile()
    graph.name = self.name
    return graph

# ❌ Bad: Return builder
def build(self):
    builder = StateGraph(State)
    # ... add nodes and edges
    return builder  # Not compiled!
```

### 6. Use Input/Output Schemas

```python
# ✅ Good: Define API boundaries
builder = StateGraph(
    State,
    input_schema=InputState,
    output_schema=OutputState
)

# ⚠️  OK but less clear: State for everything
builder = StateGraph(State)
```

## Troubleshooting

### Issue: "Node not found" error

**Symptoms**: Graph execution fails with node name error

**Fix**:
```python
# Ensure node name in add_edge matches add_node

# ❌ Bad: Typo in edge
builder.add_node("process", ProcessNode())
builder.add_edge(START, "proccess")  # Typo!

# ✅ Good: Names match
builder.add_node("process", ProcessNode())
builder.add_edge(START, "process")
```

### Issue: Node returns class instead of dict

**Symptoms**: State not updating after node execution

**Fix**:
```python
# ❌ Bad: Passing class
builder.add_node("process", ProcessNode)

# ✅ Good: Passing instance
builder.add_node("process", ProcessNode())
```

### Issue: Conditional edge not routing

**Symptoms**: Routing function called but graph doesn't branch

**Fix**:
```python
# Ensure routing function return value matches path mapping

def route(state):
    return "path_a"  # Must match key in mapping

builder.add_conditional_edges(
    "router",
    route,
    {
        "path_a": "node_a",  # ✅ Matches return value
        "path_b": "node_b"
    }
)
```

### Issue: Graph never ends

**Symptoms**: Execution hangs or times out

**Fix**:
```python
# Ensure all paths lead to END

# ❌ Bad: No edge to END
builder.add_node("process", ProcessNode())
builder.add_edge(START, "process")
# Missing: builder.add_edge("process", END)

# ✅ Good: Complete path
builder.add_node("process", ProcessNode())
builder.add_edge(START, "process")
builder.add_edge("process", END)
```

### Issue: Infinite loop

**Symptoms**: Graph keeps looping forever

**Fix**:
```python
# Ensure loop has exit condition

def should_continue(state):
    # ❌ Bad: Always loops
    return "process"

    # ✅ Good: Has exit
    if state.complete or state.iterations >= 10:
        return END
    return "process"
```

## Quick Reference

```python
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from casts.my_cast.modules.state import InputState, OutputState, State
from casts.my_cast.modules.nodes import Node1, Node2

class MyGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        builder = StateGraph(self.state, input_schema=self.input, output_schema=self.output)

        # Add nodes (use instances!)
        builder.add_node("node1", Node1())
        builder.add_node("node2", Node2())

        # Simple edges
        builder.add_edge(START, "node1")
        builder.add_edge("node1", "node2")
        builder.add_edge("node2", END)

        # Conditional edges
        builder.add_conditional_edges(
            "source",
            routing_function,
            {"path1": "node1", "path2": "node2"}
        )

        # Compile and return
        graph = builder.compile()
        graph.name = self.name
        return graph

# Create instance
my_graph = MyGraph()
```

## Related Skills

- **node-implementation**: Implement nodes for the graph
- **state-management**: Design state schemas
- **cast-development**: Overall Cast structure
- **modules-integration**: Use tools, chains, agents in graphs

## References

**Official documentation:**
- Graph API: https://docs.langchain.com/oss/python/langgraph/graph-api
- StateGraph: https://docs.langchain.com/oss/python/langgraph/graph-api#stategraph
- Edges: https://docs.langchain.com/oss/python/langgraph/graph-api#edges
- Graph Usage: https://docs.langchain.com/oss/python/langgraph/use-graph-api
