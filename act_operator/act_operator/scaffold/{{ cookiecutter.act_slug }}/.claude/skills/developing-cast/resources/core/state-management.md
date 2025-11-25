# State Management

## When to Use This Resource
Read this when implementing state schemas, adding reducers, or deciding how state should flow through your graph.

## Key Concepts

**State** = A shared data structure representing the current snapshot of your graph's execution. Typically a TypedDict or Pydantic BaseModel.

**Channel** = A key in your state schema (e.g., `messages`, `context`, `result`).

**Reducer** = A function determining how state updates are applied (e.g., append vs replace).

## State Schema Options

### Option 1: TypedDict (Recommended for Most Cases)
**When to use:** Simple state with basic types, minimal validation needs.

```python
from typing import TypedDict, Annotated
from langgraph.graph import add

class GraphState(TypedDict):
    input: str                    # Simple field (replace on update)
    messages: Annotated[         # List field (append on update)
        list[dict],
        add                       # Built-in reducer: appends new items
    ]
    result: str | None            # Optional field
```

**Trade-offs:**
- ✅ Lightweight, fast
- ✅ Type hints for IDE support
- ❌ Limited validation

### Option 2: Pydantic BaseModel
**When to use:** Need validation, default values, computed fields.

```python
from pydantic import BaseModel, Field
from typing import Annotated
from langgraph.graph import add

class GraphState(BaseModel):
    input: str = Field(..., min_length=1)  # Validated input
    messages: Annotated[list[dict], add] = Field(default_factory=list)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
```

**Trade-offs:**
- ✅ Built-in validation
- ✅ Default values
- ✅ Computed fields
- ❌ Slightly heavier

## Reducer Patterns

### Built-in Reducers
```python
from langgraph.graph import add  # Append items to list

# Usage
from typing import Annotated

messages: Annotated[list[dict], add]
```

### Custom Reducers
**When to use:** Need merge logic beyond simple append/replace.

```python
from typing import Annotated

def merge_context(existing: dict, new: dict) -> dict:
    """Merge two dicts, with new values overwriting existing."""
    return {**existing, **new}

# Usage in state
context: Annotated[dict, merge_context]
```

**Common custom reducer patterns:**
- **Merge dicts:** Combine dictionaries
- **Deduplicate lists:** Remove duplicates before appending
- **Accumulate numbers:** Sum or calculate running totals
- **Latest value:** Keep most recent from multiple updates

## Decision Framework

```
Need validation or defaults?
├─ Yes → Pydantic BaseModel
└─ No  → TypedDict

Field updates should:
├─ Replace existing value → No annotation
├─ Append to list → Annotated[list, add]
└─ Custom merge logic → Annotated[type, custom_reducer]

State growing too large?
└─ Split into multiple channels
   └─ Use separate keys for input/working/output data
```

## Act Project Convention

⚠️ **State Location:** `casts/[cast_name]/state.py`

**Example structure:**
```python
# casts/{ cast_name }/modules/state.py
from typing import TypedDict, Annotated
from langgraph.graph import add

class MyCastState(TypedDict):
    """State for MyCast graph."""
    input: str
    messages: Annotated[list[dict], add]
    result: str | None
```

## Common Mistakes

❌ **Storing too much in state**
- State persists across checkpoints
- Keep only essential data
- Store large objects elsewhere (files, databases)

❌ **Forgetting reducers for lists**
```python
# Wrong - will replace entire list
messages: list[dict]

# Right - appends to list
messages: Annotated[list[dict], add]
```

❌ **Mutable defaults in TypedDict**
```python
# Wrong - shared mutable default
class State(TypedDict):
    items: list = []  # ❌ Don't do this

# Right - use Pydantic or None
items: list | None  # Initialize in first node
```

## State Update Pattern

Nodes return dictionaries with state updates:

```python
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state: GraphState) -> dict:
        # Update specific fields
        return {
            "result": "processed",
            "messages": [{"role": "ai", "content": "done"}]
        }
```

**Key points:**
- Return only fields you're updating
- LangGraph merges with existing state
- Reducers determine merge behavior

