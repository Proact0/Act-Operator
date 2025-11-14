---
# Nodes Resource
# LangGraph 1.0 Node Implementation Patterns
---

# Implementing Nodes

## Core Pattern

All nodes extend `BaseNode` from `casts/base_node.py`:

```python
from casts.base_node import BaseNode

class MyNode(BaseNode):
    """Node description.

    Attributes:
        name: Canonical name (class name by default).
        verbose: Enable detailed logging.
    """

    def execute(self, state, runtime=None, **kwargs):
        """Execute node logic.

        Args:
            state: Current graph state dict.
            runtime: Runtime context (store, config).
            **kwargs: Additional context (config, etc.).

        Returns:
            dict: State updates to merge.
        """
        # Your logic here
        self.log(f"Processing: {state.get('input')}")

        result = self.process_logic(state)

        return {"field": result}

    def process_logic(self, state):
        """Helper method for node logic."""
        # Node-specific implementation
        pass
```

## State Access

**Reading state:**
```python
def execute(self, state, runtime=None, **kwargs):
    # Access state fields
    input_data = state.get("input_field", "default")
    messages = state.get("messages", [])

    # Check if field exists
    if "required_field" not in state:
        raise ValueError("Missing required_field")
```

**Updating state:**
```python
def execute(self, state, runtime=None, **kwargs):
    # Return dict with updates - LangGraph merges automatically
    return {
        "output_field": "value",
        "counter": state.get("counter", 0) + 1,
        "messages": [AIMessage(content="response")]
    }
```

**IMPORTANT:** Do NOT mutate state directly. Always return updates.

## Runtime Context

Access runtime for store, config, thread_id:

```python
def execute(self, state, runtime=None, **kwargs):
    if runtime:
        # Access store for memory operations
        store = runtime.store

        # Get thread_id from config
        config = kwargs.get("config", {})
        thread_id = config.get("configurable", {}).get("thread_id")

        # Use store
        if store and thread_id:
            store.put(("namespace", thread_id), "key", {"data": "value"})
            data = store.get(("namespace", thread_id), "key")
```

## Using Tools in Nodes

Tools are created in `modules/tools/`, imported in nodes:

```python
from casts.base_node import BaseNode
from .tools import my_tool  # Import from tools module

class ToolNode(BaseNode):
    """Node that uses a tool."""

    def execute(self, state, runtime=None, **kwargs):
        # Invoke tool
        query = state.get("query", "")
        result = my_tool.invoke(query)

        return {"tool_result": result}
```

**For advanced tool patterns, see `resources/tools.md`**

## Logging

BaseNode provides logging:

```python
def execute(self, state, runtime=None, **kwargs):
    # Use self.log() for consistent logging
    self.log("Starting processing")
    self.log(f"Input: {state.get('input')}")

    # Controlled by verbose flag
    if self.verbose:
        self.log("Detailed debug info")
```

## Node Examples

### Simple Transformation Node

```python
class TransformNode(BaseNode):
    """Transforms input data."""

    def execute(self, state, runtime=None, **kwargs):
        raw_input = state.get("raw_data", "")
        transformed = raw_input.upper().strip()

        return {"processed_data": transformed}
```

### Node with LLM

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

class AnalyzerNode(BaseNode):
    """Analyzes content with LLM."""

    def __init__(self):
        super().__init__()
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

    def execute(self, state, runtime=None, **kwargs):
        content = state.get("content", "")

        response = self.llm.invoke([
            HumanMessage(content=f"Analyze this: {content}")
        ])

        return {
            "analysis": response.content,
            "messages": [response]
        }
```

### Node with Conditional Logic

```python
class ValidatorNode(BaseNode):
    """Validates data and sets flags."""

    def execute(self, state, runtime=None, **kwargs):
        data = state.get("data", "")

        is_valid = len(data) > 0 and data.isalnum()

        return {
            "is_valid": is_valid,
            "validation_message": "Valid" if is_valid else "Invalid data"
        }
```

## Common Patterns

### Accessing Messages

```python
def execute(self, state, runtime=None, **kwargs):
    # For MessagesState
    messages = state.get("messages", [])

    # Get last message
    if messages:
        last_message = messages[-1]
        content = last_message.content
```

### Thread-Safe Operations

```python
def execute(self, state, runtime=None, **kwargs):
    # Get thread_id for thread-scoped operations
    config = kwargs.get("config", {})
    thread_id = self.get_thread_id(config)

    # Use thread_id for scoped storage
    if runtime and runtime.store:
        runtime.store.put(
            ("data", thread_id),
            "key",
            {"value": "data"}
        )
```

### Error Handling

```python
def execute(self, state, runtime=None, **kwargs):
    try:
        result = self.risky_operation(state)
        return {"result": result, "error": None}
    except Exception as e:
        self.log(f"Error: {e}")
        return {
            "result": None,
            "error": str(e),
            "status": "failed"
        }
```

## Location

**Node implementations:** `casts/<cast_name>/modules/nodes.py`

**One file with multiple nodes:**
```python
# modules/nodes.py
from casts.base_node import BaseNode

class Node1(BaseNode):
    ...

class Node2(BaseNode):
    ...

class Node3(BaseNode):
    ...
```

## Testing Nodes

See `testing-cast` skill for comprehensive testing patterns.

**Basic test:**
```python
def test_node():
    node = MyNode()
    state = {"input": "test"}
    result = node.execute(state)
    assert result["output"] == "expected"
```

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Mutating state directly | Return dict with updates |
| Tool in nodes.py | Import from modules/tools/ |
| Forgetting runtime param | Add runtime=None to signature |
| Not using self.log() | Use BaseNode logging |
| Complex logic in execute() | Extract to helper methods |
| Missing error handling | Try/except with error state |

## Next Steps

- **Using tools in nodes:** See `resources/tools.md`
- **Memory patterns:** See `resources/memory.md`
- **State schema:** See `resources/state.md`
- **Conditional routing:** See `resources/edges.md`

