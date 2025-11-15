# Short-Term Memory

## When to Use This Resource

Read this for in-session memory via state (conversation history, task context within single run).

## Key Concept

**Short-term memory = State.** Data persists across nodes within a single graph execution.

## Pattern: Message History

```python
from typing import Annotated
from operator import add
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add]  # Accumulates
```

**Access in node:**
```python
def execute(self, state: AgentState) -> dict:
    # Full conversation history
    history = state["messages"]
    last_message = history[-1]
    return {"messages": [AIMessage(content="Response")]}
```

## Pattern: Task Context

```python
class State(TypedDict):
    current_task: str  # Current task being processed
    completed_tasks: Annotated[list[str], add]  # Tasks done
    context: dict  # Working data
```

## Pattern: Iteration Tracking

```python
class State(TypedDict):
    iteration_count: Annotated[int, add]
    max_iterations: int
```

**Check in condition:**
```python
def should_continue(state) -> str:
    if state["iteration_count"] >= state["max_iterations"]:
        return "end"
    return "continue"
```

## When NOT Short-Term

- Data needed across sessions → Long-term memory
- Data needed after graph ends → Checkpointer
- User preferences → Long-term memory

## Decision

Within single run? → Short-term (state)
Across runs? → Long-term (Store)

## References

- State details: `01-core/state.md`
- Long-term: `03-memory/long-term-memory.md`
