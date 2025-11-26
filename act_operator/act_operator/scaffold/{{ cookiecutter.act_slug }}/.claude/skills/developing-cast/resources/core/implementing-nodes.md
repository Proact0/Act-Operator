# Implementing Nodes

## When to Use This Resource
Read this when creating new nodes, converting architecture specs to node implementations, or working with BaseNode/AsyncBaseNode.

## Key Concept

**Node** = A processing unit that receives state, performs logic, and returns state updates. In Act projects, ALL nodes inherit from `BaseNode` or `AsyncBaseNode`.

## Basic Node Pattern

### Synchronous Node (Most Common)

```python
from casts.base_node import BaseNode

class ProcessInputNode(BaseNode):
    """Processes user input and extracts intent."""

    def execute(self, state) -> dict:
        """Simple node - just state in, updates out."""
        user_input = state["input"]
        intent = extract_intent(user_input)  # Your logic

        return {"intent": intent}
```

**When to use:**
- Most standard operations
- Calling APIs (non-async)
- Data transformations
- LLM calls (sync)

### Asynchronous Node

```python
from casts.base_node import AsyncBaseNode

class FetchDataNode(AsyncBaseNode):
    """Fetches data from async API."""

    async def execute(self, state) -> dict:
        """Async operations using await."""
        user_id = state["user_id"]
        data = await async_api_call(user_id)

        return {"user_data": data}
```

**When to use:**
- Async API calls
- Concurrent I/O operations
- Async LLM calls
- Database queries (async drivers)

## Accessing Advanced Features

### Pattern 1: Access Config (thread_id, tags)

```python
class UserContextNode(BaseNode):
    def execute(self, state: dict, config=None, **kwargs) -> dict:
        # Get thread_id for user-specific operations
        thread_id = self.get_thread_id(config)
        tags = self.get_tags(config)

        return {"thread_id": thread_id, "tags": tags}
```

**Use when:** Need thread_id for memory operations, want to access tags.

### Pattern 2: Access Runtime (Store, streaming)

```python
class MemoryNode(BaseNode):
    def execute(self, state: dict, runtime=None, **kwargs) -> dict:
        # Access cross-thread memory via Store
        if runtime and runtime.store:
            user_prefs = runtime.store.get(
                namespace=("user_prefs",),
                key="preferences"
            )

        return {"preferences": user_prefs}
```

**Use when:** Need Store for cross-thread memory, want to stream custom events.

## Node Initialization

### Stateless Node (Preferred)
```python
class SimpleNode(BaseNode):
    """No __init__ needed for stateless nodes."""

    def execute(self, state) -> dict:
        return {"processed": True}
```

### Stateful Node (When Necessary)
```python
class ConfiguredNode(BaseNode):
    """Node with configuration."""

    def __init__(self, model_name: str = "gpt-4", **kwargs):
        super().__init__(**kwargs)  # Important: call parent init
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name)

    def execute(self, state) -> dict:
        response = self.llm.invoke(state["messages"])
        return {"response": response}
```

**When to use stateful:**
- Node needs LLM instance
- External service connections
- Configuration parameters

**Always:** Call `super().__init__(**kwargs)` to preserve BaseNode features (verbose, logging, etc.)

## Error Handling Patterns

### Pattern 1: Try-Catch with Fallback
```python
class RobustNode(BaseNode):
    def execute(self, state) -> dict:
        try:
            result = risky_operation(state["input"])
            return {"result": result, "error": None}
        except ValueError as e:
            self.log(f"Operation failed: {e}")
            return {"result": None, "error": str(e)}
```

### Pattern 2: Validation Before Processing
```python
class ValidatingNode(BaseNode):
    def execute(self, state) -> dict:
        if "required_field" not in state:
            return {"error": "Missing required_field"}

        # Safe to proceed
        return {"processed": state["required_field"]}
```

## Decision Framework

```
Does node have async operations (API calls, DB queries)?
├─ Yes → Use AsyncBaseNode with async def execute
└─ No  → Use BaseNode with def execute

Node needs thread_id or tags?
├─ Yes → Add config parameter: execute(self, state, config=None, **kwargs)
└─ No  → Simple signature: execute(self, state)

Node needs Store or custom streaming?
└─ Yes → Add runtime parameter: execute(self, state, runtime=None, **kwargs)

Node needs configuration (LLM, API keys)?
├─ Yes → Add __init__ (remember super().__init__(**kwargs))
└─ No  → No __init__ needed
```

## Act Project Conventions

⚠️ **Node Location:** `casts/[cast_name]/nodes.py`

**File organization:**
```python
# casts/{ cast_name }/modules/nodes.py
from casts.base_node import BaseNode, AsyncBaseNode

class FirstNode(BaseNode):
    """First processing step."""
    def execute(self, state) -> dict:
        ...

class SecondNode(AsyncBaseNode):
    """Async second step."""
    async def execute(self, state) -> dict:
        ...
```

## Common Mistakes

❌ **Forgetting to inherit from BaseNode**
```python
class MyNode:  # ❌ Wrong
    def execute(self, state):
        ...
```

❌ **Modifying state directly**
```python
def execute(self, state) -> dict:
    state["result"] = "done"  # ❌ Don't mutate
    return state              # ❌ Return modified state

# ✅ Correct - return updates only
def execute(self, state) -> dict:
    return {"result": "done"}
```

❌ **Forgetting super().__init__() with custom __init__**
```python
class MyNode(BaseNode):
    def __init__(self, config):
        self.config = config  # ❌ Missing super().__init__()
```

❌ **Using sync when async is needed**
```python
class APINode(BaseNode):  # ❌ Should be AsyncBaseNode
    def execute(self, state) -> dict:
        return requests.get(url).json()  # Blocking I/O
```

## Verbose Mode (Debugging)

Enable detailed logging:
```python
# When instantiating
node = MyNode(verbose=True)

# Automatically logs:
# [MyNode] Executing | state_keys=['input', 'messages'] | thread_id=abc123
# [MyNode] Completed | result_keys=['result']
```

