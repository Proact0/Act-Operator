---
name: state-management
description: Design and manage LangGraph state schemas - use when defining state structure, handling messages, managing data flow, or updating state patterns.
---

# State Management

**Use this skill when:**
- Designing state schemas for a Cast
- Adding or modifying state fields
- Working with messages and reducers
- Understanding state flow and updates
- Structuring input/output boundaries
- Troubleshooting state-related issues

## Overview

State is the data structure that flows through your LangGraph graph. Every node receives state, processes it, and returns updates. Proper state design is critical for maintainable and predictable graphs.

**Key concepts:**
- **State**: The complete data container that flows through the graph
- **InputState**: External API inputs (what users provide)
- **OutputState**: External API outputs (what users receive)
- **Reducers**: Functions that control how state updates merge (e.g., `add_messages`)
- **Annotations**: Metadata that adds behavior to state fields

## State Architecture

### Three-Layer Pattern

Act templates use a three-layer state pattern:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class InputState:
    """What the graph receives from users."""
    query: str

@dataclass(kw_only=True)
class OutputState:
    """What the graph returns to users."""
    messages: Annotated[list[AnyMessage], add_messages]

@dataclass(kw_only=True)
class State:
    """Complete internal state (superset of Input/Output)."""
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
```

**Why three layers?**
1. **InputState**: API contract for what users provide
2. **OutputState**: API contract for what users receive
3. **State**: Full internal state (may include intermediate data)

**Benefits:**
- Clear API boundaries
- Internal fields stay hidden from external users
- Type safety for inputs and outputs
- Flexibility to add internal-only fields

### When to Use Each Layer

**InputState only:**
```python
# Use for: Simple data-in scenarios
@dataclass(kw_only=True)
class InputState:
    document_url: str
    format: str
```

**OutputState only:**
```python
# Use for: Simple data-out scenarios
@dataclass(kw_only=True)
class OutputState:
    result: str
    metadata: dict
```

**All three layers:**
```python
# Use for: Complex graphs with internal state
@dataclass(kw_only=True)
class InputState:
    query: str

@dataclass(kw_only=True)
class OutputState:
    answer: str

@dataclass(kw_only=True)
class State:
    query: str
    answer: str
    # Internal only - not exposed via API
    intermediate_results: list[str]
    retry_count: int
```

## Dataclass Patterns

### Basic Dataclass

```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    """Always use kw_only=True for clarity."""
    query: str
    count: int = 0  # Default values
```

**`kw_only=True`** enforces keyword arguments:
```python
# ✅ Good: Explicit and clear
state = State(query="hello", count=5)

# ❌ Bad: Positional args error
state = State("hello", 5)  # TypeError
```

### Field Types

```python
from dataclasses import dataclass
from typing import Annotated

@dataclass(kw_only=True)
class State:
    # Basic types
    text: str
    count: int
    score: float
    enabled: bool

    # Collections
    items: list[str]
    metadata: dict[str, any]
    tags: set[str]

    # Optional fields
    description: str | None = None

    # With annotations (reducers)
    messages: Annotated[list[AnyMessage], add_messages]
```

### Docstrings

```python
@dataclass(kw_only=True)
class State:
    """Graph state container.

    Attributes:
        query: User's input query
        messages: Conversation history
        result: Processing result
    """

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    result: str | None = None
```

## Message Handling

### add_messages Reducer

The most common pattern for chat/agent applications:

```python
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]
```

**What `add_messages` does:**
- Appends new messages to existing list
- Handles message deduplication by ID
- Supports message updates (same ID replaces)
- Preserves message order

**Usage in nodes:**
```python
from langchain.messages import HumanMessage, AIMessage

def my_node(state: State) -> dict:
    # Add a single message
    return {
        "messages": [AIMessage(content="Hello!")]
    }

def another_node(state: State) -> dict:
    # Add multiple messages
    return {
        "messages": [
            HumanMessage(content="Question?"),
            AIMessage(content="Answer.")
        ]
    }
```

### Message Types

```python
from langchain.messages import (
    HumanMessage,      # User messages
    AIMessage,         # Assistant/model messages
    SystemMessage,     # System prompts
    ToolMessage,       # Tool responses
    FunctionMessage,   # Function call results
)

# Creating messages
human_msg = HumanMessage(content="Hello")
ai_msg = AIMessage(content="Hi there!")
system_msg = SystemMessage(content="You are a helpful assistant")

# With metadata
ai_msg = AIMessage(
    content="Result",
    additional_kwargs={"model": "gpt-4"}
)
```

### Reading Messages

```python
def process_node(state: State) -> dict:
    # Get all messages
    messages = state.messages

    # Get last message
    last_message = messages[-1] if messages else None

    # Filter by type
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]

    # Get message content
    if last_message:
        content = last_message.content

    return {"messages": [AIMessage(content="Processed")]}
```

## State Update Patterns

### Partial Updates

Nodes only return fields they want to update:

```python
def node_a(state: State) -> dict:
    # Only update 'count', leave other fields unchanged
    return {"count": state.count + 1}

def node_b(state: State) -> dict:
    # Update multiple fields
    return {
        "result": "Success",
        "processed": True
    }
```

### Default Reducer (Replace)

Without `Annotated`, fields are **replaced**:

```python
@dataclass(kw_only=True)
class State:
    items: list[str]  # No reducer = replace

def node(state: State) -> dict:
    # This REPLACES items, doesn't append
    return {"items": ["new_item"]}

# Before: items = ["a", "b"]
# After:  items = ["new_item"]
```

### Custom Reducers

Create custom merge logic:

```python
from typing import Annotated

def append_unique(existing: list, new: list) -> list:
    """Append only unique items."""
    result = existing.copy()
    for item in new:
        if item not in result:
            result.append(item)
    return result

@dataclass(kw_only=True)
class State:
    tags: Annotated[list[str], append_unique]

# Usage
# Before: tags = ["python", "langgraph"]
# Update: {"tags": ["langgraph", "fastapi"]}
# After:  tags = ["python", "langgraph", "fastapi"]
```

### Accumulating Data

```python
def sum_reducer(existing: int, new: int) -> int:
    return existing + new

@dataclass(kw_only=True)
class State:
    total: Annotated[int, sum_reducer] = 0

# Each node can add to total
def node(state: State) -> dict:
    return {"total": 5}  # Adds 5 to existing total
```

## Common State Structures

### Simple Query-Response

```python
@dataclass(kw_only=True)
class InputState:
    query: str

@dataclass(kw_only=True)
class OutputState:
    response: str

@dataclass(kw_only=True)
class State:
    query: str
    response: str
```

### Chat/Agent Application

```python
@dataclass(kw_only=True)
class InputState:
    messages: Annotated[list[AnyMessage], add_messages]

@dataclass(kw_only=True)
class OutputState:
    messages: Annotated[list[AnyMessage], add_messages]

@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]
    # Internal tracking
    tool_calls: list[dict] = None
    iterations: int = 0
```

### Data Processing Pipeline

```python
@dataclass(kw_only=True)
class InputState:
    data_url: str
    format: str

@dataclass(kw_only=True)
class OutputState:
    result: dict
    statistics: dict

@dataclass(kw_only=True)
class State:
    data_url: str
    format: str
    result: dict
    statistics: dict
    # Internal pipeline state
    raw_data: bytes = None
    parsed_data: list = None
    validated_data: list = None
```

### Multi-Step Workflow

```python
@dataclass(kw_only=True)
class InputState:
    task: str
    parameters: dict

@dataclass(kw_only=True)
class OutputState:
    status: str
    output: dict
    errors: list[str]

@dataclass(kw_only=True)
class State:
    task: str
    parameters: dict
    status: str
    output: dict
    errors: Annotated[list[str], lambda old, new: old + new]
    # Workflow tracking
    current_step: str = ""
    completed_steps: list[str] = None
    retry_count: int = 0
```

## Best Practices

### 1. Use kw_only=True Always

```python
# ✅ Good: Keyword-only arguments
@dataclass(kw_only=True)
class State:
    query: str
    count: int = 0

# ❌ Bad: Positional arguments error-prone
@dataclass
class State:
    query: str
    count: int = 0
```

### 2. Choose Reducers Carefully

```python
# ✅ Good: Messages should accumulate
messages: Annotated[list[AnyMessage], add_messages]

# ❌ Bad: Messages would be replaced
messages: list[AnyMessage]

# ✅ Good: Status should be replaced
status: str

# ❌ Bad: Status would accumulate (doesn't make sense)
status: Annotated[str, some_accumulator]
```

### 3. Provide Defaults for Optional Fields

```python
# ✅ Good: Clear defaults
@dataclass(kw_only=True)
class State:
    required_field: str
    optional_field: str | None = None
    counter: int = 0
    items: list = None

# ❌ Bad: No defaults for optional data
@dataclass(kw_only=True)
class State:
    required_field: str
    optional_field: str  # Should be optional with default
```

### 4. Document State Fields

```python
# ✅ Good: Clear documentation
@dataclass(kw_only=True)
class State:
    """Processing state.

    Attributes:
        query: User's search query
        messages: Conversation history (accumulated)
        result: Final processing result
        retry_count: Number of retry attempts
    """
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    result: str | None = None
    retry_count: int = 0
```

### 5. Keep State Flat

```python
# ✅ Good: Flat structure
@dataclass(kw_only=True)
class State:
    user_id: str
    user_name: str
    user_email: str

# ⚠️  Consider: Nested structures (harder to update)
@dataclass(kw_only=True)
class User:
    id: str
    name: str
    email: str

@dataclass(kw_only=True)
class State:
    user: User  # Requires replacing entire User object
```

### 6. Separate Internal from External State

```python
# ✅ Good: Internal fields not exposed
@dataclass(kw_only=True)
class InputState:
    query: str

@dataclass(kw_only=True)
class OutputState:
    answer: str

@dataclass(kw_only=True)
class State:
    query: str
    answer: str
    # Internal only
    _cache: dict = None
    _debug_info: list = None
```

## Troubleshooting

### Issue: State updates not working

**Symptoms**: Node returns update but state unchanged

**Causes:**
1. Returning wrong field names
2. Not returning a dict
3. Reducer behavior misunderstood

**Fix:**
```python
# ❌ Bad: Typo in field name
def node(state: State) -> dict:
    return {"messges": [...]}  # Typo!

# ✅ Good: Correct field name
def node(state: State) -> dict:
    return {"messages": [...]}

# ❌ Bad: Not returning dict
def node(state: State):
    state.messages = [...]  # Modifying in-place doesn't work
    return state

# ✅ Good: Return dict
def node(state: State) -> dict:
    return {"messages": [...]}
```

### Issue: Messages duplicating

**Symptoms**: Same messages appearing multiple times

**Fix:**
```python
# ✅ Ensure add_messages is used
messages: Annotated[list[AnyMessage], add_messages]

# Check: Are you returning existing messages?
def node(state: State) -> dict:
    # ❌ Bad: Returns ALL messages again
    return {"messages": state.messages + [new_message]}

    # ✅ Good: Only return NEW messages
    return {"messages": [new_message]}
```

### Issue: List replaced instead of appended

**Symptoms**: Previous list items disappear

**Fix:**
```python
# ❌ Bad: No reducer = replace behavior
items: list[str]

# ✅ Good: Add reducer for accumulation
def append_reducer(old: list, new: list) -> list:
    return old + new

items: Annotated[list[str], append_reducer]
```

### Issue: Cannot set state field

**Symptoms**: `AttributeError` when setting field

**Fix:**
```python
# ❌ Bad: State is immutable
def node(state: State) -> dict:
    state.count = 5  # Error!
    return {}

# ✅ Good: Return updates as dict
def node(state: State) -> dict:
    return {"count": 5}
```

### Issue: Type errors with Annotated

**Symptoms**: Type checker complains about Annotated fields

**Fix:**
```python
# Ensure proper imports
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

# Use AnyMessage for message lists
messages: Annotated[list[AnyMessage], add_messages]

# Not: list[str] or list[dict]
```

## Advanced Patterns

For more advanced state patterns including subgraphs, channels, and custom reducers, see:
- `references/state_patterns.md` - Detailed pattern catalog
- `references/annotations_guide.md` - Annotated and reducer deep dive

## Quick Reference

```python
# Basic state template
from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class InputState:
    """API inputs."""
    field: str

@dataclass(kw_only=True)
class OutputState:
    """API outputs."""
    result: str

@dataclass(kw_only=True)
class State:
    """Complete internal state."""
    field: str
    result: str
    messages: Annotated[list[AnyMessage], add_messages]

# Node update pattern
def my_node(state: State) -> dict:
    return {
        "result": "value",
        "messages": [AIMessage(content="Done")]
    }
```

## Related Skills

- **node-implementation**: Using state in nodes
- **graph-composition**: Passing state through graphs
- **cast-development**: Overall Cast structure
- **modules-integration**: State in chains and tools

## References

**Official documentation:**
- State: https://docs.langchain.com/oss/python/langgraph/graph-api#state
- Messages: https://docs.langchain.com/oss/python/langchain/messages
- Reducers: https://docs.langchain.com/oss/python/langgraph/graph-api#reducers
