# State Management

## When to Use This Resource
Read when defining cast state schema, understanding reducers, or implementing state updates.

---

## Key Concepts

**State** is a TypedDict that flows through your graph, updated by nodes at each step.

**Reducers** define how updates are applied: append (operator.add) vs overwrite (default).

---

## Basic State Pattern

```python
"""State schema for my cast."""

from typing_extensions import TypedDict

class MyState(TypedDict):
    """Cast state.

    Attributes:
        query: User query (overwrite semantics)
        result: Processing result (overwrite semantics)
    """
    query: str  # Plain field - last write wins
    result: str # Plain field - last write wins
```

**Location:** `casts/my_cast/state.py`

---

## State with Reducers

### Append-Only Messages

```python
from typing_extensions import TypedDict
from typing import Annotated
import operator

class ChatState(TypedDict):
    """Chat cast state with message history.

    Attributes:
        messages: Conversation history (append-only)
        current_mode: Current operation mode (overwrite)
    """
    messages: Annotated[list, operator.add]  # Appends new messages
    current_mode: str  # Overwrite
```

**How it works:**
```python
# Node 1 returns:
{"messages": [AIMessage("Hello")]}  # State: [AIMessage("Hello")]

# Node 2 returns:
{"messages": [HumanMessage("Hi")]}  # State: [AIMessage("Hello"), HumanMessage("Hi")]

# Reducer (operator.add) concatenates lists
```

---

### MessagesState (Built-in)

```python
from langgraph.graph import MessagesState

class MyState(MessagesState):
    """Inherit built-in message handling.

    Inherits:
        messages: Annotated[list[AnyMessage], add_messages]

    Attributes:
        custom_field: Your additional fields
    """
    custom_field: str
```

**MessagesState provides:**
- `messages` field with `add_messages` reducer
- Smart message deduplication by ID
- Handles all message types (Human, AI, System, Tool)

**When to use:**
- ✓ Chat/conversation casts
- ✓ Need message history
- ✗ Non-conversational workflows (use plain TypedDict)

---

## Reducer Types

### operator.add (Append Lists)

```python
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list[str], operator.add]

# Node returns: {"items": ["a", "b"]}
# State: ["a", "b"]

# Next node returns: {"items": ["c"]}
# State: ["a", "b", "c"]  # Appended
```

**Use when:** Accumulating items, building lists, message history

---

### Custom Reducer (Advanced)

```python
def merge_dicts(existing: dict, update: dict) -> dict:
    """Custom reducer that merges dicts."""
    return {**existing, **update}

class State(TypedDict):
    metadata: Annotated[dict, merge_dicts]
```

**Use when:** Custom merge logic needed (rare)

---

### No Reducer (Overwrite - Default)

```python
class State(TypedDict):
    result: str  # Plain field - no Annotated

# Node returns: {"result": "first"}
# State: "first"

# Next node returns: {"result": "second"}
# State: "second"  # Overwrites
```

**Use when:** Latest value is correct (most fields)

---

## Input/Output Schemas

### Separate Input and Output

```python
from typing_extensions import TypedDict

class InputState(TypedDict):
    """What graph receives."""
    query: str

class OutputState(TypedDict):
    """What graph returns."""
    result: str
    confidence: float

class State(TypedDict):
    """Internal working state."""
    query: str
    result: str
    confidence: float
    intermediate_data: list  # Not in output
```

**In graph.py:**
```python
from langgraph.graph import StateGraph

builder = StateGraph(
    State,
    input=InputState,
    output=OutputState
)
```

**Use when:** Want to hide intermediate state from external API

---

## State Update Patterns

### Partial Updates

```python
class State(TypedDict):
    field_a: str
    field_b: str
    field_c: str

# Node only updates one field:
def my_node(state: State) -> dict:
    return {"field_a": "new_value"}  # field_b, field_c unchanged
```

**Nodes return partial state** - only changed fields.

---

### Multiple Field Updates

```python
def my_node(state: State) -> dict:
    return {
        "field_a": "value_a",
        "field_b": "value_b",
        "messages": [AIMessage("Done")]  # With reducer
    }
```

---

### Conditional Updates

```python
def my_node(state: State) -> dict:
    updates = {}

    if state.get("needs_processing"):
        updates["result"] = process(state["data"])

    if state.get("mode") == "verbose":
        updates["messages"] = [AIMessage("Processed")]

    return updates  # Can be empty dict
```

---

## Common Patterns

### Chat with Tools

```python
from langgraph.graph import MessagesState

class ChatState(MessagesState):
    """Chat with tool usage.

    Inherits:
        messages: Message history with add_messages reducer

    Attributes:
        tool_results: Accumulated tool outputs
    """
    tool_results: Annotated[list[dict], operator.add]
```

---

### Multi-Stage Processing

```python
class ProcessingState(TypedDict):
    """Multi-stage data processing.

    Attributes:
        raw_data: Input data (overwrite)
        processed_data: After processing (overwrite)
        results: Accumulated results (append)
        current_stage: Current processing stage (overwrite)
    """
    raw_data: dict
    processed_data: dict
    results: Annotated[list, operator.add]  # Accumulate
    current_stage: str
```

---

### Research/Search Cast

```python
class ResearchState(MessagesState):
    """Research assistant state.

    Inherits:
        messages: Conversation history

    Attributes:
        query: Current research query (overwrite)
        search_results: Web search results (overwrite)
        documents: Retrieved documents (overwrite)
        topics: Tracked research topics (append)
    """
    query: str
    search_results: list[dict]  # Latest results only
    documents: list[dict]  # Latest documents only
    topics: Annotated[list[str], operator.add]  # Accumulate
```

---

## Anti-Patterns

### ❌ Returning Full State

```python
def my_node(state: State) -> dict:
    # ❌ WRONG - Don't return entire state
    state["field_a"] = "new_value"
    return state  # Returns everything unnecessarily
```

```python
def my_node(state: State) -> dict:
    # ✓ CORRECT - Return only updates
    return {"field_a": "new_value"}
```

---

### ❌ Wrong Reducer Type

```python
# ❌ WRONG - Returning string to list reducer
messages: Annotated[list, operator.add]

def my_node(state):
    return {"messages": "not a list"}  # TypeError!
```

```python
# ✓ CORRECT - Match reducer type
messages: Annotated[list, operator.add]

def my_node(state):
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage("correct")]}  # List
```

---

### ❌ Mutating State Directly

```python
# ❌ WRONG - Mutating input state
def my_node(state: State) -> dict:
    state["field"] = "value"  # Don't mutate!
    return state
```

```python
# ✓ CORRECT - Return new dict
def my_node(state: State) -> dict:
    return {"field": "value"}  # New dict
```

---

## Decision Framework

**Q: Should I use a reducer?**
- Accumulating data → `Annotated[list, operator.add]`
- Latest value only → Plain field
- Messages → Use `MessagesState`

**Q: MessagesState vs TypedDict?**
- Chat/conversation → `MessagesState`
- Non-conversational → `TypedDict`

**Q: Need input/output schemas?**
- External API → Yes (hide internals)
- Internal only → No (use same schema)

**Q: What type for field?**
- Follow reducers: `list` for `operator.add`
- Use appropriate types: `str`, `int`, `dict`, `list`

---

## References
- [LangGraph State Docs](https://docs.langchain.com/oss/python/langgraph/)
- Related: core/node-patterns.md (how nodes update state)
- Related: core/graph-construction.md (how to use state in graph)
