# Node Lifecycle Reference

## Table of Contents

- [Introduction](#introduction)
- [Node Execution Flow](#node-execution-flow)
  - [BaseNode Lifecycle](#basenode-lifecycle)
  - [AsyncBaseNode Lifecycle](#asyncbasenode-lifecycle)
- [The __call__ Method](#the-__call__-method)
  - [Method Signature](#method-signature)
  - [Parameter Handling](#parameter-handling)
  - [Return Value Processing](#return-value-processing)
- [The execute Method](#the-execute-method)
  - [Simple Signature](#simple-signature)
  - [With Config Parameter](#with-config-parameter)
  - [With Runtime Parameter](#with-runtime-parameter)
  - [With Both Config and Runtime](#with-both-config-and-runtime)
  - [With **kwargs](#with-kwargs)
- [Parameter Details](#parameter-details)
  - [State Parameter](#state-parameter)
  - [Config Parameter](#config-parameter)
  - [Runtime Parameter](#runtime-parameter)
- [Node Initialization](#node-initialization)
  - [Default Initialization](#default-initialization)
  - [Custom Initialization](#custom-initialization)
  - [Initialization Parameters](#initialization-parameters)
- [Logging and Debugging](#logging-and-debugging)
  - [Built-in Logging](#built-in-logging)
  - [Verbose Mode](#verbose-mode)
  - [Custom Logging](#custom-logging)
- [Error Handling](#error-handling)
  - [Try-Catch in execute](#try-catch-in-execute)
  - [Error State Updates](#error-state-updates)
  - [Exception Propagation](#exception-propagation)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Introduction

Understanding the node lifecycle is crucial for implementing robust LangGraph nodes. This guide explains how BaseNode and AsyncBaseNode handle execution, parameter passing, and state updates.

**Key Concepts:**
- `__call__`: Entry point called by LangGraph, handles parameter dispatch
- `execute`: User-defined method containing node logic
- State: Immutable input, nodes return dict updates
- Config: Optional runtime configuration (thread_id, tags, etc.)
- Runtime: Optional runtime services (store, stream)

---

## Node Execution Flow

### BaseNode Lifecycle

```
Graph invokes node
    ↓
__call__(state, config=None, runtime=None, **kwargs)
    ↓
Inspect execute() signature
    ↓
Call execute() with appropriate parameters
    ↓
execute(state, config?, runtime?, **kwargs?)
    ↓
Return dict of state updates
    ↓
LangGraph merges updates into state
```

**Example:**
```python
class MyNode(BaseNode):
    def execute(self, state):
        return {"result": "value"}

# When graph runs:
node = MyNode()
updates = node(state, config=config, runtime=runtime)
# node.__call__ inspects execute signature
# Calls: self.execute(state)
# Returns: {"result": "value"}
```

### AsyncBaseNode Lifecycle

Same flow, but with async/await:

```python
class MyAsyncNode(AsyncBaseNode):
    async def execute(self, state):
        data = await fetch_data()
        return {"data": data}

# When graph runs:
node = MyAsyncNode()
updates = await node(state, config=config, runtime=runtime)
# Calls: await self.execute(state)
```

---

## The __call__ Method

### Method Signature

```python
def __call__(self, state, config=None, runtime=None, **kwargs):
    """Entry point called by LangGraph.
    
    Args:
        state: Current graph state
        config: Optional RunnableConfig
        runtime: Optional runtime services
        **kwargs: Additional keyword arguments
        
    Returns:
        dict: State updates
    """
```

**You never override __call__**. It's implemented in BaseNode/AsyncBaseNode and handles:
1. Parameter inspection
2. Logging setup
3. Calling execute() with correct parameters
4. Return value validation

### Parameter Handling

__call__ uses introspection to determine what parameters execute() accepts:

```python
# If execute signature is:
def execute(self, state):
    pass
# __call__ calls: self.execute(state)

# If execute signature is:
def execute(self, state, config):
    pass
# __call__ calls: self.execute(state, config)

# If execute signature is:
def execute(self, state, config, runtime):
    pass
# __call__ calls: self.execute(state, config, runtime)

# If execute signature is:
def execute(self, state, **kwargs):
    pass
# __call__ calls: self.execute(state, config=config, runtime=runtime, **kwargs)
```

### Return Value Processing

__call__ expects execute() to return a dict:

```python
# ✅ Correct
def execute(self, state):
    return {"result": "value"}

# ❌ Wrong - returns non-dict
def execute(self, state):
    return "value"  # TypeError

# ❌ Wrong - returns State object
def execute(self, state):
    state.result = "value"
    return state  # Wrong!

# ✅ Correct - empty update
def execute(self, state):
    return {}  # Valid: no updates
```

---

## The execute Method

### Simple Signature

Use when only state is needed:

```python
class SimpleNode(BaseNode):
    def execute(self, state):
        """Only needs state."""
        result = process(state.input)
        return {"output": result}
```

**Advantages:**
- Simplest signature
- Clearest intent
- Fastest (no parameter passing overhead)

**Use when:**
- No need for thread_id, tags, or store
- Pure state transformation
- Most common case

### With Config Parameter

Use when need thread_id, run_id, or tags:

```python
class ConfigAwareNode(BaseNode):
    def execute(self, state, config):
        """Needs config for thread_id."""
        thread_id = self.get_thread_id(config)
        self.log(f"Processing for thread: {thread_id}")
        
        # Access config fields
        run_id = config.get("run_id") if config else None
        tags = config.get("tags", []) if config else []
        
        return {"thread_id": thread_id}
```

**Config fields:**
- `configurable`: Dict of configuration values
  - `thread_id`: Current thread identifier
  - `checkpoint_ns`: Checkpoint namespace
- `run_id`: Current run identifier
- `tags`: List of tags for this run
- `metadata`: Additional metadata

**Use when:**
- Need to track which thread/conversation
- Want to log run_id
- Conditional logic based on tags
- Per-thread customization

### With Runtime Parameter

Use when need store or stream:

```python
class RuntimeAwareNode(BaseNode):
    def execute(self, state, runtime):
        """Needs runtime for persistence."""
        if runtime and runtime.store:
            # Save to persistent store
            runtime.store.put(("user", "data"), "key", state.data)
            
            # Load from persistent store
            saved_data = runtime.store.get(("user", "data"), "key")
        
        return {"saved": True}
```

**Runtime fields:**
- `store`: BaseStore instance for persistence
- `stream`: Streaming capabilities (if enabled)

**Use when:**
- Need to persist data across runs
- Want to stream outputs
- Cross-thread data sharing

### With Both Config and Runtime

Use when need both:

```python
class FullAwareNode(BaseNode):
    def execute(self, state, config, runtime):
        """Needs both config and runtime."""
        thread_id = self.get_thread_id(config)
        
        if runtime and runtime.store:
            # Per-thread storage
            key = f"thread_{thread_id}_data"
            runtime.store.put(("threads",), key, state.data)
        
        return {"processed": True}
```

**Use when:**
- Need thread-aware persistence
- Per-thread caching
- Complex workflows

### With **kwargs

Use for maximum flexibility:

```python
class FlexibleNode(BaseNode):
    def execute(self, state, **kwargs):
        """Flexible parameter access."""
        config = kwargs.get("config")
        runtime = kwargs.get("runtime")
        
        if config:
            thread_id = self.get_thread_id(config)
            self.log(f"Thread: {thread_id}")
        
        if runtime and runtime.store:
            # Use store
            pass
        
        return {"result": "value"}
```

**Use when:**
- Optional config/runtime access
- Future-proofing
- Conditional parameter use

---

## Parameter Details

### State Parameter

**Type:** Dataclass instance (your State class)

**Properties:**
- Read-only: Don't modify in-place
- Type-hinted: IDE autocomplete works
- All fields accessible: `state.field_name`

**Example:**
```python
@dataclass(kw_only=True)
class State:
    query: str
    count: int = 0

def execute(self, state):
    # Access fields
    query = state.query
    count = state.count
    
    # ❌ Don't modify
    state.count = 5  # WRONG!
    
    # ✅ Return updates
    return {"count": count + 1}
```

### Config Parameter

**Type:** `RunnableConfig` dict (can be None)

**Structure:**
```python
{
    "configurable": {
        "thread_id": "thread-123",
        "checkpoint_ns": "namespace",
        # ... other configurable values
    },
    "run_id": "run-abc-def",
    "tags": ["tag1", "tag2"],
    "metadata": {"key": "value"}
}
```

**Accessing thread_id:**
```python
# Using helper method (recommended)
thread_id = self.get_thread_id(config)

# Manual access
if config and "configurable" in config:
    thread_id = config["configurable"].get("thread_id")
```

**Safe access pattern:**
```python
def execute(self, state, config):
    # Always check if config exists
    if config:
        thread_id = self.get_thread_id(config)
        tags = config.get("tags", [])
        metadata = config.get("metadata", {})
    else:
        thread_id = None
        tags = []
        metadata = {}
```

### Runtime Parameter

**Type:** Runtime object (can be None)

**Properties:**
- `store`: BaseStore instance or None
- `stream`: Streaming interface or None

**Store operations:**
```python
def execute(self, state, runtime):
    if runtime and runtime.store:
        # Put: store.put(namespace_tuple, key, value)
        runtime.store.put(("user", "123"), "preferences", {
            "theme": "dark",
            "language": "en"
        })
        
        # Get: store.get(namespace_tuple, key)
        prefs = runtime.store.get(("user", "123"), "preferences")
        
        # Search: store.search(namespace_tuple_prefix)
        all_user_data = runtime.store.search(("user", "123"))
```

**Namespace conventions:**
```python
# User data
("user", user_id)

# Thread data
("thread", thread_id)

# Global data
("global",)

# Hierarchical
("organization", org_id, "department", dept_id)
```

---

## Node Initialization

### Default Initialization

```python
class MyNode(BaseNode):
    pass

# Usage
node = MyNode()
# name = "MyNode" (auto-set from class name)
# verbose = False (default)
```

### Custom Initialization

```python
class ConfigurableNode(BaseNode):
    def __init__(self, multiplier=2, threshold=0.5, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier
        self.threshold = threshold
    
    def execute(self, state):
        value = state.value * self.multiplier
        if value > self.threshold:
            return {"value": value}
        return {}

# Usage
node = ConfigurableNode(multiplier=3, threshold=1.0)
node_verbose = ConfigurableNode(multiplier=3, verbose=True)
```

### Initialization Parameters

**BaseNode accepts:**
- `name`: str - Node name (defaults to class name)
- `verbose`: bool - Enable logging (default False)

**Always pass **kwargs to super().__init__:**
```python
# ✅ Correct
def __init__(self, custom_param, **kwargs):
    super().__init__(**kwargs)
    self.custom_param = custom_param

# ❌ Wrong - loses name/verbose
def __init__(self, custom_param):
    super().__init__()  # Can't pass name/verbose!
```

---

## Logging and Debugging

### Built-in Logging

```python
class LoggingNode(BaseNode):
    def execute(self, state):
        self.log("Starting processing")
        self.log("Query:", state.query)
        self.log("Data:", data={"count": len(items)})
        
        return {"result": "done"}
```

**Only logs when `verbose=True`:**
```python
node = LoggingNode(verbose=True)
# Now self.log() outputs will appear
```

### Verbose Mode

Enable globally or per-node:

```python
# Per node
node = MyNode(verbose=True)

# All nodes in graph
graph = builder.compile(debug=True)  # Note: LangGraph feature
```

### Custom Logging

```python
import logging

class CustomLogNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
    
    def execute(self, state):
        self.logger.info(f"Processing: {state.query}")
        self.log("Verbose log")  # Only if verbose=True
        return {}
```

---

## Error Handling

### Try-Catch in execute

```python
class RobustNode(BaseNode):
    def execute(self, state):
        try:
            result = risky_operation(state.input)
            return {"result": result, "error": None}
        except ValueError as e:
            self.log("ValueError:", error=str(e))
            return {"result": None, "error": f"Invalid value: {e}"}
        except Exception as e:
            self.log("Unexpected error:", error=str(e))
            return {"result": None, "error": str(e)}
```

### Error State Updates

**Pattern 1: Error field**
```python
@dataclass(kw_only=True)
class State:
    result: str | None = None
    error: str | None = None

def execute(self, state):
    try:
        return {"result": process(), "error": None}
    except Exception as e:
        return {"result": None, "error": str(e)}
```

**Pattern 2: Error accumulation**
```python
@dataclass(kw_only=True)
class State:
    errors: Annotated[list[str], lambda old, new: old + new] = None

def execute(self, state):
    try:
        return {"result": process()}
    except Exception as e:
        return {"errors": [f"NodeName: {e}"]}
```

### Exception Propagation

```python
class FailFastNode(BaseNode):
    def execute(self, state):
        # Let exceptions propagate
        result = risky_operation(state.input)
        return {"result": result}

# Graph will catch and handle
try:
    result = graph.invoke({"input": "data"})
except Exception as e:
    print(f"Graph failed: {e}")
```

---

## Best Practices

1. **Choose simplest signature**: Use only parameters you need
2. **Don't modify state**: Always return dict updates
3. **Handle None parameters**: Check `if config:`, `if runtime:`
4. **Use type hints**: Helps IDE and debugging
5. **Document execute()**: Explain what node does
6. **Use self.log()**: For debugging, not production logging
7. **Return empty dict if no updates**: `return {}` is valid
8. **Initialize with super().__init__(**kwargs)**: Always pass **kwargs
9. **Keep execute() focused**: One clear responsibility
10. **Test nodes in isolation**: Unit test execute() directly

---

## Common Patterns

### Pattern: Conditional Updates

```python
def execute(self, state):
    if should_process(state):
        return {"result": process(state.input)}
    return {}  # No updates
```

### Pattern: Multiple Field Updates

```python
def execute(self, state):
    result = process(state.input)
    return {
        "result": result,
        "count": state.count + 1,
        "timestamp": datetime.now(),
        "status": "complete"
    }
```

### Pattern: Incremental Updates

```python
def execute(self, state):
    # First update
    intermediate = step1(state.input)
    
    # Can't return multiple times!
    # Must combine into single dict
    return {
        "intermediate": intermediate,
        "final": step2(intermediate),
        "count": state.count + 1
    }
```

### Pattern: State-Based Logic

```python
def execute(self, state):
    if state.iteration == 0:
        return initialize(state)
    elif state.iteration < 5:
        return process(state)
    else:
        return finalize(state)
```

---

## Troubleshooting

### Issue: "TypeError: execute() missing required positional argument"

**Cause:** Mismatch between signature and call.

**Fix:**
```python
# ❌ Wrong
def execute(config, state):  # Wrong order!
    pass

# ✅ Correct
def execute(self, state, config):
    pass
```

### Issue: "TypeError: execute() got an unexpected keyword argument 'config'"

**Cause:** execute() doesn't accept config but __call__ passes it.

**Fix:**
```python
# If you don't need config, don't include it
def execute(self, state):  # Correct - config won't be passed
    pass

# Or accept and ignore it
def execute(self, state, **kwargs):  # Also works
    # kwargs will have config, runtime
    pass
```

### Issue: State not updating

**Cause 1:** Not returning dict
```python
# ❌ Wrong
def execute(self, state):
    state.count = 5  # Modifying in-place doesn't work
    return state

# ✅ Correct
def execute(self, state):
    return {"count": 5}
```

**Cause 2:** Returning None
```python
# ❌ Wrong
def execute(self, state):
    process(state.input)
    # Forgot to return!

# ✅ Correct
def execute(self, state):
    result = process(state.input)
    return {"result": result}
```

### Issue: "AttributeError: 'MyNode' object has no attribute 'log'"

**Cause:** Didn't call super().__init__()

**Fix:**
```python
# ❌ Wrong
class MyNode(BaseNode):
    def __init__(self, param):
        self.param = param  # Forgot super().__init__()

# ✅ Correct
class MyNode(BaseNode):
    def __init__(self, param, **kwargs):
        super().__init__(**kwargs)
        self.param = param
```

### Issue: config is always None

**Cause:** Didn't pass config when invoking graph

**Fix:**
```python
# ❌ Wrong
result = graph.invoke({"input": "data"})

# ✅ Correct
from langgraph.graph import RunnableConfig

config = RunnableConfig(
    configurable={"thread_id": "thread-123"}
)
result = graph.invoke({"input": "data"}, config=config)
```

---

## Summary

**Node Lifecycle:**
1. Graph calls `node(state, config, runtime)`
2. `__call__` inspects `execute()` signature
3. `__call__` calls `execute()` with correct params
4. `execute()` returns dict of updates
5. Graph merges updates into state

**Key Rules:**
- Never override `__call__`
- Always implement `execute`
- Return dict, not State object
- Don't modify state in-place
- Use simplest signature needed
- Check if optional params are None
- Call `super().__init__(**kwargs)`

**Signature Choices:**
- `execute(self, state)` - Most common
- `execute(self, state, config)` - Need thread_id/tags
- `execute(self, state, runtime)` - Need store/stream  
- `execute(self, state, config, runtime)` - Need both
- `execute(self, state, **kwargs)` - Maximum flexibility
