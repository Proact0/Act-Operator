---
name: node-implementation
description: Implement LangGraph nodes with BaseNode or functions. Use when creating node classes, implementing execute methods, handling state updates, or working with node patterns in Act projects.
---

# Node Implementation

## Overview

Nodes are processing units in LangGraph graphs. Each node receives state, performs operations, and returns state updates. Act supports two approaches: BaseNode classes (recommended) and function-based nodes.

## When to Use This Skill

- Creating new node classes
- Implementing node execute methods
- Converting functions to BaseNode
- Using config or runtime in nodes
- Troubleshooting node execution

## Implementation Checklist

Before implementing a node:

1. [ ] Determine if BaseNode or function approach
2. [ ] Identify required state fields
3. [ ] Decide if config/runtime needed
4. [ ] Plan error handling strategy
5. [ ] Document execute method behavior

## Workflow

### 1. Choose Node Type

**BaseNode (Recommended)**:
- Supports config and runtime access
- Built-in logging with `self.log()`
- Reusable across projects
- Better for complex nodes

**Function**:
- Simpler for basic transformations
- Less boilerplate
- Good for quick prototypes

### 2. Implement Execute Method

**BaseNode approach**:

```python
from casts.base_node import BaseNode

class ProcessNode(BaseNode):
    """Process user query."""

    def execute(self, state):
        """Transform query to uppercase.

        Args:
            state: Current graph state

        Returns:
            dict: State updates
        """
        result = state.query.upper()
        return {"result": result}
```

**Function approach**:

```python
def process_node(state):
    """Process user query."""
    result = state.query.upper()
    return {"result": result}
```

See `examples/simple_nodes.py` for complete examples.

### 3. Add to Graph

**BaseNode**:
```python
# Always use instance (not class)
builder.add_node("process", ProcessNode())
```

**Function**:
```python
# Pass function directly
builder.add_node("process", process_node)
```

### 4. Test Node

Run validation script:
```bash
uv run python scripts/validate_node.py casts/my_cast/modules/nodes.py ProcessNode
```

## BaseNode Patterns

### Pattern 1: Simple Node (State Only)

```python
class SimpleNode(BaseNode):
    def execute(self, state):
        return {"result": process(state.input)}
```

### Pattern 2: Configurable Node

```python
class ConfigurableNode(BaseNode):
    def __init__(self, multiplier=2, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier

    def execute(self, state):
        return {"result": state.value * self.multiplier}
```

### Pattern 3: Node with Config Access

```python
class ThreadAwareNode(BaseNode):
    def execute(self, state, config=None, **kwargs):
        thread_id = self.get_thread_id(config)
        self.log(f"Processing for thread: {thread_id}")
        return {"thread_id": thread_id}
```

See `examples/config_nodes.py` for complete examples.

### Pattern 4: Node with Runtime Access

```python
class PersistentNode(BaseNode):
    def execute(self, state, runtime=None, **kwargs):
        if runtime and runtime.store:
            data = runtime.store.get("key")
        return {"data": data}
```

See `examples/runtime_nodes.py` for complete examples.

### Pattern 5: Async Node

```python
from casts.base_node import AsyncBaseNode

class AsyncFetchNode(AsyncBaseNode):
    async def execute(self, state):
        data = await fetch_data(state.url)
        return {"data": data}
```

See `examples/async_nodes.py` for complete examples.

## Common Pitfalls

### ❌ Passing Class Instead of Instance

```python
# Wrong
builder.add_node("process", ProcessNode)

# Correct
builder.add_node("process", ProcessNode())
```

### ❌ Modifying State In-Place

```python
# Wrong
def node(state):
    state.count = 5
    return state

# Correct
def node(state):
    return {"count": 5}
```

### ❌ Not Returning Dict

```python
# Wrong
def node(state):
    return "result"

# Correct
def node(state):
    return {"result": "value"}
```

### ❌ Returning All State Fields

```python
# Wrong (unnecessary)
def node(state):
    return {
        "query": state.query,
        "result": state.result,
        # ... all fields
    }

# Correct (only changed fields)
def node(state):
    return {"result": new_value}
```

## Quick Reference

```python
# BaseNode
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state):
        return {"result": "value"}

# Function node
def my_node(state):
    return {"result": "value"}

# Usage in graph
builder.add_node("my_node", MyNode())  # BaseNode
builder.add_node("my_node", my_node)   # Function

# With config
def execute(self, state, config=None, **kwargs):
    thread_id = self.get_thread_id(config)
    return {"thread_id": thread_id}

# With runtime
def execute(self, state, runtime=None, **kwargs):
    if runtime and runtime.store:
        data = runtime.store.get("key")
    return {"data": data}
```

## Resources

### References

- `references/node_lifecycle.md` - Detailed execute and __call__ lifecycle
- `references/config_runtime.md` - Using config and runtime parameters
- `references/async_patterns.md` - Async node patterns and best practices

### Examples

- `examples/simple_nodes.py` - Basic node patterns (BaseNode and function)
- `examples/config_nodes.py` - Using config in nodes
- `examples/runtime_nodes.py` - Using runtime in nodes
- `examples/async_nodes.py` - Async node implementations

### Scripts

- `scripts/validate_node.py` - Validate node implementation and get feedback

### Official Documentation

- Nodes: https://docs.langchain.com/oss/python/langgraph/nodes
- Async Nodes: https://docs.langchain.com/oss/python/langgraph/async-nodes
- Runtime: https://docs.langchain.com/oss/python/langgraph/runtime
