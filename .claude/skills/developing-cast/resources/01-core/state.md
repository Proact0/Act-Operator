# State Implementation

## When to Use This Resource

Read this when defining state schemas, setting up reducers, or fixing state update issues.

## Key Concepts

**State:** Shared data structure passed between nodes, representing the current snapshot of your graph execution.

**Schema:** TypedDict, dataclass, or Pydantic model defining state structure.

**Channel:** Individual key in the state schema (e.g., `messages`, `count`, `data`).

**Reducer:** Function determining how state updates are applied (replace, append, merge).

## State Schema Patterns

### Pattern 1: TypedDict (Most Common)

**When to use:** Simple state structures, Python 3.9+

```python
from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    """State for basic agent."""
    messages: Annotated[list, add]  # Append messages
    user_input: str  # Replace on update
    results: dict  # Replace on update
```

**Why TypedDict:**
- Native Python type hinting
- No dependencies beyond typing
- IDE autocomplete support
- Lightweight and fast

### Pattern 2: Pydantic (Data Validation)

**When to use:** Need validation, complex nested data, strict types

```python
from pydantic import BaseModel, Field
from typing import Annotated
from operator import add

class AgentState(BaseModel):
    """State with validation."""
    messages: Annotated[list, add] = Field(default_factory=list)
    user_id: str = Field(min_length=1)
    score: float = Field(ge=0, le=100)

    class Config:
        arbitrary_types_allowed = True
```

**Why Pydantic:**
- Automatic validation
- Better error messages
- Complex type constraints
- JSON serialization built-in

### Pattern 3: Dataclass (Python 3.7+)

**When to use:** Simpler than Pydantic, need default values

```python
from dataclasses import dataclass, field
from typing import Annotated
from operator import add

@dataclass
class AgentState:
    """State with defaults."""
    messages: Annotated[list, add] = field(default_factory=list)
    count: int = 0
    active: bool = True
```

## Reducers: Controlling State Updates

### What Are Reducers?

Reducers tell LangGraph **how** to merge new values with existing state:
```python
new_state_value = reducer(old_state_value, update_value)
```

Without reducer: **replaces** value (default behavior)
With reducer: **merges** value (custom behavior)

### Built-in Reducers

#### operator.add (Append/Concatenate)

**Use for:** Lists, strings, numbers you want to accumulate

```python
from typing import Annotated
from operator import add

class State(TypedDict):
    messages: Annotated[list, add]  # [a] + [b] = [a, b]
    text: Annotated[str, add]  # "hello" + " world" = "hello world"
    count: Annotated[int, add]  # 5 + 3 = 8
```

**Node returns:**
```python
def execute(self, state: State) -> dict:
    return {"messages": [new_message]}  # Appends, doesn't replace
```

#### Custom Reducers

**Use for:** Complex merge logic, dictionaries, special accumulation

```python
from typing import Annotated

def merge_dicts(existing: dict, update: dict) -> dict:
    """Merge dictionaries, updating existing keys."""
    return {**existing, **update}

def append_unique(existing: list, update: list) -> list:
    """Append only unique items."""
    result = existing.copy()
    for item in update:
        if item not in result:
            result.append(item)
    return result

class State(TypedDict):
    metadata: Annotated[dict, merge_dicts]
    tags: Annotated[list, append_unique]
```

## State in Act Projects

### Location
- Define in: `casts/[cast_name]/state.py`
- Import in: `casts/[cast_name]/graph.py`

### Example Structure

**File:** `casts/my_agent/state.py`
```python
from typing import TypedDict, Annotated
from operator import add
from langchain_core.messages import BaseMessage

class MyAgentState(TypedDict):
    """State for MyAgent cast.

    Attributes:
        messages: Conversation history (appends)
        current_task: Current task description (replaces)
        results: Accumulated results (replaces)
        step_count: Number of steps executed (adds)
    """
    messages: Annotated[list[BaseMessage], add]
    current_task: str
    results: dict
    step_count: Annotated[int, add]
```

## Accessing State in Nodes

### In execute() Method

```python
from casts.base_node import BaseNode
from casts.my_agent.state import MyAgentState

class ProcessNode(BaseNode):
    """Process task from state."""

    def execute(self, state: MyAgentState) -> dict:
        # Access state fields
        task = state["current_task"]
        previous_results = state.get("results", {})

        # Process
        result = self.process_task(task, previous_results)

        # Return updates (respects reducers)
        return {
            "messages": [AIMessage(content=f"Processed: {task}")],
            "results": result,  # Replaces
            "step_count": 1,  # Adds to existing
        }
```

### Type Hints for IDE Support

```python
def execute(self, state: MyAgentState) -> dict:
    # IDE knows state["messages"] is list[BaseMessage]
    last_message = state["messages"][-1]
    # IDE autocompletes state keys
    task = state["current_task"]
```

## Common Patterns

### Message Accumulation (Chat/Agent)

```python
from langchain_core.messages import BaseMessage
from typing import Annotated
from operator import add

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add]
```

**Why:** Preserves conversation history across nodes.

### Counter/Metrics

```python
class State(TypedDict):
    step_count: Annotated[int, add]
    error_count: Annotated[int, add]
```

**Why:** Track execution metrics without manual accumulation.

### Tool Results Accumulation

```python
class State(TypedDict):
    tool_calls: Annotated[list[dict], add]
```

**Why:** Preserve all tool invocations for debugging/replay.

### Replace vs Accumulate

```python
class State(TypedDict):
    # Accumulate (with add reducer)
    history: Annotated[list, add]

    # Replace (no reducer)
    current_value: str
    latest_result: dict
```

## Decision Framework

```
Need to track conversation history?
  → messages: Annotated[list[BaseMessage], add]

Need to count/sum values across nodes?
  → counter: Annotated[int, add]

Need to collect results from multiple nodes?
  → results: Annotated[list, add]

Need to store current/latest value only?
  → value: str  (no reducer)

Need complex merge logic?
  → custom_data: Annotated[dict, custom_reducer]

Need validation/constraints?
  → Use Pydantic BaseModel instead of TypedDict
```

## Common Mistakes

### ❌ Forgetting Reducer for Lists

```python
# BAD: Node overwrites entire list
class State(TypedDict):
    messages: list  # No reducer!

def execute(self, state) -> dict:
    return {"messages": [new_msg]}  # Loses previous messages!
```

**Fix:**
```python
# GOOD: Messages accumulate
class State(TypedDict):
    messages: Annotated[list, add]

def execute(self, state) -> dict:
    return {"messages": [new_msg]}  # Appends to existing
```

### ❌ Wrong Reducer Type

```python
# BAD: Using add for dict
class State(TypedDict):
    data: Annotated[dict, add]  # dicts don't support +
```

**Fix:**
```python
# GOOD: Custom merger or no reducer
def merge_dicts(a: dict, b: dict) -> dict:
    return {**a, **b}

class State(TypedDict):
    data: Annotated[dict, merge_dicts]
```

### ❌ Returning Wrong Type from Node

```python
class State(TypedDict):
    count: Annotated[int, add]

def execute(self, state) -> dict:
    return {"count": "5"}  # String, not int!
```

**Fix:**
```python
def execute(self, state) -> dict:
    return {"count": 5}  # Correct type
```

### ❌ Not Returning Dict from execute()

```python
# BAD
def execute(self, state):
    state["value"] = "new"  # Mutates state directly
    return state  # Returns entire state
```

**Fix:**
```python
# GOOD
def execute(self, state) -> dict:
    return {"value": "new"}  # Returns only updates
```

## Act Project Conventions

⚠️ **File location:**
- State MUST be in: `casts/[cast_name]/state.py`
- Import in graph: `from casts.[cast_name].state import [StateClass]`

⚠️ **Naming:**
- Class name: `[CastName]State` (e.g., `ResearchAgentState`)
- One state class per cast

⚠️ **Documentation:**
- Docstring explaining purpose
- Docstring listing all attributes with descriptions
- Comment indicating reducer behavior

## Anti-Patterns

- ❌ **Storing LLM instances in state** → Pass in constructor or config
- ❌ **Storing non-serializable objects** → State must be checkpoint-able
- ❌ **Deeply nested state** → Keep flat, use separate keys
- ❌ **State without type hints** → Always use TypedDict/Pydantic
- ❌ **Mutable defaults without factory** → Use `field(default_factory=list)`

## References

- LangGraph State Docs: https://docs.langchain.com/oss/python/langgraph/use-graph-api
- Related resources: `01-core/nodes.md`, `01-core/graph.md`
