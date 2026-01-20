# State Definition

State is defined in `casts/{cast_name}/modules/state.py` using `TypedDict`.

## Contents

- Basic State
- With Messages (Most Common)
- Reducers
- Input/Output Schemas
- Private State
- Complete Example

## Basic State

```python
# casts/{cast_name}/modules/state.py
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str
```

---

## With Messages (Most Common)

Use `MessagesState` for chat-based graphs:

```python
# casts/{cast_name}/modules/state.py
from langgraph.graph import MessagesState

class State(MessagesState):
    """State with messages and custom fields."""
    user_id: str
    documents: list[str]
```

Or manually with `add_messages` reducer:

```python
# casts/{cast_name}/modules/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: str
```

---

## Reducers

Reducers define how state updates are applied.

| Reducer | Behavior |
|---------|----------|
| None (default) | Overwrite value |
| `operator.add` | Append lists |
| `add_messages` | Smart message handling (update by ID or append) |

```python
# casts/{cast_name}/modules/state.py
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    count: int                              # Overwrite
    items: Annotated[list[str], add]        # Append
```

---

## Input/Output Schemas

Constrain graph input and output:

```python
# casts/{cast_name}/modules/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

class InputState(TypedDict):
    """What the graph accepts as input."""
    query: str

class OutputState(TypedDict):
    """What the graph returns as output."""
    result: str

class State(TypedDict):
    """Internal state (superset of Input/Output)."""
    query: str
    result: str
    messages: Annotated[list[AnyMessage], add_messages]
    intermediate_data: dict  # Not exposed in input/output
```

```python
# casts/{cast_name}/graph.py
from casts.{cast_name}.modules.state import State, InputState, OutputState

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(
            State,
            input_schema=InputState,
            output_schema=OutputState
        )
        # ...
```

---

## Private State

For internal node communication:

```python
# casts/{cast_name}/modules/state.py
from typing_extensions import TypedDict

class State(TypedDict):
    user_input: str
    graph_output: str

class PrivateState(TypedDict):
    """Internal state not exposed to input/output."""
    intermediate_result: str
```

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode

class InternalNode(BaseNode):
    def execute(self, state):
        # Can write to PrivateState keys
        return {"intermediate_result": "processed"}

class OutputNode(BaseNode):
    def execute(self, state):
        # Read from PrivateState, write to State
        return {"graph_output": state["intermediate_result"]}
```

---

## Complete Example

```python
# casts/{cast_name}/modules/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

class InputState(TypedDict):
    """Graph input schema."""
    query: str
    user_id: str

class OutputState(TypedDict):
    """Graph output schema."""
    messages: Annotated[list[AnyMessage], add_messages]
    result: str

class State(TypedDict):
    """Full internal state."""
    # From InputState
    query: str
    user_id: str
    # From OutputState
    messages: Annotated[list[AnyMessage], add_messages]
    result: str
    # Internal only
    context: str
    processing_status: str
```
