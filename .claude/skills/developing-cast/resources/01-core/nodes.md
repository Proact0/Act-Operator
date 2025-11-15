# Node Implementation

## When to Use This Resource

Read this when creating node classes, implementing execute() methods, or troubleshooting node execution issues.

## Key Concepts

**Node:** Function or class that processes state and returns updates. In Act projects, all nodes MUST be classes inheriting from BaseNode.

**execute():** Abstract method you implement to define node logic.

**BaseNode:** Base class providing runtime access, logging, config helpers.

**AsyncBaseNode:** Async version for nodes with async operations.

## Node Class Pattern (Required in Act)

### Pattern 1: Sync Node (Most Common)

**When to use:** No async operations (API calls use requests, not aiohttp)

```python
from casts.base_node import BaseNode
from casts.my_agent.state import MyAgentState

class ProcessNode(BaseNode):
    """Processes user input and generates response."""

    def execute(self, state: MyAgentState) -> dict:
        """Process input from state.

        Args:
            state: Current graph state

        Returns:
            Dict with state updates
        """
        user_input = state["current_task"]
        result = self.process_input(user_input)

        return {
            "results": result,
            "step_count": 1,
        }

    def process_input(self, input: str) -> dict:
        """Helper method for processing."""
        # Your logic here
        return {"processed": input.upper()}
```

**Key points:**
- Inherit from `BaseNode`
- Implement `execute(self, state) -> dict`
- Return dict with state updates
- Helper methods are encouraged

### Pattern 2: Async Node

**When to use:** Async operations (aiohttp, async database, async LLM calls)

```python
from casts.base_node import AsyncBaseNode
from casts.my_agent.state import MyAgentState

class AsyncProcessNode(AsyncBaseNode):
    """Processes input asynchronously."""

    async def execute(self, state: MyAgentState) -> dict:
        """Process input async.

        Args:
            state: Current graph state

        Returns:
            Dict with state updates
        """
        user_input = state["current_task"]

        # Async operations
        result = await self.fetch_data(user_input)

        return {"results": result}

    async def fetch_data(self, query: str) -> dict:
        """Async helper method."""
        # async API call, database query, etc.
        return {"data": query}
```

**Key points:**
- Inherit from `AsyncBaseNode`
- `async def execute()`
- Use `await` for async operations
- Graph must be invoked with `.ainvoke()` or `.astream()`

### Pattern 3: Node with Dependencies

**When to use:** Node needs LLM, tools, external clients

```python
from casts.base_node import BaseNode
from langchain_anthropic import ChatAnthropic

class LLMNode(BaseNode):
    """Node with LLM dependency."""

    def __init__(self, model: ChatAnthropic, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def execute(self, state: MyAgentState) -> dict:
        """Generate response using LLM."""
        messages = state["messages"]

        # Use LLM
        response = self.model.invoke(messages)

        return {"messages": [response]}
```

**Instantiation in graph:**
```python
# In graph.py
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4")
llm_node = LLMNode(model=model)

builder.add_node("llm", llm_node)
```

## Accessing Runtime Context

### Pattern 4: Using Config (thread_id, tags, etc.)

**When to use:** Need thread_id for memory lookup, need tags for filtering

```python
from casts.base_node import BaseNode
from langchain_core.runnables import RunnableConfig

class ConfigNode(BaseNode):
    """Node that uses config."""

    def execute(
        self,
        state: MyAgentState,
        config: RunnableConfig = None,
        **kwargs
    ) -> dict:
        """Execute with config access."""

        # Get thread_id using helper method
        thread_id = self.get_thread_id(config)

        # Get tags
        tags = self.get_tags(config)

        return {
            "metadata": {
                "thread_id": thread_id,
                "tags": tags,
            }
        }
```

**Key points:**
- Add `config: RunnableConfig = None` to signature
- Use `self.get_thread_id(config)` helper
- Use `self.get_tags(config)` helper
- BaseNode handles parameter passing automatically

### Pattern 5: Using Runtime (Store, stream_writer)

**When to use:** Need cross-session memory (Store), custom streaming

```python
from casts.base_node import BaseNode
from langgraph.runtime import Runtime

class RuntimeNode(BaseNode):
    """Node with runtime access."""

    def execute(
        self,
        state: MyAgentState,
        runtime: Runtime = None,
        **kwargs
    ) -> dict:
        """Execute with runtime access."""

        if runtime and runtime.store:
            # Access Store for long-term memory
            namespace = ("user", state.get("user_id"))
            memories = runtime.store.search(namespace, query="preferences")

            return {"memories": memories}

        return {}
```

**Key points:**
- Add `runtime: Runtime = None` to signature
- Check `if runtime:` before using
- Access `runtime.store` for cross-session memory
- Access `runtime.stream_writer` for custom streaming

### Pattern 6: Using Both Config and Runtime

```python
from casts.base_node import BaseNode
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

class FullContextNode(BaseNode):
    """Node with complete context access."""

    def execute(
        self,
        state: MyAgentState,
        config: RunnableConfig = None,
        runtime: Runtime = None,
        **kwargs
    ) -> dict:
        """Execute with full context."""

        thread_id = self.get_thread_id(config)

        if runtime and runtime.store:
            # Store data with thread_id
            namespace = ("session", thread_id)
            runtime.store.put(namespace, "key", {"data": "value"})

        return {"processed": True}
```

## Node Execution Flow

```
Graph invokes node
  ↓
BaseNode.__call__() intercepts
  ↓
Logs "Executing" (if verbose=True)
  ↓
Inspects execute() signature
  ↓
Passes only parameters execute() accepts
  ↓
Calls self.execute(state, ...)
  ↓
Logs "Completed" (if verbose=True)
  ↓
Returns dict to graph
  ↓
Graph merges updates into state
```

## Logging and Debugging

### Enable Verbose Mode

```python
# When instantiating node
node = MyNode(verbose=True)

# In graph
builder.add_node("my_node", MyNode(verbose=True))
```

**Output:**
```
[MyNode] Executing
  state_keys: ['messages', 'current_task']
  thread_id: 'abc123'
[MyNode] Completed
  result_keys: ['results', 'step_count']
```

### Custom Logging

```python
class MyNode(BaseNode):
    def execute(self, state) -> dict:
        # Use self.log() for conditional logging
        self.log("Processing input", input=state["current_task"])

        result = self.process(state)

        self.log("Processing complete", result=result)

        return {"results": result}
```

**Only logs when verbose=True**

## Act Project Structure

### File Organization

**File:** `casts/my_agent/nodes.py`
```python
"""Nodes for MyAgent cast."""

from casts.base_node import BaseNode, AsyncBaseNode
from casts.my_agent.state import MyAgentState

class StartNode(BaseNode):
    """Initialize agent state."""

    def execute(self, state: MyAgentState) -> dict:
        return {"step_count": 0}

class ProcessNode(BaseNode):
    """Process user input."""

    def execute(self, state: MyAgentState) -> dict:
        # Logic here
        return {"results": {}}

class AsyncFetchNode(AsyncBaseNode):
    """Fetch data asynchronously."""

    async def execute(self, state: MyAgentState) -> dict:
        # Async logic here
        return {"data": {}}
```

### Import in Graph

**File:** `casts/my_agent/graph.py`
```python
from casts.my_agent.nodes import StartNode, ProcessNode, AsyncFetchNode

# Instantiate
start_node = StartNode()
process_node = ProcessNode(verbose=True)
fetch_node = AsyncFetchNode()

# Add to graph
builder.add_node("start", start_node)
builder.add_node("process", process_node)
builder.add_node("fetch", fetch_node)
```

## Common Patterns

### Pattern: LLM with Tools

```python
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import ToolNode
from casts.base_node import BaseNode

class AgentNode(BaseNode):
    """Agent that calls LLM with tools."""

    def __init__(self, model: ChatAnthropic, tools: list, **kwargs):
        super().__init__(**kwargs)
        self.model = model.bind_tools(tools)

    def execute(self, state: MyAgentState) -> dict:
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}
```

### Pattern: Conditional Logic

```python
class DecisionNode(BaseNode):
    """Makes decisions based on state."""

    def execute(self, state: MyAgentState) -> dict:
        score = state.get("score", 0)

        if score > 0.8:
            action = "approve"
        elif score > 0.5:
            action = "review"
        else:
            action = "reject"

        return {"action": action}
```

### Pattern: Error Handling

```python
class RobustNode(BaseNode):
    """Node with error handling."""

    def execute(self, state: MyAgentState) -> dict:
        try:
            result = self.risky_operation(state)
            return {"results": result, "error": None}

        except Exception as e:
            self.log("Error occurred", error=str(e))
            return {
                "results": None,
                "error": str(e),
                "retry_count": state.get("retry_count", 0) + 1,
            }
```

## Common Mistakes

### ❌ Not Inheriting from BaseNode

```python
# BAD: Standalone function
def my_node(state):
    return {"result": "value"}
```

**Fix:**
```python
# GOOD: Inherit from BaseNode
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state) -> dict:
        return {"result": "value"}
```

### ❌ Mutating State Directly

```python
# BAD
def execute(self, state) -> dict:
    state["results"] = "new value"  # Mutates state
    return state
```

**Fix:**
```python
# GOOD
def execute(self, state) -> dict:
    return {"results": "new value"}  # Returns updates only
```

### ❌ Not Calling super().__init__()

```python
# BAD
class MyNode(BaseNode):
    def __init__(self, param):
        self.param = param  # Forgot super().__init__()
```

**Fix:**
```python
# GOOD
class MyNode(BaseNode):
    def __init__(self, param, **kwargs):
        super().__init__(**kwargs)  # MUST call
        self.param = param
```

### ❌ Returning None

```python
# BAD
def execute(self, state) -> dict:
    self.process(state)
    # No return statement - returns None
```

**Fix:**
```python
# GOOD
def execute(self, state) -> dict:
    self.process(state)
    return {}  # Return empty dict if no updates
```

### ❌ Wrong Parameter Name

```python
# BAD: Using 'data' instead of 'state'
def execute(self, data) -> dict:
    return {"result": data["input"]}
```

**Fix:**
```python
# GOOD: First parameter must be 'state'
def execute(self, state) -> dict:
    return {"result": state["input"]}
```

## Decision Framework

```
Need async operations (aiohttp, async DB)?
  → Inherit from AsyncBaseNode
  → Use async def execute()

Need thread_id for memory/logging?
  → Add config: RunnableConfig = None parameter
  → Use self.get_thread_id(config)

Need cross-session memory (Store)?
  → Add runtime: Runtime = None parameter
  → Access runtime.store

Need LLM or external dependencies?
  → Pass in __init__()
  → Store as instance variable

Need debugging output?
  → Instantiate with verbose=True
  → Use self.log() for custom logging

Simple state transformation only?
  → Just implement execute(self, state) -> dict
```

## Act Project Conventions

⚠️ **Required:**
- ALL nodes inherit from BaseNode or AsyncBaseNode
- Nodes defined in: `casts/[cast_name]/nodes.py`
- Never use standalone functions as nodes
- Always call `super().__init__(**kwargs)` in __init__

⚠️ **Method signature:**
```python
def execute(self, state: YourStateClass) -> dict:
    """Docstring required."""
    return {"key": "value"}
```

## Anti-Patterns

- ❌ **Standalone node functions** → Must be classes
- ❌ **Storing state in instance variables** → State passed via parameters
- ❌ **Long execute() methods** → Extract to helper methods
- ❌ **No type hints** → Always type state parameter
- ❌ **Returning full state** → Return only updates

## References

- BaseNode source: `casts/base_node.py`
- Related: `01-core/state.md`, `01-core/graph.md`, `02-tools/tool-patterns.md`
