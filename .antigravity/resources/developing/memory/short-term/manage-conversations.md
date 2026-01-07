# Manage Conversations

Strategies for handling long conversations that exceed context windows.

## Contents

- Trim Messages
- Delete Messages (Specific, All)
- Summarize Messages
- Combined Strategy

## Trim Messages

Keep only recent messages using `@before_model` middleware.

```python
# casts.{cast_name}.modules.middlewares
from typing import Any
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime

@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep first message + last N messages."""
    messages = state["messages"]
    if len(messages) <= 3:
        return None
    
    first_msg = messages[0]
    recent = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *([first_msg] + recent)
        ]
    }
```

---

## Delete Messages

Remove specific messages from state using `RemoveMessage`.

### Delete Specific Messages

```python
# casts.{cast_name}.modules.middlewares
from langchain.messages import RemoveMessage
from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime

@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove earliest two messages."""
    messages = state["messages"]
    if len(messages) > 2:
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None
```

### Delete All Messages

```python
# casts.{cast_name}.modules.middlewares
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

def delete_all_messages(state):
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]}
```

**Warning:** Ensure valid message history after deletion:
- Some providers require history to start with `user` message
- `assistant` messages with tool calls must be followed by `tool` results

---

## Summarize Messages

Use built-in `SummarizationMiddleware` to compress history.

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

def set_summarizing_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[
            SummarizationMiddleware(
                model="gpt-4o-mini",        # Summarization model
                trigger={"tokens": 4000},    # When to trigger
                keep={"messages": 20},       # Messages to preserve
            )
        ],
        checkpointer=InMemorySaver(),
    )
```

---

## Combined Strategy

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from .middlewares import trim_messages, validate_response

def set_fully_managed_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[
            trim_messages,
            SummarizationMiddleware(
                model="gpt-4o-mini",
                trigger={"tokens": 4000},
                keep={"messages": 20},
            ),
            validate_response,
        ],
        checkpointer=InMemorySaver(),
    )
```
