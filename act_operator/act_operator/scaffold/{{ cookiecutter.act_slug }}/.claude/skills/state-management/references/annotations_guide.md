# Annotated and Reducers Deep Dive

Complete guide to using `Annotated` with reducers in LangGraph state.

## Table of Contents

1. [Basics](#basics)
2. [Built-in Reducers](#built-in-reducers)
3. [Custom Reducers](#custom-reducers)
4. [Reducer Patterns](#reducer-patterns)
5. [Advanced Usage](#advanced-usage)

## Basics

### What is Annotated?

`Annotated` is a Python typing feature that adds metadata to type hints:

```python
from typing import Annotated

# Basic type
messages: list[str]

# Type with metadata
messages: Annotated[list[str], "some metadata"]
```

### What are Reducers?

Reducers are functions that control **how state updates merge**:

```python
def my_reducer(existing_value, new_value):
    """Merge existing and new values."""
    return merged_value

# Use in state
field: Annotated[type, my_reducer]
```

**Without reducer:**
```python
items: list[str]  # New value REPLACES old value
```

**With reducer:**
```python
items: Annotated[list[str], my_reducer]  # my_reducer merges values
```

### How Reducers Work

```python
# Initial state
state = State(items=[])

# Node 1 updates
node_1_update = {"items": ["a", "b"]}
# State now: items = ["a", "b"]

# Node 2 updates
node_2_update = {"items": ["c"]}

# WITHOUT reducer:
# items = ["c"]  (replaced!)

# WITH append reducer:
# items = ["a", "b", "c"]  (merged!)
```

## Built-in Reducers

### add_messages

The most commonly used reducer for chat applications:

```python
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

messages: Annotated[list[AnyMessage], add_messages]
```

**Features:**
- Appends new messages
- Deduplicates by message ID
- Updates existing messages (same ID)
- Preserves order

**Example:**
```python
@dataclass(kw_only=True)
class State:
    messages: Annotated[list[AnyMessage], add_messages]

# Initial
state = State(messages=[HumanMessage(content="Hi")])

# Update 1
update_1 = {"messages": [AIMessage(content="Hello")]}
# Result: [HumanMessage("Hi"), AIMessage("Hello")]

# Update 2
update_2 = {"messages": [HumanMessage(content="How are you?")]}
# Result: [HumanMessage("Hi"), AIMessage("Hello"), HumanMessage("How are you?")]
```

**Message ID behavior:**
```python
# Same ID = replace
msg_1 = AIMessage(content="First", id="msg-1")
msg_2 = AIMessage(content="Updated", id="msg-1")

state = State(messages=[msg_1])
update = {"messages": [msg_2]}
# Result: [AIMessage("Updated", id="msg-1")]  (replaced)
```

## Custom Reducers

### Reducer Signature

```python
def my_reducer(existing: T, new: T) -> T:
    """
    Args:
        existing: Current value in state
        new: New value from node update

    Returns:
        Merged value
    """
    return merged_value
```

### Simple Append

```python
def append_list(existing: list, new: list) -> list:
    """Append new items to existing list."""
    return existing + new

@dataclass(kw_only=True)
class State:
    items: Annotated[list[str], append_list] = None
```

**Usage:**
```python
# Initial: items = []
# Update: {"items": ["a", "b"]}
# Result: items = ["a", "b"]

# Update: {"items": ["c"]}
# Result: items = ["a", "b", "c"]
```

### Sum/Counter

```python
def sum_reducer(existing: int, new: int) -> int:
    """Add new value to existing."""
    return existing + new

@dataclass(kw_only=True)
class State:
    total: Annotated[int, sum_reducer] = 0
```

**Usage:**
```python
# Initial: total = 0
# Update: {"total": 5}
# Result: total = 5

# Update: {"total": 3}
# Result: total = 8
```

### Max/Min

```python
def max_reducer(existing: float, new: float) -> float:
    """Keep maximum value."""
    return max(existing, new)

@dataclass(kw_only=True)
class State:
    max_score: Annotated[float, max_reducer] = float('-inf')
```

**Usage:**
```python
# Initial: max_score = -inf
# Update: {"max_score": 5.0}
# Result: max_score = 5.0

# Update: {"max_score": 3.0}
# Result: max_score = 5.0  (unchanged)

# Update: {"max_score": 10.0}
# Result: max_score = 10.0  (updated)
```

### Unique Append

```python
def append_unique(existing: list, new: list) -> list:
    """Append only unique items."""
    result = existing.copy() if existing else []
    for item in new:
        if item not in result:
            result.append(item)
    return result

@dataclass(kw_only=True)
class State:
    tags: Annotated[list[str], append_unique] = None
```

**Usage:**
```python
# Initial: tags = []
# Update: {"tags": ["python", "langgraph"]}
# Result: tags = ["python", "langgraph"]

# Update: {"tags": ["langgraph", "ai"]}
# Result: tags = ["python", "langgraph", "ai"]  (no duplicate)
```

### Merge Dictionaries

```python
def merge_dict(existing: dict, new: dict) -> dict:
    """Merge dictionaries (new overrides existing)."""
    return {**existing, **new}

@dataclass(kw_only=True)
class State:
    metadata: Annotated[dict, merge_dict] = None
```

**Usage:**
```python
# Initial: metadata = {}
# Update: {"metadata": {"key1": "value1"}}
# Result: metadata = {"key1": "value1"}

# Update: {"metadata": {"key2": "value2"}}
# Result: metadata = {"key1": "value1", "key2": "value2"}

# Update: {"metadata": {"key1": "updated"}}
# Result: metadata = {"key1": "updated", "key2": "value2"}
```

### Conditional Update

```python
def update_if_better(existing: str, new: str) -> str:
    """Update only if new value is longer."""
    if not existing or len(new) > len(existing):
        return new
    return existing

@dataclass(kw_only=True)
class State:
    best_response: Annotated[str, update_if_better] = ""
```

**Usage:**
```python
# Initial: best_response = ""
# Update: {"best_response": "Short"}
# Result: best_response = "Short"

# Update: {"best_response": "Hi"}
# Result: best_response = "Short"  (unchanged)

# Update: {"best_response": "Much longer response"}
# Result: best_response = "Much longer response"
```

## Reducer Patterns

### Pattern 1: Accumulate Data

```python
def accumulate(existing: list, new: list) -> list:
    return (existing or []) + new

results: Annotated[list[dict], accumulate] = None
```

### Pattern 2: Track History

```python
def track_history(existing: list, new: any) -> list:
    """Keep history of all values."""
    history = existing or []
    return history + [{"value": new, "timestamp": datetime.now()}]

value_history: Annotated[list[dict], track_history] = None
```

### Pattern 3: Sliding Window

```python
def sliding_window(existing: list, new: list, window_size: int = 10) -> list:
    """Keep only last N items."""
    combined = (existing or []) + new
    return combined[-window_size:]

# Partial application
from functools import partial
window_10 = partial(sliding_window, window_size=10)

recent_items: Annotated[list, window_10] = None
```

### Pattern 4: Aggregate Statistics

```python
@dataclass
class Stats:
    count: int = 0
    sum: float = 0
    min: float = float('inf')
    max: float = float('-inf')

def update_stats(existing: Stats, new: float) -> Stats:
    return Stats(
        count=existing.count + 1,
        sum=existing.sum + new,
        min=min(existing.min, new),
        max=max(existing.max, new)
    )

statistics: Annotated[Stats, update_stats] = Stats()
```

### Pattern 5: Set Operations

```python
def union_sets(existing: set, new: set) -> set:
    """Union of sets."""
    return (existing or set()) | new

def intersection_sets(existing: set, new: set) -> set:
    """Intersection of sets."""
    if not existing:
        return new
    return existing & new

tags: Annotated[set[str], union_sets] = None
common: Annotated[set[str], intersection_sets] = None
```

## Advanced Usage

### Lambda Reducers

For simple reducers, use lambda:

```python
@dataclass(kw_only=True)
class State:
    # Append lists
    items: Annotated[list, lambda old, new: old + new] = None

    # Sum numbers
    total: Annotated[int, lambda old, new: old + new] = 0

    # Max value
    best: Annotated[float, lambda old, new: max(old, new)] = 0.0

    # Merge dicts
    config: Annotated[dict, lambda old, new: {**old, **new}] = None
```

### Nested Reducers

Reducers for nested structures:

```python
def merge_nested_dict(existing: dict, new: dict) -> dict:
    """Deep merge dictionaries."""
    result = existing.copy() if existing else {}

    for key, value in new.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_nested_dict(result[key], value)
        else:
            result[key] = value

    return result

@dataclass(kw_only=True)
class State:
    config: Annotated[dict, merge_nested_dict] = None
```

**Usage:**
```python
# Initial: config = {"api": {"timeout": 30}}
# Update: {"config": {"api": {"retries": 3}}}
# Result: config = {"api": {"timeout": 30, "retries": 3}}
```

### Conditional Reducers

Reducers with conditions:

```python
def smart_update(existing: dict, new: dict) -> dict:
    """Update with validation."""
    result = existing.copy() if existing else {}

    for key, value in new.items():
        # Only update if value is not None
        if value is not None:
            result[key] = value

    return result

metadata: Annotated[dict, smart_update] = None
```

### Reducer with State Context

Access full state in reducer (advanced):

```python
class StateAwareReducer:
    """Reducer that needs state context."""

    def __init__(self, state_accessor):
        self.state_accessor = state_accessor

    def __call__(self, existing, new):
        # Access full state
        state = self.state_accessor()

        # Make decision based on state
        if state.some_condition:
            return existing + new
        else:
            return new

# Use in graph building
# (This is advanced and rarely needed)
```

### Type-Safe Reducers

Reducers with proper typing:

```python
from typing import TypeVar, Callable

T = TypeVar('T')

def make_append_reducer() -> Callable[[list[T], list[T]], list[T]]:
    """Factory for type-safe append reducer."""
    def append(existing: list[T], new: list[T]) -> list[T]:
        return (existing or []) + new
    return append

@dataclass(kw_only=True)
class State:
    items: Annotated[list[str], make_append_reducer()] = None
```

## Common Mistakes

### Mistake 1: Forgetting Default Values

```python
# ❌ Bad: No default for reducer field
@dataclass(kw_only=True)
class State:
    items: Annotated[list[str], append_list]

# ✅ Good: Provide default
@dataclass(kw_only=True)
class State:
    items: Annotated[list[str], append_list] = None
```

### Mistake 2: Wrong Reducer Logic

```python
# ❌ Bad: Returns existing instead of new when None
def bad_append(existing: list, new: list) -> list:
    if not existing:
        return []  # Wrong! Should return new
    return existing + new

# ✅ Good: Handle None correctly
def good_append(existing: list, new: list) -> list:
    if existing is None:
        return new
    return existing + new
```

### Mistake 3: Mutating Input

```python
# ❌ Bad: Mutates existing
def bad_merge(existing: dict, new: dict) -> dict:
    existing.update(new)  # Mutates!
    return existing

# ✅ Good: Create new object
def good_merge(existing: dict, new: dict) -> dict:
    return {**existing, **new}
```

### Mistake 4: Using Reducer for Replace Behavior

```python
# ❌ Bad: Reducer not needed
status: Annotated[str, lambda old, new: new]

# ✅ Good: No reducer for replace
status: str
```

## When to Use Reducers

**Use reducers when:**
- ✅ Accumulating data (lists, counts, sums)
- ✅ Merging data (dicts, sets)
- ✅ Tracking history or changes
- ✅ Messages in chat applications

**Don't use reducers when:**
- ❌ Simple replace behavior is needed
- ❌ Only one node updates the field
- ❌ Field represents current status/state

## Quick Reference

```python
# Common reducers
from typing import Annotated
from langgraph.graph.message import add_messages

# Messages
messages: Annotated[list[AnyMessage], add_messages]

# Append lists
items: Annotated[list, lambda old, new: old + new] = None

# Sum numbers
total: Annotated[int, lambda old, new: old + new] = 0

# Max value
best: Annotated[float, lambda old, new: max(old, new)] = 0.0

# Merge dicts
config: Annotated[dict, lambda old, new: {**old, **new}] = None

# Union sets
tags: Annotated[set, lambda old, new: old | new] = None
```

## References

- LangGraph Reducers: https://docs.langchain.com/oss/python/langgraph/graph-api#reducers
- Python Annotated: https://docs.python.org/3/library/typing.html#typing.Annotated
- Messages: https://docs.langchain.com/oss/python/langchain/messages
