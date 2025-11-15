# Node Patterns

## When to Use This Resource
Read when creating nodes, implementing node logic, or understanding BaseNode patterns.

---

## Core Pattern: BaseNode Inheritance

**ALL nodes must inherit from BaseNode (Act requirement).**

```python
from casts.base_node import BaseNode

class MyNode(BaseNode):
    """Does X.

    Clear docstring explaining what this node does.
    """

    def __init__(self, config_param=None):
        """Initialize node.

        Args:
            config_param: Optional configuration
        """
        super().__init__()  # REQUIRED
        self.config_param = config_param

    def execute(self, state: dict) -> dict:
        """Execute node logic.

        Args:
            state: Current graph state

        Returns:
            dict: State updates (partial)
        """
        # Your logic here
        result = self.do_something(state)

        # Return ONLY updated fields
        return {"result": result}
```

**Location:** `casts/my_cast/nodes.py`

---

## Execute Method Signature

### Basic Execute

```python
def execute(self, state: dict) -> dict:
    """
    Args:
        state: Full graph state as dict

    Returns:
        dict: Partial state updates
    """
    value = state.get("input_field", "default")

    # Process...

    return {"output_field": value}
```

---

### With Runtime Context

```python
def execute(self, state: dict, runtime=None, config=None) -> dict:
    """Execute with access to runtime context.

    Args:
        state: Graph state
        runtime: Runtime context (Store, etc.)
        config: Invocation config

    Returns:
        dict: State updates
    """
    # Access Store for long-term memory
    if runtime and runtime.store:
        namespace = ("my_cast", "data")
        data = runtime.store.get(namespace, "key")

    # Access thread_id from config
    if config:
        thread_id = config.get("configurable", {}).get("thread_id")
        self.log(f"Running in thread: {thread_id}")

    return {"status": "done"}
```

**See:** `tools/tool-runtime.md` for detailed Store access patterns

---

## Node Patterns

### Processing Node

```python
class ProcessorNode(BaseNode):
    """Processes input data."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        data = state.get("raw_data", [])

        processed = [self.process_item(item) for item in data]

        self.log("Processed items", count=len(processed))

        return {"processed_data": processed}

    def process_item(self, item):
        """Helper method for processing."""
        return item.upper()  # Example
```

---

### LLM Node

```python
from langchain_core.messages import AIMessage, HumanMessage

class ChatNode(BaseNode):
    """Handles chat with LLM."""

    def __init__(self, model):
        super().__init__()
        self.model = model

    def execute(self, state: dict) -> dict:
        messages = state.get("messages", [])

        # Invoke LLM
        response = self.model.invoke(messages)

        self.log("LLM response received")

        return {"messages": [response]}  # Appends via reducer
```

---

### Tool-Calling Node

```python
from casts.my_cast.modules.tools.web_search import web_search

class SearchNode(BaseNode):
    """Executes web search."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        query = state.get("query", "")

        # Invoke tool directly
        try:
            results = web_search.invoke({"query": query})
            self.log("Search completed", num_results=len(results))
            return {"search_results": results, "status": "success"}

        except Exception as e:
            self.log(f"Search failed: {e}")
            return {"search_results": [], "status": "failed"}
```

**See:** `tools/tool-creation.md` for tool creation patterns

---

### Stateful Node (with Instance Variables)

```python
class CachingNode(BaseNode):
    """Node with internal cache."""

    def __init__(self):
        super().__init__()
        self.cache = {}  # Instance variable

    def execute(self, state: dict) -> dict:
        key = state.get("cache_key")

        # Check cache
        if key in self.cache:
            self.log("Cache hit")
            return {"result": self.cache[key]}

        # Compute and cache
        result = self.compute(state)
        self.cache[key] = result

        self.log("Cache miss - computed")
        return {"result": result}

    def compute(self, state):
        # Expensive computation
        return "computed_value"
```

---

### Conditional Logic Node

```python
class RouterNode(BaseNode):
    """Routes based on input."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        query = state.get("query", "").lower()

        # Determine mode
        if "search" in query:
            mode = "search"
        elif "chat" in query:
            mode = "chat"
        else:
            mode = "default"

        self.log(f"Routing to mode: {mode}")

        return {"mode": mode}
```

---

## Async Nodes

### Basic Async Pattern

```python
from casts.base_node import AsyncBaseNode

class AsyncAPINode(AsyncBaseNode):
    """Async node for API calls."""

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

    async def execute(self, state: dict) -> dict:
        """Async execute method.

        Args:
            state: Graph state

        Returns:
            dict: State updates
        """
        query = state.get("query")

        # Await async operation
        result = await self.api_client.fetch(query)

        self.log("API call completed")

        return {"api_result": result}
```

**Important:** If using async nodes, graph must use `ainvoke()` not `invoke()`

**See:** `patterns/async-patterns.md` for comprehensive async patterns

---

## Error Handling in Nodes

### Try/Except Pattern

```python
class RobustNode(BaseNode):
    """Node with error handling."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        try:
            result = self.risky_operation(state)
            return {"result": result, "status": "success"}

        except ValueError as e:
            self.log(f"ValueError: {e}")
            return {"result": None, "status": "error", "error": str(e)}

        except Exception as e:
            self.log(f"Unexpected error: {e}")
            return {"result": None, "status": "error", "error": "unknown"}

    def risky_operation(self, state):
        # Operation that might fail
        return state["data"] / state["divisor"]
```

**See:** `patterns/error-handling.md` for comprehensive patterns

---

## Logging

### Using self.log()

```python
def execute(self, state: dict) -> dict:
    # Simple logging
    self.log("Node started")

    # With details (kwargs)
    self.log("Processing", item_count=len(state.get("items", [])))

    # With data
    self.log("Result computed", result_length=len(result))

    return {"result": result}
```

**Logging only shows when `verbose=True` in graph invocation.**

---

## Multiple Nodes in One File

```python
"""Node implementations for MyCast."""

from casts.base_node import BaseNode

class NodeA(BaseNode):
    """Does A."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        return {"a_result": "done"}


class NodeB(BaseNode):
    """Does B."""

    def __init__(self, param):
        super().__init__()
        self.param = param

    def execute(self, state: dict) -> dict:
        return {"b_result": self.param}


class NodeC(BaseNode):
    """Does C."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        return {"c_result": "done"}
```

---

## Anti-Patterns

### ❌ Standalone Functions

```python
# ❌ WRONG - Not inheriting from BaseNode
def my_node(state: dict) -> dict:
    return {"result": "value"}
```

```python
# ✓ CORRECT - Inherit from BaseNode
class MyNode(BaseNode):
    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        return {"result": "value"}
```

---

### ❌ Missing super().__init__()

```python
class MyNode(BaseNode):
    def __init__(self):
        # ❌ MISSING super().__init__()
        self.param = "value"
```

```python
class MyNode(BaseNode):
    def __init__(self):
        super().__init__()  # ✓ REQUIRED
        self.param = "value"
```

---

### ❌ Returning Full State

```python
def execute(self, state: dict) -> dict:
    # ❌ WRONG - Modifying and returning full state
    state["new_field"] = "value"
    return state
```

```python
def execute(self, state: dict) -> dict:
    # ✓ CORRECT - Return only updates
    return {"new_field": "value"}
```

---

### ❌ Wrong Method Name

```python
class MyNode(BaseNode):
    def run(self, state):  # ❌ WRONG - Should be 'execute'
        return {"result": "value"}
```

```python
class MyNode(BaseNode):
    def execute(self, state: dict) -> dict:  # ✓ CORRECT
        return {"result": "value"}
```

---

## Decision Framework

**Q: Sync or async node?**
- I/O operations (API, database) → Async
- CPU-bound logic → Sync
- Simple operations → Sync (default)

**Q: What to return from execute()?**
- Return dict with ONLY changed fields
- Can be empty dict `{}` if no changes

**Q: How to access state fields?**
- Use `.get()` with defaults: `state.get("field", default)`
- Safer than `state["field"]` (no KeyError)

**Q: Can nodes have instance variables?**
- ✓ YES - for configuration, caching, models
- Initialize in `__init__()`

---

## Adding Nodes to Graph

```python
# In graph.py
from casts.my_cast.nodes import MyNode, AnotherNode

class MyCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(self.state)

        # Add nodes as INSTANCES (not classes)
        builder.add_node("my_node", MyNode())
        builder.add_node("another_node", AnotherNode(param="value"))

        # ...
```

**CRITICAL:** Pass instances `MyNode()`, not classes `MyNode`

---

## References
- patterns/act-conventions.md (BaseNode requirements)
- core/state-management.md (state updates)
- patterns/error-handling.md (comprehensive error patterns)
- patterns/async-patterns.md (async implementation details)
