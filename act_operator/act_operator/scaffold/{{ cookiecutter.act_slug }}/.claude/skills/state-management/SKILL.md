---
name: state-management
description: Design and manage LangGraph state schemas. Use when defining state structure, handling messages, managing data flow, or updating state patterns in Act projects.
---

# State Management

## Overview

State management in LangGraph defines how data flows through the graph. Every node receives state, processes it, and returns updates. This skill provides workflows and patterns for designing effective state schemas.

## When to Use This Skill

- Defining state schemas for a new Cast
- Adding or modifying state fields
- Working with messages and reducers
- Structuring input/output boundaries
- Troubleshooting state-related issues

## Workflow

### 1. Determine State Layers

Choose the appropriate state structure:

**Simple (Single Layer)**:
```python
@dataclass(kw_only=True)
class State:
    query: str
    result: str = ""
```

**Three-Layer (Recommended)**:
```python
@dataclass(kw_only=True)
class InputState:
    """What users provide."""
    query: str

@dataclass(kw_only=True)
class OutputState:
    """What users receive."""
    messages: Annotated[list[AnyMessage], add_messages]

@dataclass(kw_only=True)
class State:
    """Complete internal state."""
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    # Internal fields
    iterations: int = 0
```

**When to use three layers**: Graphs with internal state that should not be exposed to external API.

### 2. Define Required Fields

Identify essential state fields:

```python
@dataclass(kw_only=True)
class State:
    # Required fields (no default)
    query: str

    # Optional fields (with default)
    result: str | None = None
    count: int = 0
```

### 3. Add Reducers for Accumulation

Use `Annotated` when fields should accumulate rather than replace:

```python
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class State:
    # Replaces on update
    status: str = "pending"

    # Accumulates on update
    messages: Annotated[list[AnyMessage], add_messages]
    errors: Annotated[list[str], lambda old, new: old + new] = None
```

**Common reducers**:
- `add_messages` - For message lists (handles deduplication)
- `lambda old, new: old + new` - Append lists
- `lambda old, new: max(old, new)` - Keep maximum
- `lambda old, new: {**old, **new}` - Merge dicts

### 4. Document State Fields

Add clear docstrings:

```python
@dataclass(kw_only=True)
class State:
    """Graph state container.

    Attributes:
        query: User's input query
        messages: Conversation history (accumulated)
        iterations: Number of processing iterations
        result: Final result (None until complete)
    """
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    iterations: int = 0
    result: str | None = None
```

## Common Patterns

### Message-Based State

For chat/agent applications:

```python
@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]
```

See `examples/message_state.py` for complete example.

### Data Processing State

For ETL/pipeline workflows:

```python
@dataclass(kw_only=True)
class State:
    raw_data: bytes = None
    parsed_data: list = None
    cleaned_data: list = None
    result: dict = None
```

See `examples/simple_state.py` for complete example.

### Complex State

For multi-step workflows with tracking:

```python
@dataclass(kw_only=True)
class State:
    # Input/output
    query: str
    answer: str = None

    # Tracking
    iterations: int = 0
    errors: Annotated[list[str], lambda old, new: old + new] = None

    # Internal
    intermediate_results: list = None
```

See `examples/complex_state.py` for complete example.

## Validation Checklist

Before finalizing state design:

- [ ] All required fields have no defaults
- [ ] Optional fields have appropriate defaults
- [ ] `kw_only=True` is used on all dataclasses
- [ ] Reducers are used for accumulating fields
- [ ] Messages use `add_messages` reducer
- [ ] State fields are documented in docstring
- [ ] Input/Output schemas match State schema
- [ ] No fields are duplicated across layers

## Common Issues

**Issue**: State updates not working
- **Check**: Return dict from nodes, not modified state object
- **Fix**: `return {"field": value}` not `state.field = value; return state`

**Issue**: Messages duplicating
- **Check**: Using `add_messages` reducer
- **Check**: Not returning existing messages again
- **Fix**: Return only NEW messages: `return {"messages": [new_message]}`

**Issue**: List replaced instead of appended
- **Check**: Field has reducer annotation
- **Fix**: Add reducer: `field: Annotated[list, lambda old, new: old + new]`

## Quick Reference

```python
# Basic state
from dataclasses import dataclass
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class State:
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    count: int = 0

# Node update
def my_node(state: State) -> dict:
    return {
        "count": state.count + 1,
        "messages": [AIMessage(content="Done")]
    }
```

## Resources

### References

- `references/state_patterns.md` - Comprehensive state pattern catalog with 20+ patterns
- `references/annotations_guide.md` - Deep dive into Annotated and reducers

### Examples

- `examples/simple_state.py` - Basic state for data processing
- `examples/message_state.py` - Chat/agent state with messages
- `examples/complex_state.py` - Multi-layer state with tracking

### Official Documentation

- State API: https://docs.langchain.com/oss/python/langgraph/graph-api#state
- Messages: https://docs.langchain.com/oss/python/langchain/messages
- Reducers: https://docs.langchain.com/oss/python/langgraph/graph-api#reducers
