# Access and Modify Memory

## Contents

- In Tools (Read State, Write State)
- In Middleware (Dynamic Prompt, Before Model - Trim Messages, After Model - Validate Response)

## In Tools

### Read State

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool, ToolRuntime
from langchain.agents import AgentState

class CustomState(AgentState):
    user_id: str

@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_id = runtime.state["user_id"]
    return "User is John Smith" if user_id == "user_123" else "Unknown user"
```

### Write State

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from langgraph.types import Command

@tool
def update_user_info(runtime: ToolRuntime) -> Command:
    """Update user info in state."""
    return Command(update={
        "user_name": "John Smith",
        "messages": [
            ToolMessage("Updated user info", tool_call_id=runtime.tool_call_id)
        ]
    })
```

---

## In Middleware

### Dynamic Prompt from Context

```python
# casts.{cast_name}.modules.middlewares
from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest

class CustomContext(TypedDict):
    user_name: str

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context["user_name"]
    return f"You are a helpful assistant. Address user as {user_name}."
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import dynamic_system_prompt, CustomContext

def set_dynamic_prompt_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[dynamic_system_prompt],
        context_schema=CustomContext,
    )
```

### Before Model - Trim Messages

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
    """Keep only last few messages."""
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

### After Model - Validate Response

```python
# casts.{cast_name}.modules.middlewares
from langchain.messages import RemoveMessage
from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]
    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    return None
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from .middlewares import trim_messages, validate_response

def set_memory_managed_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[trim_messages, validate_response],
        checkpointer=InMemorySaver(),
    )
```
