# Tool Runtime Access

Use `ToolRuntime` to access state, context, store, and stream writer. The `runtime` parameter is hidden from the model.

## Contents

- Access State
- Update State
- Access Context
- Access Store (Long-term Memory)
- Stream Writer

## Access State

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool, ToolRuntime

@tool
def summarize_conversation(runtime: ToolRuntime) -> str:
    """Summarize the conversation so far."""
    messages = runtime.state["messages"]
    human_msgs = sum(1 for m in messages if m.__class__.__name__ == "HumanMessage")
    ai_msgs = sum(1 for m in messages if m.__class__.__name__ == "AIMessage")
    return f"Conversation has {human_msgs} user messages, {ai_msgs} AI responses"

@tool
def get_user_preference(pref_name: str, runtime: ToolRuntime) -> str:
    """Get a user preference value."""
    preferences = runtime.state.get("user_preferences", {})
    return preferences.get(pref_name, "Not set")
```

## Update State

Use `Command` to update agent state:

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

@tool
def clear_conversation() -> Command:
    """Clear the conversation history."""
    return Command(
        update={"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]}
    )

@tool
def update_user_name(new_name: str, runtime: ToolRuntime) -> Command:
    """Update the user's name."""
    return Command(update={"user_name": new_name})
```

## Access Context

Access immutable configuration (user IDs, session info):

```python
# casts.{cast_name}.modules.tools
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class UserContext:
    user_id: str

@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Get the current user's account information."""
    user_id = runtime.context.user_id
    # Look up user in database
    return f"Account info for user: {user_id}"
```

```python
# casts.{cast_name}.modules.agents
from dataclasses import dataclass
from langchain.agents import create_agent
from .models import get_sample_model
from .tools import get_account_info

@dataclass
class UserContext:
    user_id: str

def set_context_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[get_account_info],
        context_schema=UserContext,
    )
```

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .agents import set_context_agent, UserContext

class ContextNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_context_agent()

    def execute(self, state):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": state["query"]}]},
            context=UserContext(user_id="user123")
        )
        return {"messages": result["messages"]}
```

## Access Store (Long-term Memory)

```python
# casts.{cast_name}.modules.tools
from typing import Any
from langchain.tools import tool, ToolRuntime

@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Look up user info from memory."""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """Save user info to memory."""
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info."
```

```python
# casts.{cast_name}.modules.agents
from langgraph.store.memory import InMemoryStore
from langchain.agents import create_agent
from .models import get_sample_model
from .tools import get_user_info, save_user_info

def set_memory_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[get_user_info, save_user_info],
        store=InMemoryStore(),
    )
```

## Stream Writer

Stream custom updates during tool execution:

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool, ToolRuntime

@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Get weather for a given city."""
    writer = runtime.stream_writer
    writer(f"Looking up data for city: {city}")
    writer(f"Acquired data for city: {city}")
    return f"It's always sunny in {city}!"
```
