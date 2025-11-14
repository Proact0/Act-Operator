---
# State Resource
# LangGraph 1.0 State Schema Patterns
---

# State Management

## Overview

State in LangGraph flows through nodes and gets updated. Define schemas for input, output, and internal state.

## Core Pattern

```python
# modules/state.py
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage

# Three-layer pattern

class InputState(TypedDict):
    """What the graph receives."""
    query: str
    user_id: str

class OutputState(TypedDict):
    """What the graph returns."""
    result: str
    status: str

class State(MessagesState):
    """Full internal state (includes Input + Output + intermediate fields)."""
    # InputState fields
    query: str
    user_id: str

    # OutputState fields
    result: str
    status: str

    # Intermediate fields (not in input/output)
    intermediate_data: dict
    step_count: int
    # messages inherited from MessagesState
```

## Using in Graph

```python
# graph.py
from langgraph.graph import StateGraph
from .modules.state import InputState, OutputState, State

builder = StateGraph(
    State,  # Full state
    input_schema=InputState,  # Restrict input
    output_schema=OutputState  # Restrict output
)
```

**Benefits:**
- Clear API contract (input/output)
- Type safety
- Internal fields hidden from users

## State Updates

### Returning Updates

```python
def execute(self, state, runtime=None, **kwargs):
    # Read state
    query = state.get("query", "")
    count = state.get("step_count", 0)

    # Return updates - LangGraph merges automatically
    return {
        "result": "processed",
        "step_count": count + 1,
        "intermediate_data": {"key": "value"}
    }
```

**CRITICAL:** Do NOT mutate state directly:

```python
# ❌ WRONG
def execute(self, state, runtime=None, **kwargs):
    state["result"] = "processed"  # NO! Mutation!
    return state

# ✅ CORRECT
def execute(self, state, runtime=None, **kwargs):
    return {"result": "processed"}  # Return updates
```

## MessagesState

For conversational graphs, extend `MessagesState`:

```python
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage

class State(MessagesState):
    """State with messages."""
    query: str
    other_field: str
    # messages: list[AnyMessage]  # Inherited
```

**Using messages:**
```python
from langchain_core.messages import AIMessage

def execute(self, state, runtime=None, **kwargs):
    messages = state.get("messages", [])

    # Add message
    new_message = AIMessage(content="Hello")

    return {"messages": [new_message]}  # Appends to list
```

## Reducers

Control how state updates merge with reducers:

```python
from typing import Annotated
from operator import add

class State(TypedDict):
    """State with custom reducers."""
    count: Annotated[int, add]  # Sum updates
    items: Annotated[list, add]  # Concatenate lists
    value: str  # Replace (default)
```

**Behavior:**
```python
# Initial state: {"count": 5, "items": ["a"], "value": "old"}

# Node returns: {"count": 3, "items": ["b"], "value": "new"}

# Result: {"count": 8, "items": ["a", "b"], "value": "new"}
#          ^sum         ^concatenate       ^replace
```

**Common reducers:**
- `operator.add`: Sum numbers or concatenate lists
- `operator.or_`: Merge dicts
- Custom function: `def my_reducer(current, update): ...`

## Channels

Channels are state fields with update logic:

```python
from langgraph.graph import StateGraph
from typing import Annotated

def merge_dict(current: dict, update: dict) -> dict:
    """Custom merge logic."""
    result = current.copy()
    result.update(update)
    return result

class State(TypedDict):
    data: Annotated[dict, merge_dict]  # Custom reducer
    count: int  # Default (replace)
```

## State Access Patterns

### Optional Fields

```python
def execute(self, state, runtime=None, **kwargs):
    # Safe access with defaults
    value = state.get("optional_field", "default")

    # Check existence
    if "required_field" in state:
        process(state["required_field"])
```

### Nested State

```python
class State(TypedDict):
    config: dict
    metadata: dict

def execute(self, state, runtime=None, **kwargs):
    # Access nested
    theme = state.get("config", {}).get("theme", "light")

    # Update nested
    config = state.get("config", {}).copy()
    config["theme"] = "dark"

    return {"config": config}
```

### List State

```python
class State(TypedDict):
    results: list[str]

def execute(self, state, runtime=None, **kwargs):
    results = state.get("results", [])

    # Add to list
    new_results = results + ["new item"]

    return {"results": new_results}
```

## Examples

### Simple State

```python
class State(TypedDict):
    """Minimal state."""
    input: str
    output: str
    status: str
```

### Conversational State

```python
from langgraph.graph import MessagesState

class ConversationState(MessagesState):
    """Chat with context."""
    user_id: str
    context: dict
    # messages inherited
```

### Multi-Stage State

```python
class PipelineState(TypedDict):
    """Data pipeline state."""
    raw_data: str
    cleaned_data: str
    analyzed_data: dict
    results: list[str]
    status: str
    error: str | None
```

### State with Reducers

```python
from typing import Annotated
from operator import add

class AggregationState(TypedDict):
    """State that accumulates."""
    total_count: Annotated[int, add]
    items: Annotated[list, add]
    latest_value: str  # Replaces
```

## State Validation

Using Pydantic for runtime validation:

```python
from pydantic import BaseModel, Field

class ValidatedState(BaseModel):
    """State with validation."""
    query: str = Field(min_length=1, max_length=500)
    count: int = Field(ge=0, le=100)
    email: str = Field(pattern=r"^\S+@\S+\.\S+$")
```

**Note:** LangGraph 1.0 primarily uses TypedDict. Pydantic is optional for validation.

## State in Graph Builder

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(
    State,  # State schema
    input_schema=InputState,  # Optional: restrict input
    output_schema=OutputState  # Optional: restrict output
)

builder.add_node("process", ProcessNode())
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()

# Invoke with input that matches InputState
result = graph.invoke({"query": "hello", "user_id": "123"})
# Returns output matching OutputState
```

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Mutating state directly | Return dict updates |
| Missing MessagesState for chat | Extend MessagesState |
| Not using reducers for lists | Add Annotated with operator.add |
| Overwriting nested dicts | Copy dict, update, return |
| Wrong type hints | Match actual data types |
| No input/output schemas | Define for clear API |

## Performance Tips

**Keep state small:**
- ✅ Store references/IDs, not full objects
- ✅ Use intermediate fields for temporary data
- ❌ Don't accumulate unbounded lists

**Efficient updates:**
```python
# ✅ GOOD: Return only what changed
return {"status": "complete"}

# ❌ BAD: Return entire state
return {**state, "status": "complete"}
```

## Next Steps

- **Using state in nodes:** See `resources/nodes.md`
- **Conditional routing on state:** See `resources/edges.md`
- **Memory patterns:** See `resources/memory.md`
