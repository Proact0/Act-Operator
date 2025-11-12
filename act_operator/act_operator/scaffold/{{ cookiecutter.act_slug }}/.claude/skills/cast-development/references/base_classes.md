# Base Classes API Reference

## Contents

- [BaseGraph](#basegraph)
  - [Overview](#basegraph-overview)
  - [Methods](#basegraph-methods)
  - [Usage Example](#basegraph-usage)
- [BaseNode](#basenode)
  - [Overview](#basenode-overview)
  - [Methods](#basenode-methods)
  - [Node Signatures](#node-signatures)
  - [Usage Examples](#basenode-usage)
- [AsyncBaseNode](#asyncbasenode)
  - [Overview](#asyncbasenode-overview)
  - [Usage Example](#asyncbasenode-usage)

---

## BaseGraph

### BaseGraph Overview

`BaseGraph` is the base class for all LangGraph graph definitions. It provides a consistent interface for building and compiling StateGraph instances.

**Location**: `casts/base_graph.py`

**Key Responsibilities:**
- Define graph structure (nodes and edges)
- Compile StateGraph into executable format
- Manage graph metadata (name, input/output schemas)

### BaseGraph Methods

#### `__init__(self) -> None`

Initializes the graph and assigns its canonical name from the class name.

```python
def __init__(self) -> None:
    self.name = self.__class__.__name__
```

#### `build(self) -> CompiledStateGraph` (abstract)

**Must be implemented by subclasses.**

Constructs the graph structure by:
1. Creating a `StateGraph` instance with state schema
2. Adding nodes using `builder.add_node()`
3. Adding edges using `builder.add_edge()` or `builder.add_conditional_edges()`
4. Compiling and returning the `CompiledStateGraph`

**Returns**: `CompiledStateGraph` - Compiled graph ready for execution

```python
@abstractmethod
def build(self) -> CompiledStateGraph:
    raise NotImplementedError
```

#### `__call__(self) -> CompiledStateGraph`

Allows the graph to be called like a function, returning the result of `build()`.

```python
def __call__(self) -> CompiledStateGraph:
    return self.build()
```

### BaseGraph Usage

```python
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from casts.my_cast.modules.nodes import ProcessNode
from casts.my_cast.modules.state import InputState, OutputState, State

class MyGraph(BaseGraph):
    """Custom graph definition."""

    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Build the graph structure."""
        builder = StateGraph(
            self.state,
            input_schema=self.input,
            output_schema=self.output
        )

        # Add nodes
        builder.add_node("process", ProcessNode())

        # Add edges
        builder.add_edge(START, "process")
        builder.add_edge("process", END)

        # Compile
        graph = builder.compile()
        graph.name = self.name
        return graph

# Instantiate and invoke
my_graph = MyGraph()
result = my_graph().invoke({"query": "test"})
```

---

## BaseNode

### BaseNode Overview

`BaseNode` is the base class for synchronous nodes in LangGraph graphs. It provides a flexible foundation with:
- Automatic parameter inspection
- Config and runtime access
- Verbose logging support
- Helper methods for common tasks

**Location**: `casts/base_node.py`

**Key Responsibilities:**
- Process state and return updates
- Access configuration (thread_id, tags)
- Access runtime features (store, stream_writer)
- Provide debugging support

### BaseNode Methods

#### `__init__(self, *args, **kwargs) -> None`

Initializes a node instance.

**Arguments:**
- `verbose` (bool, optional): Enable detailed logging. Defaults to `False`.

```python
def __init__(self, *args, **kwargs) -> None:
    self.name = self.__class__.__name__
    self.verbose = kwargs.get("verbose", False)
```

#### `execute(self, state, **kwargs) -> dict` (abstract)

**Must be implemented by subclasses.**

Processes the incoming state and returns state updates.

**Arguments:**
- `state`: Current graph state
- `**kwargs` (optional): May include `config` and `runtime`

**Returns**: `dict` - Key/value pairs containing state updates

```python
@abstractmethod
def execute(self, state, **kwargs) -> dict:
    raise NotImplementedError("Must be implemented in a subclass")
```

#### `log(self, message: str, **context) -> None`

Logs a message when verbose mode is enabled.

**Arguments:**
- `message` (str): The message to log
- `**context`: Additional context to include

```python
def log(self, message: str, **context) -> None:
    if not self.verbose:
        return
    LOGGER.debug("[%s] %s", self.name, message)
    for key, value in context.items():
        LOGGER.debug("  %s: %r", key, value)
```

#### `get_thread_id(self, config: Optional[RunnableConfig]) -> Optional[str]`

Extracts thread_id from config.

**Returns**: Thread ID string or `None`

```python
def get_thread_id(self, config: Optional[RunnableConfig] = None) -> Optional[str]:
    if not config:
        return None
    return config.get("configurable", {}).get("thread_id")
```

#### `get_tags(self, config: Optional[RunnableConfig]) -> list[str]`

Extracts tags from config.

**Returns**: List of tag strings, empty list if not available

```python
def get_tags(self, config: Optional[RunnableConfig] = None) -> list[str]:
    if not config:
        return []
    return config.get("tags", [])
```

### Node Signatures

Choose your `execute()` signature based on what you need:

#### Simple (state only)
```python
def execute(self, state):
    return {"result": state["input"] + " processed"}
```

#### With config
```python
def execute(self, state, config=None):
    thread_id = self.get_thread_id(config)
    return {"thread_id": thread_id}
```

#### With runtime
```python
def execute(self, state, runtime=None):
    if runtime and runtime.store:
        data = runtime.store.get("key")
    return {"data": data}
```

#### With both config and runtime
```python
def execute(self, state, config=None, runtime=None):
    thread_id = self.get_thread_id(config)
    if runtime:
        runtime.store.put("thread", thread_id)
    return {"thread_id": thread_id}
```

#### Flexible (kwargs)
```python
def execute(self, state, **kwargs):
    config = kwargs.get("config")
    runtime = kwargs.get("runtime")
    return {"result": "processed"}
```

### BaseNode Usage

#### Example 1: Simple Node

```python
from casts.base_node import BaseNode
from langchain_core.messages import AIMessage

class SimpleNode(BaseNode):
    """Process user query."""

    def execute(self, state):
        query = state["query"]
        response = f"Processing: {query}"
        return {"messages": [AIMessage(content=response)]}
```

#### Example 2: Node with Config

```python
from casts.base_node import BaseNode

class ThreadAwareNode(BaseNode):
    """Node that uses thread_id from config."""

    def execute(self, state, config=None):
        thread_id = self.get_thread_id(config)
        self.log("Processing", thread_id=thread_id)

        result = f"Thread {thread_id}: {state['query']}"
        return {"result": result}
```

#### Example 3: Node with Runtime Store

```python
from casts.base_node import BaseNode

class StatefulNode(BaseNode):
    """Node that uses runtime store for persistence."""

    def execute(self, state, runtime=None):
        if runtime and runtime.store:
            # Read from store
            count = runtime.store.get("count") or 0

            # Update count
            count += 1
            runtime.store.put("count", count)

            return {"count": count}

        return {"count": 0}
```

#### Example 4: Verbose Node

```python
from casts.base_node import BaseNode

class DebugNode(BaseNode):
    """Node with detailed logging."""

    def __init__(self):
        super().__init__(verbose=True)

    def execute(self, state, config=None):
        self.log("Starting processing", state_keys=list(state.keys()))

        # Process
        result = {"output": "processed"}

        self.log("Completed processing", result=result)
        return result
```

---

## AsyncBaseNode

### AsyncBaseNode Overview

`AsyncBaseNode` is the async version of `BaseNode` for asynchronous operations. It has the same API but all methods are async.

**Location**: `casts/base_node.py`

**Use when:**
- Making async API calls
- Using async libraries
- Performing async I/O operations

### AsyncBaseNode Usage

```python
from casts.base_node import AsyncBaseNode
from langchain_core.messages import AIMessage
import httpx

class AsyncAPINode(AsyncBaseNode):
    """Async node that calls external API."""

    async def execute(self, state):
        query = state["query"]

        # Async API call
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.example.com/search?q={query}")
            data = response.json()

        return {"messages": [AIMessage(content=str(data))]}
```

**Using in graph:**

```python
from langgraph.graph import StateGraph

builder = StateGraph(State)
builder.add_node("async_api", AsyncAPINode())
builder.add_edge(START, "async_api")
builder.add_edge("async_api", END)
```

---

## Best Practices

### 1. Node Naming
Use descriptive class names that indicate the node's purpose:
- ✅ `ProcessQueryNode`, `FetchDataNode`, `ValidateInputNode`
- ❌ `Node1`, `MyNode`, `Handler`

### 2. Single Responsibility
Each node should have one clear purpose:
```python
# ✅ Good: Focused nodes
class FetchDataNode(BaseNode): ...
class ProcessDataNode(BaseNode): ...
class SaveResultNode(BaseNode): ...

# ❌ Bad: Doing too much
class FetchProcessSaveNode(BaseNode): ...
```

### 3. Return Dict Updates
Always return a dict with state updates:
```python
# ✅ Good
def execute(self, state):
    return {"messages": [...], "status": "complete"}

# ❌ Bad: Returning state directly
def execute(self, state):
    state["messages"] = [...]
    return state
```

### 4. Use Verbose for Debugging
Enable verbose logging during development:
```python
# Development
node = MyNode(verbose=True)

# Production
node = MyNode(verbose=False)
```

### 5. Type Hints
Use type hints for clarity:
```python
from typing import Any, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

def execute(
    self,
    state: Any,
    config: Optional[RunnableConfig] = None,
    runtime: Optional[Runtime] = None
) -> dict:
    ...
```
